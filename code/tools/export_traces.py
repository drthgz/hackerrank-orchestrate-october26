"""Export relevant Codex rollout snapshots; rerun after closing the active app.

Original traces remain untouched. Only sessions whose authoritative metadata cwd
matches this checkout are included. This is separate from code.zip.
"""
import argparse
import json
import os
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[2]


def redact(text):
    text = re.sub(r'\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b', '[REDACTED]', text)
    return re.sub(r'(?i)((?:api[_-]?key|access[_-]?token|authorization|password|client[_-]?secret)\s*[=:]\s*)(["\']?)([^\s"\']{8,})', r'\1[REDACTED]', text)


def export(sessions):
    selected=[]
    for path in sessions.rglob('rollout-*.jsonl'):
        with path.open(encoding='utf-8') as source:
            first=source.readline()
        try:
            item=json.loads(first)
        except json.JSONDecodeError:
            continue
        if item.get('type')=='session_meta' and Path(item['payload'].get('cwd','')).resolve()==ROOT:
            selected.append(path)
    with ZipFile(ROOT/'agent-trace.zip','w',ZIP_DEFLATED) as archive:
        manifest=[]
        for path in sorted(selected):
            lines=[]; incomplete=0
            for line in path.read_text(encoding='utf-8').splitlines():
                try:
                    record=json.loads(line)
                except json.JSONDecodeError:
                    incomplete+=1
                    continue
                def sanitize(value):
                    if isinstance(value,str): return redact(value)
                    if isinstance(value,list): return [sanitize(x) for x in value]
                    if isinstance(value,dict): return {k:sanitize(v) for k,v in value.items()}
                    return value
                lines.append(json.dumps(sanitize(record),ensure_ascii=False))
            name='agent-trace/codex/'+path.relative_to(sessions).as_posix()
            archive.writestr(name,'\n'.join(lines)+'\n')
            manifest.append(dict(file=name,records=len(lines),incomplete_trailing_lines=incomplete))
        archive.writestr('agent-trace/README.md', '# Trace snapshot\n\nRelevant local Codex sessions only. Credential patterns redacted; originals unchanged. '
                         'The active session is a snapshot, not a complete post-quit export. Close Codex, then rerun '
                         '`python3 code/tools/export_traces.py` externally before uploading. No auth/config/credential stores included.\n')
        archive.writestr('agent-trace/manifest.json',json.dumps(manifest,indent=2)+'\n')
    print(f'Exported {len(selected)} relevant session snapshots; active session must be refreshed after app exit.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--sessions',type=Path,default=Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'sessions')
    export(parser.parse_args().sessions)
