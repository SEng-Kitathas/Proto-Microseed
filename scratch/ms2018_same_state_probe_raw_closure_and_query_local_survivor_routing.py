from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.epistemic_action import EpistemicDecisionBearingContext, EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2010_runtime_owned_referent_decision_surface import oob, bob
from scratch.ms2017_effect_time_owned_observable_contrast_reauthorization import fixture as ms2017_fixture


def _advance(m, trial, nomination, execution_result):
    execution_id = execution_result["execution"]["execution_id"]
    intent = m.action_closure.intents[nomination["intent"]["intent_id"]]
    execution = m.action_closure.executions[execution_id]
    outcome = next(o for o in m.action_closure.outcomes.values() if o.execution_id == execution_id)
    advanced = advance_epistemic_program_trial(
        trial, intent=intent, execution=execution, outcome=outcome,
        capabilities=m.capabilities, current_frame_epochs=dict(m.frames.epochs),
    )
    assert advanced.status == "COMPLETE", advanced
    return advanced


def run_ms2018():
    td, m, calls, world, trial, surface, nomination = ms2017_fixture()
    try:
        # Make the actual P2 effect advance the raw-observation world while leaving
        # the opaque control-state observation at s0. This is deliberately not a state split.
        def p2_apply(**_):
            assert world.index == 2, world.index
            world.index = 3
            world.value += 0.5
            calls.append("P2")
            return {"receipt": "P2"}

        m.capabilities.contracts["P2"].handler = p2_apply
        m.frames.bind_capability("F", "P2")
        # After the historical prefix is complete, the probe observation carries only
        # control-state + raw sensor coordinates. Epistemic probe closure must not smuggle
        # a regulatory value claim through the observation channel.
        m.capabilities.contracts["OBS"].handler = lambda **_: {
            "next_state_id": "s0",
            "raw_tokens": [str(x) for x in __import__("scratch.ms2005_bounded_referent_probe_reconstruction", fromlist=["UNIQUE_A"]).UNIQUE_A[world.index]],
        }

        forged = EpistemicDecisionBearingContext((surface["relation_sets"][0], surface["relation_sets"][0]), ())
        executed = m.execute_bounded_action(
            nomination["intent"]["intent_id"], act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(trial, decision_context=forged),
        )
        assert executed["status"] == "ACTION_EXECUTED", executed
        assert calls == ["P2"], calls
        execution_id = executed["execution"]["execution_id"]

        observed = m.record_bounded_action_outcome_via_observation_basis(
            execution_id,
            observation_capability_id="OBS", observation_obligation=oob(),
            basis_capability_id="BASIS", basis_obligation=bob(),
            evidence_id="MS2018-E-P2-AUTH", capture_id="MS2018-C-P2-AUTH",
        )
        assert observed["status"] == "ACTION_OUTCOME_OBSERVED", observed
        assert observed["outcome"]["actual_next_state_id"] == "s0", observed
        admitted = m.derive_admitted_opaque_transition_sample(execution_id)
        assert admitted["status"] == "ADMITTED_OPAQUE_TRANSITION_SAMPLE", admitted

        raw = m.record_bounded_raw_observation_coordinates(
            "OBS", oob(), evidence_id="MS2018-RAW-3", capture_id="MS2018-RAW-3", max_coordinates=8,
        )
        assert raw["status"] == "BOUNDED_RAW_OBSERVATION_RECORDED", raw
        prefix = m.derive_current_owned_opaque_probe_prefix(max_steps=3)
        assert prefix["status"] == "CURRENT_OWNED_OPAQUE_PROBE_PREFIX", prefix
        assert prefix["opaque_action_sequence"] == ("P0", "P1", "P2"), prefix

        binding_id = str(surface["binding_id"])
        before_deficit = m.epistemic_deficits.records[trial.deficit_id].state.value
        resolved = m.derive_current_partial_operational_referent_ambiguity(
            binding_id, max_probe_steps=3, max_records=4096,
        )
        assert resolved["status"] == "CURRENT_PARTIAL_OPERATIONAL_REFERENT_RESOLVED", resolved
        resolved_bucket = str(resolved["resolved_bucket_id"])

        advanced = _advance(m, trial, nomination, executed)
        complete = m.record_completed_epistemic_program_evidence(
            advanced, evidence_id="MS2018-E-COMPLETE",
        )
        assert complete["status"] == "PROGRAM_EVIDENCE_RECORDED", complete
        assert complete["truth_authority"] == complete["answer_authority"] == complete["execution_authority"] == "NONE"

        binding = m.action_outcome_learning.projection_conditioned_bindings[binding_id]
        routed = {}
        for action in ("A", "B"):
            routed[action] = m.resolve_projection_conditioned_action_outcome_relation(
                binding_id, projection_bucket_id=resolved_bucket,
                action_id=action, task_id=binding.task_id,
                channel_id=binding.channel_ids[0], horizon=binding.horizon,
            )
            assert routed[action]["status"] == "CURRENT_PARTITION_SCOPED_RELATION", routed[action]

        full_reassociation = m.resolve_current_operational_referent_class_set_conditioned_relation(
            binding_id, prefix["raw_samples"], prefix["opaque_action_sequence"],
            action_id="A", task_id=binding.task_id,
            channel_id=binding.channel_ids[0], horizon=binding.horizon,
            max_records=4096,
        )
        assert full_reassociation["status"] != "CURRENT_PARTITION_SCOPED_RELATION", full_reassociation

        return {
            "status": "PASS",
            "p2_actual_next_state_id": observed["outcome"]["actual_next_state_id"],
            "p2_calls": list(calls),
            "admitted_status": admitted["status"],
            "prefix_actions": list(prefix["opaque_action_sequence"]),
            "resolved_bucket_id": resolved_bucket,
            "deficit_state_before_program_evidence": before_deficit,
            "program_evidence_status": complete["status"],
            "deficit_state_after_program_evidence": m.epistemic_deficits.records[trial.deficit_id].state.value,
            "query_local_A_status": routed["A"]["status"],
            "query_local_B_status": routed["B"]["status"],
            "full_reassociation_status": full_reassociation["status"],
            "full_reassociation_reason": full_reassociation.get("reason"),
            "single_survivor_is_full_identity": "NO",
            "truth_authority": "NONE", "identity_authority": "NONE",
            "semantic_reference_authority": "NONE", "execution_authority": "NONE",
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


if __name__ == "__main__":
    print(json.dumps(run_ms2018(), indent=2, sort_keys=True, default=str))
