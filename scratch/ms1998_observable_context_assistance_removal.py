from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from microseed import (
    EpistemicStatus,
    ExternalProjectionQualifier,
    Microseed,
    ProjectionDiscoveryConfig,
    RehearsalTransitionObservation,
)
from microseed.development.action_learning import (
    ActionOutcomePredictiveCandidate,
    ExternalActionOutcomeRelationQualifier,
    ExternalProjectionConditionedRelationQualifier,
)
from microseed.development.predictive_adaptation import PredictiveCurrentnessConfig
from microseed.development.rehearsal import CounterfactualRehearsalConfig
from research.substrate_shadow.environment_adapter import AdapterConfig, ShadowEnvironmentAdapter
from scratch.ms1997_lived_history_to_endogenous_program import LivedThreeLocusWorld, MAIN
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


class ObservableContextWorld(LivedThreeLocusWorld):
    """MS1997 world plus a bounded organism-visible raw context channel.

    The first raw coordinate is a coarse opaque encoding of the *currently observed
    regulatory sign* rather than the hidden evaluator mode.  It remains stable while
    the regulatory value stays on one side of zero.  The second coordinate is a
    constant nuisance coordinate so projection search still has to reject a useless
    coordinate rather than receiving a one-coordinate handoff by construction.
    """

    name = "MS1998-OBSERVABLE-CONTEXT-WORLD"
    compatibility_sha256 = hashlib.sha256(
        b"MS1998-OBSERVABLE-CONTEXT-WORLD:v1:visible-regulatory-sign-plus-nuisance"
    ).hexdigest()

    def observe(self) -> dict:
        row = super().observe()
        row["raw_tokens"] = ["0" if float(row["observed_value"]) < 0.0 else "1", "x"]
        return row


def observable_only_rows(
    ms: Microseed,
    adapter: ShadowEnvironmentAdapter,
    *,
    tag: str,
) -> tuple[RehearsalTransitionObservation, ...]:
    """Externally equipped one-step guidance using organism-visible state/value only.

    This function deliberately receives no world object and no evaluator mode.  The
    sign of the predicted regulatory effect comes only from the current Microseed
    value observation.  Terminal identity remains unknown to the assistance layer.
    """

    current = ms.action_closure.current_state
    assert current is not None
    value_id = adapter.config.value_id
    latest = ms.values.latest.get(value_id)
    assert latest is not None
    observed_value = float(latest[1])

    if observed_value < float(adapter.config.viable_low):
        effect = 1.0
    elif observed_value > float(adapter.config.viable_high):
        effect = -1.0
    else:
        return ()

    specs = {
        "s0": (MAIN[0], "s1"),
        "s1": (MAIN[1], "s2"),
        # No u/v terminal label is supplied.  The real outcome is allowed to falsify
        # this neutral prediction while preserving the observed effect for learning.
        "s2": (MAIN[2], "terminal-opaque-unpredicted"),
    }
    if current.state_id not in specs:
        return ()
    action, next_state = specs[current.state_id]
    c = adapter.config
    return tuple(
        RehearsalTransitionObservation(
            f"ASSIST-MS1998-{tag}-{current.state_id}-{i}",
            current.state_id,
            action,
            next_state,
            effect,
            0,
            c.frame_id,
            0,
            c.episode_id,
            0,
        )
        for i in range(8)
    )


def _raw_before_action(ms: Microseed, adapter: ShadowEnvironmentAdapter, *, tag: str) -> dict:
    c = adapter.config
    raw = ms.record_bounded_raw_observation_coordinates(
        c.observation_capability_id,
        adapter.obs_obligation(),
        evidence_id=f"E-MS1998-RAW-{tag}",
        capture_id=f"CAP-MS1998-RAW-{tag}",
        max_coordinates=4,
    )
    assert raw["status"] == "BOUNDED_RAW_OBSERVATION_RECORDED", raw
    assert tuple(raw["raw_tokens"])[1] == "x"
    return raw


def run_assisted_episode(
    ms: Microseed,
    adapter: ShadowEnvironmentAdapter,
    world: ObservableContextWorld,
    *,
    evaluator_mode: str,
    index: int,
    phase: str,
) -> list[dict[str, object]]:
    """Run one real episode; evaluator mode configures reality but never guidance."""

    world.configure_mode(evaluator_mode)
    world.reset()
    adapter.observe_control(ms, f"{phase}-{index}-START")
    options = tuple(adapter.option(aid) for aid in MAIN)
    logs: list[dict[str, object]] = []

    for step in range(3):
        current = ms.action_closure.current_state
        assert current is not None
        before_state = current.state_id
        before_evidence = current.evidence_id
        value_before = float(ms.values.latest[adapter.config.value_id][1])
        raw = _raw_before_action(ms, adapter, tag=f"{phase}-{index}-{step}")
        rows = observable_only_rows(ms, adapter, tag=f"{phase}-{index}-{step}")
        assert rows, (phase, index, step, before_state, value_before)
        # All current opaque options are present.  No preferred action is passed.
        proposal = ms.nominate_counterfactual_rehearsal(
            rows,
            options,
            start_state_id=before_state,
            value_id=adapter.config.value_id,
            config=CounterfactualRehearsalConfig(max_horizon=1, max_nodes=16),
        )
        assert proposal is not None, (phase, index, step, before_state, value_before)
        assert len(proposal.sequence) == 1
        intent = ms.nominate_bounded_action_intent(proposal.proposal_id, adapter.act_obligation())
        assert intent["status"] == "ACTION_INTENT_NOMINATED", intent
        selected = intent["intent"]["capability_id"]
        # Evaluator oracle checks the result only after organism-side selection.
        assert selected == MAIN[step], (phase, index, step, selected)
        assert intent["intent"]["control_state_evidence_id"] == before_evidence
        execution = adapter.execute_intent(ms, intent["intent"]["intent_id"])
        assert execution["status"] == "ACTION_EXECUTED", execution
        outcome_eid = f"E-MS1998-OUT-{phase}-{index}-{step}"
        outcome = adapter.record_execution_outcome(
            ms,
            execution["execution"]["execution_id"],
            evidence_id=outcome_eid,
            capture_id=f"CAP-MS1998-OUT-{phase}-{index}-{step}",
        )
        assert outcome["status"] == "ACTION_OUTCOME_OBSERVED", outcome
        packet = outcome["outcome"]
        logs.append({
            "phase": phase,
            "step": step,
            "start_state_id": before_state,
            "control_state_evidence_id": before_evidence,
            "raw_evidence_id": raw["evidence_id"],
            "raw_tokens": tuple(raw["raw_tokens"]),
            "value_before": value_before,
            "selected_action": selected,
            "outcome_evidence_id": outcome_eid,
            "actual_next_state_id": packet["actual_next_state_id"],
            "actual_value_effect": packet["actual_value_effect"],
            "prediction_commitment": packet["prediction_commitment"]["commitment"],
        })
    return logs


def _candidate_by_action(ms: Microseed) -> dict[str, ActionOutcomePredictiveCandidate]:
    nominated = ms.nominate_action_outcome_predictive_candidates()
    out = {c.capability_id: c for c in nominated if c.capability_id in MAIN}
    assert set(out) == set(MAIN), [(c.capability_id, c.support, c.consistency) for c in nominated]
    assert all(c.support == 12 and c.consistency == 1.0 for c in out.values())
    return out


def _experience_map(ms: Microseed) -> dict[str, object]:
    return {x.evidence_id: x for x in ms._action_outcome_experiences()}


def relation_holdout_refs(
    ms: Microseed,
    candidate: ActionOutcomePredictiveCandidate,
    logs: list[dict[str, object]],
    *,
    prefix: str,
) -> tuple[object, ...]:
    exp = _experience_map(ms)
    refs = []
    rows = [r for r in logs if r["selected_action"] == candidate.capability_id]
    assert len(rows) >= 12
    for i, row in enumerate(rows[:12]):
        source_id = str(row["outcome_evidence_id"])
        assert source_id not in candidate.source_evidence_ids
        x = exp[source_id]
        refs.append(ms.append_evidence(
            f"{prefix}-{candidate.capability_id}-{i}",
            {
                "kind": "ACTION_OUTCOME_HOLDOUT",
                "start_state_id": candidate.start_state_id,
                "capability_id": candidate.capability_id,
                "capability_epoch": candidate.capability_epoch,
                "frame_epochs": [list(v) for v in candidate.frame_epochs],
                "episode_schema_epochs": [list(v) for v in candidate.episode_schema_epochs],
                "value_epoch": list(candidate.value_epoch),
                "topology_epochs": [list(v) for v in candidate.topology_epochs],
                "coordination_epochs": [list(v) for v in candidate.coordination_epochs],
                "evidence_premise_epochs": [list(v) for v in candidate.evidence_premise_epochs],
                "evidence_premise_signatures": [list(v) for v in candidate.evidence_premise_signatures],
                "actual_next_state_id": x.actual_next_state_id,
                "actual_value_effect": x.actual_value_effect,
                "source_observed_outcome_evidence_id": source_id,
            },
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="EXTERNAL-MS1998-QUALIFIER-FROM-OBSERVED-HISTORY",
        ))
    return tuple(refs)


def qualify_relations_from_later_history(
    ms: Microseed,
    candidates: dict[str, ActionOutcomePredictiveCandidate],
    logs: list[dict[str, object]],
    *,
    prefix: str,
) -> dict[str, str]:
    out: dict[str, str] = {}
    for action in MAIN:
        c = candidates[action]
        refs = relation_holdout_refs(ms, c, logs, prefix=prefix)
        ticket = ExternalActionOutcomeRelationQualifier(
            ms.evidence,
            qualifier_id=f"EXTERNAL-MS1998-{prefix}-{action}",
        ).qualify(c, qualification_evidence=refs)
        admitted = ms.qualify_action_outcome_predictive_relation(ticket)
        assert admitted["status"] == "CURRENT_PREDICTIVE_RELATION", admitted
        out[action] = admitted["relation"]["relation_id"]
    return out


def _balanced_projection_split(samples):
    groups = defaultdict(list)
    for s in samples:
        groups[(s.raw_tokens[0], s.action_token)].append(s)
    assert set(groups) == {(bit, action) for bit in ("0", "1") for action in MAIN}
    training = []
    validation = []
    for key in sorted(groups):
        rows = sorted(groups[key], key=lambda x: x.sample_id)
        assert len(rows) >= 20, (key, len(rows))
        training.extend(rows[:12])
        validation.extend(rows[12:20])
    return tuple(training), tuple(validation)


def discover_and_admit_context_projection(ms: Microseed, *, qualification_logs: list[dict[str, object]]):
    owned = ms.derive_admitted_projection_samples_from_owned_raw_observations()
    assert owned["status"] == "ADMITTED_OWNED_RAW_PROJECTION_SAMPLES", owned
    assert not owned["receipt_rejections"], owned["receipt_rejections"]
    training, validation = _balanced_projection_split(tuple(owned["samples"]))
    cfg = ProjectionDiscoveryConfig(
        max_subset=1,
        min_train_support=60,
        min_key_action_support=8,
        min_validation_accuracy=.99,
        min_lift_over_action_baseline=.15,
        min_scope_accuracy=.99,
        max_candidates=4,
    )
    searched = ms.discover_epistemic_projection_candidates_with_budget(
        training,
        validation,
        cfg,
        max_subset_evaluations=2,
    )
    assert searched["status"] == "EXHAUSTIVE_PROJECTION_SEARCH_COMPLETED", searched
    assert searched["search_complete"] is True
    assert searched["candidate_count"] == 1, searched
    cid = searched["candidates"][0]["candidate_id"]
    candidate = ms.epistemic_projection_candidates[cid]
    assert len(candidate.input_positions) == 1
    assert candidate.validation_accuracy == 1.0

    # External qualification evidence is built from a later, disjoint set of actual
    # observable-context executions.  The evaluator mode label is not copied.
    rows = []
    for row in qualification_logs:
        raw_tokens = tuple(row["raw_tokens"])
        bucket = candidate.project(raw_tokens)
        assert bucket is not None
        predicted = {
            (b, a): e for b, a, e in candidate.bucket_action_prediction
        }.get((bucket, str(row["selected_action"])))
        assert predicted == row["actual_next_state_id"], (bucket, row, predicted)
        rows.append({
            "raw_tokens": list(raw_tokens),
            "action_id": row["selected_action"],
            "actual_next_state_id": row["actual_next_state_id"],
            "projection_bucket_id": bucket,
            "source_observed_outcome_evidence_id": row["outcome_evidence_id"],
        })
    q = ms.append_evidence(
        "Q-MS1998-CONTEXT-PROJECTION",
        {
            "kind": "MS1998_OBSERVABLE_CONTEXT_PROJECTION_HOLDOUT",
            "candidate_sha256": candidate.digest(),
            "rows": rows,
        },
        EpistemicStatus.PRESSURE_SUPPORTED,
        source="EXTERNAL-MS1998-PROJECTION-QUALIFIER-FROM-OBSERVED-HISTORY",
    )
    ticket = ExternalProjectionQualifier(
        ms.evidence,
        qualifier_id="EXTERNAL-MS1998-CONTEXT-PROJECTION",
    ).qualify(candidate, qualification_evidence=(q,))
    rec = ms.admit_epistemic_projection_candidate(ticket, projection_id="P-MS1998-CONTEXT")
    assert rec.current
    return candidate, rec, owned


def derive_bucket_relation_map(candidate, historical: dict[str, str], replacement: dict[str, str], ms: Microseed):
    predictions = {(b, a): e for b, a, e in candidate.bucket_action_prediction}
    r_action = MAIN[-1]
    old_terminal = ms.action_outcome_learning.relations[historical[r_action]].next_state_id
    new_terminal = ms.action_outcome_learning.relations[replacement[r_action]].next_state_id
    old_buckets = sorted({b for (b, a), e in predictions.items() if a == r_action and e == old_terminal})
    new_buckets = sorted({b for (b, a), e in predictions.items() if a == r_action and e == new_terminal})
    assert len(old_buckets) == len(new_buckets) == 1
    assert old_buckets[0] != new_buckets[0]
    return old_buckets[0], new_buckets[0]


def routing_holdout_refs(
    ms: Microseed,
    candidate,
    projection_record,
    logs: list[dict[str, object]],
    *,
    task_id: str,
) -> tuple[object, ...]:
    refs = []
    for i, row in enumerate(logs):
        bucket = candidate.project(tuple(row["raw_tokens"]))
        assert bucket is not None
        refs.append(ms.append_evidence(
            f"ROUTE-HOLDOUT-MS1998-{i}",
            {
                "kind": "PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT",
                "projection_id": projection_record.projection_id,
                "projection_epoch": projection_record.epoch,
                "projection_signature_sha256": projection_record.signature_sha256,
                "projection_bucket_id": bucket,
                "task_id": task_id,
                "action_id": row["selected_action"],
                "channel_id": "opaque-control",
                "horizon": 1,
                "actual_next_state_id": row["actual_next_state_id"],
                "actual_value_effect": row["actual_value_effect"],
                "source_observed_outcome_evidence_id": row["outcome_evidence_id"],
            },
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="EXTERNAL-MS1998-ROUTING-QUALIFIER-FROM-OBSERVED-HISTORY",
        ))
    return tuple(refs)


def nominate_and_qualify_routing(
    ms: Microseed,
    candidate,
    projection_record,
    historical: dict[str, str],
    replacement: dict[str, str],
    logs: list[dict[str, object]],
):
    old_bucket, new_bucket = derive_bucket_relation_map(candidate, historical, replacement, ms)
    prop = ms.append_evidence(
        "ROUTE-PROP-MS1998",
        {
            "kind": "ROUTING_PROPOSAL",
            "basis": "MATCH_ADMITTED_PROJECTION_ENDPOINTS_TO_QUALIFIED_RELATION_ENDPOINTS",
            "historical_bucket": old_bucket,
            "replacement_bucket": new_bucket,
            "semantic_regime_authority": "NONE",
            "model_switch_authority": "NONE",
        },
        EpistemicStatus.PRESSURE_SUPPORTED,
        source="MICROSEED-PROPOSAL",
    )
    task_id = "MS1998-OBSERVABLE-CONTEXT"
    route = ms.nominate_projection_conditioned_relation_routing(
        projection_id=projection_record.projection_id,
        task_id=task_id,
        action_ids=MAIN,
        channel_ids=("opaque-control",),
        horizon=1,
        default_action_relations=tuple((a, replacement[a]) for a in MAIN),
        bucket_action_overrides=tuple((old_bucket, a, historical[a]) for a in MAIN),
        source_evidence_ids=(prop.evidence_id,),
    )
    refs = routing_holdout_refs(ms, candidate, projection_record, logs, task_id=task_id)
    ticket = ExternalProjectionConditionedRelationQualifier(
        ms.evidence,
        qualifier_id="EXTERNAL-MS1998-OBSERVABLE-CONTEXT-ROUTING",
    ).qualify(route, qualification_evidence=refs, relations=ms.action_outcome_learning.relations)
    admitted = ms.qualify_projection_conditioned_relation_routing(ticket)
    assert admitted["status"] == "CURRENT_PROJECTION_CONDITIONED_ROUTING", admitted
    return admitted["binding"]["binding_id"], old_bucket, new_bucket


def _derive_current_bucket_from_all_options(
    ms: Microseed,
    binding_id: str,
    *,
    task_id: str,
) -> tuple[str | None, tuple[dict[str, object], ...]]:
    results = tuple(
        ms.resolve_current_raw_projection_conditioned_relation(
            binding_id,
            action_id=action,
            task_id=task_id,
            channel_id="opaque-control",
            horizon=1,
        )
        for action in MAIN
    )
    if any(x.get("status") != "CURRENT_PARTITION_SCOPED_RELATION" for x in results):
        return None, results
    buckets = {str(x["projection_bucket_id"]) for x in results}
    if len(buckets) != 1:
        return None, results
    return next(iter(buckets)), results


def run_zero_row_episode(
    ms: Microseed,
    adapter: ShadowEnvironmentAdapter,
    world: ObservableContextWorld,
    *,
    evaluator_mode: str,
    index: int,
    binding_id: str,
    task_id: str,
) -> dict[str, object]:
    world.configure_mode(evaluator_mode)
    world.reset()
    adapter.observe_control(ms, f"ZERO-{index}-START")
    options = tuple(adapter.option(aid) for aid in MAIN)
    selected = []
    buckets = []

    for step in range(3):
        current = ms.action_closure.current_state
        assert current is not None
        _raw_before_action(ms, adapter, tag=f"ZERO-{index}-{step}")
        bucket, resolved = _derive_current_bucket_from_all_options(ms, binding_id, task_id=task_id)
        assert bucket is not None, resolved
        assert all(x["bucket_selection_authority"] == "NONE" for x in resolved)
        # The bucket is inspected above only as an audit witness.  It is NOT passed
        # into rehearsal.  The core composition bridge re-derives one consistent
        # current bucket across every eligible option and fails closed otherwise.
        proposal = ms.nominate_current_raw_projection_conditioned_rehearsal(
            (),
            options,
            start_state_id=current.state_id,
            value_id=adapter.config.value_id,
            projection_routing_id=binding_id,
            routing_task_id=task_id,
            routing_channel_id="opaque-control",
            config=CounterfactualRehearsalConfig(max_horizon=1, max_nodes=16),
        )
        assert proposal is not None, (evaluator_mode, step, current.state_id, bucket)
        intent = ms.nominate_bounded_action_intent(proposal.proposal_id, adapter.act_obligation())
        assert intent["status"] == "ACTION_INTENT_NOMINATED", intent
        action = intent["intent"]["capability_id"]
        assert action == MAIN[step]
        execution = adapter.execute_intent(ms, intent["intent"]["intent_id"])
        assert execution["status"] == "ACTION_EXECUTED"
        out = adapter.record_execution_outcome(
            ms,
            execution["execution"]["execution_id"],
            evidence_id=f"E-MS1998-ZERO-{index}-{step}",
            capture_id=f"CAP-MS1998-ZERO-{index}-{step}",
        )
        assert out["status"] == "ACTION_OUTCOME_OBSERVED", out
        selected.append(action)
        buckets.append(bucket)

    return {
        "selected_actions": selected,
        "projection_buckets": buckets,
        "final_state": world.observe()["next_state_id"],
        "final_value": world.observe()["observed_value"],
        "supplied_rehearsal_row_count": 0,
    }


def run_ms1998() -> dict[str, object]:
    td = tempfile.TemporaryDirectory(prefix="ms1998-observable-context-")
    world = ObservableContextWorld()
    adapter = ShadowEnvironmentAdapter(
        world,
        AdapterConfig(
            adapter_instance_id="MS1998-OBSERVABLE",
            viable_low=-0.25,
            viable_high=0.25,
        ),
    )
    ms = Microseed(Path(td.name))
    try:
        adapter.attach(ms)
        # Bounded raw ingress requires the current observation channel to be owned by
        # exactly one current operational frame.  ShadowEnvironmentAdapter predates
        # the raw-coordinate line, so the research fixture makes that existing frame
        # binding explicit rather than adding a new observation owner.
        for capability_id in MAIN + (adapter.config.observation_capability_id,):
            ms.frames.bind_capability(adapter.config.frame_id, capability_id)

        # Phase 1: learn the historical (+1) relations from lived outcomes.
        p_train = []
        for i in range(12):
            p_train.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="P-TRAIN"))
        historical_candidates = _candidate_by_action(ms)
        assert all(c.value_effect == 1.0 for c in historical_candidates.values())

        # Later P outcomes are independent holdout ancestry for external qualification.
        p_hold = []
        for i in range(12):
            p_hold.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="P-HOLD"))
        historical_relations = qualify_relations_from_later_history(
            ms, historical_candidates, p_hold, prefix="P-REL-HOLDOUT"
        )

        # Phase 2: switch reality to the opposite hidden dynamics.  The guidance still
        # sees only current state/value, so its effect sign flips from visible pressure.
        n_drift = []
        for i in range(16):
            n_drift.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="N", index=i, phase="N-DRIFT"))

        replacement_candidates: dict[str, ActionOutcomePredictiveCandidate] = {}
        drift_witnesses = {}
        for action in MAIN:
            rid = historical_relations[action]
            assessed = ms.assess_action_outcome_predictive_currentness(
                rid,
                config=PredictiveCurrentnessConfig(window_size=8, min_accuracy=.75, consecutive_failure_windows=2),
            )
            assert assessed["status"] == "DRIFT_WITNESS", assessed
            drift_witnesses[action] = assessed["witness"]["witness_id"]
            replacements = ms.nominate_action_outcome_replacement_candidates(
                rid,
                drift_witnesses[action],
                min_support=8,
                min_consistency=.78,
            )
            assert len(replacements) == 1, replacements
            replacement_candidates[action] = replacements[0]
            assert replacements[0].value_effect == -1.0

        n_hold = []
        for i in range(12):
            n_hold.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="N", index=i, phase="N-HOLD"))
        replacement_relations = qualify_relations_from_later_history(
            ms, replacement_candidates, n_hold, prefix="N-REPL-HOLDOUT"
        )
        for action in MAIN:
            assert ms.action_outcome_predictive_relation_status(historical_relations[action])["status"] == "STALE_PREDICTIVE_RELATION"
            new_status = ms.action_outcome_predictive_relation_status(replacement_relations[action])
            assert new_status["status"] == "CURRENT_PREDICTIVE_RELATION"
            assert new_status["replacement_lineage"]["replacement_of_relation_id"] == historical_relations[action]

        # Separate later episodes qualify the raw context projection; no mode label is
        # copied into the qualification evidence.
        projection_qual_logs = []
        for i in range(4):
            projection_qual_logs.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="PROJ-Q-P"))
            projection_qual_logs.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="N", index=i, phase="PROJ-Q-N"))
        context_candidate, projection_record, owned = discover_and_admit_context_projection(
            ms,
            qualification_logs=projection_qual_logs,
        )

        # Fully disjoint later episodes qualify the context->relation routing.
        routing_logs = []
        for i in range(12):
            routing_logs.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="ROUTE-Q-P"))
            routing_logs.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="N", index=i, phase="ROUTE-Q-N"))
        binding_id, historical_bucket, replacement_bucket = nominate_and_qualify_routing(
            ms,
            context_candidate,
            projection_record,
            historical_relations,
            replacement_relations,
            routing_logs,
        )

        # Hostile: no current raw receipt means no context choice.
        world.configure_mode("P")
        world.reset()
        adapter.observe_control(ms, "MISSING-RAW")
        missing_bucket, missing = _derive_current_bucket_from_all_options(
            ms, binding_id, task_id="MS1998-OBSERVABLE-CONTEXT"
        )
        assert missing_bucket is None
        assert all(x["status"] == "DEFER_UNKNOWN" for x in missing)
        assert all(x["reason"] == "EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_CURRENT_STATE_REQUIRED" for x in missing)

        # Hostile: duplicate current raw receipts do not create an implicit tie-break.
        _raw_before_action(ms, adapter, tag="DUP-A")
        _raw_before_action(ms, adapter, tag="DUP-B")
        duplicate_bucket, duplicate = _derive_current_bucket_from_all_options(
            ms, binding_id, task_id="MS1998-OBSERVABLE-CONTEXT"
        )
        assert duplicate_bucket is None
        assert all(x["status"] == "DEFER_UNKNOWN" for x in duplicate)
        assert all(x["reason"] == "EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_CURRENT_STATE_REQUIRED" for x in duplicate)

        # Final handoff: zero supplied rehearsal rows in each latent world mode.
        zero_p = run_zero_row_episode(
            ms, adapter, world, evaluator_mode="P", index=0,
            binding_id=binding_id, task_id="MS1998-OBSERVABLE-CONTEXT",
        )
        zero_n = run_zero_row_episode(
            ms, adapter, world, evaluator_mode="N", index=1,
            binding_id=binding_id, task_id="MS1998-OBSERVABLE-CONTEXT",
        )
        assert zero_p["selected_actions"] == zero_n["selected_actions"] == list(MAIN)
        assert zero_p["final_state"] == "u" and zero_n["final_state"] == "v"
        assert zero_p["final_value"] == zero_n["final_value"] == 0.0
        assert set(zero_p["projection_buckets"]) == {historical_bucket}
        assert set(zero_n["projection_buckets"]) == {replacement_bucket}

        # No evaluator mode label became durable organism evidence.
        durable_payloads = [
            row.get("payload", {}) for row in ms.store.events()
            if isinstance(row.get("payload", {}), dict)
        ]
        assert all("mode" not in payload for payload in durable_payloads)

        return {
            "status": "BOUNDARY_CONFIRMED",
            "historical_relation_ids": historical_relations,
            "replacement_relation_ids": replacement_relations,
            "drift_witness_ids": drift_witnesses,
            "owned_raw_projection_sample_count": owned["sample_count"],
            "context_projection_input_positions": list(context_candidate.input_positions),
            "context_projection_validation_accuracy": context_candidate.validation_accuracy,
            "historical_bucket": historical_bucket,
            "replacement_bucket": replacement_bucket,
            "routing_binding_id": binding_id,
            "zero_row_historical": zero_p,
            "zero_row_replacement": zero_n,
            "training_guidance_reads_evaluator_mode": "NO",
            "training_guidance_basis": "CURRENT_ORGANISM_VISIBLE_CONTROL_STATE_PLUS_REGULATORY_VALUE_ONLY",
            "terminal_identity_supplied_during_training": "NO",
            "caller_supplied_preferred_action": "NO__ALL_CURRENT_OPAQUE_OPTIONS_PRESENT",
            "caller_supplied_projection_bucket": "NO__CORE_BRIDGE_DERIVES_CURRENT_BUCKET_FROM_OWNED_RAW_EVIDENCE",
            "caller_supplied_routed_relation": "NO",
            "zero_row_handoff": "YES",
            "missing_raw_context_policy": "DEFER_UNKNOWN",
            "duplicate_raw_context_policy": "DEFER_UNKNOWN",
            "historical_relation_global_reactivation": "NO__STALE_RELATION_REUSED_ONLY_INSIDE_QUALIFIED_CONTEXT_ROUTE",
            "external_qualification_authority": "REMAINS_EXTERNAL_BY_CONSTITUTION",
            "routing_nomination_basis": "ADMITTED_PROJECTION_ENDPOINTS_MATCHED_TO_QUALIFIED_LEARNED_RELATION_ENDPOINTS",
            "semantic_regime_authority": "NONE",
            "model_switch_authority": "NONE",
            "execution_authority_gain": "NONE",
            "new_core_mechanism_required": "YES__NARROW_COMPOSITION_BRIDGE_ONLY__NO_NEW_STATE_OR_POLICY_OWNER",
            "earned": "ORGANISM_VISIBLE_CURRENT_CONTEXT_PLUS_LIVED_OUTCOME_DRIFT_AND_EXISTING_QUALIFIED_ROUTING_CAN_REMOVE_EVALUATOR_MODE_FROM_TRAINING_GUIDANCE_AND_HAND_OFF_TO_ZERO_ROW_CONTEXT_CONDITIONED_ACTION_SELECTION_WITHOUT_CALLER_BUCKET_RELAY_OR_A_NEW_STATE_OR_POLICY_MANAGER",
            "remaining_boundary": "EXTERNAL_QUALIFICATION_AND_ROUTING_NOMINATION_REMAIN_ASSISTED_AND_SUSTAINED_RICH_WORLD_LIFETIME_COMPOSITION_IS_NOT_YET_PROVEN",
        }
    finally:
        _close(ms)
        td.cleanup()


def main() -> None:
    print(json.dumps(run_ms1998(), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
