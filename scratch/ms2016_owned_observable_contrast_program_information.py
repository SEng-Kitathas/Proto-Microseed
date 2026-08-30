from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus, Microseed,
    Observation, OperationalFrameContract, QualificationState, ValueVariableContract,
)
from microseed.development.action_learning import projection_conditioned_hypothesis_surface_digest
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext,
    derive_current_decision_bearing_commitment_from_grounded_surface,
    derive_current_grounded_feasibility_surface,
    derive_current_program_discrimination_commitment,
)
from microseed.development.epistemic_program import (
    GeneratedEpistemicProgramCandidate, begin_generated_epistemic_program_trial,
)
from microseed.runtime.entity import action_result_digest
from scratch.ms2005_bounded_referent_probe_reconstruction import UNIQUE_A, UNIQUE_B, _persist_context, _close
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import (
    ACTS, _relation, _qualify, act_ob,
)
from scratch.ms2010_runtime_owned_referent_decision_surface import (
    PrefixWorld, _attach_history, _execute, _raw,
)


def _setup_same_state_owned_prefix():
    td = tempfile.TemporaryDirectory(prefix="ms2016-owned-contrast-")
    m = Microseed(Path(td.name))
    calls: list[str] = []

    m.register_operational_frame(OperationalFrameContract(
        "F", "opaque", "f" * 64, Authority.DERIVED_READ_ONLY, ("MS2016",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    m.register_value_variable(ValueVariableContract(
        "V", "reg", 0, 10, "v" * 64, Authority.REFERENCE_ONLY, ("MS2016",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    m.observe_value_state("V", -1.0)
    m.register_episode_schema(EpisodeSchemaContract(
        "EP", "opaque-episode", "e" * 64, Authority.DERIVED_READ_ONLY, ("MS2016",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        frame_epochs=(("F", 0),), value_epochs=(("V", 0),),
    ))
    for cid in ACTS:
        m.register_capability(CapabilityContract(
            cid, "opaque", {}, {}, (), (), Authority.EFFECT, ("MS2016",), "CURRENT", {},
            query_obligation_id="MS2008-ACT", qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _cid=cid, **_: calls.append(_cid) or {"receipt": _cid},
            operational_scope_id="S",
        ))
        m.register_capability(CapabilityContract(
            "FEAS-" + cid, "feas", {"target_capability_id": cid}, {}, (), (),
            Authority.DERIVED_READ_ONLY, ("MS2016",), "CURRENT", {}, dependencies=(cid,),
            query_obligation_id="MS2008-FEAS-" + cid,
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {"feasibility": "FEASIBLE", "reason": "CURRENT"},
            operational_scope_id="S",
        ))

    ca = _persist_context(m, "MS2016-A", UNIQUE_A)
    cb = _persist_context(m, "MS2016-B", UNIQUE_B)
    ba = str(ca["projection_bucket_id"])
    bb = str(cb["projection_bucket_id"])
    projection = m.register_epistemic_projection(
        "MS2016-REFSET", m.operational_referent_class_set_projection_signature_sha256(),
        assistance_ancestry=("SUPPLIED_OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_COORDINATE", "NO_SEMANTIC_REFERENT_AUTHORITY"),
    )

    # Downstream actions differ; P2 has the SAME opaque control-state result.
    rels_a = {
        "A": _relation(m, "MS2016-A-A", "A", "a-next", 2.0, "16AA"),
        "B": _relation(m, "MS2016-A-B", "B", "b-next", 0.0, "16AB"),
        "P2": _relation(m, "MS2016-A-P2", "P2", "s0", 0.0, "16AP"),
    }
    rels_b = {
        "A": _relation(m, "MS2016-B-A", "A", "a-next-b", 0.0, "16BA"),
        "B": _relation(m, "MS2016-B-B", "B", "b-next-b", 2.0, "16BB"),
        "P2": _relation(m, "MS2016-B-P2", "P2", "s0", 0.0, "16BP"),
    }
    binding_id = _qualify(m, projection, ba, bb, rels_a, rels_b)
    m.observe_opaque_control_state(
        Observation("MS2016-CS", "EXT", "opaque-control", "s0", authority=Authority.OBSERVATION_ONLY),
        evidence_id="MS2016-E-CS",
    )

    # Build actual owned P0/P1 history + current raw prefix.
    world = PrefixWorld()
    _attach_history(m, world)
    _raw(m, "16-0")
    _execute(m, "P0", "16-0")
    _raw(m, "16-1")
    _execute(m, "P1", "16-1")
    _raw(m, "16-2")
    m.observe_value_state("V", -1.0)
    return td, m, calls, world, binding_id, ba, bb


def run_ms2016() -> dict:
    td, m, calls, world, binding_id, ba, bb = _setup_same_state_owned_prefix()
    try:
        live = m.derive_current_partial_operational_referent_ambiguity(
            binding_id, max_probe_steps=2, max_records=2048,
        )
        assert live["status"] == "CURRENT_PARTIAL_OPERATIONAL_REFERENT_AMBIGUITY", live
        assert live["unique_probe_action_id"] == "P2", live
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
            "MS2016-E-U", {"kind": "OWNED_RAW_REFERENT_AMBIGUITY", "binding_id": binding_id},
            EpistemicStatus.UNKNOWN_INCOMPLETE, source="MS2016",
        )
        deficit = m.record_action_limited_unknown(
            deficit_id="MS2016-D", question_key="raw-ref-" + discriminator[:16],
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
        surface = m.derive_current_owned_referent_decision_surface(
            deficit.deficit_id, max_probe_steps=2, max_records=2048,
        )
        assert surface["status"] == "CURRENT_OWNED_REFERENT_DECISION_SURFACE", surface
        source_digests = tuple(surface["source_relation_digests"])
        candidate = GeneratedEpistemicProgramCandidate(
            "MS2016-P2-CAND", ("P2",), source_digests, (("F", 0),),
            assistance_ancestry=("OWNED_REFERENT_DECISION_SURFACE", "UNIQUE_INFORMATIVE_P2"),
        )
        trial = begin_generated_epistemic_program_trial(
            candidate, deficit_id=deficit.deficit_id,
            discrimination_signature_sha256=discriminator,
            capabilities=m.capabilities, obligation=act_ob(),
            current_frame_epochs=dict(m.frames.epochs),
            start_state_id="s0", start_state_evidence_id=m.action_closure.current_state.evidence_id,
        )
        decision_context = EpistemicDecisionBearingContext(tuple(surface["relation_sets"]), ())
        options, _ = derive_current_grounded_feasibility_surface(
            capabilities=m.capabilities, operational_scope_id="S",
        )
        priority = derive_current_decision_bearing_commitment_from_grounded_surface(
            trial=trial, deficit=deficit, decision_context=decision_context,
            feasibility_options=options, capabilities=m.capabilities, values=m.values,
            current_frame_epochs=dict(m.frames.epochs),
            current_episode_epochs=dict(m.episodes.epochs),
            current_topology_epochs=dict(m.topologies.epochs),
            current_coordination_epochs=dict(m.coordinations.epochs),
        )
        trace_information = derive_current_program_discrimination_commitment(
            trial=trial, decision_context=decision_context,
            decision_bearing_commitment=priority,
        )
        owned_information = m._derive_current_epistemic_program_information_commitment(
            trial=trial, decision_context=decision_context,
            decision_bearing_commitment=priority,
        )
        nomination = m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(
            trial, decision_context, act_ob(),
        )
        p2_states = [next(r for r in rows if r.capability_id == "P2").next_state_id
                     for rows in decision_context.relation_sets]

        assert priority.licenses_yes(), priority.serializable()
        assert p2_states == ["s0", "s0"], p2_states
        assert not trace_information.licenses_yes(), trace_information.serializable()
        assert trace_information.reason == "PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE"
        assert owned_information.licenses_yes(), owned_information.serializable()
        assert owned_information.reason == "PROGRAM_CAN_CHANGE_OWNED_OBSERVABLE_CONTRAST"
        assert nomination["status"] == "ACTION_INTENT_NOMINATED", nomination
        assert nomination["intent"]["capability_id"] == "P2"
        assert calls == [], calls

        return {
            "status": "PASS",
            "published_trace_semantics_unchanged": "YES",
            "p2_control_state_predictions": p2_states,
            "trace_information": trace_information.serializable(),
            "owned_observable_information": owned_information.serializable(),
            "nomination_status": nomination["status"],
            "nominated_capability_id": nomination["intent"]["capability_id"],
            "handler_calls_at_nomination": list(calls),
            "new_representation_owner_required": "NO",
            "representation_owner": "EPISTEMIC_CONTRAST_ROW",
            "new_executor_required": "NO",
            "execution_authority": "NONE", "truth_authority": "NONE",
        }
    finally:
        _close(m)
        td.cleanup()


if __name__ == "__main__":
    print(json.dumps(run_ms2016(), indent=2, sort_keys=True, default=str))
