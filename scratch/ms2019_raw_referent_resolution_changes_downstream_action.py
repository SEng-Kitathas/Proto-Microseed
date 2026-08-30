from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext, EpistemicStepExecutionContext,
    derive_current_grounded_feasibility_surface,
)
from microseed.development.rehearsal import CounterfactualRehearsalConfig
from scratch.ms2005_bounded_referent_probe_reconstruction import UNIQUE_A, UNIQUE_B
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2010_runtime_owned_referent_decision_surface import oob, bob
from scratch.ms2017_effect_time_owned_observable_contrast_reauthorization import fixture as ms2017_fixture


def run_case(raw_rows, expected_action: str) -> dict:
    td, m, calls, world, trial, surface, nomination = ms2017_fixture()
    try:
        def p2_apply(**_):
            assert world.index == 2, world.index
            world.index = 3
            world.value += 0.5
            calls.append("P2")
            return {"receipt": "P2"}

        m.capabilities.contracts["P2"].handler = p2_apply
        m.frames.bind_capability("F", "P2")
        m.capabilities.contracts["OBS"].handler = lambda **_: {
            "next_state_id": "s0",
            "raw_tokens": [str(x) for x in raw_rows[world.index]],
        }
        forged = EpistemicDecisionBearingContext((surface["relation_sets"][0], surface["relation_sets"][0]), ())
        p2 = m.execute_bounded_action(
            nomination["intent"]["intent_id"], act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(trial, decision_context=forged),
        )
        assert p2["status"] == "ACTION_EXECUTED", p2
        execution_id = p2["execution"]["execution_id"]
        observed = m.record_bounded_action_outcome_via_observation_basis(
            execution_id,
            observation_capability_id="OBS", observation_obligation=oob(),
            basis_capability_id="BASIS", basis_obligation=bob(),
            evidence_id=f"MS2019-{expected_action}-P2-OUT", capture_id=f"MS2019-{expected_action}-P2-OUT",
        )
        assert observed["status"] == "ACTION_OUTCOME_OBSERVED", observed
        assert observed["outcome"]["actual_next_state_id"] == "s0", observed
        raw = m.record_bounded_raw_observation_coordinates(
            "OBS", oob(), evidence_id=f"MS2019-{expected_action}-RAW", capture_id=f"MS2019-{expected_action}-RAW", max_coordinates=8,
        )
        assert raw["status"] == "BOUNDED_RAW_OBSERVATION_RECORDED", raw

        resolved = m.derive_current_partial_operational_referent_ambiguity(
            surface["binding_id"], max_probe_steps=3, max_records=4096,
        )
        assert resolved["status"] == "CURRENT_PARTIAL_OPERATIONAL_REFERENT_RESOLVED", resolved
        options, _ = derive_current_grounded_feasibility_surface(
            capabilities=m.capabilities, operational_scope_id="S",
        )
        ab_options = tuple(x for x in options if x.capability_id in ("A", "B"))
        binding = m.action_outcome_learning.projection_conditioned_bindings[surface["binding_id"]]
        proposal = m.nominate_counterfactual_rehearsal(
            (), ab_options, start_state_id="s0", value_id="V",
            config=CounterfactualRehearsalConfig(max_horizon=1),
            projection_routing_id=surface["binding_id"],
            projection_bucket_id=resolved["resolved_bucket_id"],
            routing_task_id=binding.task_id,
            routing_channel_id=binding.channel_ids[0],
        )
        assert proposal is not None, proposal
        assert proposal.sequence == (expected_action,), proposal.serializable()
        assert proposal.predicted_value_effect == 2.0, proposal.serializable()
        assert proposal.execution_authority == "NONE"

        downstream_nomination = m.nominate_bounded_action_intent(proposal.proposal_id, act_ob())
        assert downstream_nomination["status"] == "ACTION_INTENT_NOMINATED", downstream_nomination
        assert downstream_nomination["intent"]["capability_id"] == expected_action
        assert calls == ["P2"], calls
        downstream_execution = m.execute_bounded_action(downstream_nomination["intent"]["intent_id"], act_ob())
        assert downstream_execution["status"] == "ACTION_EXECUTED", downstream_execution
        assert calls == ["P2", expected_action], calls

        return {
            "status": "PASS",
            "resolved_bucket_id": resolved["resolved_bucket_id"],
            "p2_actual_next_state_id": observed["outcome"]["actual_next_state_id"],
            "rehearsal_sequence": list(proposal.sequence),
            "rehearsal_predicted_value_effect": proposal.predicted_value_effect,
            "downstream_nomination_status": downstream_nomination["status"],
            "downstream_execution_status": downstream_execution["status"],
            "calls": list(calls),
            "truth_authority": "NONE", "identity_authority": "NONE",
            "semantic_reference_authority": "NONE",
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2019() -> dict:
    a = run_case(UNIQUE_A, "A")
    b = run_case(UNIQUE_B, "B")
    assert a["resolved_bucket_id"] != b["resolved_bucket_id"]
    return {
        "status": "PASS",
        "A_response": a,
        "B_response": b,
        "same_control_state_probe": "YES__S0_TO_S0",
        "raw_response_changes_downstream_action": "YES",
        "new_policy_owner_required": "NO",
        "new_executor_required": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2019(), indent=2, sort_keys=True, default=str))
