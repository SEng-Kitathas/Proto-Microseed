from __future__ import annotations

import json
import tempfile
from pathlib import Path

from microseed import Authority, Microseed, Observation
from microseed.development.discovery import DiscoveryConfig
from research.run_ms1536_habitat_r2_whole_organism import (
    ACTIONS, VALUES, State, collect_pre_drift_random_training, deterministic_step,
    register_current_surfaces, seed_training,
)


def main() -> None:
    td = tempfile.TemporaryDirectory(prefix="ms1536-localize-")
    ms = Microseed(Path(td.name))
    register_current_surfaces(ms)
    seed_training(ms, collect_pre_drift_random_training(1536))
    observed = {"ENERGY": 3.2, "THERMAL": 7.6, "INTEGRITY": 6.0}
    for value_id, value in observed.items():
        ms.observe_value_state(value_id, value)
    ms.observe_opaque_control_state(
        Observation("LOCALIZE", "EVALUATOR_ASSAY", "control", "R2-OPAQUE-STATE", authority=Authority.OBSERVATION_ONLY),
        evidence_id="LOCALIZE-CONTROL",
    )
    quantization = {}
    for step in (0.5, 0.25, 0.2, 0.1, 0.05):
        result = ms.derive_multi_value_action_licenses(VALUES, config=DiscoveryConfig(quantization_step=step))
        quantization[str(step)] = {
            "status": result["status"],
            "licensed_action_ids": result["licensed_action_ids"],
            "rest_effects": {value_id: result["effect_witnesses"][f"REST::{value_id}"].get("effect") for value_id in VALUES},
        }
    state = State(observed["ENERGY"], observed["THERMAL"], observed["INTEGRITY"])
    hidden_deltas = {}
    for action in ACTIONS:
        next_state = deterministic_step(state, action, 0)
        hidden_deltas[action] = {
            "ENERGY": round(next_state.energy - state.energy, 3),
            "THERMAL": round(next_state.thermal - state.thermal, 3),
            "INTEGRITY": round(next_state.integrity - state.integrity, 3),
        }
    out = {
        "schema": "microseed.ms1536.pass09.localization.v1",
        "organism_evidence": {
            "quantization_ablation": quantization,
            "result": "SMALLER_EXISTING_QUANTIZATION_STEP_ALONE_DOES_NOT_RESTORE_A_UNIQUE_LICENSE",
        },
        "evaluator_only_diagnostic": {
            "representative_true_state": observed,
            "deterministic_one_step_deltas": hidden_deltas,
            "authority": "EVALUATOR_ONLY__NOT_ORGANISM_EVIDENCE",
        },
        "localization": "STATE_OR_CONTEXT_DEPENDENT_TOTAL_CONSEQUENCE_IS_SMEARED_BY_GLOBAL_ACTION_VALUE_EFFECT_WITNESS",
        "nonclaim": "DOES_NOT_PROVE_A_NEW_STATE_REPRESENTATION_PRIMITIVE_IS_MISSING",
    }
    Path(__file__).with_name("MS1536_PASS09_FAILURE_LOCALIZATION.json").write_text(json.dumps(out, indent=2, sort_keys=True)+"\n")
    print(json.dumps(out, indent=2, sort_keys=True))
    td.cleanup()


if __name__ == "__main__":
    main()
