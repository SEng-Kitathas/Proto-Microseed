from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from microseed import Microseed
from microseed.development.predictive_adaptation import PredictiveCurrentnessConfig
from microseed.development.rehearsal import CounterfactualRehearsalConfig
from research.substrate_shadow.environment_adapter import AdapterConfig, ShadowEnvironmentAdapter
from scratch.ms1997_lived_history_to_endogenous_program import MAIN
from scratch.ms1998_observable_context_assistance_removal import (
    ObservableContextWorld,
    _candidate_by_action,
    qualify_relations_from_later_history,
    run_assisted_episode,
)


class TerminalOnlyDriftWorld(ObservableContextWorld):
    """Same beneficial value effects, changed terminal causal outcome after drift."""
    name = "V1-SOAK-001-TERMINAL-ONLY-DRIFT-WORLD"

    def configure_mode(self, mode: str) -> None:
        if mode not in {"P", "D"}:
            raise ValueError("INVALID_WORLD_MODE")
        self.mode = mode

    @property
    def sign(self) -> float:
        return 1.0

    def reset(self) -> None:
        self.phase = 0
        self.value = -3.0

    def _state(self) -> str:
        if self.phase == 0: return "s0"
        if self.phase == 1: return "s1"
        if self.phase == 2: return "s2"
        return "u" if self.mode == "P" else "w"


def close_ms(ms: Microseed) -> None:
    ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def bootstrap(ms, adapter, world):
    train=[]
    for i in range(12): train.extend(run_assisted_episode(ms,adapter,world,evaluator_mode="P",index=i,phase="P-TRAIN"))
    candidates=_candidate_by_action(ms)
    hold=[]
    for i in range(12): hold.extend(run_assisted_episode(ms,adapter,world,evaluator_mode="P",index=i,phase="P-HOLD"))
    return qualify_relations_from_later_history(ms,candidates,hold,prefix="P-REL")


def prime_zero_row_proposals(ms: Microseed, adapter: ShadowEnvironmentAdapter, world) -> dict[str, str]:
    world.configure_mode("P"); world.reset(); adapter.observe_control(ms, "PRIME-S0")
    options = tuple(adapter.option(a) for a in MAIN)
    out = {}
    for step, expected in enumerate(MAIN):
        current = ms.action_closure.current_state; assert current is not None
        p = ms.nominate_counterfactual_rehearsal((), options, start_state_id=current.state_id, value_id=adapter.config.value_id, config=CounterfactualRehearsalConfig(max_horizon=1, max_nodes=16))
        assert p is not None and p.sequence == (expected,)
        out[current.state_id] = p.proposal_id
        intent = ms.nominate_bounded_action_intent(p.proposal_id, adapter.act_obligation()); assert intent["status"] == "ACTION_INTENT_NOMINATED"
        ex = adapter.execute_intent(ms, intent["intent"]["intent_id"]); assert ex["status"] == "ACTION_EXECUTED"
        obs = adapter.record_execution_outcome(ms, ex["execution"]["execution_id"], evidence_id=f"PRIME-OUT-{step}", capture_id=f"PRIME-CAP-{step}"); assert obs["status"] == "ACTION_OUTCOME_OBSERVED"
    return out


def execute_reused_episode(ms, adapter, world, proposal_by_state, mode, index):
    world.configure_mode(mode); world.reset(); adapter.observe_control(ms, f"{mode}-{index}-START")
    rows=[]
    for step in range(3):
        state=ms.action_closure.current_state; assert state is not None
        pid=proposal_by_state[state.state_id]
        intent=ms.nominate_bounded_action_intent(pid,adapter.act_obligation())
        rows.append({"state":state.state_id,"proposal_id":pid,"intent_status":intent["status"],"intent_reason":intent.get("reason")})
        if intent["status"]!="ACTION_INTENT_NOMINATED": return {"status":"BLOCKED","rows":rows}
        ex=adapter.execute_intent(ms,intent["intent"]["intent_id"]); assert ex["status"]=="ACTION_EXECUTED",ex
        obs=adapter.record_execution_outcome(ms,ex["execution"]["execution_id"],evidence_id=f"{mode}-{index}-{step}",capture_id=f"{mode}-CAP-{index}-{step}"); assert obs["status"]=="ACTION_OUTCOME_OBSERVED"
    return {"status":"PASS","rows":rows,"final":world.observe()}


def run_sign_flip_guard() -> dict[str, object]:
    td=tempfile.TemporaryDirectory(prefix="v1-soak-sign-flip-"); root=Path(td.name)
    ms=Microseed(root); world=ObservableContextWorld(); adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id="SIGN-FLIP",viable_low=-.25,viable_high=.25))
    try:
        adapter.attach(ms)
        for cid in MAIN+(adapter.config.observation_capability_id,): ms.frames.bind_capability(adapter.config.frame_id,cid)
        bootstrap(ms,adapter,world); proposals=prime_zero_row_proposals(ms,adapter,world)
        attempt=execute_reused_episode(ms,adapter,world,proposals,"N",0)
        assert attempt["status"]=="BLOCKED"
        return {"status":"BLOCKED_AS_EXPECTED","reason":attempt["rows"][0]["intent_reason"],"earned":"CURRENT_VALUE_REPROJECTION_BLOCKS_REUSED_POSITIVE_EFFECT_PROPOSAL_WHEN_REGULATORY_SIGN_REVERSES"}
    finally: close_ms(ms);td.cleanup()


def run_terminal_drift_violation() -> dict[str, object]:
    td=tempfile.TemporaryDirectory(prefix="v1-soak-terminal-drift-"); root=Path(td.name)
    ms=Microseed(root); world=TerminalOnlyDriftWorld(); adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id="TERMINAL-DRIFT",viable_low=-.25,viable_high=.25))
    try:
        adapter.attach(ms)
        for cid in MAIN+(adapter.config.observation_capability_id,): ms.frames.bind_capability(adapter.config.frame_id,cid)
        relations=bootstrap(ms,adapter,world); proposals=prime_zero_row_proposals(ms,adapter,world)
        runs=[execute_reused_episode(ms,adapter,world,proposals,"D",i) for i in range(16)]
        assert all(r["status"]=="PASS" for r in runs),runs
        drift={}
        for action in MAIN:
            drift[action]=ms.assess_action_outcome_predictive_currentness(relations[action],config=PredictiveCurrentnessConfig(window_size=8,min_accuracy=.75,consecutive_failure_windows=2))
        assert drift["K-17"]["status"]=="CURRENT_WITHIN_BOUNDS",drift["K-17"]
        assert drift["M-23"]["status"]=="CURRENT_WITHIN_BOUNDS",drift["M-23"]
        assert drift["R-41"]["status"]=="DRIFT_WITNESS",drift["R-41"]
        relation_status={a:ms.action_outcome_predictive_relation_status(rid) for a,rid in relations.items()}
        proposal_status={state:ms.counterfactual_rehearsal_status(pid) for state,pid in proposals.items()}
        assert relation_status["K-17"]["status"]==relation_status["M-23"]["status"]=="CURRENT_PREDICTIVE_RELATION"
        assert relation_status["R-41"]["status"]=="STALE_PREDICTIVE_RELATION"
        # Walk lawfully to s2 using the still-current K/M proposals, then pressure the old R proposal.
        world.configure_mode("D");world.reset();adapter.observe_control(ms,"POST-DRIFT")
        advance=[]
        for state_id in ("s0","s1"):
            state=ms.action_closure.current_state;assert state is not None and state.state_id==state_id
            pid=proposals[state_id]
            intent=ms.nominate_bounded_action_intent(pid,adapter.act_obligation());assert intent["status"]=="ACTION_INTENT_NOMINATED",intent
            ex=adapter.execute_intent(ms,intent["intent"]["intent_id"]);assert ex["status"]=="ACTION_EXECUTED"
            obs=adapter.record_execution_outcome(ms,ex["execution"]["execution_id"],evidence_id=f"POST-DRIFT-{state_id}",capture_id=f"POST-DRIFT-CAP-{state_id}");assert obs["status"]=="ACTION_OUTCOME_OBSERVED"
            advance.append(intent["intent"]["capability_id"])
        s2=ms.action_closure.current_state;assert s2 is not None and s2.state_id=="s2"
        pid=proposals["s2"]
        commitment=ms.derive_bounded_action_commitment(pid)
        intent=ms.nominate_bounded_action_intent(pid,adapter.act_obligation())
        violated=(proposal_status["s2"]["status"]=="CURRENT_REHEARSAL_PROPOSAL" and commitment.commitment.value=="YES" and intent["status"]=="ACTION_INTENT_NOMINATED")
        return {"status":"VIOLATED" if violated else "BLOCKED","relations":relations,"proposals":proposals,"drift_assessments":drift,"relation_status":relation_status,"proposal_status":proposal_status,"advance_to_s2":advance,"post_drift_r_commitment":commitment.serializable(),"post_drift_r_intent":intent,"violation":"STALE_R41_PREDICTIVE_RELATION_CAN_REMAIN_EXECUTION_PREMISE_THROUGH_DURABLE_REHEARSAL_REUSE" if violated else None}
    finally: close_ms(ms);td.cleanup()

def run():
    return {"sign_flip_guard":run_sign_flip_guard(),"terminal_only_drift":run_terminal_drift_violation()}

if __name__ == "__main__": print(json.dumps(run(),indent=2,sort_keys=True,default=str))
