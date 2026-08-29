from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import (
    ShadowEnvironmentAdapter, AdapterConfig, ForkedWorldQualificationSource,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


class ChoiceWorld:
    name='CHOICE-WORLD'
    action_ids=('ACT-A','ACT-Z')
    def __init__(self, effects: dict[str,float]):
        self.effects={str(k):float(v) for k,v in effects.items()}
        assert set(self.effects)==set(self.action_ids)
        payload=';'.join(f'{k}:{self.effects[k]:.3f}' for k in sorted(self.effects))
        self.compatibility_sha256=hashlib.sha256(f'CHOICE-WORLD:v1:{payload}'.encode()).hexdigest()
        self.value=0.0
    def reset(self): self.value=0.0
    def apply(self,action_id):
        assert action_id in self.effects; self.value=self.effects[action_id]
        return {'receipt':'choice-applied','action_id':action_id,'value':self.value}
    def observe(self):
        state='LOW' if self.value<2.0 else ('MID' if self.value<3.0 else 'HIGH')
        return {'next_state_id':state,'observed_value':self.value}
    def observe_outcome(self): return self.observe()
    def fork(self): return deepcopy(self)


def run_world(effects,label):
    td=tempfile.TemporaryDirectory(prefix=f'ms1955-{label.lower()}-'); root=Path(td.name)
    live=ChoiceWorld(effects); source_world=ChoiceWorld(effects)
    source=ForkedWorldQualificationSource(source_world,provider_id=f'QUAL-{label}')
    adapter=ShadowEnvironmentAdapter(live,AdapterConfig(adapter_instance_id=label,viable_low=3.0,viable_high=4.0),qualification_source=source)
    ms=Microseed(root)
    try:
        adapter.attach(ms)
        relations={}
        for aid in live.action_ids:
            rid,_=adapter.train_actual_history(ms,aid); relations[aid]=rid
        start=adapter.reset_control(ms,'FINAL-CHOICE')
        opts=tuple(adapter.option(aid) for aid in live.action_ids)
        proposal=ms.nominate_counterfactual_rehearsal((),opts,start_state_id=start['next_state_id'],value_id=adapter.config.value_id)
        assert proposal is not None
        winner=proposal.sequence[0]
        expected=max(effects,key=lambda aid:effects[aid])
        assert winner==expected,(winner,expected,proposal.serializable())
        individual={}
        # Each route independently lowers pressure, so both are lawful when isolated.
        for i,aid in enumerate(live.action_ids):
            # The winner's one-step proposal may share deterministic identity with the multi-option result.
            if aid==winner:
                p=proposal
            else:
                adapter.reset_control(ms,f'IND-{i}')
                p=ms.nominate_counterfactual_rehearsal((),(adapter.option(aid),),start_state_id='LOW',value_id=adapter.config.value_id)
                assert p is not None and p.sequence==(aid,)
            cmt=ms.derive_bounded_action_commitment(p.proposal_id)
            assert cmt.commitment.value=='YES'
            individual[aid]=cmt.reason
        adapter.reset_control(ms,'EXEC')
        cmt=ms.derive_bounded_action_commitment(proposal.proposal_id); assert cmt.commitment.value=='YES'
        intent=ms.nominate_bounded_action_intent(proposal.proposal_id,adapter.act_obligation()); assert intent['status']=='ACTION_INTENT_NOMINATED' and intent['intent']['capability_id']==winner
        ex=ms.execute_bounded_action(intent['intent']['intent_id'],adapter.act_obligation()); assert ex['status']=='ACTION_EXECUTED'
        out=adapter.record_execution_outcome(ms,ex['execution']['execution_id'],evidence_id=f'E-MS1955-{label}',capture_id=f'CAP-MS1955-{label}')
        assert out['status']=='ACTION_OUTCOME_OBSERVED'
        return {
            'label':label,'effects':effects,'winner':winner,'winner_effect':effects[winner],
            'proposal_final_state':proposal.final_state_id,'proposal_effect':proposal.predicted_value_effect,
            'actual_final_state':out['outcome']['actual_next_state_id'],'actual_value':out['outcome']['observed_value'],
            'individual_commitments':individual,'relations':relations,
        }
    finally:
        _close(ms);td.cleanup()


def run_choice_reversal():
    a=run_world({'ACT-A':3.2,'ACT-Z':2.5},'STRONG-A')
    b=run_world({'ACT-A':2.5,'ACT-Z':3.2},'STRONG-Z')
    assert a['winner']=='ACT-A' and b['winner']=='ACT-Z'
    assert a['winner_effect']==b['winner_effect']==3.2
    return {
        'status':'PASS','world_a':a,'world_b':b,
        'earned':'MULTI_ACTION_SHADOW_SUBSTRATE_SELECTION_FOLLOWS_LEARNED_REGULATORY_CONSEQUENCE_NOT_OPAQUE_IDENTIFIER_ORDER',
        'semantic_preference_authority':'NONE',
    }


def main(): print(json.dumps(run_choice_reversal(),indent=2,sort_keys=True))
if __name__=='__main__': main()
