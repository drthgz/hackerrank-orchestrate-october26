"""Small stdlib-only client. No retries; reserve costs before network access."""
import json
import os
import re
import time
import urllib.request
from pathlib import Path

MODEL = 'gpt-4.1-mini-2025-04-14'
INPUT_RATE, CACHED_RATE, OUTPUT_RATE = .40, .10, 1.60  # USD / million tokens
MAX_OUTPUT = 6000


def load_key(path):
    # Parse data; never source/execute .env shell statements.
    if not os.environ.get('OPENAI_API_KEY'):
        for line in Path(path).read_text().splitlines():
            match = re.fullmatch(r'\s*(?:export\s+)?OPENAI_API_KEY\s*=\s*(.*?)\s*', line)
            if match:
                value = match[1]
                if value[:1] in {'"', "'"} and value[-1:] == value[:1]:
                    value = value[1:-1]
                os.environ['OPENAI_API_KEY'] = value
    if not os.environ.get('OPENAI_API_KEY'):
        raise RuntimeError('Missing API key')


class Client:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.ledger = self.directory / 'usage.json'

    def call(self, tag, messages, schema):
        cache = self.directory / (tag + '.json')
        if cache.exists():
            return json.loads(cache.read_text())
        payload = dict(model=MODEL, temperature=0, max_completion_tokens=MAX_OUTPUT,
                       messages=messages, store=False,
                       response_format={'type': 'json_schema', 'json_schema': {
                           'name': 'deletion_audit', 'strict': True, 'schema': schema}})
        data = json.dumps(payload, ensure_ascii=True).encode()
        # UTF-8 byte count is a conservative text-token ceiling. Add framing
        # allowance; no tools, images, retries, or unbounded reasoning tokens.
        reserve = ((len(data) + 4096) * INPUT_RATE + MAX_OUTPUT * OUTPUT_RATE) / 1e6
        # Exclusive lock prevents concurrent reservations; fail closed on stale lock.
        lock = self.directory / 'budget.lock'
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            ledger = json.loads(self.ledger.read_text()) if self.ledger.exists() else []
            if sum(x['reserved_usd'] for x in ledger) + reserve >= 1:
                raise RuntimeError('Experiment budget exhausted')
            if sum(x['status']=='completed' for x in ledger) >= 16:
                raise RuntimeError('Eight-case two-arm call limit reached')
            row = dict(tag=tag, model=MODEL, reserved_usd=reserve, status='reserved',
                       parameters={'temperature': 0, 'max_completion_tokens': MAX_OUTPUT})
            ledger.append(row)
            self.ledger.write_text(json.dumps(ledger, indent=2) + '\n')
            started = time.perf_counter()
            request = urllib.request.Request('https://api.openai.com/v1/chat/completions', data=data,
                      headers={'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY'],
                               'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    result = json.load(response)
            except Exception as exc:
                row.update(status='uncertain_failure', error_type=type(exc).__name__,
                           latency_seconds=time.perf_counter()-started)
                self.ledger.write_text(json.dumps(ledger, indent=2) + '\n')
                raise RuntimeError('API request failed; reservation retained; no automatic retry') from None
            usage = result['usage']
            cached = usage.get('prompt_tokens_details', {}).get('cached_tokens', 0)
            cost = ((usage['prompt_tokens']-cached)*INPUT_RATE + cached*CACHED_RATE +
                    usage['completion_tokens']*OUTPUT_RATE)/1e6
            row.update(status='completed', usage=usage, estimated_cost_usd=cost,
                       response_model=result['model'], latency_seconds=time.perf_counter()-started)
            self.ledger.write_text(json.dumps(ledger, indent=2) + '\n')
            cache.write_text(json.dumps(result, indent=2) + '\n')
            if cost > reserve:
                raise RuntimeError('Usage exceeded conservative reservation; stop')
            return result
        finally:
            os.close(fd)
            lock.unlink()
