#!/usr/bin/env python3
"""Check fixture oracles against known repairs and reject the buggy seeds.

No models, downloads, or changes to source fixtures. Requires Python 3.9+ and PHP.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
REPAIRS = {
    'presence': """<?php
function applyLabel(array $patch, ?string $current): ?string
{
    if (!array_key_exists('label', $patch)) {
        return $current;
    }
    if ($patch['label'] !== null && !is_string($patch['label'])) {
        throw new InvalidArgumentException('label must be a string or null');
    }
    return $patch['label'];
}
""",
    'list-shape': """<?php
function enabledNamesJson(array $rows): string
{
    $names = [];
    foreach ($rows as $row) {
        if ($row['enabled'] === true) {
            $names[] = $row['name'];
        }
    }
    return json_encode($names, JSON_THROW_ON_ERROR);
}
""",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--php', default='php', help='PHP executable to validate with')
    args = parser.parse_args()
    php = shutil.which(args.php)
    if php is None:
        parser.error('PHP executable not found: ' + args.php)
    subprocess.run([php, '-v'], check=True)
    with tempfile.TemporaryDirectory(prefix='beautiful-php-') as directory:
        for name, repair in REPAIRS.items():
            oracle = ROOT / 'held-out' / (name + '.php')
            seed = ROOT / 'fixtures' / name / 'value.php'
            fixed = Path(directory) / (name + '.php')
            fixed.write_text(repair, encoding='utf-8')
            for path in (seed, fixed, oracle):
                subprocess.run([php, '-l', str(path)], check=True, capture_output=True)
            broken = subprocess.run([php, str(oracle), str(seed)], capture_output=True, text=True)
            if broken.returncode == 0:
                raise RuntimeError(name + ': oracle accepted the buggy seed')
            subprocess.run([php, str(oracle), str(fixed)], check=True)
            print(name + ': rejected buggy seed, accepted known repair', flush=True)


if __name__ == '__main__':
    main()
