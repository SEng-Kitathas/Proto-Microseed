from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Authority, EpistemicStatus, QualificationState, ValueVariableContract
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_priority import (
    derive_regulatory_decision_bearing_commitment,
    derive_strict_same_value_cross_deficit_selection_commitment,
)
from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed import FeasibilityState
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface
from tests.embodiment.test_ms1533_multi_pressure_bridge import VALUES, _observe, _seeded
from tests.embodiment.test_ms1477_integration import make_ms, setup


def _other_value(value_id: str = "W") -> ValueVariableContract:
    return ValueVariableContract(
        value_id,
        "opaque-other-regulatory-coordinate",
        0.0,
        10.0,
        (value_id.lower() * 64)[:64],
        Authority.DERIVED_READ_ONLY,
        ("MS2032",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("MS2032_CURRENT_SECOND_VALUE_COORDINATE",),
    )


def run_owned_opportunity_is_single_coordinate() -> dict:
    td, m, calls, _surface_rows, _comparison, _selection = _surface(True)
    try:
        m.register_value_variable(_other_value("W"))
        m.observe_value_state("W", -1.0)
        opportunities = m.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
        assert opportunities["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", opportunities
        assert len(opportunities["opportunities"]) >= 2, opportunities
        consequence_value_ids = tuple(str(row["consequence"]["value_id"]) for row in opportunities["opportunities"])
        assert set(consequence_value_ids) == {"V"}, consequence_value_ids
        assert m.values.is_current("V") and m.values.is_current("W")
        for row in opportunities["opportunities"]:
            consequence = row["consequence"]
            assert consequence["status"] == "CURRENT_SAME_VALUE_REGULATORY_CONSEQUENCE_SURFACE"
            assert "multi_value_residual_vector" not in consequence
            assert "coordinate_residuals" not in consequence
        assert calls == [], calls
        return {
            "status": "BLOCKER_REPRODUCED",
            "current_value_ids": ["V", "W"],
            "opportunity_consequence_value_ids": list(consequence_value_ids),
            "complete_cross_value_opportunity_vector_owned": "NO",
            "handler_calls": list(calls),
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_same_value_selector_refuses_cross_value_rows() -> dict:
    rows = (
        {
            "deficit_id": "D-V",
            "probe_action_id": "P2",
            "value_id": "V",
            "value_epoch": 0,
            "current_value": -1.0,
            "worst_residual_pressure": 0.0,
            "premise_ids": ("D-V", "V@0"),
        },
        {
            "deficit_id": "D-W",
            "probe_action_id": "P4",
            "value_id": "W",
            "value_epoch": 0,
            "current_value": -1.0,
            "worst_residual_pressure": 0.5,
            "premise_ids": ("D-W", "W@0"),
        },
    )
    commitment = derive_strict_same_value_cross_deficit_selection_commitment(rows)
    assert not commitment.licenses_yes(), commitment.serializable()
    assert commitment.reason == "EXACT_SAME_VALUE_COORDINATE_REQUIRED", commitment.serializable()
    assert dict(commitment.qualifiers)["selection_authority"] == "NONE"
    return {
        "status": "BLOCKER_REPRODUCED",
        "commitment": commitment.serializable(),
        "cross_value_selection_authority": "NONE",
    }


def run_multi_value_surface_is_immediate_action_effect_not_epistemic_value_of_information() -> dict:
    td, m = _seeded()
    try:
        _observe(m, energy=3.2, thermal=5.0, integrity=6.0)
        result = m.derive_multi_value_action_licenses(VALUES)
        assert result["status"] == "UNKNOWN_ACTION_SELECTION", result
        assert result["overall_commitment"]["reason"] == "MULTIPLE_LAWFUL_ACTIONS_NO_RANKING_AUTHORITY", result
        assert len(result["licensed_action_ids"]) >= 2, result
        assert result["effect_witnesses"], result
        # The surface owns current action/value effect evidence. It does not carry
        # epistemic-deficit identity or information-conditioned downstream rehearsal.
        serialized = json.dumps(result, sort_keys=True, default=str)
        assert "deficit_id" not in serialized
        assert "information_commitment" not in serialized
        assert "decision_bearing_commitment_id" not in serialized
        assert "proposal_digests" not in serialized
        return {
            "status": "BLOCKER_REPRODUCED",
            "license_status": result["status"],
            "reason": result["overall_commitment"]["reason"],
            "licensed_action_ids": list(result["licensed_action_ids"]),
            "immediate_action_effect_surface_owned": "YES",
            "information_conditioned_multi_value_consequence_owned": "NO",
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_cross_value_rehearsal_laundering_remains_rejected() -> dict:
    td, m = make_ms()
    try:
        setup(m)
        m.register_value_variable(_other_value("W"))
        m.observe_value_state("W", -1.0)
        m.observe_value_state("V", -11.0)
        m.append_evidence("MS2032-U", {"kind": "UNKNOWN"}, EpistemicStatus.UNKNOWN_INCOMPLETE)
        m.record_action_limited_unknown(
            deficit_id="MS2032-D-V",
            question_key="MS2032-Q-V",
            hypothesis_digest_sha256="a" * 64,
            unknown_evidence_id="MS2032-U",
            missing_discriminator_signature_sha256="d" * 64,
            premise_anchors=(EpistemicCurrentnessAnchor("VALUE", "V", 0),),
        )

        def relation(effect: float, value_id: str) -> RehearsalTransitionRelation:
            return RehearsalTransitionRelation(
                "S0", "A", "S1", effect, 8, 1.0, ("E",), 0, ("F", 0), ("E", 0),
                value_epoch=(value_id, 0),
            )

        out = derive_regulatory_decision_bearing_commitment(
            deficit=m.epistemic_deficits.records["MS2032-D-V"],
            values=m.values,
            relation_sets=(
                {("S0", "A"): relation(1.0, "V")},
                {("S0", "A"): relation(-1.0, "W")},
            ),
            options=(RecruitmentOption("A", FeasibilityState.FEASIBLE),),
            start_state_id="S0",
            current_capability_epochs={"A": 0},
            current_frame_epochs={"F": 0},
            current_episode_epochs={"E": 0},
        )
        assert not out.licenses_yes(), out.serializable()
        assert out.reason == "RELATIONAL_ALTERNATIVE_VALUE_COORDINATE_MISMATCH:W", out.serializable()
        return {
            "status": "BLOCKER_REPRODUCED",
            "commitment": out.serializable(),
            "cross_value_relation_laundering": "REJECTED",
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2032() -> dict:
    return {
        "status": "SUBSTANTIVE_BLOCKER_REPRODUCED",
        "owned_opportunity_single_coordinate": run_owned_opportunity_is_single_coordinate(),
        "same_value_selector_cross_value_refusal": run_same_value_selector_refuses_cross_value_rows(),
        "multi_value_immediate_effect_boundary": run_multi_value_surface_is_immediate_action_effect_not_epistemic_value_of_information(),
        "cross_value_laundering_rejected": run_cross_value_rehearsal_laundering_remains_rejected(),
        "blocker": "SINGLE_VALUE_EPISTEMIC_CONSEQUENCE + MULTI_VALUE_IMMEDIATE_ACTION_EFFECTS != MULTI_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR",
        "pareto_comparison_surface_owned": "NO",
        "cross_value_selection_authority": "NONE",
        "new_scheduler_required": "NO_EVIDENCE",
        "scalar_utility_required": "NO_EVIDENCE",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2032(), indent=2, sort_keys=True, default=str))
