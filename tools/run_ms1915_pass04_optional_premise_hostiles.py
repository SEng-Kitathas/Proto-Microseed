from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'/'ms1915_pass04_optional_premise'
REPORT.mkdir(parents=True,exist_ok=True)
OUT=REPORT/'pytest.stdout.log'; ERR=REPORT/'pytest.stderr.log'; REC=REPORT/'receipt.json'
TEST='tests/embodiment/test_ms1915_pass04_optional_priority_information_api_boundary.py'
cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q',TEST]
started=time.time()
try:
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=25)
 code,stdout,stderr=r.returncode,r.stdout,r.stderr; marker='COMPLETE'; classification='PASS' if code==0 else 'NEGATIVE_EXPECTED_OR_REPAIR_REQUIRED'
except subprocess.TimeoutExpired as exc:
 code=None; stdout=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or ''); stderr=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or ''); marker='INCOMPLETE'; classification='UNKNOWN_INCOMPLETE_TIMEOUT'
finished=time.time(); OUT.write_text(stdout,encoding='utf-8'); ERR.write_text(stderr,encoding='utf-8')
receipt={'schema':'microseed.ms1915.pass04.optional-premise-hostiles.v1','discriminator':'LOCAL_PRECHECK_OPTIONALITY != SAFE_PUBLIC_INTENT_API_IF_PRIORITY_INFORMATION_CAN_BE_OMITTED','cwd':str(ROOT),'command':cmd,'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(finished)),'duration_seconds':round(finished-started,6),'exit_code':code,'classification':classification,'completion_marker':marker,'test_sha256':hashlib.sha256((ROOT/TEST).read_bytes()).hexdigest(),'stdout_path':str(OUT.relative_to(ROOT)),'stderr_path':str(ERR.relative_to(ROOT)),'stdout_sha256':hashlib.sha256(stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(stderr.encode()).hexdigest(),'stdout_tail':'\n'.join(stdout.splitlines()[-30:]),'stderr_tail':'\n'.join(stderr.splitlines()[-20:])}
REC.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str(REC.relative_to(ROOT)),'exit_code':code,'classification':classification,'completion_marker':marker},indent=2))
raise SystemExit(0 if code==0 else 1)
