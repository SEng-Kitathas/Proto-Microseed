from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter, AdapterConfig
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


class DelayedChargeWorld:
    name='DELAYED-CHARGE-WORLD'
    action_ids=('CHARGE-DELAYED',)
    compatibility_sha256=hashlib.sha256(b'DELAYED-CHARGE-WORLD:v1:delayed-two-ticks').hexdigest()
    def __init__(self): self.level=0; self.pending=0
    def reset(self): self.level=0; self.pending=0
    def apply(self,action_id):
        assert action_id=='CHARGE-DELAYED'; self.pending=2
        return {'receipt':'scheduled','pending_ticks':self.pending}
    def tick(self):
        if self.pending>0:
            self.pending-=1
            if self.pending==0: self.level=2
    def settle(self):
        while self.pending>0: self.tick()
    def observe(self):
        if self.pending>0:
            return {'next_state_id':'PENDING','observed_value':0.0,'pending_ticks':self.pending}
        return {'next_state_id':f'LEVEL-{self.level}','observed_value':2.4 if self.level>=2 else 0.0,'pending_ticks':0}
    def settled_observation(self):
        self.settle(); return self.observe()
    def observe_outcome(self):
        return self.settled_observation()
    def fork(self): return deepcopy(self)


def run_hostile():
    td=tempfile.TemporaryDirectory(prefix='ms1953-delayed-'); ms=Microseed(Path(td.name)); world=DelayedChargeWorld(); adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id='DELAYED-0'))
    try:
        adapter.attach(ms)
        rows=adapter.equipped_seed_rows('CHARGE-DELAYED',12)
        immediate={r.next_state_id for r in rows}
        effects={r.value_effect for r in rows}
        probe=world.fork(); probe.reset(); probe.apply('CHARGE-DELAYED'); immediate_real=probe.observe(); settled_real=probe.settled_observation()
        assert immediate=={'LEVEL-2'} and effects=={2.4}
        assert immediate_real['next_state_id']=='PENDING'
        assert settled_real['next_state_id']=='LEVEL-2' and settled_real['observed_value']==2.4

        proposal=ms.nominate_counterfactual_rehearsal(rows,(adapter.option('CHARGE-DELAYED'),),start_state_id='LEVEL-0',value_id=adapter.config.value_id)
        assert proposal is not None
        commitment=ms.derive_bounded_action_commitment(proposal.proposal_id)
        result={
            'status':'PASS',
            'adapter_seed_state':proposal.final_state_id,
            'adapter_seed_effect':proposal.predicted_value_effect,
            'commitment':commitment.serializable(),
            'immediate_world_observation':immediate_real,
            'settled_world_observation':settled_real,
            'boundary':'IMMEDIATE_POST_EFFECT_OBSERVATION != SETTLED_ACTION_OUTCOME',
        }
        return result
    finally:
        _close(ms); td.cleanup()



def run_delayed_reality():
    td=tempfile.TemporaryDirectory(prefix='ms1953-delayed-reality-'); ms=Microseed(Path(td.name)); world=DelayedChargeWorld(); adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id='DELAYED-REAL'))
    try:
        adapter.attach(ms)
        relation_id,candidate=adapter.train_actual_history(ms,'CHARGE-DELAYED')
        proposal=adapter.zero_row_rehearsal(ms,'CHARGE-DELAYED')
        assert proposal is not None and proposal.final_state_id=='LEVEL-2' and proposal.predicted_value_effect==2.4
        cmt=ms.derive_bounded_action_commitment(proposal.proposal_id); assert cmt.commitment.value=='YES'
        intent=ms.nominate_bounded_action_intent(proposal.proposal_id,adapter.act_obligation()); assert intent['status']=='ACTION_INTENT_NOMINATED'
        ex=ms.execute_bounded_action(intent['intent']['intent_id'],adapter.act_obligation()); assert ex['status']=='ACTION_EXECUTED'
        out=adapter.record_execution_outcome(ms,ex['execution']['execution_id'],evidence_id='E-MS1953-FINAL',capture_id='CAP-MS1953-FINAL')
        assert out['status']=='ACTION_OUTCOME_OBSERVED' and out['outcome']['actual_next_state_id']=='LEVEL-2' and out['outcome']['observed_value']==2.4
        assert ms.action_outcome_predictive_relation_status(relation_id)['status']=='CURRENT_PREDICTIVE_RELATION'
        return {
            'status':'PASS','relation_id':relation_id,'candidate':candidate,
            'predicted_final_state':proposal.final_state_id,'predicted_value_effect':proposal.predicted_value_effect,
            'actual_final_state':out['outcome']['actual_next_state_id'],'actual_observed_value':out['outcome']['observed_value'],
            'commitment_reason':cmt.reason,
            'earned':'DELAYED_WORLD_OUTCOMES_CAN_SETTLE_AT_EXTERNAL_OBSERVATION_BOUNDARY_BEFORE_MICROSEED_ACTION_CLOSURE',
        }
    finally:
        _close(ms); td.cleanup()

def main(): print(json.dumps({"settlement_boundary":run_hostile(),"reality_run":run_delayed_reality()},indent=2,sort_keys=True))
if __name__=='__main__': main()
