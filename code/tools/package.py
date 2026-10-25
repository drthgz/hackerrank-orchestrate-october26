"""Build a deterministic source-only submission archive from an explicit allowlist."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[2]


def build():
    files = [ROOT / 'README.md', ROOT / 'problem_statement.md']
    for folder in ('code', 'tests', 'evaluation'):
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file()
                     and p.suffix in {'.py', '.md'} and '__pycache__' not in p.parts)
    files.extend(ROOT/'docs'/name for name in (
        'interview_briefing.md', 'image_review.md', 'evidence_sufficiency.md',
        'submission_contract.md', 'release/ai_judge_brief.md'))
    required = {'README.md','code/main.py','evaluation/evaluation_report.md','evaluation/usage_report.md'}
    names = {p.relative_to(ROOT).as_posix() for p in files}
    if not required <= names:
        raise ValueError('Required submission files missing')
    with ZipFile(ROOT/'code.zip','w',compression=ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            name = path.relative_to(ROOT).as_posix()
            info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info,path.read_bytes())
    with ZipFile(ROOT/'code.zip') as archive:
        assert archive.testzip() is None
        assert not any(n.startswith('dataset/') or n.endswith(('.zip','.jsonl','.env','.pyc')) for n in archive.namelist())
    print(f'Validated code.zip: {len(names)} source/report files; no dataset, credentials, caches or nested archives')


if __name__ == '__main__':
    build()
