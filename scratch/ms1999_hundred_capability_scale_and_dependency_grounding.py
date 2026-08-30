from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from microseed import (
    Authority,
    CapabilityContract,
    EpistemicStatus,
    Observation,
    QualificationState,
    QueryObligation,
)
from microseed.development.capability_admission import CapabilityCandidate, ExternalCapabilityQualifier
from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext,
    derive_current_epistemic_effect_action_tokens,
    derive_current_generated_epistemic_program_candidates,
)
from microseed.runtime.capabilities import CapabilityRegistry
from scratch.ms1996_endogenous_program_caller_choice_elimination import (
    FALLBACK,
    MAIN,
    OBLIGATION,
    _add_chain,
    _add_shared_relation,
    _close,
    _register_effect_and_feasibility,
    _rel,
)
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture


DISTRACTORS = tuple(f"D-{i:03d}" for i in range(94))
ADDED_EFFECT_ALPHABET = MAIN + (FALLBACK,) + DISTRACTORS
FIXTURE_EFFECTS = ("A", "B")
EXPECTED_EFFECT_ALPHABET = tuple(sorted(set(ADDED_EFFECT_ALPHABET + FIXTURE_EFFECTS)))
assert len(ADDED_EFFECT_ALPHABET) == 98
assert len(EXPECTED_EFFECT_ALPHABET) == 100


def _build_hundred_effect_world(order: tuple[str, ...] = ("P1", "P2", "N1", "N2")):
    td, m, calls, _, _, _ = fixture()
    for cid in ADDED_EFFECT_ALPHABET:
        _register_effect_and_feasibility(m, calls, cid)

    rows = {
        "P1": (+1.0, "u"),
        "P2": (+1.0, "u"),
        "N1": (-1.0, "v"),
        "N2": (-1.0, "v"),
    }
    for prefix in order:
        effect, terminal = rows[prefix]
        _add_chain(m, prefix, effect, terminal)

    _add_shared_relation(m, relation_id="R-MS1999-FALLBACK", action=FALLBACK, start="s0", end="sf", effect=0.0)
    m.observe_opaque_control_state(
        Observation("CS-MS1999", "EXT", "opaque-control", "s0", authority=Authority.OBSERVATION_ONLY),
        evidence_id="E-CS-MS1999",
    )
    return td, m, calls


def run_hundred_effect_arm(order: tuple[str, ...] = ("P1", "P2", "N1", "N2")) -> dict[str, object]:
    td, m, calls = _build_hundred_effect_world(order)
    try:
        before_intents = len(m.action_closure.intents)
        before_exec = len(m.action_closure.executions)
        t0 = time.perf_counter()
        generated = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=OBLIGATION,
            max_nodes=256,
        )
        generation_ms = (time.perf_counter() - t0) * 1000.0
        assert generated["status"] == "REPRESENTED_INFORMATIVE_PROGRAMS_FOUND", generated
        tokens = tuple(generated["generator_tokens"])
        assert len(tokens) == 100, len(tokens)
        assert set(tokens) == set(EXPECTED_EFFECT_ALPHABET)
        assert MAIN in tuple(tuple(x) for x in generated["programs"])
        assert generated["generator_surface_authority"] == "CURRENT_CAPABILITY_CONTRACTS_ONLY"
        assert generated["truth_authority"] == generated["execution_authority"] == "NONE"

        t1 = time.perf_counter()
        result = m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(
            deficit_id="D",
            obligation=OBLIGATION,
            max_nodes=256,
        )
        arbitration_ms = (time.perf_counter() - t1) * 1000.0
        assert result["status"] == "EPISTEMIC_TRIAL_INSTANTIATED", result
        trial = result["trial"]
        assert trial.steps == MAIN
        assert result["priority"]["commitment"] == "YES"
        assert result["information"]["commitment"] == "YES"
        assert result["execution_authority"] == "NONE"
        assert calls == []
        assert len(m.action_closure.intents) == before_intents
        assert len(m.action_closure.executions) == before_exec
        chosen = next(c for c in generated["candidates"] if c.steps == MAIN)

        budget = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=OBLIGATION,
            max_nodes=1,
        )
        assert budget["status"] == "SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED", budget
        assert budget["candidates"] == ()

        stale = m.change_capability_dependency(MAIN[2], reason="MS1999-TARGET-PRIMITIVE-DRIFT")
        assert stale == {MAIN[2], "FEAS-" + MAIN[2]}, stale
        stale_generated = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=OBLIGATION,
            max_nodes=256,
        )
        assert MAIN not in {tuple(x) for x in stale_generated.get("programs", ())}
        stale_admitted = m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(
            deficit_id="D",
            obligation=OBLIGATION,
            max_nodes=256,
        )
        assert stale_admitted["status"] == "ABSTAIN", stale_admitted
        assert stale_admitted["reason"] == "CURRENT_GENERATOR_TRANSITION_UNREPRESENTED"

        recovery_error = None
        same_id_candidate = CapabilityCandidate(
            candidate_id=MAIN[2],
            proposed_contract=CapabilityContract(
                MAIN[2], "opaque-primitive", {}, {}, (), (), Authority.EFFECT, ("MS1999",), "CURRENT", {},
                query_obligation_id="Q", qualification=QualificationState.CANDIDATE,
                operational_scope_id="S",
            ),
            evidence=(),
            nomination_basis="MS1999_REQUALIFICATION_PROBE",
        )
        try:
            m.nominate_capability_candidate(same_id_candidate)
        except Exception as exc:
            recovery_error = f"{type(exc).__name__}:{exc}"
        assert recovery_error and "duplicate candidate/capability" in recovery_error
        assert not hasattr(m, "requalify_capability")

        return {
            "status": "PASS_WITH_RECOVERY_BLOCKER",
            "effect_capability_count": len(EXPECTED_EFFECT_ALPHABET),
            "total_registered_capability_count": len(m.capabilities.contracts),
            "generated_program": list(trial.steps),
            "candidate_id": chosen.candidate_id,
            "candidate_sha256": chosen.digest(),
            "generator_token_count": len(tokens),
            "generation_ms": round(generation_ms, 3),
            "arbitration_ms": round(arbitration_ms, 3),
            "caller_supplied_preferred_action_or_program": "NO",
            "budget_status": budget["status"],
            "local_stale_set": sorted(stale),
            "local_stale_count": len(stale),
            "stale_admission_status": stale_admitted["status"],
            "stale_admission_reason": stale_admitted["reason"],
            "same_identity_requalification_path": "MISSING",
            "same_identity_requalification_probe": recovery_error,
            "execution_authority": "NONE",
            "truth_authority": "NONE",
        }
    finally:
        _close(td, m)


def _readonly_contract(cid: str, deps: tuple[str, ...] = ()) -> CapabilityContract:
    return CapabilityContract(
        cid,
        "scale-readonly",
        {},
        {},
        (),
        (),
        Authority.DERIVED_READ_ONLY,
        ("MS1999",),
        "CURRENT",
        {},
        dependencies=deps,
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda _cid=cid, **_: {"ran": _cid},
    )


def _branch_registry(branches: int = 10, depth: int = 10) -> CapabilityRegistry:
    r = CapabilityRegistry()
    for b in range(branches):
        prev = None
        for d in range(depth):
            cid = f"B{b:02d}-{d:02d}"
            deps = () if prev is None else (prev,)
            r.register(_readonly_contract(cid, deps))
            prev = cid
    return r


def _shared_registry(branches: int = 10, depth: int = 10) -> CapabilityRegistry:
    r = CapabilityRegistry()
    r.register(_readonly_contract("SHARED"))
    for b in range(branches):
        prev = "SHARED"
        for d in range(depth):
            cid = f"S{b:02d}-{d:02d}"
            r.register(_readonly_contract(cid, (prev,)))
            prev = cid
    return r



def run_hundred_tie_arm() -> dict[str, object]:
    td, m, calls, _, _, _ = fixture()
    try:
        for cid in ADDED_EFFECT_ALPHABET:
            _register_effect_and_feasibility(m, calls, cid)
        m.observe_opaque_control_state(
            Observation("CS-MS1999-TIE", "EXT", "opaque-control", "s0", authority=Authority.OBSERVATION_ONLY),
            evidence_id="E-CS-MS1999-TIE",
        )
        alternate = DISTRACTORS[0]
        positive = (
            _rel("s0", MAIN[0], "s1", +1.0), _rel("s0", FALLBACK, "sf", 0.0),
            _rel("s1", MAIN[2], "u", 0.0), _rel("s1", alternate, "x", 0.0),
        )
        negative = (
            _rel("s0", MAIN[0], "s1", -1.0), _rel("s0", FALLBACK, "sf", 0.0),
            _rel("s1", MAIN[2], "v", 0.0), _rel("s1", alternate, "y", 0.0),
        )
        dc = EpistemicDecisionBearingContext((positive, negative), ())
        generated = derive_current_generated_epistemic_program_candidates(
            decision_context=dc, start_state_id="s0", capabilities=m.capabilities,
            obligation=OBLIGATION, max_nodes=256,
        )
        assert len(generated["generator_tokens"]) == 100
        expected_a = (MAIN[0], MAIN[2])
        expected_b = (MAIN[0], alternate)
        programs = {tuple(x) for x in generated.get("programs", ())}
        assert expected_a in programs and expected_b in programs
        candidates = tuple(c for c in generated["candidates"] if c.steps in {expected_a, expected_b})
        assert len(candidates) == 2
        before_intents = len(m.action_closure.intents)
        before_exec = len(m.action_closure.executions)
        result = m.arbitrate_endogenous_epistemic_trial_candidates(
            candidates, deficit_id="D", decision_context=dc, obligation=OBLIGATION,
        )
        assert result["status"] == "MULTIPLE_CURRENT_EPISTEMIC_OPPORTUNITIES", result
        assert result["reason"] == "NO_UNIQUE_STRICT_PARTITION_REFINEMENT"
        assert result["selection_authority"] == result["execution_authority"] == result["truth_authority"] == "NONE"
        assert len(m.action_closure.intents) == before_intents
        assert len(m.action_closure.executions) == before_exec
        assert calls == []
        return {
            "status": "PASS_TIE_PRESERVED",
            "effect_capability_count": 100,
            "competing_programs": [list(expected_a), list(expected_b)],
            "arbitration_status": result["status"],
            "arbitration_reason": result["reason"],
            "selection_authority": result["selection_authority"],
            "execution_authority": result["execution_authority"],
            "truth_authority": result["truth_authority"],
            "caller_order_selection": "NO",
        }
    finally:
        _close(td, m)

def run_dependency_topology_arm() -> dict[str, object]:
    branch_root = _branch_registry()
    branch_leaf_closure = branch_root.assess_dependency_closure("B00-09")
    assert branch_leaf_closure["status"] == "CURRENT_DEPENDENCY_CLOSURE"
    assert branch_leaf_closure["visited_count"] == 10
    t0 = time.perf_counter()
    branch_stale = branch_root.invalidate("B00-00", reason="MS1999-BRANCH-ROOT")
    branch_ms = (time.perf_counter() - t0) * 1000.0
    assert len(branch_stale) == 10
    assert branch_root.assess_dependency_closure("B00-09")["status"] == "UNKNOWN_INCOMPLETE"

    leaf = _branch_registry()
    t1 = time.perf_counter()
    leaf_stale = leaf.invalidate("B00-09", reason="MS1999-LEAF")
    leaf_ms = (time.perf_counter() - t1) * 1000.0
    assert len(leaf_stale) == 1

    shared = _shared_registry()
    shared_leaf_closure = shared.assess_dependency_closure("S00-09")
    assert shared_leaf_closure["status"] == "CURRENT_DEPENDENCY_CLOSURE"
    t2 = time.perf_counter()
    shared_stale = shared.invalidate("SHARED", reason="MS1999-SHARED")
    shared_ms = (time.perf_counter() - t2) * 1000.0
    assert len(shared_stale) == 101

    # Deep-chain hostile: closure must be iterative rather than depend on Python's
    # recursion limit.  This is a traversal property, not a universal scale theorem.
    deep = CapabilityRegistry()
    prev = None
    for i in range(1500):
        cid = f"DEEP-{i:04d}"
        deep.register(_readonly_contract(cid, () if prev is None else (prev,)))
        prev = cid
    t3 = time.perf_counter()
    deep_closure = deep.assess_dependency_closure(prev)
    deep_ms = (time.perf_counter() - t3) * 1000.0
    assert deep_closure["status"] == "CURRENT_DEPENDENCY_CLOSURE"
    assert deep_closure["visited_count"] == 1500
    assert deep_closure["max_depth"] == 1500

    return {
        "status": "PASS_LOCALITY_AND_ITERATIVE_CLOSURE_ONLY",
        "branch_graph_capability_count": 100,
        "branch_leaf_dependency_closure_count": branch_leaf_closure["visited_count"],
        "branch_root_stale_count": len(branch_stale),
        "branch_root_locality_ratio_vs_global_100": 100.0 / len(branch_stale),
        "branch_root_invalidation_ms": round(branch_ms, 6),
        "leaf_stale_count": len(leaf_stale),
        "leaf_locality_ratio_vs_global_100": 100.0 / len(leaf_stale),
        "leaf_invalidation_ms": round(leaf_ms, 6),
        "shared_graph_capability_count": 101,
        "shared_leaf_dependency_closure_count": shared_leaf_closure["visited_count"],
        "shared_root_stale_count": len(shared_stale),
        "shared_root_invalidation_ms": round(shared_ms, 6),
        "deep_chain_capability_count": 1500,
        "deep_chain_closure_visited_count": deep_closure["visited_count"],
        "deep_chain_max_depth": deep_closure["max_depth"],
        "deep_chain_closure_ms": round(deep_ms, 6),
        "actual_requalification_closure": "NOT_AVAILABLE__SAME_IDENTITY_CAPABILITY_REQUALIFICATION_PATH_MISSING",
    }


def run_dependency_grounding_arm() -> dict[str, object]:
    obligation = QueryObligation("Q", "opaque")

    # Structural forward references remain legal, preserving earned deferred
    # composition.  They simply carry no executable authority until closure exists.
    missing = CapabilityRegistry()
    missing.register(_readonly_contract("MISSING-CHILD", ("NO-SUCH-DEP",)))
    missing_closure = missing.assess_dependency_closure("MISSING-CHILD")
    missing_invoke = missing.invoke("MISSING-CHILD", obligation)
    assert missing_closure["status"] == "UNKNOWN_INCOMPLETE"
    assert missing_closure["reason"] == "DEPENDENCY_NOT_REGISTERED:NO-SUCH-DEP"
    assert missing_invoke["status"] == "UNKNOWN_INCOMPLETE"
    assert missing_invoke["authority"] == "NONE"

    deferred = CapabilityRegistry()
    deferred.register(_readonly_contract("DEFERRED", ("LATER",)))
    before = deferred.invoke("DEFERRED", obligation)
    deferred.register(_readonly_contract("LATER"))
    after = deferred.invoke("DEFERRED", obligation)
    assert before["status"] == "UNKNOWN_INCOMPLETE"
    assert after["status"] == "CAPABILITY_RESULT"
    assert deferred.assess_dependency_closure("DEFERRED")["status"] == "CURRENT_DEPENDENCY_CLOSURE"

    # Cycles remain structurally representable, in accordance with the TRCH ceiling,
    # but cannot bootstrap executable currentness without a separately qualified
    # cycle-closure mechanism (none exists in the current substrate).
    cycle = CapabilityRegistry()
    cycle.register(_readonly_contract("CYCLE-A", ("CYCLE-B",)))
    cycle.register(_readonly_contract("CYCLE-B", ("CYCLE-A",)))
    cycle_a = cycle.assess_dependency_closure("CYCLE-A")
    cycle_b = cycle.assess_dependency_closure("CYCLE-B")
    assert cycle_a["status"] == cycle_b["status"] == "UNKNOWN_INCOMPLETE"
    assert cycle_a["reason"].startswith("DEPENDENCY_CYCLE_UNQUALIFIED:")
    assert cycle.invoke("CYCLE-A", obligation)["authority"] == "NONE"
    assert cycle.invoke("CYCLE-B", obligation)["authority"] == "NONE"

    td = tempfile.TemporaryDirectory(prefix="ms1999-grounding-")
    from microseed import Microseed
    m = Microseed(Path(td.name))
    try:
        # Missing declared dependency may be nominated as a proposal, but external
        # qualification cannot turn absent dependency closure into admission.
        prop = m.append_evidence(
            "E-MS1999-MISSING-PROP", {"kind": "CAPABILITY_PROPOSAL"},
            EpistemicStatus.PRESSURE_SUPPORTED, source="MS1999",
        )
        qual = m.append_evidence(
            "Q-MS1999-MISSING-QUAL", {"kind": "CAPABILITY_QUALIFICATION"},
            EpistemicStatus.PRESSURE_SUPPORTED, source="EXTERNAL-MS1999",
        )
        proposed_missing = CapabilityContract(
            "CHILD-MISSING", "scale-readonly", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("MS1999",), "CURRENT", {}, dependencies=("NO-CAND-DEP",),
            qualification=QualificationState.CANDIDATE,
        )
        candidate_missing = CapabilityCandidate(
            "CHILD-MISSING", proposed_missing, (prop,),
            nomination_basis="MS1999_MISSING_DEPENDENCY_ADMISSION_HOSTILE",
        )
        m.nominate_capability_candidate(candidate_missing)
        ticket_missing = ExternalCapabilityQualifier(m.evidence, qualifier_id="EXTERNAL-MS1999-MISSING").qualify(
            candidate_missing, qualification_evidence=(qual,),
        )
        missing_admission_error = None
        try:
            m.admit_capability_candidate(ticket_missing, handler=lambda **_: {"ran": "CHILD-MISSING"})
        except Exception as exc:
            missing_admission_error = f"{type(exc).__name__}:{exc}"
        assert missing_admission_error and "CANDIDATE_DEPENDENCY_CLOSURE_INCOMPLETE:NO-CAND-DEP" in missing_admission_error
        assert "CHILD-MISSING" not in m.capabilities.contracts

        # Existing but stale dependencies are likewise insufficient.
        m.register_capability(_readonly_contract("BASE"))
        m.change_capability_dependency("BASE", reason="MS1999-STALE-BASE")
        prop2 = m.append_evidence(
            "E-MS1999-STALE-PROP", {"kind": "CAPABILITY_PROPOSAL"},
            EpistemicStatus.PRESSURE_SUPPORTED, source="MS1999",
        )
        qual2 = m.append_evidence(
            "Q-MS1999-STALE-QUAL", {"kind": "CAPABILITY_QUALIFICATION"},
            EpistemicStatus.PRESSURE_SUPPORTED, source="EXTERNAL-MS1999",
        )
        proposed_stale = CapabilityContract(
            "CHILD-STALE", "scale-readonly", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("MS1999",), "CURRENT", {}, dependencies=("BASE",),
            qualification=QualificationState.CANDIDATE,
        )
        candidate_stale = CapabilityCandidate(
            "CHILD-STALE", proposed_stale, (prop2,),
            nomination_basis="MS1999_STALE_DEPENDENCY_ADMISSION_HOSTILE",
        )
        m.nominate_capability_candidate(candidate_stale)
        ticket_stale = ExternalCapabilityQualifier(m.evidence, qualifier_id="EXTERNAL-MS1999-STALE").qualify(
            candidate_stale, qualification_evidence=(qual2,),
        )
        stale_admission_error = None
        try:
            m.admit_capability_candidate(ticket_stale, handler=lambda **_: {"ran": "CHILD-STALE"})
        except Exception as exc:
            stale_admission_error = f"{type(exc).__name__}:{exc}"
        assert stale_admission_error and "CANDIDATE_DEPENDENCY_CLOSURE_INCOMPLETE:BASE" in stale_admission_error
        assert "CHILD-STALE" not in m.capabilities.contracts

        # When explicit epoch bindings are supplied, they must cover exactly the
        # declared dependency set; omission cannot silently downgrade the check.
        m.register_capability(_readonly_contract("GOOD"))
        prop3 = m.append_evidence(
            "E-MS1999-BIND-PROP", {"kind": "CAPABILITY_PROPOSAL"},
            EpistemicStatus.PRESSURE_SUPPORTED, source="MS1999",
        )
        qual3 = m.append_evidence(
            "Q-MS1999-BIND-QUAL", {"kind": "CAPABILITY_QUALIFICATION"},
            EpistemicStatus.PRESSURE_SUPPORTED, source="EXTERNAL-MS1999",
        )
        proposed_bound = CapabilityContract(
            "CHILD-BOUND", "scale-readonly", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("MS1999",), "CURRENT", {}, dependencies=("GOOD",),
            qualification=QualificationState.CANDIDATE,
        )
        candidate_bound = CapabilityCandidate(
            "CHILD-BOUND", proposed_bound, (prop3,),
            nomination_basis="MS1999_DEPENDENCY_EPOCH_SET_HOSTILE",
            operational_signature={"dependency_epochs": []},
        )
        m.nominate_capability_candidate(candidate_bound)
        ticket_bound = ExternalCapabilityQualifier(m.evidence, qualifier_id="EXTERNAL-MS1999-BIND").qualify(
            candidate_bound, qualification_evidence=(qual3,),
        )
        epoch_set_error = None
        try:
            m.admit_capability_candidate(ticket_bound, handler=lambda **_: {"ran": "CHILD-BOUND"})
        except Exception as exc:
            epoch_set_error = f"{type(exc).__name__}:{exc}"
        assert epoch_set_error == "ValueError:CANDIDATE_DEPENDENCY_EPOCH_SET_MISMATCH"

        # Endogenous action-alphabet derivation must use full dependency closure, not
        # the local qualification bit.  Missing/cyclic EFFECT contracts stay out.
        missing_effect = CapabilityContract(
            "EFFECT-MISSING", "opaque-effect", {}, {}, (), (), Authority.EFFECT, ("MS1999",),
            "CURRENT", {}, dependencies=("NO-EFFECT-DEP",), query_obligation_id="Q",
            qualification=QualificationState.SHADOW_QUALIFIED, handler=lambda **_: {"ran": True},
        )
        cycle_effect_a = CapabilityContract(
            "EFFECT-CYCLE-A", "opaque-effect", {}, {}, (), (), Authority.EFFECT, ("MS1999",),
            "CURRENT", {}, dependencies=("EFFECT-CYCLE-B",), query_obligation_id="Q",
            qualification=QualificationState.SHADOW_QUALIFIED, handler=lambda **_: {"ran": True},
        )
        cycle_effect_b = CapabilityContract(
            "EFFECT-CYCLE-B", "opaque-effect", {}, {}, (), (), Authority.EFFECT, ("MS1999",),
            "CURRENT", {}, dependencies=("EFFECT-CYCLE-A",), query_obligation_id="Q",
            qualification=QualificationState.SHADOW_QUALIFIED, handler=lambda **_: {"ran": True},
        )
        m.register_capability(missing_effect)
        m.register_capability(cycle_effect_a)
        m.register_capability(cycle_effect_b)
        effect_tokens = derive_current_epistemic_effect_action_tokens(
            capabilities=m.capabilities, obligation=QueryObligation("Q", "opaque", required_authority=Authority.EFFECT),
        )
        assert "EFFECT-MISSING" not in effect_tokens
        assert "EFFECT-CYCLE-A" not in effect_tokens
        assert "EFFECT-CYCLE-B" not in effect_tokens
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()

    return {
        "status": "BOUNDARY_CONFIRMED",
        "missing_dependency_structural_registration": "ALLOWED",
        "missing_dependency_use": missing_invoke["status"],
        "missing_dependency_use_authority": missing_invoke["authority"],
        "deferred_dependency_before": before["status"],
        "deferred_dependency_after": after["status"],
        "cycle_structural_representation": "ALLOWED",
        "cycle_a_reason": cycle_a["reason"],
        "cycle_b_reason": cycle_b["reason"],
        "cycle_execution_authority": "NONE",
        "missing_dependency_candidate_admission": missing_admission_error,
        "stale_dependency_candidate_admission": stale_admission_error,
        "dependency_epoch_set_mismatch": epoch_set_error,
        "unclosed_effects_in_endogenous_action_alphabet": [],
        "dependency_grounding_authority": "USE_TIME_PLUS_CANDIDATE_ADMISSION_CURRENTNESS_ONLY",
        "new_manager_required": "NO",
    }


def run_ms1999() -> dict[str, object]:
    left = run_hundred_effect_arm(("P1", "P2", "N1", "N2"))
    right = run_hundred_effect_arm(("N2", "P2", "N1", "P1"))
    assert left["generated_program"] == right["generated_program"] == list(MAIN)
    assert left["candidate_id"] == right["candidate_id"]
    assert left["candidate_sha256"] == right["candidate_sha256"]

    tie = run_hundred_tie_arm()
    topology = run_dependency_topology_arm()
    grounding = run_dependency_grounding_arm()

    return {
        "status": "MIXED_BOUNDARY_CONFIRMED",
        "hundred_effect_left": left,
        "hundred_effect_right": right,
        "hundred_effect_tie": tie,
        "dependency_topology": topology,
        "dependency_grounding": grounding,
        "earned_positive": "ONE_HUNDRED_CURRENT_EFFECT_CAPABILITIES_CAN_PRESERVE_CALLER_FREE_ENDOGENOUS_PROGRAM_CONSTRUCTION_BUDGET_CURRENTNESS_AND_INSERTION_ORDER_BOUNDARIES_WITHOUT_A_NEW_SEARCH_MANAGER",
        "earned_repair": "EXECUTABLE_CAPABILITY_CURRENTNESS_CAN_REQUIRE_A_FULLY_REGISTERED_CURRENT_ACYCLIC_DEPENDENCY_CLOSURE_WHILE_PRESERVING_UNRESOLVED_GRAPH_SHAPES_AS_NONAUTHORITATIVE_REPRESENTATION",
        "earned_negative": "LOCAL_INVALIDATION_AT_SCALE_DOES_NOT_YET_HAVE_A_LAWFUL_SAME_IDENTITY_CAPABILITY_REQUALIFICATION_CLOSURE_PATH",
        "new_core_mechanism_required": "YES__EPHEMERAL_DEPENDENCY_CLOSURE_ASSESSOR_AND_USE_ADMISSION_RECHECKS__NO_MANAGER",
        "remaining_blocker": "CAPABILITY_REQUALIFICATION_OR_EXPLICIT_REPLACEMENT_LIFECYCLE_REQUIRED_BEFORE_LARGE_N_QUALIFICATION_CLOSURE_CAN_BE_CLAIMED",
        "execution_authority_gain": "NONE",
        "truth_authority_gain": "NONE",
    }


def main() -> None:
    print(json.dumps(run_ms1999(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
