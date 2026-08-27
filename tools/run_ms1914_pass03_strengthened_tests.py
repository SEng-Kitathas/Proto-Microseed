from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'/'ms1914_pass03_strengthened'
REPORT.mkdir(parents=True,exist_ok=True)
receipt_path=REPORT/'receipt.json'
files=[
 'tests/embodiment/test_ms1709_decision_bearing_priority.py',
 'tests/embodiment/test_ms1706_grounded_feasibility_epistemic_step.py',
]
cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q',*files]
started=time.time()
try:
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=20)
 code=r.returncode; out=r.stdout; err=r.stderr; marker='COMPLETE'
 classification='PASS' if code==0 else 'NEGATIVE_OR_REPAIR_REQUIRED'
except subprocess.TimeoutExpired as exc:
 code=None; out=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
 err=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
 marker='INCOMPLETE'; classification='UNKNOWN_INCOMPLETE_TIMEOUT'
(REPORT/'pytest.stdout.log').write_text(out,encoding='utf-8')
(REPORT/'pytest.stderr.log').write_text(err,encoding='utf-8')
receipt={
 'schema':'microseed.ms1914.pass03.strengthened-tests.v1',
 'discriminator':'STANCE_MATCH != MECHANISM_VERIFIED_FOR_INHERITED_EPISTEMIC_GUARDS',
 'cwd':str(ROOT),'command':cmd,'python':sys.version,
 'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),
 'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(time.time())),
 'duration_seconds':round(time.time()-started,6),'exit_code':code,
 'classification':classification,'completion_marker':marker,
 'files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
 'stdout_sha256':hashlib.sha256(out.encode()).hexdigest(),
 'stderr_sha256':hashlib.sha256(err.encode()).hexdigest(),
 'stdout_path':'reports/ms1914_pass03_strengthened/pytest.stdout.log',
 'stderr_path':'reports/ms1914_pass03_strengthened/pytest.stderr.log',
}
receipt_path.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str(receipt_path.relative_to(ROOT)),'exit_code':code,'classification':classification},indent=2))
raise SystemExit(0 if code==0 else 1)
