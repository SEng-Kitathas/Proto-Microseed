from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus
from microseed.runtime.entity import action_result_digest
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2021_cross_deficit_selection_blocker_replayed_with_raw_contrast import enumerate_opportunities
from scratch.ms2022_same_value_cross_deficit_regulatory_dominance_quarry import derive_strict_same_value_regulatory_dominance
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface, derive_selection_commitment


def persist_and_nominate_selected_current_opportunity(m, surface: dict) -> dict:
    before_deficits = len(m.epistemic_deficits.records)
    before_intents = len(m.action_closure.intents)
    before_exec = len(m.action_closure.executions)
    if surface.get("status") != "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES":
        return {
            "status": "ABSTAIN",
            "reason": str(surface.get("reason", surface.get("status", "MULTIPLE_CURRENT_OPPORTUNITIES_REQUIRED"))),
            "selection_authority": "NONE",
            "execution_authority": "NONE",
            "deficit_delta": len(m.epistemic_deficits.records) - before_deficits,
            "intent_delta": len(m.action_closure.intents) - before_intents,
            "execution_delta": len(m.action_closure.executions) - before_exec,
        }
    opportunities = tuple(surface["opportunities"])
    comparison = derive_strict_same_value_regulatory_dominance(m, opportunities)
    selection = derive_selection_commitment(comparison, opportunities)
    if not selection.licenses_yes():
        return {
            "status": "ABSTAIN",
            "reason": selection.reason,
            "selection_commitment": selection.serializable(),
            "comparison": comparison,
            "selection_authority": "NONE",
            "execution_authority": "NONE",
            "deficit_delta": len(m.epistemic_deficits.records) - before_deficits,
            "intent_delta": len(m.action_closure.intents) - before_intents,
            "execution_delta": len(m.action_closure.executions) - before_exec,
        }
    q = dict(selection.qualifiers)
    selected_deficit = str(q["selected_deficit_id"])
    selected_probe = str(q["selected_probe_action_id"])
    matches = tuple(
        op for op in opportunities
        if str(op["deficit"].deficit_id) == selected_deficit and str(op["probe_action_id"]) == selected_probe
    )
    if len(matches) != 1:
        return {
            "status": "ABSTAIN",
            "reason": "EXACT_SELECTED_CURRENT_OPPORTUNITY_REQUIRED",
            "selection_commitment": selection.serializable(),
            "selection_authority": "NONE",
            "execution_authority": "NONE",
            "deficit_delta": len(m.epistemic_deficits.records) - before_deficits,
            "intent_delta": len(m.action_closure.intents) - before_intents,
            "execution_delta": len(m.action_closure.executions) - before_exec,
        }
    op = matches[0]
    d = op["deficit"]
    # The ephemeral opportunity uses the latest authenticated raw observation as a
    # read-only premise. Durable deficit lifecycle requires an explicit UNKNOWN
    # evidence record. Reuse the endogenous-discovery pattern: write our own
    # inference as UNKNOWN_INCOMPLETE, content-bound to the selected opportunity
    # and its raw provenance, so self-generated structure cannot masquerade as
    # external support.
    unknown_payload = {
        "kind": "SELECTED_OWNED_REFERENT_EPISTEMIC_UNKNOWN",
        "selected_ephemeral_deficit_id": str(d.deficit_id),
        "selected_trial_id": str(op["trial"].trial_id),
        "selected_trial_digest": str(op["trial"].digest()),
        "priority_commitment_id": str(op["priority"].commitment_id),
        "information_commitment_id": str(op["contrast_information"].commitment_id),
        "step_commitment_id": str(op["commitment"].commitment_id),
        "binding_id": str(op["binding_id"]),
        "probe_action_id": selected_probe,
        "source_raw_observation_evidence_id": str(d.unknown_evidence_id),
        "hypothesis_digest_sha256": str(d.hypothesis_digest_sha256),
        "missing_discriminator_signature_sha256": str(d.missing_discriminator_signature_sha256),
        "selection_commitment_id": str(selection.commitment_id),
        "proposal_only": True,
        "authority_gain": "NONE",
    }
    unknown_id = "SELECTED-REFERENT-UNKNOWN-" + action_result_digest(unknown_payload)[:24]
    unknown = m.append_evidence(
        unknown_id, unknown_payload, EpistemicStatus.UNKNOWN_INCOMPLETE,
        source="MICROSEED_ENDOGENOUS_SELECTED_EPISTEMIC_OPPORTUNITY",
    )
    persisted = m.record_action_limited_unknown(
        deficit_id=d.deficit_id,
        question_key=d.question_key,
        hypothesis_digest_sha256=d.hypothesis_digest_sha256,
        unknown_evidence_id=unknown.evidence_id,
        missing_discriminator_signature_sha256=d.missing_discriminator_signature_sha256,
        premise_anchors=d.premise_anchors,
        assistance_ancestry=tuple(d.assistance_ancestry) + (
            "ENDOGENOUS_UNKNOWN_MATERIALIZED_AFTER_STRICT_CROSS_DEFICIT_SELECTION",
        ),
    )
    nomination = m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(
        op["trial"], op["decision_context"], act_ob(),
    )
    return {
        "status": "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED" if nomination.get("status") == "ACTION_INTENT_NOMINATED" else "SELECTED_OPPORTUNITY_PERSISTED_BUT_NOT_NOMINATED",
        "reason": str(nomination.get("reason", nomination.get("status", "UNKNOWN"))),
        "selected_deficit_id": selected_deficit,
        "selected_probe_action_id": selected_probe,
        "persisted_deficit": persisted.serializable(),
        "selection_commitment": selection.serializable(),
        "comparison": comparison,
        "nomination": nomination,
        "selection_authority": q["selection_authority"],
        "execution_authority": "NONE",
        "deficit_delta": len(m.epistemic_deficits.records) - before_deficits,
        "intent_delta": len(m.action_closure.intents) - before_intents,
        "execution_delta": len(m.action_closure.executions) - before_exec,
    }


def run_symmetric() -> dict:
    td, m, calls, opportunities, comparison, selection = _surface(False)
    try:
        result = persist_and_nominate_selected_current_opportunity(m, opportunities)
        assert result["status"] == "ABSTAIN", result
        assert result["reason"] == "WORST_RESIDUAL_PRESSURE_TIE", result
        assert result["deficit_delta"] == result["intent_delta"] == result["execution_delta"] == 0, result
        assert calls == [], calls
        return {"status": "PASS", "result": result, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_asymmetric() -> dict:
    td, m, calls, opportunities, comparison, selection = _surface(True)
    try:
        result = persist_and_nominate_selected_current_opportunity(m, opportunities)
        assert result["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", result
        assert result["selected_probe_action_id"] == "P2", result
        assert result["deficit_delta"] == 1 and result["intent_delta"] == 1 and result["execution_delta"] == 0, result
        assert result["nomination"]["status"] == "ACTION_INTENT_NOMINATED", result
        assert result["nomination"]["intent"]["capability_id"] == "P2", result
        assert calls == [], calls
        return {"status": "PASS", "result": result, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_value_drift_before_selection() -> dict:
    td, m, calls, opportunities, comparison, selection = _surface(True)
    try:
        m.observe_value_state("V", 5.0)
        fresh = enumerate_opportunities(m)
        result = persist_and_nominate_selected_current_opportunity(m, fresh)
        assert result["status"] == "ABSTAIN", result
        assert result["deficit_delta"] == result["intent_delta"] == result["execution_delta"] == 0, result
        assert calls == [], calls
        return {"status": "PASS", "fresh_surface_status": fresh.get("status"), "result": result, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2024() -> dict:
    return {
        "status": "PASS",
        "symmetric": run_symmetric(),
        "asymmetric": run_asymmetric(),
        "value_drift_before_selection": run_value_drift_before_selection(),
        "new_scheduler_required": "NO",
        "persistent_opportunity_registry_required": "NO",
        "execution_authority": "NONE",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2024(), indent=2, sort_keys=True, default=str))
