from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) != 3:
    raise SystemExit('usage: run_ms1914_pass03_full_suite_shard.py SHARD_INDEX SHARD_COUNT')
idx = int(sys.argv[1])
count = int(sys.argv[2])
if idx < 0 or count < 1 or idx >= count:
    raise SystemExit('invalid shard index/count')

all_files = sorted(str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT / 'tests').rglob('test_*.py'))
files = all_files[idx::count]
report = ROOT / 'reports' / 'ms1914_pass03_full_suite_shards' / f'shard_{idx:02d}_of_{count:02d}'
report.mkdir(parents=True, exist_ok=True)
out_path = report / 'pytest.stdout.log'
err_path = report / 'pytest.stderr.log'
receipt_path = report / 'receipt.json'

cmd = [sys.executable, 'tools/run_pytest_cleanup_neutral.py', '-q', *files]
started = time.time()
started_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started))
try:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=80)
    code, stdout, stderr = r.returncode, r.stdout, r.stderr
    marker = 'COMPLETE'
    classification = 'PASS' if code == 0 else 'NEGATIVE_OR_COMPATIBILITY_REVIEW_REQUIRED'
except subprocess.TimeoutExpired as exc:
    code = None
    stdout = (exc.stdout or b'').decode('utf-8', errors='replace') if isinstance(exc.stdout, bytes) else (exc.stdout or '')
    stderr = (exc.stderr or b'').decode('utf-8', errors='replace') if isinstance(exc.stderr, bytes) else (exc.stderr or '')
    marker = 'INCOMPLETE'
    classification = 'UNKNOWN_INCOMPLETE_TIMEOUT'
finished = time.time()
out_path.write_text(stdout, encoding='utf-8')
err_path.write_text(stderr, encoding='utf-8')
receipt = {
    'schema': 'microseed.ms1914.pass03.full-suite-shard.receipt.v1',
    'purpose': 'bounded compatibility shard; NOT mutation adequacy evidence',
    'shard_index': idx,
    'shard_count': count,
    'cwd': str(ROOT),
    'command': cmd,
    'file_count': len(files),
    'files': files,
    'started_at': started_iso,
    'finished_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(finished)),
    'duration_seconds': round(finished - started, 6),
    'exit_code': code,
    'classification': classification,
    'completion_marker': marker,
    'stdout_path': str(out_path.relative_to(ROOT)),
    'stderr_path': str(err_path.relative_to(ROOT)),
    'stdout_sha256': hashlib.sha256(stdout.encode('utf-8')).hexdigest(),
    'stderr_sha256': hashlib.sha256(stderr.encode('utf-8')).hexdigest(),
    'stdout_tail': '\n'.join(stdout.splitlines()[-10:]),
    'stderr_tail': '\n'.join(stderr.splitlines()[-10:]),
}
receipt_path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'receipt': str(receipt_path.relative_to(ROOT)), 'shard': [idx, count], 'file_count': len(files), 'exit_code': code, 'classification': classification, 'completion_marker': marker}, indent=2))
raise SystemExit(0 if code == 0 else 1)
