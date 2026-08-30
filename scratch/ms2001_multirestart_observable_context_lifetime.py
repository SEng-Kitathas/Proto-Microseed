from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter, AdapterConfig
from scratch.ms1997_lived_history_to_endogenous_program import MAIN
from scratch.ms1998_observable_context_assistance_removal import (
    ObservableContextWorld,
    _candidate_by_action,
    _close,
    discover_and_admit_context_projection,
    nominate_and_qualify_routing,
    qualify_relations_from_later_history,
    run_assisted_episode,
    run_zero_row_episode,
)
from microseed.development.predictive_adaptation import PredictiveCurrentnessConfig
from microseed.development.capability_admission import ExternalCapabilityQualifier
from scratch.ms2000_same_identity_capability_requalification import _effect, _fresh_support


def _attach(root: Path, session: int):
    ms = Microseed(root)
    world = ObservableContextWorld()
    adapter = ShadowEnvironmentAdapter(
        world,
        AdapterConfig(
            adapter_instance_id=f"MS2001-SESSION-{session}",
            viable_low=-0.25,
            viable_high=0.25,
        ),
    )
    adapter.attach(ms)
    for capability_id in MAIN + (adapter.config.observation_capability_id,):
        ms.frames.bind_capability(adapter.config.frame_id, capability_id)
    return ms, world, adapter


def run_ms2001() -> dict[str, object]:
    td = tempfile.TemporaryDirectory(prefix="ms2001-multirestart-observable-")
    root = Path(td.name)
    receipts: list[dict[str, object]] = []

    historical_relations: dict[str, str]
    replacement_relations: dict[str, str]
    context_candidate_id: str
    projection_record_id: str
    binding_id: str
    historical_bucket: str
    replacement_bucket: str

    # Session 1: acquire historical +1 relations from lived outcomes and independent holdout.
    ms, world, adapter = _attach(root, 1)
    try:
        p_train = []
        for i in range(12):
            p_train.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="S1-P-TRAIN"))
        historical_candidates = _candidate_by_action(ms)
        assert all(c.value_effect == 1.0 for c in historical_candidates.values())
        p_hold = []
        for i in range(12):
            p_hold.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="S1-P-HOLD"))
        historical_relations = qualify_relations_from_later_history(
            ms, historical_candidates, p_hold, prefix="S1-P-REL-HOLDOUT"
        )
        assert all(ms.action_outcome_predictive_relation_status(rid)["status"] == "CURRENT_PREDICTIVE_RELATION" for rid in historical_relations.values())
        receipts.append({"session": 1, "phase": "historical_acquisition", "outcomes": len(ms.action_closure.outcomes)})
    finally:
        _close(ms)

    # Session 2: fresh environment authority; persisted historical relations must be re-grounded,
    # then drift and replacement are learned from current organism-visible pressure only.
    ms, world, adapter = _attach(root, 2)
    try:
        pre = {a: ms.action_outcome_predictive_relation_status(rid)["status"] for a, rid in historical_relations.items()}
        # Fresh adapter/environment authority should make old learned relations usable only if
        # their represented action/frame dependencies are current again.
        assert all(status in {"CURRENT_PREDICTIVE_RELATION", "STALE_PREDICTIVE_RELATION"} for status in pre.values())
        n_drift = []
        for i in range(16):
            n_drift.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="N", index=i, phase="S2-N-DRIFT"))
        replacement_candidates = {}
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
            assert len(replacements) == 1
            replacement_candidates[action] = replacements[0]
            assert replacements[0].value_effect == -1.0
        n_hold = []
        for i in range(12):
            n_hold.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="N", index=i, phase="S2-N-HOLD"))
        replacement_relations = qualify_relations_from_later_history(
            ms, replacement_candidates, n_hold, prefix="S2-N-REPL-HOLDOUT"
        )
        assert all(ms.action_outcome_predictive_relation_status(rid)["status"] == "CURRENT_PREDICTIVE_RELATION" for rid in replacement_relations.values())
        receipts.append({"session": 2, "phase": "drift_replacement", "pre_relation_status": pre, "outcomes": len(ms.action_closure.outcomes)})
    finally:
        _close(ms)

    # Session 3: qualify owned raw projection and context->relation routing from disjoint later history.
    ms, world, adapter = _attach(root, 3)
    try:
        projection_qual_logs = []
        for i in range(4):
            projection_qual_logs.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="S3-PROJ-Q-P"))
            projection_qual_logs.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="N", index=i, phase="S3-PROJ-Q-N"))
        context_candidate, projection_record, owned = discover_and_admit_context_projection(ms, qualification_logs=projection_qual_logs)
        context_candidate_id = context_candidate.candidate_id
        projection_record_id = projection_record.projection_id
        routing_logs = []
        for i in range(12):
            routing_logs.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="S3-ROUTE-Q-P"))
            routing_logs.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="N", index=i, phase="S3-ROUTE-Q-N"))
        binding_id, historical_bucket, replacement_bucket = nominate_and_qualify_routing(
            ms,
            context_candidate,
            projection_record,
            historical_relations,
            replacement_relations,
            routing_logs,
        )
        receipts.append({"session": 3, "phase": "projection_routing", "owned_samples": owned["sample_count"], "binding_id": binding_id, "outcomes": len(ms.action_closure.outcomes)})
    finally:
        _close(ms)

    # Session 4: no new training rows. Fresh environment authority only; persisted qualified
    # projection/routing/relation state must reconstruct enough for zero-row selection in both modes.
    ms, world, adapter = _attach(root, 4)
    try:
        # Co-present capability lifecycle pressure in the same active lifetime session.
        # This does not persist a Python handler through restart; fresh executable
        # capability authority remains session-local, consistent with MS1951.
        rq = _effect("MS2001-RQ")
        ms.register_capability(rq)
        rq_sig = ms.capabilities.contracts["MS2001-RQ"].computed_signature_sha256()
        rq_authority = ms.capabilities.contracts["MS2001-RQ"].authority.value
        ms.invalidate_capability("MS2001-RQ", reason="MS2001-LIFETIME-DRIFT")
        rq_epoch = ms.capabilities.epochs["MS2001-RQ"]
        rq_support = _fresh_support(ms, "MS2001-RQ-SUPPORT")
        rq_ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="MS2001-HSP-EXTERNAL").requalify(
            ms.capabilities.contracts["MS2001-RQ"],
            stale_epoch=rq_epoch,
            qualification_evidence=(rq_support,),
        )
        ms.requalify_capability(rq_ticket)
        assert ms.capabilities.is_current("MS2001-RQ")
        assert ms.capabilities.contracts["MS2001-RQ"].computed_signature_sha256() == rq_sig
        assert ms.capabilities.contracts["MS2001-RQ"].authority.value == rq_authority

        zero_p = run_zero_row_episode(ms, adapter, world, evaluator_mode="P", index=0, binding_id=binding_id, task_id="MS1998-OBSERVABLE-CONTEXT")
        zero_n = run_zero_row_episode(ms, adapter, world, evaluator_mode="N", index=1, binding_id=binding_id, task_id="MS1998-OBSERVABLE-CONTEXT")
        assert zero_p["selected_actions"] == zero_n["selected_actions"] == list(MAIN)
        assert zero_p["final_state"] == "u" and zero_n["final_state"] == "v"
        assert zero_p["final_value"] == zero_n["final_value"] == 0.0
        assert set(zero_p["projection_buckets"]) == {historical_bucket}
        assert set(zero_n["projection_buckets"]) == {replacement_bucket}
        receipts.append({"session": 4, "phase": "zero_row_reentry", "zero_p": zero_p, "zero_n": zero_n, "outcomes": len(ms.action_closure.outcomes)})
        return {
            "status": "PASS",
            "sessions": receipts,
            "historical_relations": historical_relations,
            "replacement_relations": replacement_relations,
            "context_candidate_id": context_candidate_id,
            "projection_record_id": projection_record_id,
            "routing_binding_id": binding_id,
            "historical_bucket": historical_bucket,
            "replacement_bucket": replacement_bucket,
            "automatic_reauthorization": "NO__FRESH_ENVIRONMENT_AUTHORITY_EACH_SESSION",
            "caller_supplied_projection_bucket": "NO",
            "caller_supplied_routed_relation": "NO",
            "evaluator_mode_durable_evidence": "NO",
            "new_cross_cutting_manager": "NO",
            "projection_subset_evaluation_budget": 2,
            "projection_search_complete_under_budget": "YES",
            "capability_requalification_co_present": "YES",
            "capability_requalification_authority_gain": "NONE",
            "capability_requalification_signature_preserved": True,
            "remaining_boundary": "REFERENT_PRESSURE_NOT_YET_COMPOSED_AS_A_PERSISTED_LIFETIME_OWNER_AND_RUNTIME_CAPABILITY_HANDLERS_STILL_REQUIRE_FRESH_SESSION_REATTACHMENT",
        }
    finally:
        _close(ms)
        td.cleanup()


def main() -> None:
    print(json.dumps(run_ms2001(), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
