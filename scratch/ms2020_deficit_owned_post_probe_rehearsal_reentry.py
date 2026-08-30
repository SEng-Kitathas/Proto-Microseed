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
from scratch.ms2018_same_state_probe_raw_closure_and_query_local_survivor_routing import _advance


def _close(m, td):
    m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def _through_raw(raw_rows, tag: str):
    td, m, calls, world, trial, surface, nomination = ms2017_fixture()
    def p2_apply(**_):
        assert world.index == 2, world.index
        world.index = 3; world.value += 0.5; calls.append("P2")
        return {"receipt": "P2"}
    m.capabilities.contracts["P2"].handler = p2_apply
    m.frames.bind_capability("F", "P2")
    m.capabilities.contracts["OBS"].handler = lambda **_: {
        "next_state_id": "s0", "raw_tokens": [str(x) for x in raw_rows[world.index]],
    }
    forged = EpistemicDecisionBearingContext((surface["relation_sets"][0], surface["relation_sets"][0]), ())
    execution = m.execute_bounded_action(
        nomination["intent"]["intent_id"], act_ob(),
        epistemic_step_context=EpistemicStepExecutionContext(trial, decision_context=forged),
    )
    assert execution["status"] == "ACTION_EXECUTED", execution
    eid = execution["execution"]["execution_id"]
    observed = m.record_bounded_action_outcome_via_observation_basis(
        eid, observation_capability_id="OBS", observation_obligation=oob(),
        basis_capability_id="BASIS", basis_obligation=bob(),
        evidence_id=f"MS2020-{tag}-OUT", capture_id=f"MS2020-{tag}-OUT",
    )
    assert observed["status"] == "ACTION_OUTCOME_OBSERVED", observed
    raw = m.record_bounded_raw_observation_coordinates(
        "OBS", oob(), evidence_id=f"MS2020-{tag}-RAW", capture_id=f"MS2020-{tag}-RAW", max_coordinates=8,
    )
    assert raw["status"] == "BOUNDED_RAW_OBSERVATION_RECORDED", raw
    return td, m, calls, trial, nomination, execution


def _options(m):
    options, _ = derive_current_grounded_feasibility_surface(capabilities=m.capabilities, operational_scope_id="S")
    return tuple(x for x in options if x.capability_id in ("A", "B"))


def run_completed_case(raw_rows, expected_action: str):
    td, m, calls, trial, nomination, execution = _through_raw(raw_rows, expected_action)
    try:
        advanced = _advance(m, trial, nomination, execution)
        complete = m.record_completed_epistemic_program_evidence(
            advanced, evidence_id=f"MS2020-{expected_action}-COMPLETE",
        )
        assert complete["status"] == "PROGRAM_EVIDENCE_RECORDED", complete
        context = m.derive_current_resolved_referent_routing_context(
            trial.deficit_id, max_probe_steps=3, max_records=4096,
        )
        assert context["status"] == "CURRENT_RESOLVED_REFERENT_ROUTING_CONTEXT", context
        proposal = m.nominate_current_resolved_referent_rehearsal(
            trial.deficit_id, (), _options(m), start_state_id="s0", value_id="V",
            config=CounterfactualRehearsalConfig(max_horizon=1), max_probe_steps=3, max_records=4096,
        )
        assert proposal is not None, context
        assert proposal.sequence == (expected_action,), proposal.serializable()
        return {
            "status": "PASS",
            "resolved_bucket_id": context["resolved_bucket_id"],
            "rehearsal_sequence": list(proposal.sequence),
            "caller_supplied_binding_id": "NO",
            "caller_supplied_bucket_id": "NO",
            "deficit_state": m.epistemic_deficits.records[trial.deficit_id].state.value,
            "identity_authority": context["identity_authority"],
            "semantic_reference_authority": context["semantic_reference_authority"],
            "execution_authority": context["execution_authority"],
        }
    finally:
        _close(m, td)


def run_precompletion_block():
    td, m, calls, trial, nomination, execution = _through_raw(UNIQUE_A, "PRE")
    try:
        context = m.derive_current_resolved_referent_routing_context(
            trial.deficit_id, max_probe_steps=3, max_records=4096,
        )
        proposal = m.nominate_current_resolved_referent_rehearsal(
            trial.deficit_id, (), _options(m), start_state_id="s0", value_id="V",
            config=CounterfactualRehearsalConfig(max_horizon=1), max_probe_steps=3, max_records=4096,
        )
        assert context["status"] == "DEFER_UNKNOWN", context
        assert context["reason"] == "CURRENT_COMPLETED_REFERENT_DEFICIT_REQUIRED", context
        assert proposal is None
        return {"status": "PASS", "reason": context["reason"], "proposal": None}
    finally:
        _close(m, td)


def run_postcompletion_duplicate_block():
    td, m, calls, trial, nomination, execution = _through_raw(UNIQUE_A, "DUP")
    try:
        advanced = _advance(m, trial, nomination, execution)
        complete = m.record_completed_epistemic_program_evidence(advanced, evidence_id="MS2020-DUP-COMPLETE")
        assert complete["status"] == "PROGRAM_EVIDENCE_RECORDED", complete
        dup = m.record_bounded_raw_observation_coordinates(
            "OBS", oob(), evidence_id="MS2020-DUP-RAW-2", capture_id="MS2020-DUP-RAW-2", max_coordinates=8,
        )
        assert dup["status"] == "BOUNDED_RAW_OBSERVATION_RECORDED", dup
        context = m.derive_current_resolved_referent_routing_context(
            trial.deficit_id, max_probe_steps=3, max_records=4096,
        )
        assert context["status"] == "DEFER_UNKNOWN", context
        assert context["reason"] == "EXACT_SINGLE_CURRENT_RESOLVED_REFERENT_ROUTING_CONTEXT_REQUIRED", context
        return {"status": "PASS", "reason": context["reason"], "matching_binding_ids": list(context["matching_binding_ids"])}
    finally:
        _close(m, td)


def run_ms2020():
    a = run_completed_case(UNIQUE_A, "A")
    b = run_completed_case(UNIQUE_B, "B")
    return {
        "status": "PASS",
        "A_response": a, "B_response": b,
        "precompletion": run_precompletion_block(),
        "postcompletion_duplicate": run_postcompletion_duplicate_block(),
        "new_rehearsal_owner_required": "NO",
        "new_referent_manager_required": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2020(), indent=2, sort_keys=True, default=str))
