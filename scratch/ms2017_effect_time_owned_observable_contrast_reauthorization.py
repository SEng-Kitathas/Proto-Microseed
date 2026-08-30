from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus
from microseed.development.action_learning import projection_conditioned_hypothesis_surface_digest
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, EpistemicStepExecutionContext
from microseed.development.epistemic_program import GeneratedEpistemicProgramCandidate, begin_generated_epistemic_program_trial
from microseed.runtime.entity import action_result_digest
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2010_runtime_owned_referent_decision_surface import _raw, oob
from scratch.ms2016_owned_observable_contrast_program_information import _setup_same_state_owned_prefix


def fixture():
    td, m, calls, world, binding_id, ba, bb = _setup_same_state_owned_prefix()
    live = m.derive_current_partial_operational_referent_ambiguity(binding_id, max_probe_steps=2, max_records=2048)
    assert live["status"] == "CURRENT_PARTIAL_OPERATIONAL_REFERENT_AMBIGUITY", live
    binding = m.action_outcome_learning.projection_conditioned_bindings[binding_id]
    hypothesis = projection_conditioned_hypothesis_surface_digest(binding, m.action_outcome_learning.relations)
    raw_candidate = next(x for x in live["informative_candidates"] if x["action_id"] == "P2")
    discriminator = action_result_digest({
        "hypothesis": hypothesis,
        "survivors": list(live["surviving_bucket_ids"]),
        "probe": "P2",
        "partition": raw_candidate["predicted_response_partition"],
    })
    unknown = m.append_evidence(
        "MS2017-E-U", {"kind": "OWNED_RAW_REFERENT_AMBIGUITY", "binding_id": binding_id},
        EpistemicStatus.UNKNOWN_INCOMPLETE, source="MS2017",
    )
    deficit = m.record_action_limited_unknown(
        deficit_id="MS2017-D", question_key="raw-ref-" + discriminator[:16],
        hypothesis_digest_sha256=hypothesis, unknown_evidence_id=unknown.evidence_id,
        missing_discriminator_signature_sha256=discriminator,
        premise_anchors=(
            EpistemicCurrentnessAnchor("VALUE", "V", 0),
            EpistemicCurrentnessAnchor("PROJECTION", binding.projection_id, binding.projection_epoch),
        ),
        assistance_ancestry=(
            "DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY",
            "QUALIFIED_ROUTING_SURFACE", "NO_CALLER_ALTERNATIVE_SET",
        ),
    )
    surface = m.derive_current_owned_referent_decision_surface(deficit.deficit_id, max_probe_steps=2, max_records=2048)
    assert surface["status"] == "CURRENT_OWNED_REFERENT_DECISION_SURFACE", surface
    candidate = GeneratedEpistemicProgramCandidate(
        "MS2017-P2-CAND", ("P2",), tuple(surface["source_relation_digests"]), (("F", 0),),
        assistance_ancestry=("OWNED_REFERENT_DECISION_SURFACE", "UNIQUE_INFORMATIVE_P2"),
    )
    trial = begin_generated_epistemic_program_trial(
        candidate, deficit_id=deficit.deficit_id,
        discrimination_signature_sha256=discriminator,
        capabilities=m.capabilities, obligation=act_ob(),
        current_frame_epochs=dict(m.frames.epochs),
        start_state_id="s0", start_state_evidence_id=m.action_closure.current_state.evidence_id,
    )
    dc = EpistemicDecisionBearingContext(tuple(surface["relation_sets"]), ())
    nomination = m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial, dc, act_ob())
    assert nomination["status"] == "ACTION_INTENT_NOMINATED", nomination
    assert calls == [], calls
    return td, m, calls, world, trial, surface, nomination


def run_success():
    td, m, calls, world, trial, surface, nomination = fixture()
    try:
        forged = EpistemicDecisionBearingContext((surface["relation_sets"][0], surface["relation_sets"][0]), ())
        result = m.execute_bounded_action(
            nomination["intent"]["intent_id"], act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(trial, decision_context=forged),
        )
        assert result["status"] == "ACTION_EXECUTED", result
        assert calls == ["P2"], calls
        return {
            "status": "PASS",
            "execution_status": result["status"],
            "calls": list(calls),
            "forged_caller_context_ignored": "YES",
            "ordinary_executor": "YES",
            "execution_commitment_id": result["execution"]["execution_commitment_id"],
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_duplicate_raw_block():
    td, m, calls, world, trial, surface, nomination = fixture()
    try:
        dup = m.record_bounded_raw_observation_coordinates(
            "OBS", oob(), evidence_id="MS2017-RAW-DUP", capture_id="MS2017-RAW-DUP", max_coordinates=8,
        )
        assert dup["status"] == "BOUNDED_RAW_OBSERVATION_RECORDED", dup
        forged = EpistemicDecisionBearingContext((surface["relation_sets"][0], surface["relation_sets"][0]), ())
        result = m.execute_bounded_action(
            nomination["intent"]["intent_id"], act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(trial, decision_context=forged),
        )
        assert result["status"] == "NO_EXECUTION", result
        assert calls == [], calls
        assert result["reason"] == "CURRENT_OWNED_REFERENT_DECISION_SURFACE_REQUIRED_AT_EXECUTION", result
        return {"status": "PASS", "reason": result["reason"], "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2017():
    return {
        "status": "PASS",
        "success": run_success(),
        "duplicate_raw": run_duplicate_raw_block(),
        "new_executor_required": "NO",
        "execution_path": "ORDINARY_EXECUTE_BOUNDED_ACTION",
        "execution_authority_gain": "NONE",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2017(), indent=2, sort_keys=True, default=str))
