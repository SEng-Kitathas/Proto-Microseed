from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.capability_admission import ExternalCapabilityQualifier
from microseed.development.epistemic_action import derive_current_epistemic_effect_action_tokens
from scratch.ms2000_same_identity_capability_requalification import _effect, _fresh_support
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2036_full_frame_bound_pareto_research import _fixture, _p2_dominates_effects


LARGE_IDS = tuple(f"LARGE-{i:03d}" for i in range(94))
CHAIN_IDS = LARGE_IDS[:10]


def _add_large_effect_alphabet(ms) -> None:
    for i, cid in enumerate(LARGE_IDS):
        deps = () if i == 0 or i >= 10 else (LARGE_IDS[i - 1],)
        ms.register_capability(_effect(cid, deps))


def _tokens(ms) -> tuple[str, ...]:
    return derive_current_epistemic_effect_action_tokens(capabilities=ms.capabilities, obligation=act_ob())


def _selection(ms) -> dict:
    return ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob())


def _qualifier(ms, prefix: str):
    hsp = ExternalCapabilityQualifier(ms.evidence, qualifier_id=f"{prefix}-HSP")
    def ticket(cid: str):
        support = _fresh_support(ms, f"{prefix}-SUPPORT-{cid}")
        return hsp.requalify(
            ms.capabilities.contracts[cid],
            stale_epoch=ms.capabilities.epochs[cid],
            qualification_evidence=(support,),
        )
    return ticket


def run_unrelated_chain_cycle() -> dict:
    td, ms, calls, *_ = _fixture(_p2_dominates_effects())
    try:
        _add_large_effect_alphabet(ms)
        before_tokens = _tokens(ms)
        before_selection = _selection(ms)
        assert len(before_tokens) == 100, len(before_tokens)
        assert before_selection["status"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", before_selection
        assert before_selection["selected_probe_action_id"] == "P2"
        signatures = {cid: ms.capabilities.contracts[cid].computed_signature_sha256() for cid in CHAIN_IDS}
        authorities = {cid: ms.capabilities.contracts[cid].authority.value for cid in CHAIN_IDS}

        stale = ms.change_capability_dependency(CHAIN_IDS[0], reason="MS2042-LARGE-BRANCH-ROOT-DRIFT")
        during_tokens = _tokens(ms)
        during_selection = _selection(ms)
        assert stale == set(CHAIN_IDS), stale
        assert len(during_tokens) == 90, len(during_tokens)
        assert during_selection["status"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", during_selection
        assert during_selection["selected_probe_action_id"] == "P2"

        make_ticket = _qualifier(ms, "MS2042-CHAIN")
        tickets = {cid: make_ticket(cid) for cid in CHAIN_IDS}
        ahead_error = None
        try:
            ms.requalify_capability(tickets[CHAIN_IDS[1]])
        except ValueError as exc:
            ahead_error = str(exc)
        assert ahead_error and ahead_error.startswith(f"CAPABILITY_REACTIVATION_DEPENDENCY_NOT_CURRENT:{CHAIN_IDS[0]}:"), ahead_error

        requalified = []
        for cid in CHAIN_IDS:
            ms.requalify_capability(tickets[cid])
            requalified.append(cid)
            assert ms.capabilities.is_current(cid)
            if cid != CHAIN_IDS[-1]:
                next_id = CHAIN_IDS[CHAIN_IDS.index(cid) + 1]
                assert not ms.capabilities.is_current(next_id)

        after_tokens = _tokens(ms)
        after_selection = _selection(ms)
        assert len(after_tokens) == 100, len(after_tokens)
        assert after_selection["status"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", after_selection
        assert after_selection["selected_probe_action_id"] == "P2"
        assert {cid: ms.capabilities.contracts[cid].computed_signature_sha256() for cid in CHAIN_IDS} == signatures
        assert {cid: ms.capabilities.contracts[cid].authority.value for cid in CHAIN_IDS} == authorities
        events = [e for e in ms.store.events() if e["kind"] == "CAPABILITY_REQUALIFIED" and e["payload"]["capability_id"] in CHAIN_IDS]
        assert [e["payload"]["capability_id"] for e in events] == list(CHAIN_IDS)
        assert all(e["payload"]["authority_gain"] == "NONE" for e in events)
        assert all(e["payload"]["dependent_auto_reactivation"] == "NONE" for e in events)
        assert calls == []
        return {
            "status": "PASS",
            "registered_capability_count": len(ms.capabilities.contracts),
            "before_effect_count": len(before_tokens),
            "during_effect_count": len(during_tokens),
            "after_effect_count": len(after_tokens),
            "stale_count": len(stale),
            "stale_ids": sorted(stale),
            "dependent_before_root": ahead_error,
            "requalified_in_order": requalified,
            "selection_before": before_selection["status"],
            "selection_during": during_selection["status"],
            "selection_after": after_selection["status"],
            "selected_probe_before_after": [before_selection["selected_probe_action_id"], after_selection["selected_probe_action_id"]],
            "same_identity_signatures_preserved": True,
            "authority_gain": "NONE",
            "dependent_auto_reactivation": "NONE",
            "new_manager_required": "NO",
            "handler_calls": list(calls),
        }
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_critical_p2_requalification_boundary() -> dict:
    td, ms, calls, *_ = _fixture(_p2_dominates_effects())
    try:
        _add_large_effect_alphabet(ms)
        before_tokens = _tokens(ms)
        before_selection = _selection(ms)
        assert len(before_tokens) == 100
        assert before_selection["selected_probe_action_id"] == "P2"
        original_signatures = {cid: ms.capabilities.contracts[cid].computed_signature_sha256() for cid in ("P2", "FEAS-P2")}

        stale = ms.change_capability_dependency("P2", reason="MS2042-P2-DRIFT")
        assert stale == {"P2", "FEAS-P2"}, stale
        during_tokens = _tokens(ms)
        during_selection = _selection(ms)
        assert len(during_tokens) == 99
        assert during_selection["status"] == "NO_CURRENT_FULL_FRAME_CROSS_DEFICIT_SELECTION_REQUIRED", during_selection
        assert tuple(during_selection["probe_action_ids"]) == ("P4",)

        make_ticket = _qualifier(ms, "MS2042-P2")
        p2_ticket = make_ticket("P2")
        feas_ticket = make_ticket("FEAS-P2")
        ms.requalify_capability(p2_ticket)
        assert ms.capabilities.is_current("P2")
        assert not ms.capabilities.is_current("FEAS-P2")
        ms.requalify_capability(feas_ticket)
        assert ms.capabilities.is_current("FEAS-P2")

        after_tokens = _tokens(ms)
        after_selection = _selection(ms)
        assert len(after_tokens) == 100
        assert {cid: ms.capabilities.contracts[cid].computed_signature_sha256() for cid in original_signatures} == original_signatures
        # Capability currentness has recovered, but old relation/projection evidence bound
        # to the pre-drift capability epoch must not silently reauthorize itself.
        assert after_selection["status"] == "NO_CURRENT_FULL_FRAME_CROSS_DEFICIT_SELECTION_REQUIRED", after_selection
        assert tuple(after_selection["probe_action_ids"]) == ("P4",)
        assert calls == []
        return {
            "status": "PASS_BOUNDARY",
            "before_effect_count": len(before_tokens),
            "during_effect_count": len(during_tokens),
            "after_effect_count": len(after_tokens),
            "stale_ids": sorted(stale),
            "p2_epoch_after_requalification": ms.capabilities.epochs["P2"],
            "feas_p2_epoch_after_requalification": ms.capabilities.epochs["FEAS-P2"],
            "selection_before": before_selection["status"],
            "selection_during": during_selection["status"],
            "selection_after_requalification": after_selection["status"],
            "same_identity_signatures_preserved": True,
            "derived_relational_evidence_auto_requalified": "NO",
            "handler_calls": list(calls),
        }
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_ms2042() -> dict:
    return {
        "status": "MODERN_LARGE_N_CAPABILITY_CYCLE_EARNED",
        "unrelated_chain": run_unrelated_chain_cycle(),
        "critical_p2_boundary": run_critical_p2_requalification_boundary(),
        "earned": "MODERN_DESCENDANT_CAN_COMPLETE_A_100_EFFECT_CAPABILITY_INVALIDATION_AND_SAME_IDENTITY_REQUALIFICATION_CYCLE_WITH_CURRENT_FULL_FRAME_REFERENT_SELECTION_CO_PRESENT_WITHOUT_A_NEW_LIFECYCLE_MANAGER",
        "boundary": "CAPABILITY_REQUALIFICATION_CURRENTNESS != DERIVED_RELATIONAL_EVIDENCE_REQUALIFICATION",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2042(), indent=2, sort_keys=True, default=str))
