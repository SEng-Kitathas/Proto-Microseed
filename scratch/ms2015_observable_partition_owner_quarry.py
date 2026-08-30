from __future__ import annotations

import json
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus, Microseed,
    Observation, OperationalFrameContract, QualificationState, ValueVariableContract,
)
from microseed.development.action_learning import projection_conditioned_hypothesis_surface_digest
from microseed.development.epistemic import (
    EpistemicContrastRow, EpistemicCurrentnessAnchor, derive_pre_evidence_discriminator_signature,
)
from microseed.development.epistemic_action import (
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
    ACTS, _relation, _qualify, derive_owned_referent_decision_context, act_ob,
)


def _setup_same_state_probe():
    td = tempfile.TemporaryDirectory(prefix="ms2015-observable-partition-")
    m = Microseed(Path(td.name))
    calls: list[str] = []

    m.register_operational_frame(OperationalFrameContract(
        "F", "opaque", "f" * 64, Authority.DERIVED_READ_ONLY, ("MS2015",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    m.register_value_variable(ValueVariableContract(
        "V", "reg", 0, 10, "v" * 64, Authority.REFERENCE_ONLY, ("MS2015",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    m.observe_value_state("V", -1.0)
    m.register_episode_schema(EpisodeSchemaContract(
        "EP", "opaque-episode", "e" * 64, Authority.DERIVED_READ_ONLY, ("MS2015",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        frame_epochs=(("F", 0),), value_epochs=(("V", 0),),
    ))

    for cid in ACTS:
        m.register_capability(CapabilityContract(
            cid, "opaque", {}, {}, (), (), Authority.EFFECT, ("MS2015",), "CURRENT", {},
            query_obligation_id="MS2008-ACT", qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _cid=cid, **_: calls.append(_cid) or {"receipt": _cid},
            operational_scope_id="S",
        ))
        m.register_capability(CapabilityContract(
            "FEAS-" + cid, "feas", {"target_capability_id": cid}, {}, (), (),
            Authority.DERIVED_READ_ONLY, ("MS2015",), "CURRENT", {}, dependencies=(cid,),
            query_obligation_id="MS2008-FEAS-" + cid,
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {"feasibility": "FEASIBLE", "reason": "CURRENT"},
            operational_scope_id="S",
        ))

    ca = _persist_context(m, "MS2015-A", UNIQUE_A)
    cb = _persist_context(m, "MS2015-B", UNIQUE_B)
    ba = str(ca["projection_bucket_id"])
    bb = str(cb["projection_bucket_id"])
    projection = m.register_epistemic_projection(
        "MS2015-REFSET", m.operational_referent_class_set_projection_signature_sha256(),
        assistance_ancestry=("SUPPLIED_OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_COORDINATE", "NO_SEMANTIC_REFERENT_AUTHORITY"),
    )

    # Regulatory consequences differ, but P2's control-state transition is identical.
    rels_a = {
        "A": _relation(m, "MS2015-A-A", "A", "a-next", 2.0, "15AA"),
        "B": _relation(m, "MS2015-A-B", "B", "b-next", 0.0, "15AB"),
        "P2": _relation(m, "MS2015-A-P2", "P2", "s0", 0.0, "15AP"),
    }
    rels_b = {
        "A": _relation(m, "MS2015-B-A", "A", "a-next-b", 0.0, "15BA"),
        "B": _relation(m, "MS2015-B-B", "B", "b-next-b", 2.0, "15BB"),
        "P2": _relation(m, "MS2015-B-P2", "P2", "s0", 0.0, "15BP"),
    }
    binding_id = _qualify(m, projection, ba, bb, rels_a, rels_b)
    m.observe_opaque_control_state(
        Observation("MS2015-CS", "EXT", "opaque-control", "s0", authority=Authority.OBSERVATION_ONLY),
        evidence_id="MS2015-E-CS",
    )
    return td, m, calls, binding_id, ba, bb


def run_ms2015() -> dict:
    td, m, calls, binding_id, ba, bb = _setup_same_state_probe()
    try:
        owned = derive_owned_referent_decision_context(m, binding_id, UNIQUE_A[:3], ("P0", "P1"))
        live = owned["live"]
        raw_probe = live["probe_surface"]
        assert raw_probe["status"] == "CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE", raw_probe
        assert raw_probe["probe_action_id"] == "P2", raw_probe
        raw_candidate = raw_probe["informative_candidates"][0]

        binding = m.action_outcome_learning.projection_conditioned_bindings[binding_id]
        hypothesis = projection_conditioned_hypothesis_surface_digest(binding, m.action_outcome_learning.relations)
        legacy_disc = action_result_digest({
            "hypothesis": hypothesis,
            "survivors": list(live["surviving_bucket_ids"]),
            "probe": "P2",
            "partition": raw_candidate["predicted_response_partition"],
        })
        ue = m.append_evidence(
            "MS2015-E-U", {"kind": "RAW_REFERENT_AMBIGUITY"}, EpistemicStatus.UNKNOWN_INCOMPLETE,
            source="MS2015-HOSTILE",
        )
        deficit = m.record_action_limited_unknown(
            deficit_id="MS2015-D", question_key="raw-ref",
            hypothesis_digest_sha256=hypothesis, unknown_evidence_id=ue.evidence_id,
            missing_discriminator_signature_sha256=legacy_disc,
            premise_anchors=(
                EpistemicCurrentnessAnchor("VALUE", "V", 0),
                EpistemicCurrentnessAnchor("PROJECTION", binding.projection_id, binding.projection_epoch),
            ),
            assistance_ancestry=(
                "DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY",
                "QUALIFIED_ROUTING_SURFACE", "NO_CALLER_ALTERNATIVE_SET",
            ),
        )
        p2_digests = [next(r for r in rows if r.capability_id == "P2").digest()
                      for rows in owned["decision_context"].relation_sets]
        candidate = GeneratedEpistemicProgramCandidate(
            "MS2015-P2", ("P2",), tuple(sorted(set(p2_digests))), (("F", 0),),
            assistance_ancestry=("OWNED_REFERENT_DECISION_SURFACE", "UNIQUE_INFORMATIVE_P2"),
        )
        trial = begin_generated_epistemic_program_trial(
            candidate, deficit_id=deficit.deficit_id,
            discrimination_signature_sha256=legacy_disc,
            capabilities=m.capabilities, obligation=act_ob(),
            current_frame_epochs=dict(m.frames.epochs),
            start_state_id="s0", start_state_evidence_id="MS2015-E-CS",
        )
        options, _ = derive_current_grounded_feasibility_surface(
            capabilities=m.capabilities, operational_scope_id="S",
        )
        priority = derive_current_decision_bearing_commitment_from_grounded_surface(
            trial=trial, deficit=deficit, decision_context=owned["decision_context"],
            feasibility_options=options, capabilities=m.capabilities, values=m.values,
            current_frame_epochs=dict(m.frames.epochs),
            current_episode_epochs=dict(m.episodes.epochs),
            current_topology_epochs=dict(m.topologies.epochs),
            current_coordination_epochs=dict(m.coordinations.epochs),
        )
        trace_information = derive_current_program_discrimination_commitment(
            trial=trial, decision_context=owned["decision_context"],
            decision_bearing_commitment=priority,
        )

        outcome_rows = tuple(
            (str(bucket), action_result_digest({"opaque_raw_response_multiset": response}))
            for bucket, response in raw_candidate["predicted_response_partition"]
        )
        condition = action_result_digest({
            "task_id": binding.task_id, "action_id": "P2",
            "channel_ids": list(binding.channel_ids), "horizon": int(binding.horizon),
            "observable_kind": "OPAQUE_RAW_RESPONSE_MULTISET",
        })
        row = EpistemicContrastRow(
            binding.projection_id, binding.projection_epoch, outcome_rows,
            condition_signature_sha256=condition,
        )
        projection = m.epistemic_projections.records[binding.projection_id]
        contrast_signature = derive_pre_evidence_discriminator_signature(
            hypothesis_digest_sha256=hypothesis, rows=(row,),
            projection_content_signatures={binding.projection_id: projection.signature_sha256},
        )
        changed_rows = list(row.candidate_outcome_digests)
        changed_rows[0] = (changed_rows[0][0], "f" * 64)
        changed = EpistemicContrastRow(
            row.projection_id, row.projection_epoch, tuple(changed_rows),
            condition_signature_sha256=row.condition_signature_sha256,
        )
        changed_signature = derive_pre_evidence_discriminator_signature(
            hypothesis_digest_sha256=hypothesis, rows=(changed,),
            projection_content_signatures={binding.projection_id: projection.signature_sha256},
        )
        payload = row.serializable()
        forbidden = tuple(x for x in ("state_id", "capability_id", "next_state_id", "value_effect", "relation_set") if x in payload)

        p2_states = [next(r for r in rows if r.capability_id == "P2").next_state_id
                     for rows in owned["decision_context"].relation_sets]
        assert priority.licenses_yes(), priority.serializable()
        assert not trace_information.licenses_yes() and trace_information.reason == "PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE"
        assert p2_states == ["s0", "s0"], p2_states
        assert len({digest for _, digest in row.candidate_outcome_digests}) == 2
        assert not forbidden
        assert contrast_signature != changed_signature
        assert calls == []

        return {
            "status": "PASS",
            "priority": priority.serializable(),
            "trace_information": trace_information.serializable(),
            "p2_control_state_predictions": p2_states,
            "raw_probe_action_id": raw_probe["probe_action_id"],
            "raw_contrast_row": row.serializable(),
            "raw_contrast_signature_sha256": contrast_signature,
            "changed_raw_contrast_signature_sha256": changed_signature,
            "contrast_signature_content_sensitive": contrast_signature != changed_signature,
            "transition_model_fields_in_contrast_row": list(forbidden),
            "existing_owner_sufficient": "YES__EPISTEMIC_CONTRAST_ROW",
            "missing_surface": "PROGRAM_INFORMATION_WIRING_TO_OWNED_OBSERVABLE_CONTRAST",
            "execution_authority": "NONE", "truth_authority": "NONE",
            "semantic_reference_authority": "NONE", "handler_calls": list(calls),
        }
    finally:
        _close(m)
        td.cleanup()


if __name__ == "__main__":
    print(json.dumps(run_ms2015(), indent=2, sort_keys=True))
