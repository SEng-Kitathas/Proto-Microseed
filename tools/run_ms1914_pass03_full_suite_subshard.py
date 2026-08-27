from __future__ import annotations

from pathlib import Path
import hashlib, json, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) != 5:
    raise SystemExit('usage: run_ms1914_pass03_full_suite_subshard.py PARENT_INDEX PARENT_COUNT CHILD_INDEX CHILD_COUNT')
parent_idx, parent_count, child_idx, child_count = map(int, sys.argv[1:])
all_files = sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'tests').rglob('test_*.py'))
parent_files = all_files[parent_idx::parent_count]
files = parent_files[child_idx::child_count]
report = ROOT/'reports'/'ms1914_pass03_full_suite_subshards'/f'parent_{parent_idx:02d}_of_{parent_count:02d}'/f'child_{child_idx:02d}_of_{child_count:02d}'
report.mkdir(parents=True, exist_ok=True)
out_path, err_path, receipt_path = report/'pytest.stdout.log', report/'pytest.stderr.log', report/'receipt.json'
cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q',*files]
started=time.time()
try:
    r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=40)
    code,stdout,stderr=r.returncode,r.stdout,r.stderr; marker='COMPLETE'; classification='PASS' if code==0 else 'NEGATIVE_OR_COMPATIBILITY_REVIEW_REQUIRED'
except subprocess.TimeoutExpired as exc:
    code=None
    stdout=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
    stderr=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
    marker='INCOMPLETE'; classification='UNKNOWN_INCOMPLETE_TIMEOUT'
finished=time.time(); out_path.write_text(stdout,encoding='utf-8'); err_path.write_text(stderr,encoding='utf-8')
receipt={
 'schema':'microseed.ms1914.pass03.full-suite-subshard.receipt.v1',
 'purpose':'recursive bounded compatibility shard; NOT mutation adequacy evidence',
 'parent_index':parent_idx,'parent_count':parent_count,'child_index':child_idx,'child_count':child_count,
 'file_count':len(files),'files':files,'cwd':str(ROOT),'command':cmd,
 'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),
 'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(finished)),
 'duration_seconds':round(finished-started,6),'exit_code':code,'classification':classification,'completion_marker':marker,
 'stdout_path':str(out_path.relative_to(ROOT)),'stderr_path':str(err_path.relative_to(ROOT)),
 'stdout_sha256':hashlib.sha256(stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(stderr.encode()).hexdigest(),
 'stdout_tail':'\n'.join(stdout.splitlines()[-10:]),'stderr_tail':'\n'.join(stderr.splitlines()[-10:])}
receipt_path.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str(receipt_path.relative_to(ROOT)),'parent':[parent_idx,parent_count],'child':[child_idx,child_count],'file_count':len(files),'exit_code':code,'classification':classification},indent=2))
raise SystemExit(0 if code==0 else 1)
