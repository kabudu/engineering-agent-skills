"""Check evaluation inputs and packaging; never execute the unsound fixture."""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SKILLS = [ROOT / 'skills' / name for name in ('rust-best-practices', 'rust-review')]


def main():
    with tempfile.TemporaryDirectory(prefix='rust-skill-check-') as output:
        subprocess.run(['rustc', '--edition=2021', '--crate-type=lib',
                        str(ROOT / 'evals/rust/fixtures/review.rs'),
                        '-o', str(Path(output) / 'review.rlib')], check=True)
        executable = str(Path(output) / 'clean-tests')
        subprocess.run(['rustc', '--edition=2021', '--test',
                        str(ROOT / 'evals/rust/fixtures/clean.rs'),
                        '-o', executable], check=True)
        subprocess.run([executable], check=True)
    for skill in SKILLS:
        licence = (skill / 'LICENSE').read_text()
        assert 'Copyright (c) 2026 Morgan Linton' in licence
        assert 'Permission is hereby granted' in licence
        for path in skill.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    assert (path.parent / target.split('#')[0]).exists(), (path, target)
        content = (skill / 'SKILL.md').read_text()
        print(f'{skill.name}: {len(content.split())} words, {len(content.encode())} bytes')
    print('Fixture and packaging checks passed; model effectiveness is not evaluated.')


if __name__ == '__main__':
    main()
