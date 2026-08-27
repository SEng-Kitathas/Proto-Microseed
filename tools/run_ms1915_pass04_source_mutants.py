from __future__ import annotations

from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile, time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'/'ms1915_pass04_source_mutants'
REPORT.mkdir(parents=True,exist_ok=True)
TARGET='microseed/development/epistemic_action.py'
TEST='tests/embodiment/test_ms1915_pass04_optional_priority_information_api_boundary.py'

MUTANTS={
 'ALLOW_MISSING_PRIORITY':(
'''    if priority_commitment is None:\n        return _missing_epistemic_decision_premise(\n            target=target, reason="EPISTEMIC_DECISION_BEARING_PRIORITY_REQUIRED",\n            premise_ids=(trial.deficit_id,), detail=None,\n        )\n''',
'''    if priority_commitment is None:\n        return local\n'''),
 'ALLOW_MISSING_INFORMATION':(
'''    if information_commitment is None:\n        return _missing_epistemic_decision_premise(\n            target=target, reason="EPISTEMIC_PROGRAM_INFORMATION_REQUIRED",\n            premise_ids=(trial.deficit_id,priority_commitment.commitment_id), detail=None,\n        )\n''',
'''    if information_commitment is None:\n        return _finalize_epistemic_program_step_commitment(\n            trial=trial, deficit=deficit, feasibility=feasibility, idx=idx, target=target,\n            expected_cid=expected_cid, required=(need,priority_commitment,feas,route),\n            reason_prefix="EPISTEMIC_PROGRAM_STEP", decision_premises="PRIORITY_ONLY_MUTANT",\n        )\n'''),
 'DROP_PRIORITY_BINDING':(
'''    if priority_commitment.target_id != expected_priority_target or trial.deficit_id not in priority_commitment.premise_ids:\n''',
'''    if False:\n'''),
 'DROP_INFORMATION_BINDING':(
'''    if (\n        information_commitment.target_id != expected_information_target\n''',
'''    if False and (\n        information_commitment.target_id != expected_information_target\n'''),
}

def ignore(_path,names):
    return {'.git','reports','.pytest_cache','__pycache__'}

def apply_mutant(root:Path,name:str,old:str,new:str):
    p=root/TARGET
    raw=p.read_text(encoding='utf-8')
    if old not in raw:
        raise RuntimeError(f'MUTATION_PATTERN_NOT_FOUND:{name}')
    mutated=raw.replace(old,new,1)
    p.write_text(mutated,encoding='utf-8')
    return hashlib.sha256(raw.encode()).hexdigest(),hashlib.sha256(mutated.encode()).hexdigest()

def run(name,old,new):
    started=time.time()
    with tempfile.TemporaryDirectory(prefix=f'ms1915_{name}_') as td:
        dst=Path(td)/'repo'; shutil.copytree(ROOT,dst,ignore=ignore)
        clean_sha,mut_sha=apply_mutant(dst,name,old,new)
        cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q',TEST]
        try:
            r=subprocess.run(cmd,cwd=dst,capture_output=True,text=True,timeout=20)
            code,out,err=r.returncode,r.stdout,r.stderr; marker='COMPLETE'
            status='SURVIVED' if code==0 else 'REJECTED'
        except subprocess.TimeoutExpired as exc:
            code=None; out=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
            err=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
            marker='INCOMPLETE'; status='UNKNOWN_INCOMPLETE_TIMEOUT'
        op=REPORT/f'{name}.stdout.log'; ep=REPORT/f'{name}.stderr.log'; op.write_text(out,encoding='utf-8'); ep.write_text(err,encoding='utf-8')
        return {'mutant':name,'status':status,'exit_code':code,'completion_marker':marker,'duration_seconds':round(time.time()-started,6),'clean_source_sha256':clean_sha,'mutant_source_sha256':mut_sha,'stdout_path':str(op.relative_to(ROOT)),'stderr_path':str(ep.relative_to(ROOT)),'stdout_tail':'\n'.join(out.splitlines()[-12:]),'stderr_tail':'\n'.join(err.splitlines()[-8:])}

started=time.time(); results=[]
for name,(old,new) in MUTANTS.items(): results.append(run(name,old,new))
receipt={'schema':'microseed.ms1915.pass04.source-mutants.v1','discriminator':'OMITTED_OR_UNBOUND_DECISION_PREMISE != SATISFIED_DECISION_PREMISE','started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'results':results,'survivors':[r['mutant'] for r in results if r['status']=='SURVIVED'],'rejected':[r['mutant'] for r in results if r['status']=='REJECTED'],'unknown':[r['mutant'] for r in results if r['status'].startswith('UNKNOWN')],'completion_marker':'COMPLETE' if all(r['completion_marker']=='COMPLETE' for r in results) else 'INCOMPLETE'}
(REPORT/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str((REPORT/'receipt.json').relative_to(ROOT)),'survivors':receipt['survivors'],'rejected':receipt['rejected'],'unknown':receipt['unknown'],'completion_marker':receipt['completion_marker']},indent=2))
raise SystemExit(0 if receipt['completion_marker']=='COMPLETE' and not receipt['survivors'] else 2)
