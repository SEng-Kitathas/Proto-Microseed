from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.epistemic_action import EpistemicStepExecutionContext
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2035_organism_owned_current_value_frame_completeness import _contract
from scratch.ms2036_full_frame_bound_pareto_research import _fixture, _p2_dominates_effects


def run_ms2040() -> dict:
    td, ms, calls, by_probe, _effects = _fixture(_p2_dominates_effects())
    try:
        selected = by_probe["P2"]
        nominated = ms.nominate_current_strict_full_frame_referent_epistemic_opportunity(act_ob())
        assert nominated["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", nominated
        assert nominated["selected_probe_action_id"] == "P2"
        intent_id = nominated["nomination"]["intent"]["intent_id"]

        # Expand the current constitutional frame after nomination without supplying
        # the downstream action/X effect evidence required to compare all opportunities.
        ms.register_value_variable(_contract("X"))
        ms.observe_value_state("X", 1.0)

        fresh = ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob())
        assert fresh["status"] == "NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", fresh
        assert fresh["selection_authority"] == "NONE", fresh
        assert fresh["reason"].startswith("CURRENT_DOWNSTREAM_ACTION_VALUE_EFFECT_REQUIRED:"), fresh

        execution = ms.execute_bounded_action(
            intent_id,
            act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(
                selected["trial"], decision_context=selected["decision_context"],
            ),
        )

        # This campaign is a violation reproducer. Current code is expected to execute
        # because the full-frame selected-origin marker is not yet recognized by the
        # effect-time global-selection gate.
        assert execution["status"] == "ACTION_EXECUTED", execution
        assert calls == ["P2"], calls
        return {
            "status": "VIOLATION_REPRODUCED",
            "nomination": nominated,
            "fresh_full_frame_selection": fresh,
            "execution": execution,
            "handler_calls": list(calls),
            "violation": "NOMINATION_TIME_FULL_FRAME_SELECTION != EFFECT_TIME_FULL_FRAME_SELECTION_CURRENTNESS",
            "marker_bypass": "UNRECOGNIZED_SELECTED_ORIGIN_MARKER_BYPASSES_EFFECT_TIME_GLOBAL_SELECTION_REAUTHORIZATION",
        }
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


if __name__ == "__main__":
    print(json.dumps(run_ms2040(), indent=2, sort_keys=True, default=str))
