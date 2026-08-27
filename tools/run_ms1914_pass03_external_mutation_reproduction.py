from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / 'reports' / 'ms1914_pass03_mutants'
REPORT_DIR.mkdir(parents=True, exist_ok=True)
RECEIPT = REPORT_DIR / 'receipt.json'

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

MUTANTS = {
    'IGNORE_ZERO_PRESSURE': {
        'file': 'microseed/development/epistemic_priority.py',
        'old': '''    if float(pressure.get("pressure_magnitude", 0.0)) <= 0.0:\n        return RelationalCommitment(_sha({"target": target, "pressure": pressure}), target, TernaryCommitment.NO, reason="NO_CURRENT_REGULATORY_PRESSURE", qualifiers=qnone, premise_ids=(deficit.deficit_id, anchor.object_id))\n''',
        'new': '',
    },
    'IGNORE_CAPABILITY_EPOCH_DRIFT': {
        'file': 'microseed/development/epistemic_priority.py',
        'old': '''            if current_capability_epochs.get(rel.capability_id) != rel.capability_epoch:\n                return RelationalCommitment(_sha({"target": target, "capability": rel.capability_id}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_CAPABILITY_EPOCH_DRIFT:{rel.capability_id}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))\n''',
        'new': '',
    },
    'ACCEPT_NONCURRENT_VALUE': {
        'file': 'microseed/development/epistemic_priority.py',
        'old': '''    if not values.is_current(anchor.object_id, anchor.epoch):\n        return RelationalCommitment(_sha({"target": target, "value": anchor.serializable(), "current": False}), target, TernaryCommitment.UNKNOWN, reason="VALUE_PREMISE_NOT_CURRENT", qualifiers=qnone, premise_ids=(deficit.deficit_id, anchor.object_id))\n''',
        'new': '',
    },
    'ALLOW_NON_ACTION_LIMITED_DEFICIT': {
        'file': 'microseed/development/epistemic_priority.py',
        'old': '''    if deficit is None or deficit.state != EpistemicDeficitState.ACTION_LIMITED:\n        return RelationalCommitment(_sha({"target": target, "deficit": None}), target, TernaryCommitment.UNKNOWN, reason="ACTION_LIMITED_DEFICIT_REQUIRED", qualifiers=qnone)\n''',
        'new': '''    if deficit is None:\n        return RelationalCommitment(_sha({"target": target, "deficit": None}), target, TernaryCommitment.UNKNOWN, reason="ACTION_LIMITED_DEFICIT_REQUIRED", qualifiers=qnone)\n''',
    },
    'FEASIBILITY_NOT_REQUIRED_CURRENT': {
        'file': 'microseed/development/epistemic_action.py',
        'old': '''    if cap.qualification not in {QualificationState.QUALIFIED, QualificationState.SHADOW_QUALIFIED} or cap.currentness != "CURRENT":\n        return _unknown("FEASIBILITY_CAPABILITY_NOT_CURRENT")\n''',
        'new': '''    if cap.qualification not in {QualificationState.QUALIFIED, QualificationState.SHADOW_QUALIFIED}:\n        return _unknown("FEASIBILITY_CAPABILITY_NOT_CURRENT")\n''',
    },
}


def ignore(path: str, names: list[str]):
    return {'.git', 'reports', '.pytest_cache', '__pycache__'}


def patch(root: Path, spec: dict) -> tuple[str, str]:
    p = root / spec['file']
    raw = p.read_text(encoding='utf-8')
    old = spec['old'].replace('\n', '\r\n') if '\r\n' in raw else spec['old']
    new = spec['new'].replace('\n', '\r\n') if '\r\n' in raw else spec['new']
    if old not in raw:
        raise RuntimeError(f"MUTATION_PATTERN_NOT_FOUND:{spec['file']}")
    mutated = raw.replace(old, new, 1)
    p.write_text(mutated, encoding='utf-8')
    return hashlib.sha256(raw.encode('utf-8')).hexdigest(), hashlib.sha256(mutated.encode('utf-8')).hexdigest()


def run_mutant(name: str, spec: dict) -> dict:
    started = time.time()
    with tempfile.TemporaryDirectory(prefix=f'ms1914_{name}_') as td:
        dst = Path(td) / 'repo'
        shutil.copytree(ROOT, dst, ignore=ignore)
        clean_sha, mutant_sha = patch(dst, spec)
        cmd = [sys.executable, 'tools/run_pytest_cleanup_neutral.py', '-q', *INHERITED]
        try:
            r = subprocess.run(cmd, cwd=dst, capture_output=True, text=True, timeout=20)
            exit_code = r.returncode
            stdout = r.stdout
            stderr = r.stderr
            status = 'SURVIVED' if exit_code == 0 else 'REJECTED'
            marker = 'COMPLETE'
        except subprocess.TimeoutExpired as exc:
            exit_code = None
            stdout = (exc.stdout or b'').decode('utf-8', errors='replace') if isinstance(exc.stdout, bytes) else (exc.stdout or '')
            stderr = (exc.stderr or b'').decode('utf-8', errors='replace') if isinstance(exc.stderr, bytes) else (exc.stderr or '')
            status = 'UNKNOWN_INCOMPLETE_TIMEOUT'
            marker = 'INCOMPLETE'
        out = REPORT_DIR / f'{name}.stdout.log'
        err = REPORT_DIR / f'{name}.stderr.log'
        out.write_text(stdout, encoding='utf-8')
        err.write_text(stderr, encoding='utf-8')
        return {
            'mutant': name,
            'source_file': spec['file'],
            'clean_source_sha256': clean_sha,
            'mutant_source_sha256': mutant_sha,
            'command': cmd,
            'exit_code': exit_code,
            'status': status,
            'completion_marker': marker,
            'duration_seconds': round(time.time() - started, 6),
            'stdout_path': str(out.relative_to(ROOT)),
            'stderr_path': str(err.relative_to(ROOT)),
            'stdout_sha256': hashlib.sha256(stdout.encode('utf-8')).hexdigest(),
            'stderr_sha256': hashlib.sha256(stderr.encode('utf-8')).hexdigest(),
            'stdout_tail': '\n'.join(stdout.splitlines()[-8:]),
            'stderr_tail': '\n'.join(stderr.splitlines()[-8:]),
        }


started = time.time()
results = []
for name, spec in MUTANTS.items():
    results.append(run_mutant(name, spec))

receipt = {
    'schema': 'microseed.ms1914.pass03.external-mutation-reproduction.v1',
    'discriminator': 'STANCE_MATCH != MECHANISM_VERIFIED_FOR_INHERITED_EPISTEMIC_GUARDS',
    'cwd': str(ROOT),
    'python': sys.version,
    'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started)),
    'finished_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time())),
    'results': results,
    'survivors': [x['mutant'] for x in results if x['status'] == 'SURVIVED'],
    'rejected': [x['mutant'] for x in results if x['status'] == 'REJECTED'],
    'unknown': [x['mutant'] for x in results if x['status'].startswith('UNKNOWN')],
    'completion_marker': 'COMPLETE' if all(x['completion_marker'] == 'COMPLETE' for x in results) else 'INCOMPLETE',
}
RECEIPT.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({
    'receipt': str(RECEIPT.relative_to(ROOT)),
    'survivors': receipt['survivors'],
    'rejected': receipt['rejected'],
    'unknown': receipt['unknown'],
    'completion_marker': receipt['completion_marker'],
}, indent=2))
raise SystemExit(0 if receipt['completion_marker'] == 'COMPLETE' else 2)
