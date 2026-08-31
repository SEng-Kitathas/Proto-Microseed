from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus
from microseed.development.discovery import DiscoveryConfig
from microseed.runtime.entity import action_result_digest
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2035_organism_owned_current_value_frame_completeness import _contract
from scratch.ms2036_full_frame_bound_pareto_research import (
    _fixture,
    _p2_dominates_effects,
    _tradeoff_effects,
)

CFG = DiscoveryConfig(min_singleton_samples=5, quantization_step=0.5, min_consistency=0.99)
MARKER = "ENDOGENOUS_UNKNOWN_MATERIALIZED_AFTER_STRICT_FULL_FRAME_PARETO_SELECTION"
SOURCE = "MICROSEED_ENDOGENOUS_SELECTED_FULL_FRAME_EPISTEMIC_OPPORTUNITY"
KIND = "SELECTED_OWNED_REFERENT_FULL_FRAME_EPISTEMIC_UNKNOWN"
AUTHORITY = "STRICT_FULL_FRAME_PARETO_REGULATORY_DOMINANCE_ONLY"


def nominate_current_full_frame_selected_opportunity_research(ms, obligation) -> dict:
    before = (len(ms.epistemic_deficits.records), len(ms.action_closure.intents), len(ms.action_closure.executions))
    surface = ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(obligation, config=CFG)
    if surface.get("status") != "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION":
        return {
            "status": "ABSTAIN", "reason": str(surface.get("reason", surface.get("status"))),
            "selection_surface": surface, "selection_authority": "NONE", "execution_authority": "NONE",
            "deficit_delta": len(ms.epistemic_deficits.records)-before[0],
            "intent_delta": len(ms.action_closure.intents)-before[1],
            "execution_delta": len(ms.action_closure.executions)-before[2],
        }
    if str(surface.get("selection_authority")) != AUTHORITY:
        return {"status":"ABSTAIN","reason":"STRICT_FULL_FRAME_SELECTION_AUTHORITY_REQUIRED","selection_authority":"NONE","execution_authority":"NONE","deficit_delta":0,"intent_delta":0,"execution_delta":0}
    selected_deficit = str(surface["selected_deficit_id"]); selected_probe = str(surface["selected_probe_action_id"])
    ops = ms._current_owned_referent_epistemic_opportunities(obligation)
    selected = next((op for op in ops if str(op["deficit"].deficit_id)==selected_deficit and str(op["probe_action_id"])==selected_probe), None)
    if selected is None:
        return {"status":"ABSTAIN","reason":"SELECTED_CURRENT_OPPORTUNITY_REQUIRED","selection_authority":"NONE","execution_authority":"NONE","deficit_delta":0,"intent_delta":0,"execution_delta":0}
    d=selected["deficit"]
    if d.deficit_id in ms.epistemic_deficits.records:
        return {"status":"ABSTAIN","reason":"SELECTED_EPISTEMIC_DEFICIT_ALREADY_PERSISTED","selected_deficit_id":d.deficit_id,"selected_probe_action_id":selected_probe,"selection_authority":"NONE","execution_authority":"NONE","deficit_delta":0,"intent_delta":0,"execution_delta":0}
    sc = dict(surface["selection_commitment"])
    payload = {
        "kind": KIND,
        "selected_ephemeral_deficit_id": d.deficit_id,
        "selected_trial_id": selected["trial"].trial_id,
        "selected_trial_digest": selected["trial"].digest(),
        "binding_id": selected["binding_id"],
        "probe_action_id": selected_probe,
        "source_raw_observation_evidence_id": d.unknown_evidence_id,
        "hypothesis_digest_sha256": d.hypothesis_digest_sha256,
        "missing_discriminator_signature_sha256": d.missing_discriminator_signature_sha256,
        "priority_commitment_id": selected["priority"].commitment_id,
        "information_commitment_id": selected["contrast_information"].commitment_id,
        "step_commitment_id": selected["commitment"].commitment_id,
        "opportunity_content_signature_sha256": selected["content_signature_sha256"],
        "cross_deficit_selection_commitment_id": str(sc["commitment_id"]),
        "cross_deficit_selection_authority": AUTHORITY,
        "complete_value_frame_digest_sha256": str(surface["complete_value_frame"]["frame_digest_sha256"]),
        "proposal_only": True,
        "authority_gain": "NONE",
    }
    unknown_id = "SELECTED-FULL-FRAME-REFERENT-UNKNOWN-" + action_result_digest(payload)[:24]
    existing = ms.evidence.get(unknown_id)
    if existing is None:
        unknown = ms.append_evidence(unknown_id, payload, EpistemicStatus.UNKNOWN_INCOMPLETE, source=SOURCE)
        unknown_evidence_id = unknown.evidence_id
    else:
        if existing.get("disposition") != EpistemicStatus.UNKNOWN_INCOMPLETE.value or existing.get("payload") != payload or existing.get("source") != SOURCE:
            return {"status":"ABSTAIN","reason":"SELECTED_ENDOGENOUS_UNKNOWN_EVIDENCE_COLLISION","selection_authority":"NONE","execution_authority":"NONE","deficit_delta":0,"intent_delta":0,"execution_delta":0}
        unknown_evidence_id = unknown_id
    persisted = ms.record_action_limited_unknown(
        deficit_id=d.deficit_id,
        question_key=d.question_key,
        hypothesis_digest_sha256=d.hypothesis_digest_sha256,
        unknown_evidence_id=unknown_evidence_id,
        missing_discriminator_signature_sha256=d.missing_discriminator_signature_sha256,
        premise_anchors=d.premise_anchors,
        assistance_ancestry=tuple(d.assistance_ancestry)+(MARKER,),
    )
    nomination = ms.nominate_endogenous_epistemic_program_step_intent_from_current_surface(
        selected["trial"], selected["decision_context"], obligation,
    )
    return {
        "status": "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED" if nomination.get("status")=="ACTION_INTENT_NOMINATED" else "SELECTED_OPPORTUNITY_PERSISTED_BUT_NOT_NOMINATED",
        "reason": str(nomination.get("reason", nomination.get("status", "UNKNOWN"))),
        "selected_deficit_id": d.deficit_id,
        "selected_probe_action_id": selected_probe,
        "unknown_evidence_id": unknown_evidence_id,
        "persisted_deficit": persisted.serializable(),
        "selection_surface": surface,
        "nomination": nomination,
        "selection_authority": AUTHORITY,
        "execution_authority": "NONE",
        "deficit_delta": len(ms.epistemic_deficits.records)-before[0],
        "intent_delta": len(ms.action_closure.intents)-before[1],
        "execution_delta": len(ms.action_closure.executions)-before[2],
    }


def run_tradeoff_abstains() -> dict:
    td, ms, calls, *_ = _fixture(_tradeoff_effects())
    try:
        r=nominate_current_full_frame_selected_opportunity_research(ms, act_ob())
        assert r["status"]=="ABSTAIN", r
        assert r["deficit_delta"]==r["intent_delta"]==r["execution_delta"]==0
        assert calls==[]
        return {"status":"PASS","result":r,"handler_calls":list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_dominance_persists_and_nominates() -> dict:
    td, ms, calls, *_ = _fixture(_p2_dominates_effects())
    try:
        r=nominate_current_full_frame_selected_opportunity_research(ms, act_ob())
        assert r["status"]=="SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", r
        assert r["selected_probe_action_id"]=="P2"
        assert r["deficit_delta"]==1 and r["intent_delta"]==1 and r["execution_delta"]==0, r
        ev=ms.evidence.get(r["unknown_evidence_id"])
        assert ev is not None and ev["disposition"]==EpistemicStatus.UNKNOWN_INCOMPLETE.value and ev["source"]==SOURCE
        assert ev["payload"]["kind"]==KIND and ev["payload"]["cross_deficit_selection_authority"]==AUTHORITY
        deficit=ms.epistemic_deficits.records[r["selected_deficit_id"]]
        assert MARKER in deficit.assistance_ancestry
        assert calls==[]
        return {"status":"PASS","result":r,"handler_calls":list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_idempotent() -> dict:
    td, ms, calls, *_ = _fixture(_p2_dominates_effects())
    try:
        first=nominate_current_full_frame_selected_opportunity_research(ms, act_ob())
        second=nominate_current_full_frame_selected_opportunity_research(ms, act_ob())
        assert first["status"]=="SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED"
        assert second["status"]=="ABSTAIN" and second["reason"]=="SELECTED_EPISTEMIC_DEFICIT_ALREADY_PERSISTED", second
        assert second["deficit_delta"]==second["intent_delta"]==second["execution_delta"]==0
        assert calls==[]
        return {"status":"PASS","first":first,"second":second,"handler_calls":list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_incomplete_frame_abstains() -> dict:
    td, ms, calls, *_ = _fixture(_p2_dominates_effects())
    try:
        ms.register_value_variable(_contract("X"))
        r=nominate_current_full_frame_selected_opportunity_research(ms, act_ob())
        assert r["status"]=="ABSTAIN" and r["reason"]=="CURRENT_VALUE_FRAME_OBSERVATION_MISSING:X", r
        assert r["deficit_delta"]==r["intent_delta"]==r["execution_delta"]==0
        assert calls==[]
        return {"status":"PASS","result":r,"handler_calls":list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_ms2038() -> dict:
    return {
        "status":"FULL_FRAME_SELECTED_OPPORTUNITY_LIFECYCLE_EARNED_RESEARCH_ONLY",
        "tradeoff":run_tradeoff_abstains(),
        "dominance":run_dominance_persists_and_nominates(),
        "idempotent":run_idempotent(),
        "incomplete_frame":run_incomplete_frame_abstains(),
        "runtime_promotion_authorized":"NO",
        "execution_authority":"NONE",
    }


if __name__=="__main__":
    print(json.dumps(run_ms2038(),indent=2,sort_keys=True,default=str))
