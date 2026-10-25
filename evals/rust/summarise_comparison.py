#!/usr/bin/env python3
"""Summarise completed model runs without treating missing grades as passes."""
import argparse
import json
from pathlib import Path
from statistics import mean, median


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    args = parser.parse_args()
    results = (json.loads((args.directory/'runs.json').read_text()) if (args.directory/'runs.json').exists()
               else [json.loads(p.read_text()) for p in args.directory.glob('*/result.json')])
    rows = []
    for result in results:
        if result['exit_code'] != 0 or not result['usage']:
            continue
        usage = {key:sum(u.get(key,0) for u in result['usage']) for key in ('input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens')}
        usage['uncached_input_tokens'] = usage['input_tokens']-usage['cached_input_tokens']
        usage['total_tokens'] = usage['input_tokens']+usage['output_tokens']
        checks = result['checks']
        machine_quality = None
        if result['case'] == 'library':
            machine_quality = checks.get('independent_tests',False)
        elif result['case'] == 'cli':
            machine_quality = checks.get('independent_tests',False) and checks.get('cli_contract',False)
        elif result['case'] == 'refactor':
            machine_quality = checks.get('independent_tests',False) and checks.get('other_functions_preserved',False)
        rows.append({'id':result['id'],'case':result['case'],'condition':result['condition'],'repeat':result['repeat'],**usage,'elapsed_seconds':result['elapsed_seconds'],'command_count':result['command_count'],'machine_quality_pass':machine_quality})
    summary = {'runs':rows,'by_condition':{},'by_case':{}}
    metrics = ('input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens','total_tokens','elapsed_seconds','command_count')
    for key,groups in [('condition',['none','original','condensed']),('case',sorted(set(r['case'] for r in rows)))]:
        for group in groups:
            selected = [r for r in rows if r[key] == group]
            summary['by_'+key][group] = {'n':len(selected),**{m:{'sum':sum(r[m] for r in selected),'mean':mean(r[m] for r in selected) if selected else None,'median':median(r[m] for r in selected) if selected else None} for m in metrics}}
    summary['failed_or_incomplete'] = [{'id':r['id'],'exit_code':r['exit_code']} for r in results if r['exit_code'] != 0 or not r['usage']]
    (args.directory/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary['by_condition'],indent=2))


if __name__ == '__main__':
    main()
