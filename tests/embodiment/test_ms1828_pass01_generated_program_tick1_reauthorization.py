from microseed import Authority, Observation
from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, act_ob, fob
from tests.embodiment.test_ms1820_pass13_owned_three_locus_surface_generates_program import _add_effect_c, _add_recurrent_chain
from tests.embodiment.test_ms1822_pass15_three_locus_shared_background_priority import _add_shared_fallback


def _add_later_shared_fallback(m):
    for state, next_state, rid in (("s1", "sd1", "R-D1"), ("s2", "sd2", "R-D2")):
        m.action_outcome_learning.add_relation(QualifiedActionOutcomePredictiveRelation(
            relation_id=rid, candidate_id="C-" + rid, candidate_sha256=("e" if state == "s1" else "f") * 64,
            start_state_id=state, capability_id="D", next_state_id=next_state, value_effect=0.0,
            support=12, consistency=1.0, source_evidence_ids=("E-" + rid,), qualification_evidence_ids=("Q-" + rid,),
            holdout_support=12, holdout_accuracy=1.0, capability_epoch=0,
            frame_epochs=(("F", 0),), episode_schema_epochs=(("EP", 0),), value_epoch=("V", 0),
        ))


def _generated_fixture():
    td, m, calls, _, _, _ = fixture()
    _add_effect_c(m, calls)
    _add_shared_fallback(m, calls)
    _add_later_shared_fallback(m)
    for prefix, effect, end in (("P1", 1.0, "u"), ("P2", 1.0, "u"), ("N1", -1.0, "v"), ("N2", -1.0, "v")):
        _add_recurrent_chain(m, prefix, effect, end)
    m.observe_opaque_control_state(
        Observation("CS-1828", "EXT", "opaque-control", "s0", authority=Authority.OBSERVATION_ONLY),
        evidence_id="E-CS-1828",
    )
    admitted = m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(deficit_id="D", obligation=act_ob())
    assert admitted["status"] == "EPISTEMIC_TRIAL_INSTANTIATED", admitted
    trial = admitted["trial"]
    assert trial.steps == ("A", "B", "C")
    surface = m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
    dc = EpistemicDecisionBearingContext(tuple(surface["relation_sets"]), ())
    return td, m, calls, trial, dc


def _execute_first_and_advance(m, trial, dc, *, next_state="s1", evidence_id="E-OUT-1828-A"):
    n1 = m.nominate_endogenous_epistemic_program_step_intent(trial, dc, "FEAS-A", fob("A"), act_ob())
    assert n1["status"] == "ACTION_INTENT_NOMINATED", n1
    ctx1 = EpistemicStepExecutionContext(trial, feasibility_capability_id="FEAS-A", feasibility_obligation=fob("A"), decision_context=dc)
    ex1 = m.execute_bounded_action(n1["intent"]["intent_id"], act_ob(), epistemic_step_context=ctx1)
    assert ex1["status"] == "ACTION_EXECUTED", ex1
    xid = ex1["execution"]["execution_id"]
    obs = Observation("OBS-1828-A-" + next_state, "EXT", f"action-execution:{xid}", {"next_state_id": next_state}, authority=Authority.OBSERVATION_ONLY)
    out = m.record_bounded_action_outcome(xid, obs, evidence_id=evidence_id)
    assert out["status"] == "ACTION_OUTCOME_OBSERVED", out
    t2 = advance_epistemic_program_trial(
        trial,
        intent=m.action_closure.intents[n1["intent"]["intent_id"]],
        execution=m.action_closure.executions[xid],
        outcome=m.action_closure.outcomes[out["outcome"]["outcome_id"]],
        capabilities=m.capabilities,
        current_frame_epochs=dict(m.frames.epochs),
    )
    assert t2.status == "OPEN" and len(t2.step_records) == 1
    return t2


def test_generated_three_step_trial_reearns_second_primitive_from_actual_tick1_state():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        t2 = _execute_first_and_advance(m, trial, dc, next_state="s1")
        assert calls == ["A"]
        n2 = m.nominate_endogenous_epistemic_program_step_intent(t2, dc, "FEAS-B", fob("B"), act_ob())
        assert n2["status"] == "ACTION_INTENT_NOMINATED", n2
        assert n2["intent"]["capability_id"] == "B"
        assert n2["intent"]["start_state_id"] == "s1"
        assert n2["intent"]["control_state_evidence_id"] == "E-OUT-1828-A"
        assert calls == ["A"]  # nomination is inert; no macro execution
        assert "C" not in calls
    finally:
        td.cleanup()


def test_unexpected_actual_intermediate_state_blocks_carried_forward_generated_word():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        t2 = _execute_first_and_advance(m, trial, dc, next_state="sx", evidence_id="E-OUT-1828-X")
        n2 = m.nominate_endogenous_epistemic_program_step_intent(t2, dc, "FEAS-B", fob("B"), act_ob())
        assert n2["status"] == "ABSTAIN", n2
        assert calls == ["A"]
        assert n2["reason"] in {
            "HYPOTHESIS_CONDITIONED_EXECUTABLE_ACTION_UNRESOLVED",
            "PROGRAM_OBSERVABLE_TRACE_UNRESOLVED",
            "EPISTEMIC_PROGRAM_INFORMATION_UNRESOLVED",
        }
    finally:
        td.cleanup()
