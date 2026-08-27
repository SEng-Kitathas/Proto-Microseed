from __future__ import annotations

from pathlib import Path
import hashlib
import tempfile

from microseed import (
    Microseed, Authority, CapabilityContract, FeasibilityState,
    QualificationState, ValueVariableContract,
)
from microseed.development.recruitment import RecruitmentOption


def make_ms():
    td = tempfile.TemporaryDirectory(prefix="microseed-ms1002-")
    return td, Microseed(Path(td.name))


def cap(cid: str, *, deps=(), scope=None):
    return CapabilityContract(
        cid, "opaque-child-capability", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS978-1002-TEST",), "CURRENT", {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
        operational_scope_id=scope,
    )


def value_contract(vid="V"):
    return ValueVariableContract(
        value_id=vid, purpose="opaque-regulatory-variable", viable_low=.4, viable_high=.8,
        signature_sha256=hashlib.sha256(f"{vid}:.4:.8".encode()).hexdigest(),
        authority=Authority.DERIVED_READ_ONLY, lineage=("MS953-977",), currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE", "SUPPLIED_VIABILITY_INTERVAL"),
        invariants=("NO_SEMANTIC_GOAL_AUTHORITY",),
    )


def test_current_feasible_recruitment_proposal_composes_without_authority_gain():
    td, ms = make_ms()
    try:
        ms.register_capability(cap("A"))
        ms.register_capability(cap("B"))
        p = ms.nominate_recruitment(
            (
                RecruitmentOption("A", FeasibilityState.FEASIBLE, predicted_effect=(.5, -.2), local_cost=.1, resource_tags=("rA",)),
                RecruitmentOption("B", FeasibilityState.FEASIBLE, predicted_effect=(.4, .3), local_cost=.2, resource_tags=("rB",)),
            ),
            ("A", "B"),
            assistance_ancestry=("SUPPLIED_ROLE_TOPOLOGY", "RESEARCH_ONLY_FORWARD_MODEL"),
        )
        assert p.authority == Authority.MODEL_OUTPUT_ONLY.value
        assert p.semantic_goal_authority == "NONE"
        assert p.role_topology_origin == "SUPPLIED_AND_PROVENANCED"
        assert ms.recruitment_status(p.proposal_id)["status"] == "CURRENT"
        result = ms.compose_recruitment(p.proposal_id)
        assert result["status"] == "COMPOSED_EPHEMERAL"
        assert result["proposal_authority"] == Authority.MODEL_OUTPUT_ONLY.value
        assert result["semantic_goal_authority"] == "NONE"
        assert result["composition_authority"] == Authority.DERIVED_READ_ONLY.value
    finally:
        td.cleanup()


def test_refused_child_cannot_be_selected_by_parent_recruitment():
    td, ms = make_ms()
    try:
        ms.register_capability(cap("A"))
        try:
            ms.nominate_recruitment((RecruitmentOption("A", FeasibilityState.REFUSED),), ("A",))
        except ValueError as exc:
            assert "RECRUITMENT_NOT_FEASIBLE:A:REFUSED" in str(exc)
        else:
            raise AssertionError("parent proposal overrode subordinate refusal")
    finally:
        td.cleanup()


def test_unknown_child_feasibility_cannot_be_silently_treated_as_feasible():
    td, ms = make_ms()
    try:
        ms.register_capability(cap("A"))
        try:
            ms.nominate_recruitment((RecruitmentOption("A", FeasibilityState.UNKNOWN),), ("A",))
        except ValueError as exc:
            assert "RECRUITMENT_NOT_FEASIBLE:A:UNKNOWN" in str(exc)
        else:
            raise AssertionError("UNKNOWN child feasibility was converted into permission")
    finally:
        td.cleanup()


def test_joint_resource_conflict_is_rejected_even_when_children_are_individually_feasible():
    td, ms = make_ms()
    try:
        ms.register_capability(cap("A"))
        ms.register_capability(cap("B"))
        options = (
            RecruitmentOption("A", FeasibilityState.FEASIBLE, resource_tags=("shared",)),
            RecruitmentOption("B", FeasibilityState.FEASIBLE, resource_tags=("shared",)),
        )
        try:
            ms.nominate_recruitment(options, ("A", "B"))
        except ValueError as exc:
            assert "RECRUITMENT_RESOURCE_CONFLICT" in str(exc)
        else:
            raise AssertionError("locally feasible children were accepted despite joint conflict")
    finally:
        td.cleanup()


def test_child_capability_epoch_drift_makes_recruitment_unknown_and_unexecutable():
    td, ms = make_ms()
    try:
        ms.register_capability(cap("A"))
        p = ms.nominate_recruitment((RecruitmentOption("A", FeasibilityState.FEASIBLE),), ("A",))
        assert ms.recruitment_status(p.proposal_id)["status"] == "CURRENT"
        ms.change_capability_dependency("A", reason="CHILD_POLICY_DRIFT")
        st = ms.recruitment_status(p.proposal_id)
        assert st["status"] == "UNKNOWN_INCOMPLETE"
        assert "RECRUITMENT_CAPABILITY_NOT_CURRENT:A" in st["reason"] or "RECRUITMENT_CAPABILITY_EPOCH_DRIFT:A" in st["reason"]
        result = ms.compose_recruitment(p.proposal_id)
        assert result["status"] == "UNKNOWN_INCOMPLETE"
        assert result["plan"] == []
        assert result["composition_authority"] == Authority.NONE.value
    finally:
        td.cleanup()


def test_value_epoch_drift_makes_value_bound_recruitment_unknown():
    td, ms = make_ms()
    try:
        ms.register_capability(cap("A"))
        ms.register_value_variable(value_contract())
        p = ms.nominate_recruitment(
            (RecruitmentOption("A", FeasibilityState.FEASIBLE),), ("A",), value_ids=("V",)
        )
        assert ms.recruitment_status(p.proposal_id)["status"] == "CURRENT"
        ms.change_value_variable("V", reason="VALUE_PRIOR_CHANGED")
        st = ms.recruitment_status(p.proposal_id)
        assert st["status"] == "UNKNOWN_INCOMPLETE"
        assert st["reason"] == "RECRUITMENT_VALUE_EPOCH_DRIFT:V"
    finally:
        td.cleanup()


def test_status_preserves_topology_assistance_ceiling_and_ms1003_hard_stop():
    td, ms = make_ms()
    try:
        s = ms.status()
        assert s["research_terminal_ms"] >= 1152
        assert s["integration_evidence_through_ms"] >= 1152
        assert s["next_ms"] >= 1203
        assert s["next_ms"] >= 1278
        assert s["frontier"].startswith("ATTN-MS")
        assert "ENDOGENOUS_PAIRWISE_CONSTRUCTOR_RESEARCH_ONLY" in s["hierarchy_topology"]
        assert s["topology_identity_authority"] == "NONE"
        assert "PLANNER_RESEARCH_ONLY" in s["hierarchical_recruitment"]
        assert s["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
        assert s["identity_claim"] == "NOT_QUALIFIED"
    finally:
        td.cleanup()


def test_unqualified_topology_origin_cannot_be_claimed_by_model_output():
    td, ms = make_ms()
    try:
        ms.register_capability(cap("A"))
        try:
            ms.nominate_recruitment(
                (RecruitmentOption("A", FeasibilityState.FEASIBLE),), ("A",),
                role_topology_origin="ENDOGENOUS_DISCOVERY",
            )
        except ValueError as exc:
            assert "RECRUITMENT_TOPOLOGY_ORIGIN_UNQUALIFIED" in str(exc)
        else:
            raise AssertionError("model output claimed endogenous topology authority")
    finally:
        td.cleanup()


def test_duplicate_child_option_handles_are_rejected_as_ambiguous():
    td, ms = make_ms()
    try:
        ms.register_capability(cap("A"))
        try:
            ms.nominate_recruitment(
                (
                    RecruitmentOption("A", FeasibilityState.FEASIBLE, predicted_effect=(1.0,)),
                    RecruitmentOption("A", FeasibilityState.REFUSED, predicted_effect=(0.0,)),
                ),
                ("A",),
            )
        except ValueError as exc:
            assert "RECRUITMENT_DUPLICATE_OPTION_CAPABILITY" in str(exc)
        else:
            raise AssertionError("ambiguous duplicate child options were accepted")
    finally:
        td.cleanup()


def test_recruitment_registry_rejects_authority_escalation_even_if_bypassing_entity_constructor():
    from microseed.development.recruitment import RecruitmentProposal
    td, ms = make_ms()
    try:
        forged = RecruitmentProposal(
            proposal_id="forged",
            options=(),
            selected_capability_ids=("A",),
            capability_epochs=(("A", 0),),
            assistance_ancestry=("SUPPLIED_RECRUITMENT_TOPOLOGY",),
            authority=Authority.EFFECT.value,
        )
        try:
            ms.recruitments.add(forged)
        except ValueError as exc:
            assert "RECRUITMENT_AUTHORITY_ESCALATION" in str(exc)
        else:
            raise AssertionError("forged recruitment authority was accepted")
    finally:
        td.cleanup()
