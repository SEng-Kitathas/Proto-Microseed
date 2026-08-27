from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / 'reports' / 'ms1912_pass01'
REPORT_DIR.mkdir(parents=True, exist_ok=True)
STDOUT_PATH = REPORT_DIR / 'pytest.stdout.log'
STDERR_PATH = REPORT_DIR / 'pytest.stderr.log'
REPORT_PATH = REPORT_DIR / 'receipt.json'
TEST_PATH = ROOT / 'tests' / 'embodiment' / 'test_ms1912_pass01_completed_program_evidence_hardening.py'

command = [
    sys.executable,
    '-m',
    'pytest',
    '-q',
    str(TEST_PATH.relative_to(ROOT)),
]
started = time.time()
started_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started))
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=20)
finished = time.time()
finished_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(finished))
STDOUT_PATH.write_text(result.stdout, encoding='utf-8')
STDERR_PATH.write_text(result.stderr, encoding='utf-8')
receipt = {
    'schema': 'microseed.ms1912.pass01.receipt.v1',
    'discriminator': 'COMPLETE_MATCHING_DISCRIMINATOR != COMPLETED_PROGRAM_EVIDENCE_ENTITLED_TO_PROMOTION_IF_SOURCE_ANCESTRY_IS_FORGED',
    'cwd': str(ROOT),
    'command': command,
    'python': sys.version,
    'started_at': started_iso,
    'finished_at': finished_iso,
    'duration_seconds': round(finished - started, 6),
    'exit_code': result.returncode,
    'test_sha256': hashlib.sha256(TEST_PATH.read_bytes()).hexdigest(),
    'stdout_path': str(STDOUT_PATH.relative_to(ROOT)),
    'stderr_path': str(STDERR_PATH.relative_to(ROOT)),
    'stdout_sha256': hashlib.sha256(result.stdout.encode('utf-8')).hexdigest(),
    'stderr_sha256': hashlib.sha256(result.stderr.encode('utf-8')).hexdigest(),
    'completion_marker': 'COMPLETE',
    'classification': 'PASS' if result.returncode == 0 else 'NEGATIVE_OR_HARNESS_REVIEW_REQUIRED',
}
REPORT_PATH.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'receipt': str(REPORT_PATH.relative_to(ROOT)), 'exit_code': result.returncode, 'classification': receipt['classification']}, indent=2))
raise SystemExit(result.returncode)
