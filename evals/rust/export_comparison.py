#!/usr/bin/env python3
"""Export selected completed runs with reproducible evidence, excluding auth/state files."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--repeat',type=int,default=1,help='Repeat to export; 0 exports all completed repeats')
    args = parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    results = []
    for path in sorted(args.input.glob('*/result.json')):
        record = json.loads(path.read_text())
        if (args.repeat and record['repeat'] != args.repeat) or record['exit_code'] != 0 or not record['usage']:
            continue
        evidence = {k:record[k] for k in ('exit_code','id','case','condition','repeat','model','reasoning_effort','elapsed_seconds','usage','command_count','final','checks','skill_sha256')}
        evidence['commands'] = [c.get('command','') for c in record['commands']]
        evidence['prompt'] = (path.parent/'prompt.txt').read_text()
        evidence['raw_result_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        evidence['grader_revision'] = record.get('grader_revision','initial')
        workspace = path.parent/'workspace'
        # Whitelist benchmark sources; never copy runtime config, logs, or authentication.
        evidence['artifacts'] = {}
        evidence['manifest'] = (workspace/'Cargo.toml').read_text()
        if record['case'] in ('library','cli','refactor'):
            for base in (workspace/'src',workspace/'tests'):
                for source in sorted(base.rglob('*.rs')) if base.exists() else []:
                    evidence['artifacts'][str(source.relative_to(workspace))] = source.read_text()
        results.append(evidence)
    (args.output/'runs.json').write_text(json.dumps(results,indent=2)+'\n')
    metadata = json.loads((args.input/'metadata.json').read_text())
    metadata['published_repeat'] = args.repeat
    metadata['selection'] = 'All successful runs for this repeat; failed or unfinished attempts excluded from comparisons and disclosed in the report.'
    (args.output/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('Exported',len(results),'runs')


if __name__ == '__main__':
    main()
