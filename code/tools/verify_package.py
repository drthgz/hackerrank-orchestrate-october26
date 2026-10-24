"""Replay the source archive in a fresh extraction and dependency-free venv.

The supplied participant dataset is attached outside the archive, as documented.
No experiment client or model endpoint is imported. Subprocess credentials are
not inherited. Diagnostics report incomplete coverage without manufacturing rows.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import venv
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]


def verify():
    with tempfile.TemporaryDirectory(prefix='ghost-package-') as directory:
        temporary = Path(directory)
        extracted = temporary / 'source'
        with ZipFile(ROOT / 'code.zip') as archive:
            for name in archive.namelist():
                if Path(name).is_absolute() or '..' in Path(name).parts:
                    raise ValueError('Unsafe archive member')
            archive.extractall(extracted)
        try:
            (extracted / 'dataset').symlink_to(ROOT / 'dataset', target_is_directory=True)
        except OSError:
            shutil.copytree(ROOT / 'dataset', extracted / 'dataset')
        venv_path = temporary / 'venv'
        venv.EnvBuilder(with_pip=False).create(venv_path)
        python = venv_path / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        environment = {k: os.environ[k] for k in ('PATH', 'SYSTEMROOT', 'WINDIR', 'LANG', 'LC_ALL', 'TMP', 'TEMP')
                       if k in os.environ}
        environment['PYTHONHASHSEED'] = '0'

        def run(arguments, expected=0):
            result = subprocess.run([str(python), *arguments], cwd=extracted, env=environment,
                                    capture_output=True, text=True, timeout=180)
            if result.returncode != expected:
                raise RuntimeError(f'Clean command failed: {arguments}: {result.stderr[-2000:]}')
            return result

        tests = run(['-m', 'unittest', 'discover', '-s', 'tests', '-q'])
        full = run(['code/main.py', '--all', '--mode', 'best-effort', '--diagnostics', 'artifacts/run.json'], expected=2)
        summary = json.loads(full.stdout)
        assert summary['attempted'] == 518 and summary['unsupported']
        assert not (extracted / 'output.csv').exists()
        actual = (extracted / 'artifacts/supported.csv').read_bytes()
        assert actual == (ROOT / 'artifacts/supported.csv').read_bytes()
        run(['code/evaluation/main.py', '--all-samples', '--mode', 'best-effort', '--output-dir', 'artifacts/benchmark'])
        assert ((extracted / 'artifacts/benchmark/predictions.csv').read_bytes()
                == (ROOT / 'artifacts/submission-benchmark/predictions.csv').read_bytes())
        result = dict(clean_extraction=True, fresh_venv=True, python_packages_installed=0,
                      tests=tests.stderr.strip(), full_run_exit=full.returncode,
                      attempted=summary['attempted'], produced=summary['produced'],
                      unsupported=len(summary['unsupported']), full_output_exists=False,
                      partial_sha256=hashlib.sha256(actual).hexdigest(),
                      partial_matches=True, benchmark_matches=True,
                      inherited_credentials=False)
        (ROOT / 'artifacts/package-validation.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    verify()
