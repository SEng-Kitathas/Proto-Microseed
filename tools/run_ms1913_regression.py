from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / 'reports' / 'ms1913_regression'
REPORT_DIR.mkdir(parents=True, exist_ok=True)
RECEIPT_PATH = REPORT_DIR / 'receipt.json'

MODERN = [
    'tests/embodiment/test_ms1913_pass02_lifecycle_bypass_audit.py',
    'tests/embodiment/test_ms1912_pass01_completed_program_evidence_hardening.py',
    'tests/embodiment/test_ms1908_copied_discriminator_loophole.py',
    'tests/embodiment/test_ms1909_program_discriminator_satisfaction_restart.py',
    'tests/embodiment/test_ms1910_program_satisfaction_exact_source_and_drift.py',
    'tests/embodiment/test_ms1911_program_satisfaction_requirement_equivalence.py',
    'tests/embodiment/test_ms1899_1901_unique_direct_probe_availability.py',
    'tests/embodiment/test_ms1902_probe_available_need_gate_collision.py',
    'tests/embodiment/test_ms1904_1905_endogenous_direct_probe_program.py',
]

INHERITED = [
    'tests/embodiment/test_ms1152_integration.py',
    'tests/embodiment/test_ms1703_epistemic_step_intent_research.py',
    'tests/embodiment/test_ms1706_grounded_feasibility_epistemic_step.py',
    'tests/embodiment/test_ms1709_decision_bearing_priority.py',
    'tests/embodiment/test_ms1710_endogenous_epistemic_initiation.py',
    'tests/embodiment/test_ms1712_epistemic_state_only_outcome.py',
    'tests/embodiment/test_ms1713_tick_reauthorization.py',
    'tests/embodiment/test_ms1715_program_information_value.py',
    'tests/embodiment/test_ms1717_program_evidence_revisit.py',
    'tests/embodiment/test_ms1719_endogenous_episode_hostiles.py',
    'tests/embodiment/test_ms1724_source_owner_guards.py',
    'tests/embodiment/test_ms1831_pass04_program_step_model_space_challenge_revisit.py',
    'tests/embodiment/test_ms1837_pass10_full_generated_three_tick_realization.py',
    'tests/embodiment/test_ms1838_pass11_completed_program_evidence_preserves_physical_ancestry.py',
    'tests/embodiment/test_ms1857_pass10_model_challenge_not_automatic_history_refinement.py',
    'tests/embodiment/test_ms1858_pass11_live_second_step_challenge_participates_in_owned_history_refinement.py',
]

def run_group(name: str, command: list[str], timeout: int) -> dict:
    started = time.time()
    started_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started))
    try:
        r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        exit_code = r.returncode
        stdout = r.stdout
        stderr = r.stderr
        classification = 'PASS' if exit_code == 0 else 'NEGATIVE_OR_REPAIR_REQUIRED'
        marker = 'COMPLETE'
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        stdout = (exc.stdout or '') if isinstance(exc.stdout, str) else (exc.stdout or b'').decode('utf-8', errors='replace')
        stderr = (exc.stderr or '') if isinstance(exc.stderr, str) else (exc.stderr or b'').decode('utf-8', errors='replace')
        classification = 'UNKNOWN_INCOMPLETE_TIMEOUT'
        marker = 'INCOMPLETE'
    finished = time.time()
    out_path = REPORT_DIR / f'{name}.stdout.log'
    err_path = REPORT_DIR / f'{name}.stderr.log'
    out_path.write_text(stdout, encoding='utf-8')
    err_path.write_text(stderr, encoding='utf-8')
    return {
        'name': name,
        'command': command,
        'started_at': started_iso,
        'finished_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(finished)),
        'duration_seconds': round(finished - started, 6),
        'exit_code': exit_code,
        'classification': classification,
        'completion_marker': marker,
        'stdout_path': str(out_path.relative_to(ROOT)),
        'stderr_path': str(err_path.relative_to(ROOT)),
        'stdout_sha256': hashlib.sha256(stdout.encode('utf-8')).hexdigest(),
        'stderr_sha256': hashlib.sha256(stderr.encode('utf-8')).hexdigest(),
    }

started = time.time()
groups = []
groups.append(run_group(
    'modern', [sys.executable, '-m', 'pytest', '-q', *MODERN], 30
))
groups.append(run_group(
    'inherited_cleanup_neutral', [sys.executable, 'tools/run_pytest_cleanup_neutral.py', '-q', *INHERITED], 30
))
groups.append(run_group(
    'compileall', [sys.executable, '-m', 'compileall', '-q', 'microseed',
                   'tests/embodiment/test_ms1913_pass02_lifecycle_bypass_audit.py'], 20
))

all_pass = all(g['exit_code'] == 0 for g in groups)
receipt = {
    'schema': 'microseed.ms1913.regression.receipt.v1',
    'cwd': str(ROOT),
    'python': sys.version,
    'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started)),
    'finished_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time())),
    'groups': groups,
    'overall_classification': 'PASS' if all_pass else 'REVIEW_REQUIRED',
    'completion_marker': 'COMPLETE' if all(g['completion_marker'] == 'COMPLETE' for g in groups) else 'INCOMPLETE',
}
RECEIPT_PATH.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'receipt': str(RECEIPT_PATH.relative_to(ROOT)), 'overall_classification': receipt['overall_classification'], 'groups': [(g['name'], g['exit_code'], g['classification']) for g in groups]}, indent=2))
raise SystemExit(0 if all_pass else 1)
