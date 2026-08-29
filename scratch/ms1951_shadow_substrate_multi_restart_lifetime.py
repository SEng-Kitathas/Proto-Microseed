from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter, AdapterConfig
from scratch.ms1949_shadow_substrate_adapter import ChargeWorld
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def record_one(ms,adapter,proposal_id,tag):
    adapter.reset_control(ms,f'{tag}-RESET')
    cmt=ms.derive_bounded_action_commitment(proposal_id); assert cmt.commitment.value=='YES'
    intent=ms.nominate_bounded_action_intent(proposal_id,adapter.act_obligation()); assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],adapter.act_obligation()); assert ex['status']=='ACTION_EXECUTED'
    out=adapter.record_execution_outcome(ms,ex['execution']['execution_id'],evidence_id=f'E-MS1951-{tag}',capture_id=f'CAP-MS1951-{tag}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED' and out['outcome']['actual_next_state_id']=='LEVEL-2'
    return out


def run_lifetime(sessions=3,executions_per_session=3):
    td=tempfile.TemporaryDirectory(prefix='ms1951-lifetime-'); root=Path(td.name)
    m=Microseed(root); a=ShadowEnvironmentAdapter(ChargeWorld(),AdapterConfig(adapter_instance_id='BOOT-0'))
    try:
        a.attach(m); relation_id,_=a.train_actual_history(m,'CHARGE'); p=a.zero_row_rehearsal(m,'CHARGE'); assert p
        proposal_id=p.proposal_id
        baseline_outcomes=len(m.action_closure.outcomes)
    finally:
        _close(m)

    receipts=[]
    for session in range(1,sessions+1):
        ms=Microseed(root)
        try:
            assert relation_id in ms.action_outcome_learning.relations
            pre_rel=ms.action_outcome_predictive_relation_status(relation_id)
            pre_prop=ms.counterfactual_rehearsal_status(proposal_id)
            assert pre_rel['status']=='STALE_PREDICTIVE_RELATION'
            assert pre_prop['status']=='UNKNOWN_INCOMPLETE'
            assert 'CHARGE' not in ms.capabilities.contracts

            adapter=ShadowEnvironmentAdapter(ChargeWorld(),AdapterConfig(adapter_instance_id=f'BOOT-{session}'))
            adapter.attach(ms)
            post_rel=ms.action_outcome_predictive_relation_status(relation_id)
            post_prop=ms.counterfactual_rehearsal_status(proposal_id)
            assert post_rel['status']=='CURRENT_PREDICTIVE_RELATION'
            assert post_prop['status']=='CURRENT_REHEARSAL_PROPOSAL'

            for j in range(executions_per_session):
                record_one(ms,adapter,proposal_id,f'S{session}-X{j}')
            receipts.append({'session':session,'pre_relation':pre_rel['status'],'pre_proposal':pre_prop['status'],'post_relation':post_rel['status'],'post_proposal':post_prop['status'],'outcome_count':len(ms.action_closure.outcomes)})
        finally:
            _close(ms)

    final=Microseed(root)
    try:
        final_outcomes=len(final.action_closure.outcomes)
        assert final_outcomes==baseline_outcomes+sessions*executions_per_session
        assert 'CHARGE' not in final.capabilities.contracts
        assert final.action_outcome_predictive_relation_status(relation_id)['status']=='STALE_PREDICTIVE_RELATION'
        result={'status':'PASS','baseline_outcomes':baseline_outcomes,'final_outcomes':final_outcomes,'sessions':receipts,'earned':'REPEATED_RESTARTS_PRESERVE_AND_EXTEND_DEVELOPMENTAL_HISTORY_WHILE_REQUIRING_FRESH_ENVIRONMENT_AUTHORITY_EACH_SESSION','automatic_reauthorization':'NO'}
        return result
    finally:
        _close(final); td.cleanup()


def main(): print(json.dumps(run_lifetime(),indent=2,sort_keys=True))
if __name__=='__main__': main()
