from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Authority, CapabilityContract, EpistemicStatus, QualificationState
from microseed.development.action_learning import (
    ExternalProjectionConditionedRelationQualifier,
    projection_conditioned_hypothesis_surface_digest,
)
from microseed.development.epistemic import EpistemicContrastRow, EpistemicCurrentnessAnchor, EpistemicDeficitRecord
from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext,
    derive_current_decision_bearing_commitment_from_grounded_surface,
    derive_current_grounded_feasibility_surface,
    derive_current_program_discrimination_commitment,
    derive_epistemic_program_step_commitment,
)
from microseed.development.epistemic_priority import derive_program_contrast_discrimination_commitment
from microseed.development.epistemic_program import GeneratedEpistemicProgramCandidate, begin_generated_epistemic_program_trial
from microseed.runtime.entity import action_result_digest
from scratch.ms2005_bounded_referent_probe_reconstruction import ACTIONS, _persist_context, _samples_from_boundaries
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _relation, act_ob
from scratch.ms2016_owned_observable_contrast_program_information import _setup_same_state_owned_prefix

P4_D = _samples_from_boundaries(((1,), (1,), (2, 5), (2, 5)), len(ACTIONS))


def _holdouts(m, projection, task, bucket, rels, tag):
    refs = []
    for action, rel in rels.items():
        for i in range(12):
            refs.append(m.append_evidence(
                f"MS2021-H-{tag}-{action}-{i}",
                {
                    "kind": "PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT",
                    "projection_id": projection.projection_id,
                    "projection_epoch": projection.epoch,
                    "projection_signature_sha256": projection.signature_sha256,
                    "task_id": task, "horizon": 1, "action_id": action,
                    "channel_id": "opaque-control", "projection_bucket_id": bucket,
                    "actual_next_state_id": rel.next_state_id,
                    "actual_value_effect": rel.value_effect,
                },
                EpistemicStatus.PRESSURE_SUPPORTED, source="MS2021-HOLDOUT",
            ))
    return refs


def _second_same_state_binding(m, projection, bucket_a, bucket_d):
    for cid in ("C", "D", "P4"):
        m.register_capability(CapabilityContract(
            cid, "opaque", {}, {}, (), (), Authority.EFFECT, ("MS2021",), "CURRENT", {},
            query_obligation_id="MS2008-ACT", qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _cid=cid, **_: {"receipt": _cid}, operational_scope_id="S",
        ))
        m.register_capability(CapabilityContract(
            "FEAS-" + cid, "feas", {"target_capability_id": cid}, {}, (), (),
            Authority.DERIVED_READ_ONLY, ("MS2021",), "CURRENT", {}, dependencies=(cid,),
            query_obligation_id="MS2008-FEAS-" + cid,
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {"feasibility": "FEASIBLE", "reason": "CURRENT"},
            operational_scope_id="S",
        ))
    # P4 is raw-informative but control-state non-discriminative.
    rel_a = {
        "C": _relation(m, "MS2021-A-C", "C", "c-next", 2.0, "21AC"),
        "D": _relation(m, "MS2021-A-D", "D", "d-next", 0.0, "21AD"),
        "P4": _relation(m, "MS2021-A-P4", "P4", "s0", 0.0, "21AP"),
    }
    rel_d = {
        "C": _relation(m, "MS2021-D-C", "C", "c-next-d", 0.0, "21DC"),
        "D": _relation(m, "MS2021-D-D", "D", "d-next-d", 2.0, "21DD"),
        "P4": _relation(m, "MS2021-D-P4", "P4", "s0", 0.0, "21DP"),
    }
    proposal_evidence = m.append_evidence(
        "MS2021-ROUTE2-PROP", {"kind": "ROUTING_PROPOSAL", "basis": "SECOND_RAW_REFERENT_PRESSURE"},
        EpistemicStatus.PRESSURE_SUPPORTED, source="MS2021",
    )
    route = m.nominate_projection_conditioned_relation_routing(
        projection_id=projection.projection_id, task_id="MS2021-DECISION-2",
        action_ids=("C", "D", "P4"), channel_ids=("opaque-control",), horizon=1,
        default_action_relations=tuple((a, rel_a[a].relation_id) for a in ("C", "D", "P4")),
        bucket_action_overrides=tuple((bucket_d, a, rel_d[a].relation_id) for a in ("C", "D", "P4")),
        source_evidence_ids=(proposal_evidence.evidence_id,),
    )
    refs = _holdouts(m, projection, "MS2021-DECISION-2", bucket_a, rel_a, "A")
    refs += _holdouts(m, projection, "MS2021-DECISION-2", bucket_d, rel_d, "D")
    ticket = ExternalProjectionConditionedRelationQualifier(m.evidence, qualifier_id="EXTERNAL-MS2021-ROUTE2").qualify(
        route, qualification_evidence=tuple(refs), relations=m.action_outcome_learning.relations,
        min_support=12, min_accuracy=.95,
    )
    admitted = m.qualify_projection_conditioned_relation_routing(ticket)
    assert admitted["status"] == "CURRENT_PROJECTION_CONDITIONED_ROUTING", admitted
    return str(admitted["binding"]["binding_id"])


def _opportunity(m, binding):
    live = m.derive_current_partial_operational_referent_ambiguity(
        binding.binding_id, max_probe_steps=2, max_records=4096,
    )
    if live.get("status") != "CURRENT_PARTIAL_OPERATIONAL_REFERENT_AMBIGUITY":
        return None
    if live.get("informative_probe_status") != "CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE":
        return None
    probe = str(live["unique_probe_action_id"])
    hypothesis = projection_conditioned_hypothesis_surface_digest(binding, m.action_outcome_learning.relations)
    raw_candidate = next(x for x in live["informative_candidates"] if x["action_id"] == probe)
    discriminator = action_result_digest({
        "hypothesis": hypothesis, "survivors": list(live["surviving_bucket_ids"]),
        "probe": probe, "partition": raw_candidate["predicted_response_partition"],
    })
    relation_sets = []
    probe_digests = []
    frame_epochs = set()
    value_epochs = set()
    for bucket in live["surviving_bucket_ids"]:
        rows = []
        for action in binding.action_ids:
            rid = binding.relation_id_for(str(bucket), str(action))
            relation = m.action_outcome_learning.relations.get(str(rid)) if rid else None
            if relation is None or not m._action_outcome_relation_current(relation):
                return None
            edge = relation.as_epistemic_alternative_relation()
            if edge is None:
                return None
            rows.append(edge)
            frame_epochs.add(tuple(edge.frame_epoch))
            if edge.value_epoch is not None:
                value_epochs.add(tuple(edge.value_epoch))
            if str(action) == probe:
                probe_digests.append(edge.digest())
        relation_sets.append(tuple(rows))
    if len(value_epochs) != 1:
        return None
    value_id, value_epoch = next(iter(value_epochs))
    raw_ids = tuple(live["probe_prefix"]["raw_observation_evidence_ids"])
    deficit = EpistemicDeficitRecord(
        deficit_id="MS2021-OP-" + action_result_digest({"binding": binding.binding_id, "probe": probe})[:20],
        question_key="raw-referent-" + discriminator[:20],
        hypothesis_digest_sha256=hypothesis,
        unknown_evidence_id=raw_ids[-1],
        missing_discriminator_signature_sha256=discriminator,
        premise_anchors=(
            EpistemicCurrentnessAnchor("VALUE", value_id, value_epoch),
            EpistemicCurrentnessAnchor("PROJECTION", binding.projection_id, binding.projection_epoch),
        ),
        assistance_ancestry=(
            "DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY",
            "QUALIFIED_ROUTING_SURFACE", "NO_CALLER_BINDING_OR_DEFICIT",
        ),
    )
    candidate = GeneratedEpistemicProgramCandidate(
        "MS2021-PROGRAM-" + probe, (probe,), tuple(sorted(set(probe_digests))), tuple(sorted(frame_epochs)),
        assistance_ancestry=("OWNED_REFERENT_DECISION_SURFACE", "UNIQUE_INFORMATIVE_PROBE"),
    )
    trial = begin_generated_epistemic_program_trial(
        candidate, deficit_id=deficit.deficit_id,
        discrimination_signature_sha256=discriminator,
        capabilities=m.capabilities, obligation=act_ob(),
        current_frame_epochs=dict(m.frames.epochs),
        start_state_id=m.action_closure.current_state.state_id,
        start_state_evidence_id=m.action_closure.current_state.evidence_id,
    )
    dc = EpistemicDecisionBearingContext(tuple(relation_sets), ())
    options, _ = derive_current_grounded_feasibility_surface(capabilities=m.capabilities, operational_scope_id="S")
    option = next((x for x in options if x.capability_id == probe), None)
    if option is None:
        return None
    priority = derive_current_decision_bearing_commitment_from_grounded_surface(
        trial=trial, deficit=deficit, decision_context=dc,
        feasibility_options=options, capabilities=m.capabilities, values=m.values,
        current_frame_epochs=dict(m.frames.epochs), current_episode_epochs=dict(m.episodes.epochs),
        current_topology_epochs=dict(m.topologies.epochs), current_coordination_epochs=dict(m.coordinations.epochs),
    )
    if not priority.licenses_yes():
        return None
    trace_information = derive_current_program_discrimination_commitment(
        trial=trial, decision_context=dc, decision_bearing_commitment=priority,
    )
    outcomes = tuple(
        (str(bucket), action_result_digest({"opaque_raw_response_multiset": response}))
        for bucket, response in raw_candidate["predicted_response_partition"]
    )
    condition = action_result_digest({
        "task_id": binding.task_id, "action_id": probe,
        "channel_ids": list(binding.channel_ids), "horizon": int(binding.horizon),
        "observable_kind": "OPAQUE_RAW_RESPONSE_MULTISET",
    })
    contrast = EpistemicContrastRow(
        binding.projection_id, binding.projection_epoch, outcomes,
        condition_signature_sha256=condition,
    )
    contrast_information = derive_program_contrast_discrimination_commitment(
        trial=trial, contrast_rows=(contrast,), decision_bearing_commitment=priority,
        source_premise_ids=(binding.binding_id, *raw_ids, *tuple(sorted(set(probe_digests)))),
    )
    if not contrast_information.licenses_yes():
        return None
    commitment = derive_epistemic_program_step_commitment(
        trial=trial, deficit=deficit, feasibility=option,
        capabilities=m.capabilities, obligation=act_ob(),
        current_frame_epochs=dict(m.frames.epochs), current_state=m.action_closure.current_state,
        priority_commitment=priority, information_commitment=contrast_information,
    )
    if not commitment.licenses_yes():
        return None
    probe_states = tuple(next(r for r in rows if r.capability_id == probe).next_state_id for rows in dc.relation_sets)
    return {
        "binding_id": binding.binding_id,
        "probe_action_id": probe,
        "deficit": deficit, "trial": trial, "decision_context": dc,
        "priority": priority, "trace_information": trace_information,
        "contrast_information": contrast_information, "commitment": commitment,
        "probe_control_state_predictions": probe_states,
        "selection_authority": "NONE", "execution_authority": "NONE",
    }


def enumerate_opportunities(m):
    coordinate = m.operational_referent_class_set_projection_signature_sha256()
    rows = []
    for binding in sorted(m.action_outcome_learning.projection_conditioned_bindings.values(), key=lambda b: b.binding_id):
        projection = m.epistemic_projections.records.get(binding.projection_id)
        if projection is None or projection.signature_sha256 != coordinate or not m._projection_conditioned_binding_current(binding):
            continue
        op = _opportunity(m, binding)
        if op is not None:
            rows.append(op)
    probes = tuple(sorted(set(x["probe_action_id"] for x in rows)))
    if not rows:
        return {"status": "NO_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY", "opportunities": (), "selection_authority": "NONE"}
    if len(rows) == 1:
        return {"status": "CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY", "opportunities": tuple(rows), "probe_action_ids": probes, "selection_authority": "CONTENT_UNIQUENESS_ONLY"}
    if len(probes) == 1:
        return {"status": "MULTIPLE_REFERENT_PRESSURES_SHARED_PROBE", "opportunities": tuple(rows), "probe_action_ids": probes, "selection_authority": "SHARED_ACTION_COMPOSITION_ONLY"}
    return {
        "status": "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES",
        "reason": "NO_CROSS_DEFICIT_SELECTION_AUTHORITY",
        "opportunities": tuple(rows), "probe_action_ids": probes,
        "selection_authority": "NONE", "execution_authority": "NONE",
    }


def run_ms2021():
    td, m, calls, world, binding1, bucket_a, bucket_b = _setup_same_state_owned_prefix()
    try:
        first = enumerate_opportunities(m)
        assert first["status"] == "CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY", first
        assert first["probe_action_ids"] == ("P2",), first
        op1 = first["opportunities"][0]
        assert op1["probe_control_state_predictions"] == ("s0", "s0"), op1
        assert not op1["trace_information"].licenses_yes(), op1["trace_information"].serializable()
        assert op1["contrast_information"].licenses_yes(), op1["contrast_information"].serializable()

        bucket_d = str(_persist_context(m, "MS2021-D", P4_D)["projection_bucket_id"])
        projection = m.epistemic_projections.records[m.action_outcome_learning.projection_conditioned_bindings[binding1].projection_id]
        binding2 = _second_same_state_binding(m, projection, bucket_a, bucket_d)
        multiple = enumerate_opportunities(m)
        assert multiple["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", multiple
        assert multiple["reason"] == "NO_CROSS_DEFICIT_SELECTION_AUTHORITY", multiple
        assert set(multiple["probe_action_ids"]) == {"P2", "P4"}, multiple
        assert calls == [], calls
        summaries = []
        for op in multiple["opportunities"]:
            assert len(set(op["probe_control_state_predictions"])) == 1, op
            assert not op["trace_information"].licenses_yes(), op["trace_information"].serializable()
            assert op["contrast_information"].licenses_yes(), op["contrast_information"].serializable()
            assert op["commitment"].licenses_yes(), op["commitment"].serializable()
            summaries.append({
                "binding_id": op["binding_id"], "probe_action_id": op["probe_action_id"],
                "probe_control_state_predictions": list(op["probe_control_state_predictions"]),
                "trace_information": op["trace_information"].serializable(),
                "contrast_information": op["contrast_information"].serializable(),
                "step_commitment": op["commitment"].serializable(),
            })
        return {
            "status": "BLOCKED_AS_DESIGNED",
            "unique_before_second_pressure": first["status"],
            "multiple_status": multiple["status"],
            "reason": multiple["reason"],
            "probe_action_ids": list(multiple["probe_action_ids"]),
            "opportunities": summaries,
            "selection_authority": multiple["selection_authority"],
            "execution_authority": multiple["execution_authority"],
            "handler_calls": list(calls),
            "trace_leakage_required": "NO",
            "existing_selection_owner": "NONE_FOUND",
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


if __name__ == "__main__":
    print(json.dumps(run_ms2021(), indent=2, sort_keys=True, default=str))
