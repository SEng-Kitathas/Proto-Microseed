from __future__ import annotations

from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile, time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'/'ms1919_pass08_source_mutants'
if REPORT.exists(): shutil.rmtree(REPORT)
REPORT.mkdir(parents=True,exist_ok=True)
TEST='tests/embodiment/test_ms1919_pass08_probe_lifecycle_evidence_recheck.py'
TARGET='microseed/runtime/entity.py'

MUTANTS={
 'COLLAPSE_PROBE_LIFECYCLE_TO_CURRENT_STATE':(
'''        return bool(\n            deficit is not None\n            and (\n                deficit.state == EpistemicDeficitState.PROBE_AVAILABLE\n                or deficit.probe_capability_id is not None\n                or deficit.probe_capability_epoch is not None\n            )\n        )\n''',
'''        return bool(deficit is not None and deficit.state == EpistemicDeficitState.PROBE_AVAILABLE)\n'''),
 'DROP_BEARING_SATISFACTION_RECHECK':(
'''        satisfaction = None\n        if self._probe_lifecycle_evidence_rechecks_required(deficit):\n            satisfaction = self.derive_current_program_discriminator_satisfaction(prior_trial)\n''',
'''        satisfaction = None\n        if False and self._probe_lifecycle_evidence_rechecks_required(deficit):\n            satisfaction = self.derive_current_program_discriminator_satisfaction(prior_trial)\n'''),
 'DROP_BEARING_AUTHENTICATED_OBSERVATION_RECHECK':(
'''        if self._probe_lifecycle_evidence_rechecks_required(deficit):\n            authenticated,auth_detail=self._authenticated_probe_program_step_observation(rec)\n            if authenticated is None:\n                return {\n                    "status":"PROGRAM_STEP_BEARING_UNRESOLVED",\n''',
'''        if False and self._probe_lifecycle_evidence_rechecks_required(deficit):\n            authenticated,auth_detail=self._authenticated_probe_program_step_observation(rec)\n            if authenticated is None:\n                return {\n                    "status":"PROGRAM_STEP_BEARING_UNRESOLVED",\n'''),
 'DROP_COMPLETED_EVIDENCE_SATISFACTION_RECHECK':(
'''        if self._probe_lifecycle_evidence_rechecks_required(deficit):\n            satisfaction=self.derive_current_program_discriminator_satisfaction(trial)\n            if not satisfaction.licenses_yes():\n''',
'''        if False and self._probe_lifecycle_evidence_rechecks_required(deficit):\n            satisfaction=self.derive_current_program_discriminator_satisfaction(trial)\n            if not satisfaction.licenses_yes():\n'''),
 'DROP_COMPLETED_EVIDENCE_AUTHENTICATED_OBSERVATION_RECHECK':(
'''            if self._probe_lifecycle_evidence_rechecks_required(deficit):\n                authenticated,auth_detail=self._authenticated_probe_program_step_observation(rec)\n                if authenticated is None:\n                    return {\n                        "status":"PROGRAM_EVIDENCE_REJECTED",\n''',
'''            if False and self._probe_lifecycle_evidence_rechecks_required(deficit):\n                authenticated,auth_detail=self._authenticated_probe_program_step_observation(rec)\n                if authenticated is None:\n                    return {\n                        "status":"PROGRAM_EVIDENCE_REJECTED",\n'''),
}

def ignore(_path,names):
    return {'.git','reports','.pytest_cache','__pycache__'}

def apply(root:Path,name:str,old:str,new:str):
    p=root/TARGET; raw=p.read_text(encoding='utf-8')
    if old not in raw: raise RuntimeError(f'MUTATION_PATTERN_NOT_FOUND:{name}')
    mutated=raw.replace(old,new,1); p.write_text(mutated,encoding='utf-8')
    return hashlib.sha256(raw.encode()).hexdigest(),hashlib.sha256(mutated.encode()).hexdigest()

def run(name,old,new):
    started=time.time()
    with tempfile.TemporaryDirectory(prefix=f'ms1919_{name}_') as td:
        dst=Path(td)/'repo'; shutil.copytree(ROOT,dst,ignore=ignore)
        clean_sha,mut_sha=apply(dst,name,old,new)
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
        return {'mutant':name,'status':status,'exit_code':code,'completion_marker':marker,'duration_seconds':round(time.time()-started,6),'clean_source_sha256':clean_sha,'mutant_source_sha256':mut_sha,'stdout_path':str(op.relative_to(ROOT)),'stderr_path':str(ep.relative_to(ROOT)),'stdout_tail':'\n'.join(out.splitlines()[-16:]),'stderr_tail':'\n'.join(err.splitlines()[-8:])}

started=time.time(); results=[run(name,*spec) for name,spec in MUTANTS.items()]
receipt={'schema':'microseed.ms1919.pass08.source-mutants.v1','discriminator':'CURRENT_STATE_LABEL != DURABLE_PROBE_LIFECYCLE_OWNERSHIP','started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'results':results,'survivors':[r['mutant'] for r in results if r['status']=='SURVIVED'],'rejected':[r['mutant'] for r in results if r['status']=='REJECTED'],'unknown':[r['mutant'] for r in results if r['status'].startswith('UNKNOWN')],'completion_marker':'COMPLETE' if all(r['completion_marker']=='COMPLETE' for r in results) else 'INCOMPLETE'}
(REPORT/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str((REPORT/'receipt.json').relative_to(ROOT)),'survivors':receipt['survivors'],'rejected':receipt['rejected'],'unknown':receipt['unknown'],'completion_marker':receipt['completion_marker']},indent=2))
raise SystemExit(0 if receipt['completion_marker']=='COMPLETE' and not receipt['survivors'] else 2)
