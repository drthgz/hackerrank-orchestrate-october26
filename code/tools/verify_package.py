"""Replay the source archive in a fresh extraction and dependency-free venv.

The supplied participant dataset is attached outside the archive, as documented.
No experiment client or model endpoint is imported. Subprocess credentials are
not inherited. Both the unchanged partial audit and complete prediction replay.
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
        prediction = run(['code/main.py', '--all', '--mode', 'prediction', '--diagnostics', 'artifacts/prediction-run.json'])
        predicted_summary = json.loads(prediction.stdout)
        assert predicted_summary['attempted'] == predicted_summary['produced'] == 518
        assert not predicted_summary['unsupported']
        output_bytes = (extracted / 'output.csv').read_bytes()
        assert output_bytes == (ROOT / 'output.csv').read_bytes()
        run(['code/tools/validate_candidate.py', '--baseline', 'artifacts/supported.csv'])
        run(['code/evaluation/main.py', '--all-samples', '--mode', 'prediction', '--output-dir', 'artifacts/prediction-benchmark'])
        assert ((extracted / 'artifacts/prediction-benchmark/predictions.csv').read_bytes()
                == (ROOT / 'artifacts/prediction-benchmark/predictions.csv').read_bytes())
        run(['code/evaluation/main.py', '--all-samples', '--mode', 'strict', '--output-dir', 'artifacts/strict-benchmark'])
        assert ((extracted / 'artifacts/strict-benchmark/predictions.csv').read_bytes()
                == (ROOT / 'artifacts/final-strict-benchmark/predictions.csv').read_bytes())
        result = dict(clean_extraction=True, fresh_venv=True, python_packages_installed=0,
                      tests=tests.stderr.strip(), baseline_run_exit=full.returncode,
                      baseline_produced=summary['produced'], baseline_unsupported=len(summary['unsupported']),
                      full_run_exit=prediction.returncode, attempted=predicted_summary['attempted'],
                      produced=predicted_summary['produced'], uncertain_statuses=len(predicted_summary['uncertain_status_predictions']),
                      unsupported=len(predicted_summary['unsupported']), full_output_exists=True,
                      output_sha256=hashlib.sha256(output_bytes).hexdigest(), prediction_matches=True,
                      prediction_benchmark_matches=True, strict_benchmark_matches=True,
                      partial_sha256=hashlib.sha256(actual).hexdigest(),
                      partial_matches=True, benchmark_matches=True,
                      inherited_credentials=False)
        (ROOT / 'artifacts/package-validation.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    verify()
