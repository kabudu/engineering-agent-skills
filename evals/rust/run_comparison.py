#!/usr/bin/env python3
"""Run controlled local Codex comparisons; never copies or prints credentials.

Usage: python3 evals/rust/run_comparison.py --upstream /path/to/BeautifulRust --output /tmp/results
Model runs consume the authenticated account's Codex allowance. No API keys are handled.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import selectors
import signal
import threading
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
PIN = '2b2d53a66f6f36ab4b8d6a93070183d91e77fad4'
CASES = ['library', 'cli', 'refactor', 'review', 'clean-review', 'scope']
PROMPTS = {
    'library': '''Implement a dependency-free Rust library in the existing crate parsing exactly three decimal u16 components separated by dots. Reject whitespace, signs, non-ASCII digits, leading zeroes except zero itself, missing/extra components, and overflow. Expose a public Version type with read-only major(), minor(), patch() accessors, FromStr, and a public error implementing std::error::Error. Add tests. Do not add semver extensions. Use src/lib.rs. Finish with a concise summary of behaviour and checks.''',
    'cli': '''Implement a dependency-free Rust CLI in the existing crate. Read stdin lines containing exactly a nonempty ASCII alphanumeric category and a decimal ASCII u64 separated by one comma. Reject signs, whitespace, empty fields, extra commas, and invalid numeric input. Skip malformed lines and count them. Sum values per category with checked accumulation; exit nonzero on overflow or I/O failure. Print totals in lexicographic category order as category,total lines on stdout, and exactly skipped=N on stderr on success. Add tests. Use src/main.rs. Finish with a concise summary of behaviour and checks.''',
    'refactor': '''Refactor only first and wire_len in src/lib.rs to eliminate failures from externally supplied input. Public signature changes are allowed but must be explained. Empty input must be represented explicitly and a length above 255 must return an error. Do not change the other functions. Add boundary tests. Never execute the view function: its unsafe code is outside this refactor's scope. Finish with a concise summary of behaviour and checks.''',
    'review': '''Review src/lib.rs for correctness and soundness. Do not modify the file. Prioritise actionable findings with locations, consequences, and remedies. Never execute view: review its unsafe code by reading only. You may compile the crate or run non-executing static checks. Finish with checks actually run and meaningful limitations.''',
    'clean-review': '''Review src/lib.rs for actionable correctness defects. Do not modify the file. Report evidence-backed findings, if any, and checks actually run and meaningful limitations.''',
    'scope': 'Explain what borrowing means in Rust in two sentences.',
}
LIB_TEST = r'''
use rust_eval::Version;
fn parse(s: &str) -> Result<Version, impl std::error::Error> { s.parse::<Version>() }
#[test] fn valid_boundaries() {
 for (s,a,b,c) in [("0.1.65535",0,1,65535),("0.0.0",0,0,0),("65535.65535.65535",65535,65535,65535),("12.34.56",12,34,56)] {
  let v = parse(s).unwrap(); assert_eq!((v.major(),v.minor(),v.patch()),(a,b,c));
 }
}
#[test] fn invalid_inputs() {
 for s in ["", "01.2.3", "+1.2.3", "1.2", "1.2.3.4", "65536.0.0", " 1.2.3", "1.2.3 ", "1.-2.3", "1..3", "1.2.3\n", "1.2.3-alpha", "１.2.3", "1.2.3+build", "1.2.+3"] {
  assert!(parse(s).is_err(), "accepted {s:?}");
 }
}
#[test] fn long_numeric_input() { assert!(parse(&format!("{}.0.0", "9".repeat(5000))).is_err()); }
'''
REFACTOR_TEST = r'''
use rust_eval::{first, wire_len};
#[test] fn empty_and_nonempty() {
 assert_eq!(first(&[]), None); assert_eq!(first(&[9]), Some(9));
}
#[test] fn field_boundaries() {
 assert_eq!(wire_len(&[]).unwrap(), 0);
 assert_eq!(wire_len(&[0;255]).unwrap(), 255);
 assert!(wire_len(&[0;256]).is_err());
}
'''


STOP = threading.Event()
LIVE_PROCESSES = set()
PROCESS_LOCK = threading.RLock()


def stop_runs(signum=None, frame=None):
    STOP.set()
    with PROCESS_LOCK:
        for process in list(LIVE_PROCESSES):
            if process.poll() is None:
                process.terminate()


def run_model(command, prompt, output, errors, timeout):
    with PROCESS_LOCK:
        if STOP.is_set():
            return -1, 'interrupted'
        process = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=output,stderr=errors,text=True)
        LIVE_PROCESSES.add(process)
        if STOP.is_set():
            process.terminate()
    error = None
    try:
        process.communicate(input=prompt,timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        error = 'timeout'
    finally:
        with PROCESS_LOCK:
            LIVE_PROCESSES.discard(process)
    if STOP.is_set():
        error = 'interrupted'
    return process.returncode,error


def call(cmd, cwd=None, timeout=120, **kwargs):
    return subprocess.run(cmd, cwd=cwd, timeout=timeout, text=True, capture_output=True, **kwargs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disabled_skills():
    paths = set()
    for base in (Path.home()/'.codex/skills', Path.home()/'.agents/skills', Path('/etc/codex/skills')):
        if base.exists():
            # rglob does not follow symlinked skill folders; include direct discovery too.
            for file in set(base.rglob('SKILL.md')) | set(base.glob('*/SKILL.md')):
                paths.update((str(file), str(file.resolve())))
    return '['+','.join('{path = '+json.dumps(path)+', enabled = false}' for path in sorted(paths))+']'


def verify_isolation(args, disabled):
    """Fail before spending model tokens if discovery differs from the test conditions."""
    with tempfile.TemporaryDirectory(prefix='rust-skill-isolation-') as temporary:
        directories = {}
        for condition in ('none','original','condensed'):
            workspace = Path(temporary)/condition
            workspace.mkdir()
            call(['git','init','-q'],workspace)
            if condition != 'none':
                source = args.upstream if condition == 'original' else ROOT
                for name in ('rust-best-practices','rust-review'):
                    shutil.copytree(source/'skills'/name,workspace/'.agents/skills'/name)
            directories[condition] = workspace.resolve()
        command = ['codex','app-server','--stdio','-c','skills.config='+disabled,
                   '-c','skills.bundled.enabled=false','-c','features.plugins=false',
                   '-c','features.apps=false']
        with tempfile.TemporaryFile(mode='w+') as errors:
            process = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                       stderr=errors,text=True,bufsize=1)
            def send(value):
                process.stdin.write(json.dumps(value)+'\n')
                process.stdin.flush()
            send({'id':1,'method':'initialize','params':{'clientInfo':{'name':'rust-skill-isolation-check','version':'1.0'},'capabilities':{'experimentalApi':True}}})
            selector = selectors.DefaultSelector()
            selector.register(process.stdout,selectors.EVENT_READ)
            deadline, response = time.monotonic()+30, None
            try:
                while time.monotonic()<deadline:
                    if not selector.select(1):
                        continue
                    line = process.stdout.readline()
                    if not line:
                        break
                    value = json.loads(line)
                    if value.get('id') == 1:
                        if 'error' in value:
                            raise RuntimeError(value['error'])
                        send({'method':'initialized'})
                        send({'id':2,'method':'skills/list','params':{'cwds':[str(p) for p in directories.values()],'forceReload':True}})
                    if value.get('id') == 2:
                        response = value
                        break
            finally:
                selector.close()
                process.terminate()
                process.wait(timeout=10)
            if response is None or 'error' in response:
                raise RuntimeError('Could not verify skill isolation before model execution')
            discovered = {}
            for group in response['result']['data']:
                if group.get('errors'):
                    raise RuntimeError(group['errors'])
                condition = next(k for k,p in directories.items() if str(p) == group['cwd'])
                enabled = sorted(s['name'] for s in group['skills'] if s.get('enabled',True))
                expected = [] if condition == 'none' else ['rust-best-practices','rust-review']
                if enabled != expected:
                    raise RuntimeError(f'Unexpected skill catalogue in {condition}: {enabled}')
                discovered[condition] = enabled
            if set(discovered) != set(directories):
                raise RuntimeError('Incomplete skill discovery response')
            print('Verified skill isolation: '+json.dumps(discovered),flush=True)
            return discovered


def check_outputs(case, workspace, original):
    checks = {}
    if case in ('review', 'clean-review', 'scope'):
        checks['read_only'] = (workspace/'src/lib.rs').read_text() == original
        return checks
    tests = workspace/'tests'
    tests.mkdir(exist_ok=True)
    if case == 'library':
        (tests/'independent.rs').write_text(LIB_TEST)
    if case == 'refactor':
        # The prompt leaves Option versus Result open. Accept Result for absence too.
        src = (workspace/'src/lib.rs').read_text()
        test = REFACTOR_TEST
        if re.search(r'fn\s+first\([^)]*\)\s*->\s*Result', src):
            test = test.replace('assert_eq!(first(&[]), None); assert_eq!(first(&[9]), Some(9));',
                                'assert!(first(&[]).is_err()); assert_eq!(first(&[9]).unwrap(), 9);')
        (tests/'independent.rs').write_text(test)
        # Compare unchanged function bodies; docs/imports for changed APIs are in scope.
        def untouched(text):
            blocks = []
            for name in ('snapshot', 'invariant', 'reset_on_poison', 'view'):
                match = re.search(r'pub fn '+name+r'\b', text)
                if not match:
                    return None
                opening = text.index('{', match.start())
                depth, end = 1, opening+1
                while depth:
                    depth += (text[end] == '{') - (text[end] == '}')
                    end += 1
                blocks.append(re.sub(r'\s+', '', text[match.start():end]))
            # Preserve the original Key type and trait implementations as well.
            start = text.index('#[derive(')
            end = text.index('/// Shared immutable')
            blocks.append(re.sub(r'\s+', '', text[start:end]))
            return blocks
        checks['other_functions_preserved'] = untouched(src) == untouched(original)
    result = call(['cargo', 'test', '--offline', '--quiet'], workspace)
    checks['independent_tests'] = result.returncode == 0
    checks['test_output'] = (result.stdout+result.stderr)[-8000:]
    if case == 'cli':
        build = call(['cargo', 'build', '--offline', '--quiet'], workspace)
        checks['build'] = build.returncode == 0
        checks['cli_samples'] = []
        if build.returncode == 0:
            binary = workspace/'target/debug/rust_eval'
            samples = [
                ('b,2\na,1\nb,3\nbad\na,nope\n',0,'a,1\nb,5\n','skipped=2\n'),
                ('',0,'','skipped=0\n'),
                ('a,18446744073709551615\na,1\n',1,None,None),
                ('a,1,2\n,2\na,-1\na,+1\na, 1\na,１\nwhite space,1\na,18446744073709551616\nz,0\n',0,'z,0\n','skipped=8\n'),
                ('A,3\na,2\nA,4',0,'A,7\na,2\n','skipped=0\n'),
            ]
            for stdin,code,stdout,stderr in samples:
                r = call([str(binary)],workspace,input=stdin)
                okay = ((r.returncode == 0) if code == 0 else (r.returncode != 0))
                if stdout is not None: okay &= r.stdout == stdout
                if stderr is not None: okay &= r.stderr == stderr
                checks['cli_samples'].append({'passed':okay,'input':stdin,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        checks['cli_contract'] = build.returncode == 0 and all(x['passed'] for x in checks['cli_samples'])
    return checks


def one_run(args, condition, case, repeat, disabled):
    if STOP.is_set():
        return None
    label = f'{case}-{condition}-{repeat}'
    record_dir = args.output/label
    if (record_dir/'result.json').exists():
        existing = json.loads((record_dir/'result.json').read_text())
        if existing.get('model') != args.model:
            raise RuntimeError('Cannot resume a different model into the same output directory')
        if condition != 'none':
            source = args.upstream if condition == 'original' else ROOT
            expected = {}
            for name in ('rust-best-practices','rust-review'):
                for file in (source/'skills'/name).rglob('*.md'):
                    if 'evals' not in file.relative_to(source/'skills'/name).parts:
                        expected['.agents/skills/'+str(file.relative_to(source/'skills'))] = digest(file)
            if existing.get('skill_sha256') != expected:
                raise RuntimeError('Skill contents changed; use a new output directory')
        if existing.get('exit_code') == 0 and existing.get('usage'):

            print(json.dumps({'resumed':label}),flush=True)
            return existing
    if record_dir.exists():
        archive = args.output/'failed-attempts'
        archive.mkdir(exist_ok=True)
        shutil.move(str(record_dir),str(archive/(label+'-'+str(time.time_ns()))))
    record_dir.mkdir(parents=True)
    workspace = record_dir/'workspace'
    (workspace/'src').mkdir(parents=True)
    (workspace/'Cargo.toml').write_text('[package]\nname = "rust_eval"\nversion = "0.1.0"\nedition = "2021"\n')
    original = ''
    if case in ('refactor','review'):
        original = (ROOT/'evals/rust/fixtures/review.rs').read_text()
    elif case == 'clean-review':
        original = (ROOT/'evals/rust/fixtures/clean.rs').read_text()
    (workspace/'src/lib.rs').write_text(original)
    if case == 'cli':
        (workspace/'src/lib.rs').unlink()
        (workspace/'src/main.rs').write_text('fn main() {}\n')
    call(['git','init','-q'],workspace)
    # Both installed for the primary matrix, matching upstream's documented install.
    if condition != 'none':
        source = args.upstream if condition == 'original' else ROOT
        for name in ('rust-best-practices','rust-review'):
            target = workspace/'.agents/skills'/name
            shutil.copytree(source/'skills'/name,target)
            # Evaluation rubrics must not be visible to the task agent.
            shutil.rmtree(target/'evals',ignore_errors=True)
    prompt = PROMPTS[case]
    if condition != 'none' and case != 'scope':
        skill = 'rust-review' if case in ('review','clean-review') else 'rust-best-practices'
        prompt = f'Use ${skill} for this task.\n\n'+prompt
    command = ['codex','exec','--ignore-user-config','--ignore-rules','--ephemeral','--json',
               '--sandbox','workspace-write','-C',str(workspace),'-m',args.model,
               '-c','approval_policy="never"','-c','project_doc_max_bytes=0',
               '-c','skills.bundled.enabled=false','-c','features.plugins=false',
               '-c','features.apps=false','-c','features.memories=false',
               '-c','features.multi_agent=false','-c','web_search="disabled"',
               '-c','model_reasoning_effort="low"','-c','skills.config='+disabled,'-']
    (record_dir/'prompt.txt').write_text(prompt)
    start = time.monotonic()
    error = None
    with (record_dir/'events.jsonl').open('w') as out,(record_dir/'stderr.txt').open('w') as err:
        exit_code,error = run_model(command,prompt,out,err,args.timeout)
    elapsed = time.monotonic()-start
    events = []
    for line in (record_dir/'events.jsonl').read_text().splitlines():
        try: events.append(json.loads(line))
        except json.JSONDecodeError: pass
    usages = [e['usage'] for e in events if e.get('type') == 'turn.completed']
    messages = [e['item'].get('text','') for e in events if e.get('type') == 'item.completed' and e.get('item',{}).get('type') == 'agent_message']
    commands = [e['item'] for e in events if e.get('type') == 'item.completed' and e.get('item',{}).get('type') == 'command_execution']
    final = messages[-1] if messages else ''
    (record_dir/'final.md').write_text(final+'\n')
    checks = {}
    if exit_code == 0 and usages:
        try: checks = check_outputs(case,workspace,original)
        except Exception as exc: checks = {'grader_error':str(exc)}
    result = {'id':label,'condition':condition,'case':case,'repeat':repeat,'model':args.model,
              'reasoning_effort':'low','exit_code':exit_code,'error':error,'elapsed_seconds':round(elapsed,2),
              'usage':usages,'command_count':len(commands),'commands':commands,'final':final,'checks':checks,
              'skill_sha256':{str(p.relative_to(workspace)):digest(p) for p in (workspace/'.agents/skills').rglob('*.md')} if (workspace/'.agents/skills').exists() else {}}
    result = json.loads(json.dumps(result).replace(str(workspace),'<workspace>'))
    (record_dir/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'completed':label,'exit_code':exit_code,'seconds':round(elapsed,1),'usage':usages,'checks':{k:v for k,v in checks.items() if isinstance(v,bool)}}),flush=True)
    return result


def main():
    signal.signal(signal.SIGINT,stop_runs)
    signal.signal(signal.SIGTERM,stop_runs)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--model',default='gpt-6.1-sol')
    parser.add_argument('--repeats',type=int,default=1)
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--timeout',type=int,default=600)
    parser.add_argument('--cases',nargs='+',choices=CASES,default=CASES)
    args = parser.parse_args()
    if args.repeats < 1 or args.workers < 1 or args.timeout < 1:
        parser.error('repeats, workers, and timeout must be positive')
    args.upstream = args.upstream.resolve()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True,exist_ok=True)
    upstream_revision = call(['git','rev-parse','HEAD'],args.upstream).stdout.strip()
    if upstream_revision != PIN: raise SystemExit('Upstream revision does not match the benchmark pin')
    cases = [(condition,case,repeat) for repeat in range(1,args.repeats+1) for case in args.cases for condition in ('none','original','condensed')]
    random.Random(20261025).shuffle(cases)
    # Finish balanced preliminary blocks before adding repetitions.
    priority = ['scope', 'review', 'clean-review', 'refactor', 'library', 'cli']
    cases.sort(key=lambda item:(item[2],priority.index(item[1])))
    disabled = disabled_skills()
    isolation = verify_isolation(args,disabled)
    metadata = {'skill_isolation':isolation,'upstream_revision':PIN,'adapted_revision':call(['git','rev-parse','HEAD'],ROOT).stdout.strip(),
                'cli_version':call(['codex','--version']).stdout.strip(),'rustc_version':call(['rustc','--version']).stdout.strip(),
                'model':args.model,'reasoning_effort':'low','workers':args.workers,'timeout_seconds':args.timeout,
                'order':cases,'seed':20261025,'notes':'Explicit skill invocation except scope case. Personal skills disabled; user config, rules, memories, plugins, apps, web and project docs disabled. Skills themselves discovered from project .agents/skills. Normal built-in tool/instruction overhead remains.'}
    if (args.output/'metadata.json').exists():
        previous = json.loads((args.output/'metadata.json').read_text())
        if previous.get('model') != args.model or previous.get('skill_isolation') != isolation:
            raise RuntimeError('Model or isolation configuration changed; use a new output directory')
        shutil.copyfile(args.output/'metadata.json',args.output/('metadata-attempt-'+str(time.time_ns())+'.json'))
    (args.output/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(one_run,args,*case,disabled) for case in cases]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is None:
                continue
            results.append(result)
            (args.output/'results.json').write_text(json.dumps(sorted(results,key=lambda r:r['id']),indent=2)+'\n')
    print('Finished',len(results),'runs.',flush=True)


if __name__ == '__main__':
    main()
