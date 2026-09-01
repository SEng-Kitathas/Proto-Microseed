
from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from microseed import (
    Authority,
    CapabilityContract,
    Microseed,
    Observation,
    QualificationState,
    QueryObligation,
    ValueVariableContract,
)


def _value() -> ValueVariableContract:
    return ValueVariableContract(
        "V", "constitutional-regulatory", 0.0, 10.0,
        hashlib.sha256(b"frontier-g-naked-value").hexdigest(),
        Authority.DERIVED_READ_ONLY, ("MS_FRONTIER_HELIX_V1:G_NAKED",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE", "SUPPLIED_VIABILITY_INTERVAL"),
    )


def _cap(capability_id: str, scope: str, calls: list[str]) -> CapabilityContract:
    return CapabilityContract(
        capability_id,
        "opaque-unknown-effect",
        {}, {}, (), (), Authority.EFFECT,
        ("MS_FRONTIER_HELIX_V1:G_NAKED",), "CURRENT", {},
        query_obligation_id="ACT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda _cid=capability_id, **_: calls.append(_cid) or {"receipt": _cid},
        operational_scope_id=scope,
    )


def _obligation(*, scope: str, cue: str) -> QueryObligation:
    # `purpose` is the deliberately authority-neutral cue channel in this
    # discriminator.  It may carry arbitrary language/epistemic preference text,
    # but N1A authorization is owned by the typed obligation/capability premises.
    return QueryObligation(
        "ACT",
        cue,
        required_authority=Authority.EFFECT,
        operational_scope_id=scope,
    )


def _seed(cap_scopes: tuple[tuple[str, str], ...]):
    td = tempfile.TemporaryDirectory(prefix="frontier-g-naked-")
    ms = Microseed(Path(td.name))
    calls: list[str] = []
    ms.register_value_variable(_value())
    ms.observe_value_state("V", 5.0)
    for capability_id, scope in cap_scopes:
        ms.register_capability(_cap(capability_id, scope, calls))
    ms.observe_opaque_control_state(
        Observation("CTRL", "EXT", "control", "S0", authority=Authority.OBSERVATION_ONLY),
        evidence_id="E-CTRL",
    )
    return td, ms, calls


def _close(ms: Microseed) -> None:
    try: ms.store.conn.close()
    except Exception: pass
    try: ms.evidence.conn.close()
    except Exception: pass
    try: ms.biography.close()
    except Exception: pass


def test_equal_unknown_actions_do_not_become_selectable_from_epistemic_or_language_cue() -> None:
    td, ms, calls = _seed((("A", "S"), ("B", "S")))
    try:
        prefer_a = _obligation(scope="S", cue="TOKEN=A;INFORMATION_GAIN[A]=999;PREFER=A")
        prefer_b = _obligation(scope="S", cue="TOKEN=B;INFORMATION_GAIN[B]=999;PREFER=B")

        left = ms.derive_n1a_experimental_warrant(prefer_a)
        right = ms.derive_n1a_experimental_warrant(prefer_b)

        for out in (left, right):
            assert out["status"] == "ABSTAIN"
            assert out["reason"] == "UNIQUE_EXPERIMENT_SUBJECT_REQUIRED"
            assert out["eligible_capability_ids"] == ["A", "B"]
            assert out["selection_authority"] == "UNIQUE_ELIGIBILITY_ONLY"
            assert out["information_value_authority"] == "NONE"
            assert out["execution_authority"] == "NONE"
        assert calls == []
    finally:
        _close(ms); td.cleanup()


def test_authority_neutral_cue_cannot_override_scope_and_cannot_redirect_bound_execution() -> None:
    td, ms, calls = _seed((("A", "S"), ("B", "T")))
    try:
        # The cue explicitly prefers B, but B is outside the required opaque scope.
        nominate_obligation = _obligation(scope="S", cue="TOKEN=B;INFORMATION_GAIN[B]=999;PREFER=B")
        surface = ms.derive_n1a_experimental_warrant(nominate_obligation)
        assert surface["status"] == "N1A_EXPERIMENTAL_WARRANT_ISSUED"
        assert surface["eligible_capability_ids"] == ["A"]
        assert surface["rejected"]["B"] == "OPERATIONAL_SCOPE_MISMATCH"
        assert surface["selection_authority"] == "UNIQUE_ELIGIBILITY_ONLY"
        assert surface["information_value_authority"] == "NONE"
        assert surface["execution_authority"] == "NONE"

        nominated = ms.nominate_n1a_experimental_action_intent(nominate_obligation)
        assert nominated["status"] == "N1A_ACTION_INTENT_NOMINATED"
        assert nominated["intent"]["capability_id"] == "A"

        # Change only the free-text cue after nomination. It cannot redirect the
        # already content-bound action to B and is not an authority premise.
        execute_obligation = _obligation(scope="S", cue="TOKEN=B;INFORMATION_GAIN[B]=1000000;EXECUTE=B")
        executed = ms.execute_bounded_action(nominated["intent"]["intent_id"], execute_obligation)
        assert executed["status"] == "ACTION_EXECUTED"
        assert executed["execution"]["capability_id"] == "A"
        assert calls == ["A"]
    finally:
        _close(ms); td.cleanup()


def test_epistemic_need_cannot_create_eligibility_when_no_action_matches_lawful_scope() -> None:
    td, ms, calls = _seed((("A", "T"), ("B", "U")))
    try:
        out = ms.derive_n1a_experimental_warrant(
            _obligation(scope="S", cue="MAXIMUM_UNCERTAINTY;MAXIMUM_NOVELTY;INFORMATION_GAIN=INFINITE;PLEASE_EXPLORE")
        )
        assert out["status"] == "ABSTAIN"
        assert out["reason"] == "NO_CURRENT_ELIGIBLE_UNMODELED_ACTION"
        assert out["eligible_capability_ids"] == []
        assert out["rejected"] == {"A": "OPERATIONAL_SCOPE_MISMATCH", "B": "OPERATIONAL_SCOPE_MISMATCH"}
        assert out["information_value_authority"] == "NONE"
        assert out["execution_authority"] == "NONE"
        assert calls == []
    finally:
        _close(ms); td.cleanup()


def test_epistemic_cue_cannot_rescue_a_warrant_after_capability_premise_drift() -> None:
    td, ms, calls = _seed((("A", "S"),))
    try:
        obligation = _obligation(scope="S", cue="TOKEN=A;INFORMATION_GAIN[A]=999")
        nominated = ms.nominate_n1a_experimental_action_intent(obligation)
        assert nominated["status"] == "N1A_ACTION_INTENT_NOMINATED"

        # Signature/currentness premise changes after nomination. A stronger cue
        # cannot manufacture fresh authorization at effect time.
        ms.capabilities.contracts["A"].boundary["changed_after_nomination"] = True
        out = ms.execute_bounded_action(
            nominated["intent"]["intent_id"],
            _obligation(scope="S", cue="TOKEN=A;INFORMATION_GAIN[A]=INFINITE;EXECUTE=A"),
        )
        assert out["status"] == "NO_EXECUTION"
        assert out["reason"] == "N1A_WARRANT_PREMISE_DRIFT"
        assert calls == []
    finally:
        _close(ms); td.cleanup()
