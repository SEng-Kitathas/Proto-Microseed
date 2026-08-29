from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter, AdapterConfig
from scratch.ms1956_process_isolated_environment import ProcessChargeWorld, ProcessQualificationSource
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def run_pre_repair_hostile():
    td=tempfile.TemporaryDirectory(prefix='ms1957-pre-'); root=Path(td.name)
    world=ProcessChargeWorld(); source=ProcessQualificationSource()
    adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id='MS1957-PRE'),qualification_source=source)
    ms=Microseed(root)
    try:
        adapter.attach(ms)
        relation_id,_=adapter.train_actual_history(ms,'PROC-CHARGE')
        proposal=adapter.zero_row_rehearsal(ms,'PROC-CHARGE'); assert proposal is not None
        cmt=ms.derive_bounded_action_commitment(proposal.proposal_id); assert cmt.commitment.value=='YES'
        adapter.reset_control(ms,'PRE-KILL')
        intent=ms.nominate_bounded_action_intent(proposal.proposal_id,adapter.act_obligation()); assert intent['status']=='ACTION_INTENT_NOMINATED'

        before={
            'relation':ms.action_outcome_predictive_relation_status(relation_id),
            'proposal':ms.counterfactual_rehearsal_status(proposal.proposal_id),
            'capability_qualification':ms.capabilities.contracts['PROC-CHARGE'].qualification.value,
            'execution_count':len(ms.action_closure.executions),
        }
        assert before['relation']['status']=='CURRENT_PREDICTIVE_RELATION'
        assert before['proposal']['status']=='CURRENT_REHEARSAL_PROPOSAL'

        # External reality disappears after the internal decision is current.
        world.proc.kill(); world.proc.wait(timeout=5)
        assert world.proc.poll() is not None

        after_kill_before_execution={
            'relation':ms.action_outcome_predictive_relation_status(relation_id),
            'proposal':ms.counterfactual_rehearsal_status(proposal.proposal_id),
            'capability_qualification':ms.capabilities.contracts['PROC-CHARGE'].qualification.value,
        }

        raised=None
        try:
            ms.execute_bounded_action(intent['intent']['intent_id'],adapter.act_obligation())
        except Exception as exc:
            raised=f'{type(exc).__name__}:{exc}'

        result={
            'status':'VIOLATED' if (
                after_kill_before_execution['relation']['status']=='CURRENT_PREDICTIVE_RELATION'
                and after_kill_before_execution['proposal']['status']=='CURRENT_REHEARSAL_PROPOSAL'
                and raised is not None
            ) else 'BLOCKED',
            'before_kill':before,
            'after_kill_before_execution':after_kill_before_execution,
            'execution_exception':raised,
            'execution_count_after_failure':len(ms.action_closure.executions),
            'outcome_count_after_failure':len(ms.action_closure.outcomes),
            'boundary':'CURRENT_INTERNAL_PREMISES != CURRENT_EXTERNAL_ENDPOINT_LIVENESS',
        }
        assert result['execution_count_after_failure']==before['execution_count']
        assert result['outcome_count_after_failure']>=0
        return result
    finally:
        _close(ms); world.close(); td.cleanup()



def _current_fixture(root: Path, instance: str):
    world=ProcessChargeWorld(); source=ProcessQualificationSource()
    adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id=instance),qualification_source=source)
    ms=Microseed(root)
    adapter.attach(ms)
    relation_id,_=adapter.train_actual_history(ms,'PROC-CHARGE')
    proposal=adapter.zero_row_rehearsal(ms,'PROC-CHARGE'); assert proposal is not None
    cmt=ms.derive_bounded_action_commitment(proposal.proposal_id); assert cmt.commitment.value=='YES'
    adapter.reset_control(ms,f'{instance}-READY')
    intent=ms.nominate_bounded_action_intent(proposal.proposal_id,adapter.act_obligation()); assert intent['status']=='ACTION_INTENT_NOMINATED'
    return ms,world,adapter,relation_id,proposal,intent


def run_known_dead_and_reentry():
    td=tempfile.TemporaryDirectory(prefix='ms1957-dead-'); root=Path(td.name)
    ms,world,adapter,relation_id,proposal,intent=_current_fixture(root,'MS1957-DEAD')
    proposal_id=proposal.proposal_id
    before_exec=len(ms.action_closure.executions); before_out=len(ms.action_closure.outcomes)
    try:
        world.proc.kill(); world.proc.wait(timeout=5); assert not world.is_available()
        # Internal state has not polled reality yet.
        assert ms.action_outcome_predictive_relation_status(relation_id)['status']=='CURRENT_PREDICTIVE_RELATION'
        result=adapter.execute_intent(ms,intent['intent']['intent_id'])
        assert result['status']=='NO_EXECUTION',result
        assert result['reason']=='EXTERNAL_ENDPOINT_NOT_CURRENT'
        assert len(ms.action_closure.executions)==before_exec
        assert len(ms.action_closure.outcomes)==before_out
        stale_rel=ms.action_outcome_predictive_relation_status(relation_id)
        stale_prop=ms.counterfactual_rehearsal_status(proposal_id)
        assert stale_rel['status']=='STALE_PREDICTIVE_RELATION',stale_rel
        assert stale_prop['status']=='UNKNOWN_INCOMPLETE',stale_prop
    finally:
        _close(ms); world.close()

    # Compatible reality reattachment occurs through a fresh runtime session.
    world2=ProcessChargeWorld(); source2=ProcessQualificationSource()
    adapter2=ShadowEnvironmentAdapter(world2,AdapterConfig(adapter_instance_id='MS1957-REENTRY'),qualification_source=source2)
    ms2=Microseed(root)
    try:
        assert relation_id in ms2.action_outcome_learning.relations
        adapter2.attach(ms2)
        rel2=ms2.action_outcome_predictive_relation_status(relation_id)
        prop2=ms2.counterfactual_rehearsal_status(proposal_id)
        assert rel2['status']=='CURRENT_PREDICTIVE_RELATION',rel2
        assert prop2['status']=='CURRENT_REHEARSAL_PROPOSAL',prop2
        adapter2.reset_control(ms2,'REENTRY-READY')
        cmt=ms2.derive_bounded_action_commitment(proposal_id); assert cmt.commitment.value=='YES'
        intent2=ms2.nominate_bounded_action_intent(proposal_id,adapter2.act_obligation()); assert intent2['status']=='ACTION_INTENT_NOMINATED'
        ex=adapter2.execute_intent(ms2,intent2['intent']['intent_id']); assert ex['status']=='ACTION_EXECUTED',ex
        out=adapter2.record_execution_outcome(ms2,ex['execution']['execution_id'],evidence_id='E-MS1957-REENTRY',capture_id='CAP-MS1957-REENTRY')
        assert out['status']=='ACTION_OUTCOME_OBSERVED' and out['outcome']['actual_next_state_id']=='PROC-LEVEL-2'
        return {
            'status':'PASS',
            'dead_endpoint_result':result,
            'stale_relation_after_dead_preflight':stale_rel,
            'stale_proposal_after_dead_preflight':stale_prop,
            'reentry_relation':rel2,
            'reentry_proposal':prop2,
            'reentry_actual_state':out['outcome']['actual_next_state_id'],
            'automatic_reauthorization':'NO',
            'earned':'KNOWN_DEAD_EXTERNAL_ENDPOINT_INVALIDATES_SHADOW_SUBSTRATE_AUTHORITY_BEFORE_EFFECT_AND_COMPATIBLE_REATTACHMENT_RESTORES_HISTORICAL_COMPETENCE',
        }
    finally:
        _close(ms2); world2.close(); td.cleanup()


def run_ambiguous_dispatch():
    td=tempfile.TemporaryDirectory(prefix='ms1957-ambiguous-'); root=Path(td.name)
    ms,world,adapter,relation_id,proposal,intent=_current_fixture(root,'MS1957-AMB')
    try:
        before_exec=len(ms.action_closure.executions); before_out=len(ms.action_closure.outcomes)
        world.crash_after_apply=True
        result=adapter.execute_intent(ms,intent['intent']['intent_id'])
        assert result['status']=='UNKNOWN_EXECUTION',result
        assert result['reason']=='EXTERNAL_ENDPOINT_DISPATCH_AMBIGUOUS'
        # Core must not claim an execution because no handler result was received.
        assert len(ms.action_closure.executions)==before_exec
        assert len(ms.action_closure.outcomes)==before_out
        rel=ms.action_outcome_predictive_relation_status(relation_id)
        prop=ms.counterfactual_rehearsal_status(proposal.proposal_id)
        assert rel['status']=='STALE_PREDICTIVE_RELATION',rel
        assert prop['status']=='UNKNOWN_INCOMPLETE',prop
        assert not world.is_available()
        return {
            'status':'PASS',
            'execution_result':result,
            'relation_after_ambiguous_dispatch':rel,
            'proposal_after_ambiguous_dispatch':prop,
            'execution_count_unchanged':True,
            'outcome_count_unchanged':True,
            'earned':'AMBIGUOUS_EXTERNAL_DISPATCH_REMAINS_UNKNOWN_AND_INVALIDATES_CURRENT_REALITY_PREMISES_WITHOUT_FABRICATING_OUTCOME',
        }
    finally:
        _close(ms); world.close(); td.cleanup()


def run_post_repair():
    return {'known_dead':run_known_dead_and_reentry(),'ambiguous_dispatch':run_ambiguous_dispatch()}

def main(): print(json.dumps(run_post_repair(),indent=2,sort_keys=True))
if __name__=='__main__': main()
