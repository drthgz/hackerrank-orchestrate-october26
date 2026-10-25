"""Verify source parity and replay the release in a fresh credential-free venv.

Participant data and expected CSVs stay outside the archive. Python needs no
third-party packages; Poppler must be installed on the host as documented.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import venv
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]


def verify():
    if not shutil.which('pdftotext'):
        raise RuntimeError('Install Poppler pdftotext before clean replay')
    with tempfile.TemporaryDirectory(prefix='ghost-package-') as directory:
        temporary = Path(directory)
        extracted = temporary / 'source'
        with ZipFile(ROOT / 'code.zip') as archive:
            assert archive.testzip() is None
            names = archive.namelist()
            assert len(names) == len(set(names))
            for name in names:
                path = Path(name)
                if (path.is_absolute() or '..' in path.parts or name.startswith(('dataset/', 'artifacts/', 'experiments/'))
                        or path.suffix not in {'.py', '.md'} or '__pycache__' in path.parts):
                    raise ValueError('Unexpected archive member: ' + name)
                assert archive.read(name) == (ROOT / name).read_bytes(), 'Archive/source mismatch: ' + name
            archive.extractall(extracted)
        # Check local Markdown file links in the shipped documentation.
        for path in extracted.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    linked = (path.parent / target.split('#')[0]).resolve()
                    assert linked.is_relative_to(extracted) and linked.exists(), (path, target)
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

        def run(arguments):
            result = subprocess.run([str(python), *arguments], cwd=extracted, env=environment,
                                    capture_output=True, text=True, timeout=180)
            if result.returncode:
                raise RuntimeError(f'Clean command failed: {arguments}: {result.stderr[-3000:]}')
            return result

        tests = run(['-m', 'unittest', 'discover', '-s', 'tests', '-q'])
        full = run(['code/main.py', '--all', '--mode', 'prediction',
                    '--diagnostics', 'artifacts/prediction-run.json'])
        summary = json.loads(full.stdout)
        assert summary['attempted'] == summary['produced'] == 518 and not summary['unsupported']
        output_bytes = (extracted / 'output.csv').read_bytes()
        assert output_bytes == (ROOT / 'output.csv').read_bytes()
        run(['code/tools/validate_candidate.py'])
        validation = json.loads((extracted / 'artifacts/candidate-validation.json').read_text())
        run(['code/evaluation/main.py', '--all-samples', '--mode', 'prediction',
             '--output-dir', 'artifacts/prediction-benchmark'])
        public_bytes = (extracted / 'artifacts/prediction-benchmark/predictions.csv').read_bytes()
        assert public_bytes == (ROOT / 'artifacts/prediction-benchmark/predictions.csv').read_bytes()
        result = dict(clean_extraction=True, zip_integrity=True, archive_source_parity=True,
                      documentation_links_valid=True, fresh_venv=True, python_packages_installed=0,
                      tests=tests.stderr.strip(), full_run_exit=full.returncode,
                      attempted=summary['attempted'], produced=summary['produced'],
                      uncertain_statuses=len(summary['uncertain_status_predictions']),
                      incomplete_or_unproved_plans=len(summary['incomplete_or_unproved_plans']),
                      stronger_validator_failures=len(summary['audit_validator_failures']),
                      structural_invalid=validation['structural_invalid'],
                      citation_or_resource_provenance_invalid=validation['citation_or_resource_provenance_invalid'],
                      output_sha256=hashlib.sha256(output_bytes).hexdigest(), prediction_matches=True,
                      public_sha256=hashlib.sha256(public_bytes).hexdigest(), public_benchmark_matches=True,
                      archive_sha256=hashlib.sha256((ROOT / 'code.zip').read_bytes()).hexdigest(),
                      inherited_credentials=False, semantic_compliance_certified=False)
        (ROOT / 'artifacts/package-validation.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    verify()
