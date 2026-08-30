from __future__ import annotations
import hashlib, json, math
from typing import Iterable, Mapping

from ..runtime.commitment import RelationalCommitment, TernaryCommitment
from .epistemic import EpistemicContrastRow, EpistemicDeficitRecord, EpistemicDeficitState
from .recruitment import RecruitmentOption
from .rehearsal import CounterfactualRehearsalConfig, RehearsalTransitionRelation, propose_counterfactual_rehearsal
from .value import ValueVariableRegistry


def _sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def derive_regulatory_decision_bearing_commitment(
    *,
    deficit: EpistemicDeficitRecord | None,
    values: ValueVariableRegistry,
    relation_sets: Iterable[Mapping[tuple[str, str], RehearsalTransitionRelation]],
    options: Iterable[RecruitmentOption],
    start_state_id: str,
    current_capability_epochs: Mapping[str, int],
    current_frame_epochs: Mapping[str, int],
    current_episode_epochs: Mapping[str, int],
    current_topology_epochs: Mapping[str, int] | None = None,
    current_coordination_epochs: Mapping[str, int] | None = None,
    current_capability_signatures: Mapping[str, str] | None = None,
) -> RelationalCommitment:
    """Derive bounded normative priority from current regulatory decision divergence.

    This is not curiosity and not a scheduler.  It asks only whether the supplied
    live relational alternatives would choose different *currently executable*
    first actions under one current constitutional regulatory pressure.  The
    result grants no truth, semantic-goal, selection, or execution authority.
    """
    target = "epistemic-decision-bearing:" + ("NONE" if deficit is None else deficit.deficit_id)
    qnone = (("authority_gain", "NONE"), ("execution_authority", "NONE"), ("truth_authority", "NONE"), ("semantic_goal_authority", "NONE"))
    rows = tuple(dict(x) for x in relation_sets)
    bound_probe_premises: tuple[str, ...] = ()
    if deficit is None or deficit.state not in {EpistemicDeficitState.ACTION_LIMITED, EpistemicDeficitState.PROBE_AVAILABLE}:
        return RelationalCommitment(
            _sha({"target": target, "deficit": None if deficit is None else deficit.serializable()}),
            target, TernaryCommitment.UNKNOWN,
            reason="ACTION_LIMITED_OR_EXACT_BOUND_PROBE_AVAILABLE_REQUIRED", qualifiers=qnone,
            premise_ids=() if deficit is None else (deficit.deficit_id,),
        )
    if deficit.state == EpistemicDeficitState.PROBE_AVAILABLE:
        probe_id = deficit.probe_capability_id
        probe_epoch = deficit.probe_capability_epoch
        if not probe_id or probe_epoch is None:
            return RelationalCommitment(
                _sha({"target": target, "probe": probe_id, "epoch": probe_epoch}), target,
                TernaryCommitment.UNKNOWN, reason="EXACT_BOUND_PROBE_REQUIRED", qualifiers=qnone,
                premise_ids=(deficit.deficit_id,),
            )
        if current_capability_epochs.get(probe_id) != probe_epoch:
            return RelationalCommitment(
                _sha({"target": target, "probe": probe_id, "bound_epoch": probe_epoch, "current_epoch": current_capability_epochs.get(probe_id)}),
                target, TernaryCommitment.UNKNOWN, reason="BOUND_PROBE_CAPABILITY_EPOCH_NOT_CURRENT",
                qualifiers=qnone, premise_ids=(deficit.deficit_id, probe_id),
            )
        probe_slot = (str(start_state_id), str(probe_id))
        probe_edges = []
        for rs in rows:
            rel = rs.get(probe_slot)
            if rel is None or int(rel.capability_epoch) != int(probe_epoch):
                return RelationalCommitment(
                    _sha({"target": target, "probe_slot": probe_slot, "bound_epoch": probe_epoch}),
                    target, TernaryCommitment.UNKNOWN, reason="BOUND_PROBE_RELATION_REQUIRED_AT_CURRENT_STATE",
                    qualifiers=qnone, premise_ids=(deficit.deficit_id, probe_id),
                )
            probe_edges.append(rel.digest())
        bound_probe_premises = (str(probe_id),)
    value_anchors = [a for a in deficit.premise_anchors if a.kind == "VALUE"]
    if len(value_anchors) != 1:
        return RelationalCommitment(_sha({"target": target, "anchors": [a.serializable() for a in deficit.premise_anchors]}), target, TernaryCommitment.UNKNOWN, reason="EXACT_CURRENT_VALUE_ANCHOR_REQUIRED", qualifiers=qnone, premise_ids=(deficit.deficit_id,))
    anchor = value_anchors[0]
    if not values.is_current(anchor.object_id, anchor.epoch):
        return RelationalCommitment(_sha({"target": target, "value": anchor.serializable(), "current": False}), target, TernaryCommitment.UNKNOWN, reason="VALUE_PREMISE_NOT_CURRENT", qualifiers=qnone, premise_ids=(deficit.deficit_id, anchor.object_id))
    pressure = values.pressure(anchor.object_id)
    if pressure.get("status") != "CURRENT":
        return RelationalCommitment(_sha({"target": target, "pressure": pressure}), target, TernaryCommitment.UNKNOWN, reason="CURRENT_VALUE_OBSERVATION_REQUIRED", qualifiers=qnone, premise_ids=(deficit.deficit_id, anchor.object_id))
    if float(pressure.get("pressure_magnitude", 0.0)) <= 0.0:
        return RelationalCommitment(_sha({"target": target, "pressure": pressure}), target, TernaryCommitment.NO, reason="NO_CURRENT_REGULATORY_PRESSURE", qualifiers=qnone, premise_ids=(deficit.deficit_id, anchor.object_id))

    if len(rows) < 2:
        return RelationalCommitment(_sha({"target": target, "alternatives": len(rows)}), target, TernaryCommitment.UNKNOWN, reason="MULTIPLE_LIVE_RELATIONAL_ALTERNATIVES_REQUIRED", qualifiers=qnone, premise_ids=(deficit.deficit_id,))

    tcur = current_topology_epochs or {}
    ccur = current_coordination_epochs or {}
    sigcur = current_capability_signatures or {}
    for rs in rows:
        for rel in rs.values():
            if rel.value_epoch is not None and rel.value_epoch != (anchor.object_id, anchor.epoch):
                return RelationalCommitment(_sha({"target": target, "relation_value_epoch": rel.value_epoch, "required_value_epoch": (anchor.object_id, anchor.epoch)}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_VALUE_COORDINATE_MISMATCH:{rel.value_epoch[0]}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))
            if current_capability_epochs.get(rel.capability_id) != rel.capability_epoch:
                return RelationalCommitment(_sha({"target": target, "capability": rel.capability_id}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_CAPABILITY_EPOCH_DRIFT:{rel.capability_id}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))
            if current_frame_epochs.get(rel.frame_epoch[0]) != rel.frame_epoch[1]:
                return RelationalCommitment(_sha({"target": target, "frame": rel.frame_epoch}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_FRAME_EPOCH_DRIFT:{rel.frame_epoch[0]}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))
            if current_episode_epochs.get(rel.episode_schema_epoch[0]) != rel.episode_schema_epoch[1]:
                return RelationalCommitment(_sha({"target": target, "episode": rel.episode_schema_epoch}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_EPISODE_EPOCH_DRIFT:{rel.episode_schema_epoch[0]}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))
            if rel.topology_epoch is not None and tcur.get(rel.topology_epoch[0]) != rel.topology_epoch[1]:
                return RelationalCommitment(_sha({"target": target, "topology": rel.topology_epoch}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_TOPOLOGY_EPOCH_DRIFT:{rel.topology_epoch[0]}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))
            if rel.coordination_epoch is not None and ccur.get(rel.coordination_epoch[0]) != rel.coordination_epoch[1]:
                return RelationalCommitment(_sha({"target": target, "coordination": rel.coordination_epoch}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_COORDINATION_EPOCH_DRIFT:{rel.coordination_epoch[0]}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))
            for cid, epoch in rel.evidence_premise_epochs:
                if current_capability_epochs.get(cid) != epoch:
                    return RelationalCommitment(_sha({"target": target, "evidence_premise_epoch": (cid, epoch)}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_EVIDENCE_PREMISE_EPOCH_DRIFT:{cid}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))
            for cid, signature in rel.evidence_premise_signatures:
                if sigcur.get(cid) != signature:
                    return RelationalCommitment(_sha({"target": target, "evidence_premise_signature": (cid, signature)}), target, TernaryCommitment.UNKNOWN, reason=f"RELATIONAL_ALTERNATIVE_EVIDENCE_PREMISE_SIGNATURE_DRIFT:{cid}", qualifiers=qnone, premise_ids=(deficit.deficit_id,))

    contract = values.contracts[anchor.object_id]
    latest = values.latest.get(anchor.object_id)
    if latest is None or latest[0] != anchor.epoch:
        return RelationalCommitment(_sha({"target": target, "latest": latest}), target, TernaryCommitment.UNKNOWN, reason="CURRENT_VALUE_OBSERVATION_REQUIRED", qualifiers=qnone, premise_ids=(deficit.deficit_id, anchor.object_id))
    cfg = CounterfactualRehearsalConfig(max_horizon=1, max_nodes=64, min_support=1, min_consistency=0.99)
    opts = tuple(options)
    first_actions: list[str] = []
    proposal_digests: list[str] = []
    for rs in rows:
        p = propose_counterfactual_rehearsal(
            rs, start_state_id=str(start_state_id), start_value=float(latest[1]),
            viable_low=float(contract.viable_low), viable_high=float(contract.viable_high),
            value_epoch=(anchor.object_id, anchor.epoch), options=opts, cfg=cfg,
        )
        if p is None or not p.sequence:
            return RelationalCommitment(_sha({"target": target, "proposal": None}), target, TernaryCommitment.UNKNOWN, reason="HYPOTHESIS_CONDITIONED_EXECUTABLE_ACTION_UNRESOLVED", qualifiers=qnone, premise_ids=(deficit.deficit_id, anchor.object_id))
        first_actions.append(p.sequence[0]); proposal_digests.append(p.digest())
    stance = TernaryCommitment.YES if len(set(first_actions)) > 1 else TernaryCommitment.NO
    reason = "DISCRIMINATION_CAN_CHANGE_CURRENT_REGULATORY_ACTION" if stance == TernaryCommitment.YES else "DISCRIMINATION_CANNOT_CHANGE_CURRENT_EXECUTABLE_ACTION"
    cid = _sha({"target": target, "deficit": deficit.serializable(), "pressure": pressure, "first_actions": first_actions, "proposals": proposal_digests, "options": [o.serializable() for o in opts]})
    return RelationalCommitment(
        cid, target, stance, reason=reason,
        qualifiers=qnone + (("first_actions", "|".join(first_actions)), ("value_id", anchor.object_id), ("value_epoch", str(anchor.epoch))),
        premise_ids=(deficit.deficit_id, deficit.unknown_evidence_id, anchor.object_id, *bound_probe_premises),
    )


def derive_strict_same_value_cross_deficit_selection_commitment(
    opportunity_rows: Iterable[Mapping[str, object]],
) -> RelationalCommitment:
    """Derive one narrow cross-deficit selection from an exact shared regulatory coordinate.

    The rows are current, read-only consequence summaries produced by existing
    opportunity/rehearsal owners.  This function does not enumerate opportunities,
    persist deficits, rank different value variables, or execute anything.  It asks
    only whether one live opportunity has strictly lower *worst residual pressure*
    than every other live opportunity on the same exact value coordinate.
    """
    target="cross-deficit-epistemic-selection"
    qnone=(("authority_gain","NONE"),("selection_authority","NONE"),("execution_authority","NONE"),("truth_authority","NONE"),("semantic_goal_authority","NONE"))
    rows=tuple(dict(x) for x in opportunity_rows)
    base_premises=tuple(sorted({str(pid) for row in rows for pid in row.get("premise_ids",())}))
    if len(rows)<2:
        return RelationalCommitment(
            _sha({"target":target,"rows":rows}),target,TernaryCommitment.UNKNOWN,
            reason="MULTIPLE_CURRENT_CROSS_DEFICIT_OPPORTUNITIES_REQUIRED",qualifiers=qnone,
            premise_ids=base_premises,
        )
    required=("deficit_id","probe_action_id","value_id","value_epoch","current_value","worst_residual_pressure")
    if any(any(key not in row for key in required) for row in rows):
        return RelationalCommitment(
            _sha({"target":target,"rows":rows,"reason":"shape"}),target,TernaryCommitment.UNKNOWN,
            reason="CROSS_DEFICIT_REGULATORY_CONSEQUENCE_ROW_INCOMPLETE",qualifiers=qnone,
            premise_ids=base_premises,
        )
    deficits=tuple(str(row["deficit_id"]) for row in rows)
    probes=tuple(str(row["probe_action_id"]) for row in rows)
    if len(set(deficits))!=len(deficits):
        return RelationalCommitment(
            _sha({"target":target,"deficits":deficits}),target,TernaryCommitment.UNKNOWN,
            reason="DISTINCT_CURRENT_DEFICITS_REQUIRED",qualifiers=qnone,premise_ids=base_premises,
        )
    if len(set(probes))<2:
        return RelationalCommitment(
            _sha({"target":target,"probes":probes}),target,TernaryCommitment.UNKNOWN,
            reason="CROSS_DEFICIT_SELECTION_NOT_REQUIRED_FOR_SHARED_PROBE",qualifiers=qnone,
            premise_ids=base_premises,
        )
    coordinates=[]; scored=[]
    try:
        for row in rows:
            current_value=float(row["current_value"]); residual=float(row["worst_residual_pressure"])
            if not math.isfinite(current_value) or not math.isfinite(residual) or residual<0.0:
                raise ValueError("NONFINITE_OR_NEGATIVE")
            coordinates.append((str(row["value_id"]),int(row["value_epoch"]),current_value))
            scored.append((residual,str(row["probe_action_id"]),str(row["deficit_id"]),row))
    except (TypeError,ValueError,OverflowError):
        return RelationalCommitment(
            _sha({"target":target,"rows":rows,"reason":"numeric"}),target,TernaryCommitment.UNKNOWN,
            reason="FINITE_NONNEGATIVE_REGULATORY_CONSEQUENCE_REQUIRED",qualifiers=qnone,
            premise_ids=base_premises,
        )
    if len(set(coordinates))!=1:
        return RelationalCommitment(
            _sha({"target":target,"coordinates":coordinates}),target,TernaryCommitment.UNKNOWN,
            reason="EXACT_SAME_VALUE_COORDINATE_REQUIRED",qualifiers=qnone,premise_ids=base_premises,
        )
    ranked=tuple(sorted(scored,key=lambda x:(x[0],x[1],x[2])))
    best=ranked[0][0]; winners=tuple(x for x in ranked if x[0]==best)
    if len(winners)!=1:
        return RelationalCommitment(
            _sha({"target":target,"coordinate":coordinates[0],"scores":[(x[2],x[1],x[0]) for x in ranked]}),
            target,TernaryCommitment.UNKNOWN,reason="WORST_RESIDUAL_PRESSURE_TIE",qualifiers=qnone,
            premise_ids=base_premises,
        )
    next_score=ranked[1][0]
    if not best<next_score:
        return RelationalCommitment(
            _sha({"target":target,"coordinate":coordinates[0],"scores":[(x[2],x[1],x[0]) for x in ranked]}),
            target,TernaryCommitment.UNKNOWN,reason="NO_STRICT_SAME_VALUE_REGULATORY_DOMINANCE",qualifiers=qnone,
            premise_ids=base_premises,
        )
    winner=winners[0]; row=winner[3]
    premise_ids=tuple(sorted(set(base_premises+(str(row["deficit_id"]),))))
    cid=_sha({
        "target":target,"coordinate":coordinates[0],"selected_deficit_id":winner[2],
        "selected_probe_action_id":winner[1],"best":best,"next":next_score,
        "scores":[(x[2],x[1],x[0]) for x in ranked],"premises":premise_ids,
    })
    return RelationalCommitment(
        cid,target,TernaryCommitment.YES,
        reason="STRICT_SAME_VALUE_CROSS_DEFICIT_REGULATORY_DOMINANCE",
        qualifiers=(
            ("authority_gain","NONE"),
            ("selection_authority","STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY"),
            ("execution_authority","NONE"),("truth_authority","NONE"),("semantic_goal_authority","NONE"),
            ("selected_probe_action_id",winner[1]),("selected_deficit_id",winner[2]),
            ("comparison_basis","EXACT_SAME_VALUE_COORDINATE__STRICT_WORST_RESIDUAL_PRESSURE_ONLY"),
            ("dominant_worst_residual_pressure",str(best)),("next_worst_residual_pressure",str(next_score)),
        ),
        premise_ids=premise_ids,
    )


def derive_program_contrast_discrimination_commitment(
    *,
    trial,
    contrast_rows: Iterable[EpistemicContrastRow],
    decision_bearing_commitment: RelationalCommitment,
    source_premise_ids: Iterable[str] = (),
) -> RelationalCommitment:
    """Ask whether one bounded open program step partitions live alternatives by opaque outcomes.

    ``EpistemicContrastRow`` already owns candidate -> opaque predicted-outcome
    partitions without transition-model semantics.  This adapter therefore does not
    reinterpret outcome digests as states, truth, identity, or effects.  It only
    asks whether the exact current one-step program is associated with more than
    one opaque observable signature across the same bounded candidate set.

    Multi-step observable composition is intentionally not inferred here.
    """
    idx=len(trial.step_records)
    target=f"epistemic-program-information:{trial.trial_id}:step:{idx}"
    qnone=(("authority_gain","NONE"),("execution_authority","NONE"),("truth_authority","NONE"),("selection_authority","NONE"))
    premises=(trial.trial_id,decision_bearing_commitment.commitment_id,*tuple(str(x) for x in source_premise_ids))
    if not decision_bearing_commitment.licenses_yes():
        return RelationalCommitment(_sha({"target":target,"priority":decision_bearing_commitment.commitment_id,"kind":"contrast"}),target,TernaryCommitment.UNKNOWN,reason="CURRENT_DECISION_BEARING_PREMISE_REQUIRED",qualifiers=qnone,premise_ids=premises)
    if trial.status!="OPEN" or idx>=len(trial.steps):
        return RelationalCommitment(_sha({"target":target,"trial":trial.digest(),"kind":"contrast"}),target,TernaryCommitment.NO,reason="NO_OPEN_PROGRAM_REMAINDER",qualifiers=qnone,premise_ids=premises)
    remaining=tuple(trial.steps[idx:])
    if len(remaining)!=1:
        return RelationalCommitment(_sha({"target":target,"remaining":remaining,"kind":"contrast"}),target,TernaryCommitment.UNKNOWN,reason="OWNED_OBSERVABLE_CONTRAST_SINGLE_STEP_REQUIRED",qualifiers=qnone,premise_ids=premises)
    rows=tuple(contrast_rows)
    if not rows:
        return RelationalCommitment(_sha({"target":target,"rows":0,"kind":"contrast"}),target,TernaryCommitment.UNKNOWN,reason="OWNED_OBSERVABLE_CONTRAST_REQUIRED",qualifiers=qnone,premise_ids=premises)
    candidate_sets=[tuple(cid for cid,_ in row.candidate_outcome_digests) for row in rows]
    expected=candidate_sets[0]
    if len(expected)<2 or any(candidates!=expected for candidates in candidate_sets[1:]):
        return RelationalCommitment(_sha({"target":target,"candidate_sets":candidate_sets,"kind":"contrast"}),target,TernaryCommitment.UNKNOWN,reason="OWNED_OBSERVABLE_CONTRAST_CANDIDATE_SET_MISMATCH",qualifiers=qnone,premise_ids=premises)
    signatures=[]
    for candidate in expected:
        signatures.append(tuple(dict(row.candidate_outcome_digests)[candidate] for row in rows))
    partition_count=len(set(signatures))
    stance=TernaryCommitment.YES if partition_count>1 else TernaryCommitment.NO
    reason="PROGRAM_CAN_CHANGE_OWNED_OBSERVABLE_CONTRAST" if stance==TernaryCommitment.YES else "PROGRAM_CANNOT_CHANGE_OWNED_OBSERVABLE_CONTRAST"
    return RelationalCommitment(
        _sha({"target":target,"trial":trial.digest(),"rows":[row.serializable() for row in rows],"priority":decision_bearing_commitment.commitment_id,"source_premises":list(source_premise_ids)}),
        target,stance,reason=reason,
        qualifiers=qnone+(("observable_partition_count",str(partition_count)),("contrast_row_count",str(len(rows)))),
        premise_ids=premises,
    )


def derive_program_trace_discrimination_commitment(
    *,
    trial,
    relation_sets: Iterable[Mapping[tuple[str, str], RehearsalTransitionRelation]],
    decision_bearing_commitment: RelationalCommitment,
) -> RelationalCommitment:
    """Ask whether the remaining embodied program can change observable evidence.

    The relation alternatives are representation-only inputs.  This adapter does
    not select, schedule, execute, or qualify anything.  It only compares the
    *observable opaque state traces* predicted by the already-represented
    remaining program under the same live alternatives whose currentness was
    established by ``decision_bearing_commitment``.
    """
    idx=len(trial.step_records)
    target=f"epistemic-program-information:{trial.trial_id}:step:{idx}"
    qnone=(("authority_gain","NONE"),("execution_authority","NONE"),("truth_authority","NONE"),("selection_authority","NONE"))
    if not decision_bearing_commitment.licenses_yes():
        return RelationalCommitment(_sha({"target":target,"priority":decision_bearing_commitment.commitment_id}),target,TernaryCommitment.UNKNOWN,reason="CURRENT_DECISION_BEARING_PREMISE_REQUIRED",qualifiers=qnone,premise_ids=(decision_bearing_commitment.commitment_id,))
    if trial.status!="OPEN" or idx>=len(trial.steps):
        return RelationalCommitment(_sha({"target":target,"trial":trial.digest()}),target,TernaryCommitment.NO,reason="NO_OPEN_PROGRAM_REMAINDER",qualifiers=qnone,premise_ids=(trial.trial_id,decision_bearing_commitment.commitment_id))
    state=trial.start_state_id if idx==0 else trial.step_records[-1].actual_next_state_id
    remaining=trial.steps[idx:]
    rows=tuple(dict(x) for x in relation_sets)
    if len(rows)<2:
        return RelationalCommitment(_sha({"target":target,"alternatives":len(rows)}),target,TernaryCommitment.UNKNOWN,reason="MULTIPLE_LIVE_RELATIONAL_ALTERNATIVES_REQUIRED",qualifiers=qnone,premise_ids=(trial.trial_id,decision_bearing_commitment.commitment_id))
    traces=[]
    for rs in rows:
        cur=state; trace=[]
        for action in remaining:
            rel=rs.get((cur,action))
            if rel is None:
                return RelationalCommitment(_sha({"target":target,"missing":[cur,action]}),target,TernaryCommitment.UNKNOWN,reason=f"PROGRAM_OBSERVABLE_TRACE_UNRESOLVED:{cur}:{action}",qualifiers=qnone,premise_ids=(trial.trial_id,decision_bearing_commitment.commitment_id))
            cur=rel.next_state_id; trace.append(cur)
        traces.append(tuple(trace))
    stance=TernaryCommitment.YES if len(set(traces))>1 else TernaryCommitment.NO
    reason="PROGRAM_CAN_CHANGE_OBSERVABLE_EVIDENCE" if stance==TernaryCommitment.YES else "PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE"
    return RelationalCommitment(
        _sha({"target":target,"trial":trial.digest(),"traces":traces,"priority":decision_bearing_commitment.commitment_id}),target,stance,reason=reason,
        qualifiers=qnone+(("predicted_trace_count",str(len(set(traces)))),),
        premise_ids=(trial.trial_id,decision_bearing_commitment.commitment_id),
    )
