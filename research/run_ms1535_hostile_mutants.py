from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MUTANTS = [
    (
        "INTENDED_EFFECT_AS_LEARNING_LABEL",
        "microseed/development/action_closure.py",
        'actual_effect = round(observed - pre_values[value_id], 3)',
        'actual_effect = round(float(effect_witnesses[f"{capability_id}::{value_id}"]["effect"]), 3)',
        "tests/embodiment/test_ms1535_multi_pressure_outcome_closure.py::test_vector_outcome_does_not_use_intended_or_predicted_effect_as_learning_label",
    ),
    (
        "FABRICATE_MISSING_COORDINATE",
        "microseed/development/action_closure.py",
        '        if value_id not in observed_values:\n            continue\n        observed = observed_values[value_id]',
        '        observed = observed_values.get(value_id, pre_values.get(value_id, 0.0))',
        "tests/embodiment/test_ms1535_multi_pressure_outcome_closure.py::test_missing_coordinate_remains_local_without_fabricating_complete_vector",
    ),
    (
        "LEARN_WITH_UNKNOWN_ANCESTRY",
        "microseed/runtime/entity.py",
        '                    if coordinate.learning_ancestry_status!="CURRENT":\n                        continue',
        '                    if False:\n                        continue',
        "tests/embodiment/test_ms1535_multi_pressure_outcome_closure.py::test_missing_current_learning_ancestry_preserves_outcome_but_withholds_learning_row",
    ),
    (
        "ACCEPT_UNBOUND_VALUE_COORDINATE",
        "microseed/runtime/entity.py",
        '        if any(value_id not in required_epochs for value_id in observed_values):\n            return {"status":"OUTCOME_REJECTED","reason":"MULTI_VALUE_OUTCOME_UNBOUND_VALUE"}',
        '        if False:\n            return {"status":"OUTCOME_REJECTED","reason":"MULTI_VALUE_OUTCOME_UNBOUND_VALUE"}',
        "tests/embodiment/test_ms1535_multi_pressure_outcome_closure.py::test_unbound_coordinate_is_rejected_instead_of_expanding_outcome_scope",
    ),
    (
        "ALLOW_SECOND_OUTCOME_FOR_ONE_EXECUTION",
        "microseed/runtime/entity.py",
        '        if any(o.execution_id==execution_id for o in self.action_closure.outcomes.values()): return {"status":"OUTCOME_REJECTED","reason":"EXECUTION_ALREADY_HAS_OUTCOME"}',
        '        if False: return {"status":"OUTCOME_REJECTED","reason":"EXECUTION_ALREADY_HAS_OUTCOME"}',
        "tests/embodiment/test_ms1535_multi_pressure_outcome_closure.py::test_one_execution_still_accepts_only_one_durable_outcome_record",
    ),
]


def main() -> int:
    results = []
    for name, rel, old, new, test in MUTANTS:
        with tempfile.TemporaryDirectory(prefix="ms1535-mutant-") as td:
            mutant = Path(td) / "repo"
            shutil.copytree(ROOT, mutant, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))
            path = mutant / rel
            text = path.read_text()
            if old not in text:
                results.append((name, "MUTATION_PATTERN_NOT_FOUND"))
                continue
            path.write_text(text.replace(old, new, 1))
            proc = subprocess.run(
                ["python", "-m", "pytest", "-q", test], cwd=mutant,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12,
            )
            results.append((name, "REJECTED" if proc.returncode != 0 else "SURVIVED_UNSAFELY"))
    for name, status in results:
        print(f"{name}: {status}")
    return 0 if all(status == "REJECTED" for _, status in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
