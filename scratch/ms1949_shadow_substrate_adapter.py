from __future__ import annotations

import json
import hashlib
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


class ChargeWorld:
    name='CHARGE-WORLD'; action_ids=('CHARGE',)
    compatibility_sha256=hashlib.sha256(b'CHARGE-WORLD:v1:CHARGE->LEVEL-2:value2.4').hexdigest()
    def __init__(self): self.level=0
    def reset(self): self.level=0
    def apply(self,action_id):
        assert action_id=='CHARGE'; self.level=min(2,self.level+2); return {'receipt':'charged','level':self.level}
    def observe(self): return {'next_state_id':f'LEVEL-{self.level}','observed_value':2.4 if self.level>=2 else 0.0,'raw_level':self.level}
    def fork(self): return deepcopy(self)


class ParityWorld:
    name='PARITY-WORLD'; action_ids=('STEP',)
    compatibility_sha256=hashlib.sha256(b'PARITY-WORLD:v1:STEP->ODD:value2.4').hexdigest()
    def __init__(self): self.counter=0
    def reset(self): self.counter=0
    def apply(self,action_id):
        assert action_id=='STEP'; self.counter+=1; return {'receipt':'stepped','counter':self.counter}
    def observe(self): return {'next_state_id':'ODD' if self.counter%2 else 'EVEN','observed_value':2.4 if self.counter%2 else 0.0,'raw_counter':self.counter}
    def fork(self): return deepcopy(self)


def run_world(world):
    td=tempfile.TemporaryDirectory(prefix=f'ms1949-{world.name.lower()}-'); root=Path(td.name)
    ms=Microseed(root); adapter=ShadowEnvironmentAdapter(world)
    try:
        adapter.attach(ms)
        action=world.action_ids[0]
        rel,candidate=adapter.train_actual_history(ms,action)
        p=adapter.zero_row_rehearsal(ms,action); assert p is not None and p.sequence==(action,)
        cmt=ms.derive_bounded_action_commitment(p.proposal_id); assert cmt.commitment.value=='YES'
        intent=ms.nominate_bounded_action_intent(p.proposal_id,adapter.act_obligation()); assert intent['status']=='ACTION_INTENT_NOMINATED'
        ex=ms.execute_bounded_action(intent['intent']['intent_id'],adapter.act_obligation()); assert ex['status']=='ACTION_EXECUTED'
        out=adapter.record_execution_outcome(ms,ex['execution']['execution_id'],evidence_id=f'E-MS1949-FINAL-{world.name}',capture_id=f'CAP-MS1949-FINAL-{world.name}')
        assert out['status']=='ACTION_OUTCOME_OBSERVED'
        assert ms.action_outcome_predictive_relation_status(rel)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert p.truth_authority==p.execution_authority=='NONE'
        return {'world':world.name,'action':action,'relation_id':rel,'predicted_final_state':p.final_state_id,'predicted_value_effect':p.predicted_value_effect,'actual_final_state':out['outcome']['actual_next_state_id'],'commitment_reason':cmt.reason,'adapter_type':type(adapter).__name__,'language':ms.status()['language']}
    finally:
        _close(ms); td.cleanup()


def main():
    a=run_world(ChargeWorld()); b=run_world(ParityWorld())
    assert a['adapter_type']==b['adapter_type']=='ShadowEnvironmentAdapter'
    assert a['predicted_final_state']==a['actual_final_state']=='LEVEL-2'
    assert b['predicted_final_state']==b['actual_final_state']=='ODD'
    assert a['predicted_value_effect']==b['predicted_value_effect']==2.4
    print(json.dumps({'status':'PASS','worlds':[a,b],'earned':'ONE_EXTERNAL_SHADOW_ADAPTER_SHAPE_CAN_CONNECT_UNCHANGED_MICROSEED_CORE_TO_DISTINCT_WORLD_DYNAMICS_FOR_ACTUAL_HISTORY_QUALIFICATION_AND_ZERO_ROW_REHEARSAL','authority':'NONE','substrate_promotion':'NOT_YET'},indent=2,sort_keys=True))

if __name__=='__main__': main()
