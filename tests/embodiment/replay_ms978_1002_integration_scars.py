from __future__ import annotations

import hashlib
import json
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from microseed import (
    Microseed, Authority, CapabilityContract, FeasibilityState,
    QualificationState, ValueVariableContract,
)
from microseed.development.recruitment import RecruitmentOption


def cap(cid: str):
    return CapabilityContract(
        cid, "opaque-child", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS978-1002-REPLAY",), "CURRENT", {},
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def value_contract():
    return ValueVariableContract(
        value_id="V", purpose="opaque-regulatory-variable", viable_low=.4, viable_high=.8,
        signature_sha256=hashlib.sha256(b"MS1002-V").hexdigest(),
        authority=Authority.DERIVED_READ_ONLY, lineage=("MS953-977",), currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE",),
        invariants=("NO_SEMANTIC_GOAL_AUTHORITY",),
    )


def main():
    with tempfile.TemporaryDirectory(prefix="ms978-1002-replay-") as td:
        ms = Microseed(Path(td))
        ms.register_capability(cap("A")); ms.register_capability(cap("B"))
        ms.register_value_variable(value_contract())

        p = ms.nominate_recruitment(
            (
                RecruitmentOption("A", FeasibilityState.FEASIBLE, predicted_effect=(.8, -.1), local_cost=.2, resource_tags=("ra",), model_evidence_ids=("MODEL-A",)),
                RecruitmentOption("B", FeasibilityState.FEASIBLE, predicted_effect=(.3, .7), local_cost=.1, resource_tags=("rb",), model_evidence_ids=("MODEL-B",)),
            ),
            ("A", "B"), value_ids=("V",),
            assistance_ancestry=("SUPPLIED_ROLE_TOPOLOGY", "RESEARCH_ONLY_FORWARD_MODEL", "SUPPLIED_CONTEXT_REGIME"),
        )
        current = ms.recruitment_status(p.proposal_id)
        composed = ms.compose_recruitment(p.proposal_id)

        refusal_rejected = False
        try:
            ms.nominate_recruitment((RecruitmentOption("A", FeasibilityState.REFUSED),), ("A",))
        except ValueError as exc:
            refusal_rejected = "RECRUITMENT_NOT_FEASIBLE:A:REFUSED" in str(exc)

        unknown_rejected = False
        try:
            ms.nominate_recruitment((RecruitmentOption("A", FeasibilityState.UNKNOWN),), ("A",))
        except ValueError as exc:
            unknown_rejected = "RECRUITMENT_NOT_FEASIBLE:A:UNKNOWN" in str(exc)

        conflict_rejected = False
        try:
            ms.nominate_recruitment(
                (
                    RecruitmentOption("A", FeasibilityState.FEASIBLE, resource_tags=("shared",)),
                    RecruitmentOption("B", FeasibilityState.FEASIBLE, resource_tags=("shared",)),
                ), ("A", "B"),
            )
        except ValueError as exc:
            conflict_rejected = "RECRUITMENT_RESOURCE_CONFLICT" in str(exc)

        topology_spoof_rejected = False
        try:
            ms.nominate_recruitment(
                (RecruitmentOption("A", FeasibilityState.FEASIBLE),), ("A",),
                role_topology_origin="ENDOGENOUS_DISCOVERY",
            )
        except ValueError as exc:
            topology_spoof_rejected = "RECRUITMENT_TOPOLOGY_ORIGIN_UNQUALIFIED" in str(exc)

        ms.change_capability_dependency("A", reason="MS1002_REPLAY_CHILD_DRIFT")
        after_child_drift = ms.recruitment_status(p.proposal_id)
        after_child_compose = ms.compose_recruitment(p.proposal_id)

        # Independent value-currentness specimen, so child drift does not confound it.
        ms.register_capability(cap("C"))
        pv = ms.nominate_recruitment(
            (RecruitmentOption("C", FeasibilityState.FEASIBLE),), ("C",), value_ids=("V",),
            assistance_ancestry=("SUPPLIED_ROLE_TOPOLOGY",),
        )
        ms.change_value_variable("V", reason="MS1002_REPLAY_VALUE_DRIFT")
        after_value_drift = ms.recruitment_status(pv.proposal_id)

        status = ms.status()
        checks = {
            "current_feasible_proposal_is_only_model_output": current["status"] == "CURRENT" and p.authority == Authority.MODEL_OUTPUT_ONLY.value,
            "semantic_goal_authority_not_created": p.semantic_goal_authority == "NONE" and composed["semantic_goal_authority"] == "NONE",
            "qualified_children_can_be_composed_without_authority_gain": composed["status"] == "COMPOSED_EPHEMERAL" and composed["composition_authority"] == Authority.DERIVED_READ_ONLY.value,
            "role_topology_remains_supplied": p.role_topology_origin == "SUPPLIED_AND_PROVENANCED",
            "child_refusal_is_not_effect_or_permission": refusal_rejected,
            "unknown_child_feasibility_is_not_permission": unknown_rejected,
            "locally_feasible_children_do_not_bypass_joint_resource_conflict": conflict_rejected,
            "model_output_cannot_claim_endogenous_topology_origin": topology_spoof_rejected,
            "child_epoch_drift_invalidates_parent_recruitment_model": after_child_drift["status"] == "UNKNOWN_INCOMPLETE",
            "stale_recruitment_cannot_execute": after_child_compose["status"] == "UNKNOWN_INCOMPLETE" and after_child_compose["plan"] == [],
            "value_premise_drift_invalidates_recruitment": after_value_drift["status"] == "UNKNOWN_INCOMPLETE" and after_value_drift["reason"] == "RECRUITMENT_VALUE_EPOCH_DRIFT:V",
            "entity_has_no_recruitment_self_qualification": not hasattr(ms, "qualify_recruitment"),
            "endogenous_topology_not_promoted": "ENDOGENOUS_PAIRWISE_CONSTRUCTOR_RESEARCH_ONLY" in status["hierarchy_topology"] and status["topology_identity_authority"] == "NONE",
            "persistent_selfhood_not_promoted": status["identity_claim"] == "NOT_QUALIFIED",
            "prelingual_hard_stop": status["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE" and status["next_ms"] >= 1203 and status.get(f"ms{status['next_ms']}_started") is False,
            "selected_cross_family_frontier": status['research_terminal_ms']>=1252 and status['frontier'].startswith('ATTN-MS'),
        }
        out = {
            "schema": "microseed.ms978-1002-maindev-replay.v0.8",
            "proposal": p.serializable(),
            "current_status": current,
            "composition": composed,
            "after_child_drift": after_child_drift,
            "after_value_drift": after_value_drift,
            "status": status,
            "checks": checks,
            "all_pass": all(checks.values()),
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
