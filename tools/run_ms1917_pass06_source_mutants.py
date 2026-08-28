from __future__ import annotations

from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile, time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'/'ms1917_pass06_source_mutants'
REPORT.mkdir(parents=True,exist_ok=True)
TEST='tests/embodiment/test_ms1917_pass06_execution_fresh_direct_probe_surface.py'

MUTANTS={
 'DROP_EXECUTION_FRESH_SURFACE_REDERIVATION':(
  'microseed/runtime/entity.py',
  '            fresh_probe_context,probe_context_reason,probe_context_detail=self._fresh_revised_direct_probe_decision_context_for_trial(trial)\n',
  '            fresh_probe_context,probe_context_reason,probe_context_detail=(None,"NOT_APPLICABLE",None)\n'),
 'FALLBACK_TO_CACHED_CONTEXT_ON_FRESH_SURFACE_FAILURE':(
  'microseed/runtime/entity.py',
  '''                if fresh_probe_context is None:\n                    return None,probe_context_reason or "CURRENT_REVISED_DIRECT_PROBE_DECISION_SURFACE_REQUIRED_AT_EXECUTION",probe_context_detail\n                execution_decision_context=fresh_probe_context\n''',
  '''                if fresh_probe_context is None:\n                    fresh_probe_context=execution_decision_context\n                if fresh_probe_context is not None:\n                    execution_decision_context=fresh_probe_context\n'''),
 'DROP_EXECUTION_PREDECESSOR_UNIQUENESS':(
  'microseed/runtime/entity.py',
  '        if len(predecessors)!=1:\n',
  '        if not predecessors:\n'),
 'DROP_EXECUTION_SOURCE_DIGEST_BINDING':(
  'microseed/runtime/entity.py',
  '        if tuple(sorted(str(x) for x in surface.get("source_relation_digests",())))!=tuple(sorted(trial.source_relation_digests)):\n',
  '        if False and tuple(sorted(str(x) for x in surface.get("source_relation_digests",())))!=tuple(sorted(trial.source_relation_digests)):\n'),
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
    with tempfile.TemporaryDirectory(prefix=f'ms1917_{name}_') as td:
        dst=Path(td)/'repo'; shutil.copytree(ROOT,dst,ignore=ignore)
        clean_sha,mut_sha=apply(dst,name,target,old,new)
        cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q',TEST]
        try:
            r=subprocess.run(cmd,cwd=dst,capture_output=True,text=True,timeout=24)
            code,out,err=r.returncode,r.stdout,r.stderr; marker='COMPLETE'; status='SURVIVED' if code==0 else 'REJECTED'
        except subprocess.TimeoutExpired as exc:
            code=None; out=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
            err=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
            marker='INCOMPLETE'; status='UNKNOWN_INCOMPLETE_TIMEOUT'
        op=REPORT/f'{name}.stdout.log'; ep=REPORT/f'{name}.stderr.log'; op.write_text(out,encoding='utf-8'); ep.write_text(err,encoding='utf-8')
        return {'mutant':name,'target':target,'status':status,'exit_code':code,'completion_marker':marker,'duration_seconds':round(time.time()-started,6),'clean_source_sha256':clean_sha,'mutant_source_sha256':mut_sha,'stdout_path':str(op.relative_to(ROOT)),'stderr_path':str(ep.relative_to(ROOT)),'stdout_tail':'\n'.join(out.splitlines()[-18:]),'stderr_tail':'\n'.join(err.splitlines()[-8:])}

started=time.time(); results=[run(name,spec) for name,spec in MUTANTS.items()]
receipt={'schema':'microseed.ms1917.pass06.source-mutants.v1','discriminator':'NOMINATION_CURRENT_DECISION_CONTEXT != EXECUTION_CURRENT_DECISION_SURFACE','started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'results':results,'survivors':[r['mutant'] for r in results if r['status']=='SURVIVED'],'rejected':[r['mutant'] for r in results if r['status']=='REJECTED'],'unknown':[r['mutant'] for r in results if r['status'].startswith('UNKNOWN')],'completion_marker':'COMPLETE' if all(r['completion_marker']=='COMPLETE' for r in results) else 'INCOMPLETE'}
(REPORT/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str((REPORT/'receipt.json').relative_to(ROOT)),'survivors':receipt['survivors'],'rejected':receipt['rejected'],'unknown':receipt['unknown'],'completion_marker':receipt['completion_marker']},indent=2))
raise SystemExit(0 if receipt['completion_marker']=='COMPLETE' and not receipt['survivors'] else 2)
