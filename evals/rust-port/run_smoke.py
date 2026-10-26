#!/usr/bin/env python3
"""Run two bounded porting smoke cases. Requires an authenticated Codex CLI.

Uses the existing comparison runner's isolation settings and process cancellation.
These are functional smoke cases, not a comparative model benchmark. Model calls
consume account allowance; CI never invokes this script.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('comparison', ROOT/'evals/rust/run_comparison.py')
COMMON = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMMON
SPEC.loader.exec_module(COMMON)
PROMPTS = {
    'c-bytes': 'Use $rust-port to port pair.c/pair.h and test_pair.c into this Rust library crate. Preserve the byte-oriented behaviour and error precedence, including null input. The requested Rust API is parse_pair(input: Option<&[u8]>) -> Result<(u8, u16), ParseError>, with public ParseError::InvalidFormat and ParseError::Overflow variants. The C output pointers become the Rust return value, not FFI. Write PORTING.md and preserve the original source files.',
    'python-lines': 'Use $rust-port to port lines.py and test_lines.py into this Rust library crate with the same behaviour. Inputs are valid Unicode scalar text. The requested Rust API is split_nonempty(input: &str) -> Vec<String>. Write PORTING.md and preserve the original source files.',
}
TESTS = {
    'c-bytes': r'''use rust_port_smoke::{parse_pair, ParseError};
#[test] fn public_error_contract() {
 fn accepts_error<E: std::error::Error>() {}
 accepts_error::<ParseError>();
}
#[test] fn raw_keys_and_bounds() {
 assert_eq!(parse_pair(Some(&[0xff, b'=', b'9'])).unwrap(), (0xff,9));
 assert_eq!(parse_pair(Some(&[0, b'=', b'0'])).unwrap(), (0,0));
 assert_eq!(parse_pair(Some(b"a=00")).unwrap(), (b'a',0));
 assert_eq!(parse_pair(Some(b"a=65535")).unwrap(), (b'a',65535));
}
#[test] fn errors_and_precedence() {
 assert!(matches!(parse_pair(None), Err(ParseError::InvalidFormat)));
 assert!(matches!(parse_pair(Some(b"a=")), Err(ParseError::InvalidFormat)));
 assert!(matches!(parse_pair(Some(b"a=1x")), Err(ParseError::InvalidFormat)));
 assert!(matches!(parse_pair(Some(b"a=65536")), Err(ParseError::Overflow)));
 assert!(matches!(parse_pair(Some(b"a=655360x")), Err(ParseError::Overflow)));
}
''',
    'python-lines': r'''use rust_port_smoke::split_nonempty;
#[test] fn separators_and_unicode() {
 for sep in ["\n","\r","\r\n","\u{b}","\u{c}","\u{1c}","\u{1d}","\u{1e}","\u{85}","\u{2028}","\u{2029}"] {
  assert_eq!(split_nonempty(&format!("a{sep}b{sep}")), vec!["a", "b"]);
 }
 assert_eq!(split_nonempty("é\u{2028}中"), vec!["é", "中"]);
}
#[test] fn preservation_and_empty_input() {
 assert_eq!(split_nonempty(" a \n \nb "), vec![" a ", " ", "b "]);
 assert!(split_nonempty("\n\r\n").is_empty());
 assert!(split_nonempty("").is_empty());
 assert_eq!(split_nonempty("a\u{1f}b"), vec!["a\u{1f}b"]);
}
''',
}


def catalogue(workspaces, disabled):
    command = ['codex','app-server','--stdio','-c','skills.config='+disabled,
               '-c','skills.bundled.enabled=false','-c','features.plugins=false','-c','features.apps=false']
    with tempfile.TemporaryFile(mode='w+') as errors:
        process = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors,text=True,bufsize=1)
        def send(value):
            process.stdin.write(json.dumps(value)+'\n')
            process.stdin.flush()
        send({'id':1,'method':'initialize','params':{'clientInfo':{'name':'rust-port-smoke','version':'1.0'},'capabilities':{'experimentalApi':True}}})
        selector = selectors.DefaultSelector()
        selector.register(process.stdout,selectors.EVENT_READ)
        response, deadline = None, time.monotonic()+30
        try:
            while time.monotonic()<deadline and not COMMON.STOP.is_set():
                if not selector.select(1):continue
                line = process.stdout.readline()
                if not line:break
                value = json.loads(line)
                if value.get('id') == 1:
                    if 'error' in value:raise RuntimeError(value['error'])
                    send({'method':'initialized'})
                    send({'id':2,'method':'skills/list','params':{'cwds':[str(w) for w in workspaces],'forceReload':True}})
                if value.get('id') == 2:
                    response = value
                    break
        finally:
            selector.close()
            process.terminate()
            process.wait(timeout=10)
    if not response or 'error' in response:raise RuntimeError('Skill isolation preflight failed')
    groups = response['result']['data']
    if len(groups) != len(workspaces):raise RuntimeError('Incomplete skill catalogue')
    for group in groups:
        enabled = sorted(s['name'] for s in group['skills'] if s.get('enabled',True))
        if group.get('errors') or enabled != ['rust-port']:
            raise RuntimeError('Unexpected enabled skills: '+repr(enabled))
    return ['rust-port']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--model',default='gpt-6-luna')
    parser.add_argument('--timeout',type=int,default=180)
    args = parser.parse_args()
    if args.timeout <= 0:parser.error('timeout must be positive')
    output = args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    signal.signal(signal.SIGINT,COMMON.stop_runs)
    signal.signal(signal.SIGTERM,COMMON.stop_runs)
    disabled, workspaces = COMMON.disabled_skills(), {}
    for case in PROMPTS:
        workspace = output/case
        shutil.copytree(ROOT/'evals/rust-port/fixtures'/case,workspace)
        (workspace/'src').mkdir()
        (workspace/'src/lib.rs').write_text('')
        (workspace/'Cargo.toml').write_text('[package]\nname="rust_port_smoke"\nversion="0.1.0"\nedition="2021"\n')
        subprocess.run(['git','init','-q'],cwd=workspace,check=True)
        subprocess.run(['git','add','.'],cwd=workspace,check=True)
        subprocess.run(['git','-c','user.name=SkillEval','-c','user.email=skill-eval@example.invalid','commit','-qm','Initial fixture'],cwd=workspace,check=True)
        shutil.copytree(ROOT/'skills/rust-port',workspace/'.agents/skills/rust-port')
        workspaces[case] = workspace
    enabled = catalogue(list(workspaces.values()),disabled)
    results = []
    for case,workspace in workspaces.items():
        if COMMON.STOP.is_set():break
        if case == 'c-bytes':
            original = COMMON.call(['cc','-std=c11','-Wall','-Wextra','-Werror','pair.c','test_pair.c','-o',str(output/'original-c-tests')],workspace)
            if original.returncode == 0:original = COMMON.call([str(output/'original-c-tests')],workspace)
        else:
            original = COMMON.call([sys.executable,'-m','unittest','-v','test_lines.py'],workspace)
        if original.returncode:raise RuntimeError(original.stdout+original.stderr)
        command = ['codex','exec','--ignore-user-config','--ignore-rules','--ephemeral','--json','--sandbox','workspace-write','-C',str(workspace),'-m',args.model,
                   '-c','approval_policy="never"','-c','project_doc_max_bytes=0','-c','skills.bundled.enabled=false','-c','features.plugins=false','-c','features.apps=false',
                   '-c','features.memories=false','-c','features.multi_agent=false','-c','web_search="disabled"','-c','model_reasoning_effort="low"','-c','skills.config='+disabled,'-']
        with (output/(case+'.jsonl')).open('w') as out,(output/(case+'.stderr')).open('w') as err:
            status,error = COMMON.run_model(command,PROMPTS[case],out,err,args.timeout)
        events = [json.loads(line) for line in (output/(case+'.jsonl')).read_text().splitlines() if line.strip()]
        messages = [e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
        checks = {}
        if status == 0:
            test_dir = workspace/'tests'
            test_dir.mkdir(exist_ok=True)
            independent = test_dir/'__smoke_contract.rs'
            if independent.exists():raise RuntimeError('Refusing to overwrite model test')
            independent.write_text(TESTS[case])
            tested = COMMON.call(['cargo','test','--offline'],workspace)
            checks = {'contract_tests_passed':tested.returncode==0,'output':tested.stdout+tested.stderr,'porting_notes_present':(workspace/'PORTING.md').is_file(),
                      'original_sources_unchanged':COMMON.call(['git','diff','--exit-code','--',* [p.name for p in (ROOT/'evals/rust-port/fixtures'/case).iterdir()]],workspace).returncode==0}
        row = {'case':case,'model':args.model,'reasoning_effort':'low','enabled_skills':enabled,'status':status,'error':error,'prompt':PROMPTS[case],
               'usage':[e['usage'] for e in events if e.get('type')=='turn.completed'],
               'commands':[{'command':e['item']['command'],'exit_code':e['item'].get('exit_code')} for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution'],'response':messages[-1] if messages else '',
               'original_tests_passed':original.returncode==0,'checks':checks,'artifacts':{str(p.relative_to(workspace)):p.read_text() for p in [*workspace.glob('src/*.rs'),*workspace.glob('tests/*.rs'),*workspace.glob('PORTING.md')]},
               'skill_sha256':{str(p.relative_to(ROOT/'skills/rust-port')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'skills/rust-port').rglob('*') if p.is_file()}}
        row = json.loads(json.dumps(row).replace(str(workspace),'<workspace>'))
        results.append(row)
        (output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps({'case':case,'status':status,'checks':{k:v for k,v in checks.items() if isinstance(v,bool)}}),flush=True)
    if len(results)!=2 or not all(r['status']==0 and all(r['checks'].get(k,False) for k in ('contract_tests_passed','porting_notes_present','original_sources_unchanged')) for r in results):
        raise SystemExit('Smoke validation incomplete or failed; inspect the recorded evidence')


if __name__ == '__main__':
    main()
