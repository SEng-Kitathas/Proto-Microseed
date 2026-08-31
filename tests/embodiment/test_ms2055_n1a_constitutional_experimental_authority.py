from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import pytest

from microseed import (
    Authority,
    CapabilityContract,
    Microseed,
    Observation,
    QualificationState,
    QueryObligation,
    ValueVariableContract,
)
from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation


def _obligation(scope: str = "S") -> QueryObligation:
    return QueryObligation("ACT", "n1a-first-unmodeled-effect", required_authority=Authority.EFFECT, operational_scope_id=scope)


def _value(value_id: str, low: float = 0.0, high: float = 10.0) -> ValueVariableContract:
    return ValueVariableContract(
        value_id, "constitutional-regulatory", low, high,
        hashlib.sha256(f"{value_id}:{low}:{high}".encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY, ("MS2055-N1A",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE", "SUPPLIED_VIABILITY_INTERVAL"),
    )


def _cap(capability_id: str, calls: list[str], *, scope: str = "S", handler=None) -> CapabilityContract:
    if handler is None:
        handler=lambda _cid=capability_id, **_: calls.append(_cid) or {"receipt": _cid}
    return CapabilityContract(
        capability_id, "opaque-physical-effect", {}, {}, (), (), Authority.EFFECT,
        ("MS2055-N1A",), "CURRENT", {}, query_obligation_id="ACT",
        qualification=QualificationState.SHADOW_QUALIFIED, handler=handler,
        operational_scope_id=scope,
    )


def _seed(*, values=("V",), caps=("A",), handler=None):
    td=tempfile.TemporaryDirectory(prefix="microseed-ms2055-n1a-")
    ms=Microseed(Path(td.name)); calls=[]
    for value_id in values:
        ms.register_value_variable(_value(value_id))
        ms.observe_value_state(value_id, 5.0)
    for cid in caps:
        ms.register_capability(_cap(cid,calls,handler=handler if len(caps)==1 else None))
    ms.observe_opaque_control_state(
        Observation("CTRL-0","EXT","control","S0",authority=Authority.OBSERVATION_ONLY),
        evidence_id="E-CTRL-0",
    )
    return td,ms,calls


def _close(ms: Microseed) -> None:
    try: ms.store.conn.close()
    except Exception: pass
    try: ms.evidence.conn.close()
    except Exception: pass
    try: ms.biography.close()
    except Exception: pass


def test_n1a_requires_complete_current_constitutional_value_frame() -> None:
    td=tempfile.TemporaryDirectory(prefix="microseed-ms2055-n1a-novalue-")
    ms=Microseed(Path(td.name)); calls=[]
    try:
        ms.register_capability(_cap("A",calls))
        ms.observe_opaque_control_state(Observation("CTRL","EXT","control","S0",authority=Authority.OBSERVATION_ONLY),evidence_id="E-CTRL")
        out=ms.derive_n1a_experimental_warrant(_obligation())
        assert out["status"]=="ABSTAIN"
        assert out["reason"]=="COMPLETE_CURRENT_VALUE_FRAME_REQUIRED"
        assert out["execution_authority"]=="NONE"
    finally:
        _close(ms); td.cleanup()


def test_n1a_unknownness_does_not_rank_multiple_eligible_actions() -> None:
    td,ms,_=_seed(caps=("A","B"))
    try:
        out=ms.derive_n1a_experimental_warrant(_obligation())
        assert out["status"]=="ABSTAIN"
        assert out["reason"]=="UNIQUE_EXPERIMENT_SUBJECT_REQUIRED"
        assert out["eligible_capability_ids"]==["A","B"]
        assert out["selection_authority"]=="UNIQUE_ELIGIBILITY_ONLY"
        assert out["information_value_authority"]=="NONE"
    finally:
        _close(ms); td.cleanup()


def test_n1a_one_exact_unknown_action_executes_once_with_residual_risk_explicit_and_no_safety_claim() -> None:
    td,ms,calls=_seed(values=("V","W"))
    try:
        derived=ms.derive_n1a_experimental_warrant(_obligation())
        assert derived["status"]=="N1A_EXPERIMENTAL_WARRANT_ISSUED"
        assert derived["execution_authority"]=="NONE"
        assert derived["downstream_risk_status"]=="UNKNOWN_INCOMPLETE_ACCEPTED_BY_N1A_CONSTITUTION"
        assert derived["moral_compass"]=="CURRENT_VALUE_FRAME_PRESENT__KNOWN_CONSEQUENCE_CANNOT_USE_N1A"
        nominated=ms.nominate_n1a_experimental_action_intent(_obligation())
        assert nominated["status"]=="N1A_ACTION_INTENT_NOMINATED"
        executed=ms.execute_bounded_action(nominated["intent"]["intent_id"],_obligation())
        assert executed["status"]=="ACTION_EXECUTED"
        assert executed["n1a_warrant_reserved_before_effect"] is True
        assert executed["downstream_risk_status"]=="UNKNOWN_INCOMPLETE_ACCEPTED_BY_N1A_CONSTITUTION"
        assert calls==["A"]
        # The same capability epoch can never regain a first-exposure warrant.
        again=ms.derive_n1a_experimental_warrant(_obligation())
        assert again["status"]=="ABSTAIN"
        assert again["reason"]=="NO_CURRENT_ELIGIBLE_UNMODELED_ACTION"
        assert again["rejected"]["A"] in {"N1A_FIRST_EXPOSURE_ALREADY_CONSUMED","CONSEQUENCE_ALREADY_MODELED:CAPABILITY_ALREADY_EXECUTED_THIS_EPOCH"}
    finally:
        _close(ms); td.cleanup()


def test_n1a_effect_time_state_scope_signature_and_value_frame_drift_block_execution() -> None:
    # state drift
    td,ms,calls=_seed();
    try:
        intent=ms.nominate_n1a_experimental_action_intent(_obligation())["intent"]
        ms.observe_opaque_control_state(Observation("CTRL-1","EXT","control","S1",authority=Authority.OBSERVATION_ONLY),evidence_id="E-CTRL-1")
        out=ms.execute_bounded_action(intent["intent_id"],_obligation())
        assert out["reason"]=="CONTROL_STATE_DRIFT" and calls==[]
    finally: _close(ms); td.cleanup()
    # scope drift
    td,ms,calls=_seed();
    try:
        intent=ms.nominate_n1a_experimental_action_intent(_obligation())["intent"]
        out=ms.execute_bounded_action(intent["intent_id"],_obligation("T"))
        assert out["reason"]=="ACTION_OBLIGATION_DRIFT" and calls==[]
    finally: _close(ms); td.cleanup()
    # signature drift without qualification/currentness laundering
    td,ms,calls=_seed();
    try:
        intent=ms.nominate_n1a_experimental_action_intent(_obligation())["intent"]
        ms.capabilities.contracts["A"].boundary["mutated"]="after-nomination"
        out=ms.execute_bounded_action(intent["intent_id"],_obligation())
        assert out["reason"]=="N1A_WARRANT_PREMISE_DRIFT" and calls==[]
    finally: _close(ms); td.cleanup()
    # live value changed after nomination: same constitutional variable, different current frame digest
    td,ms,calls=_seed();
    try:
        intent=ms.nominate_n1a_experimental_action_intent(_obligation())["intent"]
        ms.observe_value_state("V",6.0)
        out=ms.execute_bounded_action(intent["intent_id"],_obligation())
        assert out["reason"]=="N1A_WARRANT_PREMISE_DRIFT" and calls==[]
    finally: _close(ms); td.cleanup()


def test_n1a_reservation_is_consumed_before_effect_and_survives_handler_crash_and_restart() -> None:
    def boom(**_):
        raise RuntimeError("simulated-effect-handler-crash")
    td,ms,_=_seed(handler=boom)
    state_dir=Path(td.name)
    try:
        intent=ms.nominate_n1a_experimental_action_intent(_obligation())["intent"]
        subject=intent["experimental_subject_id"]
        with pytest.raises(RuntimeError,match="simulated-effect-handler-crash"):
            ms.execute_bounded_action(intent["intent_id"],_obligation())
        reserved=ms.store.get(ms._n1a_subject_consumption_key(subject))
        assert reserved is not None and reserved["consumed_before_effect"] is True
        assert len(ms.action_closure.executions)==0
        _close(ms)
        # Reincarnate from the same durable state, then restore ordinary current contracts.
        ms2=Microseed(state_dir); calls=[]
        try:
            ms2.register_value_variable(_value("V")); ms2.observe_value_state("V",5.0)
            ms2.register_capability(_cap("A",calls))
            # Current control witness is replayed from durable action closure.
            out=ms2.derive_n1a_experimental_warrant(_obligation())
            assert out["status"]=="ABSTAIN"
            assert out["rejected"]["A"]=="N1A_FIRST_EXPOSURE_ALREADY_CONSUMED"
            assert calls==[]
        finally:
            _close(ms2)
    finally:
        try: _close(ms)
        except Exception: pass
        td.cleanup()


def test_n1a_actual_outcome_sovereignty_records_complete_value_effects_without_retrospective_safety() -> None:
    td,ms,calls=_seed(values=("V","W"))
    try:
        intent=ms.nominate_n1a_experimental_action_intent(_obligation())["intent"]
        executed=ms.execute_bounded_action(intent["intent_id"],_obligation())
        eid=executed["execution"]["execution_id"]
        # One coordinate gets materially worse. N1A never said it was safe; the actual outcome wins.
        result=ms.record_bounded_action_outcome(
            eid,
            Observation("OUT","EXT",f"action-execution:{eid}",{"next_state_id":"S1","observed_values":{"V":2.0,"W":6.0}},authority=Authority.OBSERVATION_ONLY),
            evidence_id="E-OUT",
        )
        assert result["status"]=="N1A_ACTION_OUTCOME_OBSERVED"
        assert result["actual_value_effects"]=={"V":-3.0,"W":1.0}
        assert result["retrospective_safety_authority"]=="NONE"
        assert result["requires_redeliberation"] is True
        outcome=result["outcome"]
        assert outcome["prediction_commitment"]["commitment"]=="UNKNOWN"
        assert outcome["prediction_commitment"]["reason"]=="N1A_FIRST_EXPOSURE_HAD_NO_PRIOR_CONSEQUENCE_PREDICTION"
        assert {row["value_id"] for row in outcome["value_outcomes"]}=={"V","W"}
        assert len(ms._action_outcome_experiences())==2
        assert calls==["A"]
    finally:
        _close(ms); td.cleanup()


def test_n1a_outcome_requires_complete_issue_value_frame_not_caller_subset() -> None:
    td,ms,_=_seed(values=("V","W"))
    try:
        intent=ms.nominate_n1a_experimental_action_intent(_obligation())["intent"]
        executed=ms.execute_bounded_action(intent["intent_id"],_obligation())
        eid=executed["execution"]["execution_id"]
        result=ms.record_bounded_action_outcome(
            eid,
            Observation("OUT-MISS","EXT",f"action-execution:{eid}",{"next_state_id":"S1","observed_values":{"V":4.0}},authority=Authority.OBSERVATION_ONLY),
            evidence_id="E-OUT-MISS",
        )
        assert result["status"]=="OUTCOME_REJECTED"
        assert result["reason"]=="N1A_COMPLETE_ISSUE_VALUE_FRAME_OBSERVATION_REQUIRED"
        assert result["required_value_ids"]==["V","W"]
        assert len(ms.action_closure.outcomes)==0
    finally:
        _close(ms); td.cleanup()


def test_n1a_cannot_launder_a_current_known_harm_as_residual_unknown() -> None:
    td,ms,calls=_seed()
    try:
        relation=QualifiedActionOutcomePredictiveRelation(
            relation_id="R-HARM",candidate_id="C-HARM",candidate_sha256="c"*64,
            start_state_id="S0",capability_id="A",next_state_id="S-HARM",value_effect=-4.0,
            support=12,consistency=1.0,source_evidence_ids=("E-HARM",),qualification_evidence_ids=("Q-HARM",),
            holdout_support=6,holdout_accuracy=1.0,capability_epoch=0,frame_epochs=(),episode_schema_epochs=(),
            value_epoch=("V",0),
        )
        ms.action_outcome_learning.add_relation(relation)
        out=ms.derive_n1a_experimental_warrant(_obligation())
        assert out["status"]=="ABSTAIN"
        assert out["reason"]=="NO_CURRENT_ELIGIBLE_UNMODELED_ACTION"
        assert "CURRENT_PREDICTIVE_RELATION_EXISTS" in out["rejected"]["A"]
        assert calls==[]
    finally:
        _close(ms); td.cleanup()
