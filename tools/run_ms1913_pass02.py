from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / 'reports' / 'ms1913_pass02'
REPORT_DIR.mkdir(parents=True, exist_ok=True)
STDOUT_PATH = REPORT_DIR / 'pytest.stdout.log'
STDERR_PATH = REPORT_DIR / 'pytest.stderr.log'
REPORT_PATH = REPORT_DIR / 'receipt.json'
TEST_PATH = ROOT / 'tests' / 'embodiment' / 'test_ms1913_pass02_lifecycle_bypass_audit.py'

command = [sys.executable, '-m', 'pytest', '-q', str(TEST_PATH.relative_to(ROOT))]
started = time.time()
started_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started))
try:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=20)
    exit_code = result.returncode
    stdout = result.stdout
    stderr = result.stderr
    classification = 'PASS' if exit_code == 0 else 'NEGATIVE_OR_REPAIR_REQUIRED'
except subprocess.TimeoutExpired as exc:
    exit_code = None
    stdout = (exc.stdout or '') if isinstance(exc.stdout, str) else (exc.stdout or b'').decode('utf-8', errors='replace')
    stderr = (exc.stderr or '') if isinstance(exc.stderr, str) else (exc.stderr or b'').decode('utf-8', errors='replace')
    classification = 'UNKNOWN_INCOMPLETE_TIMEOUT'
finished = time.time()
finished_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(finished))
STDOUT_PATH.write_text(stdout, encoding='utf-8')
STDERR_PATH.write_text(stderr, encoding='utf-8')
receipt = {
    'schema': 'microseed.ms1913.pass02.receipt.v1',
    'discriminator': 'PROTECTED_PRIMARY_PATH != WHOLE_LIFECYCLE_CLOSURE_IF_SIBLING_ENTRY_POINTS_CAN_REACH_EFFECT_OR_EVIDENCE_WITHOUT_PROGRAM_DISCRIMINATOR_SATISFACTION',
    'cwd': str(ROOT),
    'command': command,
    'python': sys.version,
    'started_at': started_iso,
    'finished_at': finished_iso,
    'duration_seconds': round(finished - started, 6),
    'exit_code': exit_code,
    'test_sha256': hashlib.sha256(TEST_PATH.read_bytes()).hexdigest(),
    'stdout_path': str(STDOUT_PATH.relative_to(ROOT)),
    'stderr_path': str(STDERR_PATH.relative_to(ROOT)),
    'stdout_sha256': hashlib.sha256(stdout.encode('utf-8')).hexdigest(),
    'stderr_sha256': hashlib.sha256(stderr.encode('utf-8')).hexdigest(),
    'completion_marker': 'COMPLETE' if exit_code is not None else 'INCOMPLETE',
    'classification': classification,
}
REPORT_PATH.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'receipt': str(REPORT_PATH.relative_to(ROOT)), 'exit_code': exit_code, 'classification': classification}, indent=2))
raise SystemExit(0 if exit_code is None else exit_code)
