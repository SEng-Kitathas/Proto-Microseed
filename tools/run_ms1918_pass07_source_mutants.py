from __future__ import annotations

from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile, time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'/'ms1918_pass07_source_mutants'
if REPORT.exists(): shutil.rmtree(REPORT)
REPORT.mkdir(parents=True,exist_ok=True)
TEST='tests/embodiment/test_ms1918_pass07_authenticated_probe_observation_closure.py'

MUTANTS={
 'DROP_COMPLETED_PROGRAM_AUTHENTICATED_OBSERVATION_GATE':(
  'microseed/runtime/entity.py',
'''            if deficit.state==EpistemicDeficitState.PROBE_AVAILABLE:\n                authenticated,auth_detail=self._authenticated_probe_program_step_observation(rec)\n                if authenticated is None:\n                    return {\n                        "status":"PROGRAM_EVIDENCE_REJECTED",\n                        "reason":auth_detail["reason"],\n                        "observation_admission":auth_detail.get("observation_admission"),\n                    }\n''',
'''            if deficit.state==EpistemicDeficitState.PROBE_AVAILABLE:\n                pass\n'''),
 'DROP_STEP_BEARING_AUTHENTICATED_OBSERVATION_GATE':(
  'microseed/runtime/entity.py',
'''        if deficit.state==EpistemicDeficitState.PROBE_AVAILABLE:\n            authenticated,auth_detail=self._authenticated_probe_program_step_observation(rec)\n            if authenticated is None:\n                return {\n                    "status":"PROGRAM_STEP_BEARING_UNRESOLVED",\n                    "reason":auth_detail["reason"],\n                    "observation_admission":auth_detail.get("observation_admission"),\n                    "truth_authority":"NONE","answer_authority":"NONE",\n                    "model_replacement_authority":"NONE","execution_authority":"NONE",\n                }\n''',
'''        if deficit.state==EpistemicDeficitState.PROBE_AVAILABLE:\n            pass\n'''),
 'DROP_LIVE_OBSERVATION_AND_BASIS_CURRENTNESS_RECHECK':(
  'microseed/runtime/entity.py',
'''            for prefix in ("observation_capability", "observation_basis_capability"):\n''',
'''            for prefix in ():\n'''),
}

def ignore(_path,names):
    return {'.git','reports','.pytest_cache','__pycache__'}

def apply(root:Path,name:str,target:str,old:str,new:str):
    p=root/target; raw=p.read_text(encoding='utf-8')
    if old not in raw: raise RuntimeError(f'MUTATION_PATTERN_NOT_FOUND:{name}')
    mutated=raw.replace(old,new,1); p.write_text(mutated,encoding='utf-8')
    return hashlib.sha256(raw.encode()).hexdigest(),hashlib.sha256(mutated.encode()).hexdigest()

def run(name,spec):
    target,old,new=spec; started=time.time()
    with tempfile.TemporaryDirectory(prefix=f'ms1918_{name}_') as td:
        dst=Path(td)/'repo'; shutil.copytree(ROOT,dst,ignore=ignore)
        clean_sha,mut_sha=apply(dst,name,target,old,new)
        cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q',TEST]
        try:
            r=subprocess.run(cmd,cwd=dst,capture_output=True,text=True,timeout=25)
            code,out,err=r.returncode,r.stdout,r.stderr; marker='COMPLETE'; status='SURVIVED' if code==0 else 'REJECTED'
        except subprocess.TimeoutExpired as exc:
            code=None; out=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
            err=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
            marker='INCOMPLETE'; status='UNKNOWN_INCOMPLETE_TIMEOUT'
        op=REPORT/f'{name}.stdout.log'; ep=REPORT/f'{name}.stderr.log'
        op.write_text(out,encoding='utf-8'); ep.write_text(err,encoding='utf-8')
        return {'mutant':name,'target':target,'status':status,'exit_code':code,'completion_marker':marker,'duration_seconds':round(time.time()-started,6),'clean_source_sha256':clean_sha,'mutant_source_sha256':mut_sha,'stdout_path':str(op.relative_to(ROOT)),'stderr_path':str(ep.relative_to(ROOT)),'stdout_tail':'\n'.join(out.splitlines()[-18:]),'stderr_tail':'\n'.join(err.splitlines()[-10:])}

started=time.time(); results=[run(name,spec) for name,spec in MUTANTS.items()]
receipt={'schema':'microseed.ms1918.pass07.source-mutants.v1','discriminator':'RECORDED_OUTCOME != AUTHENTICATED_PROGRAM_EVIDENCE_OR_REVISIT','started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'results':results,'survivors':[r['mutant'] for r in results if r['status']=='SURVIVED'],'rejected':[r['mutant'] for r in results if r['status']=='REJECTED'],'unknown':[r['mutant'] for r in results if r['status'].startswith('UNKNOWN')],'completion_marker':'COMPLETE' if all(r['completion_marker']=='COMPLETE' for r in results) else 'INCOMPLETE'}
(REPORT/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str((REPORT/'receipt.json').relative_to(ROOT)),'survivors':receipt['survivors'],'rejected':receipt['rejected'],'unknown':receipt['unknown'],'completion_marker':receipt['completion_marker']},indent=2))
# diagnostic run: return success only if no UNKNOWN; survivors are interpreted separately.
raise SystemExit(0 if receipt['completion_marker']=='COMPLETE' and not receipt['unknown'] else 2)
