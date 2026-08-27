from __future__ import annotations
from microseed import Observation, Authority
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial, begin_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import candidate, act_ob, fob
from tests.embodiment.test_ms1713_tick_reauthorization import two_tick_fixture


def complete_trial(m,trial,dc):
    current=trial
    for idx,(cid,next_state,evid) in enumerate((('A','s1','E-OUT-A'),('B','s2','E-OUT-B'))):
        n=m.nominate_endogenous_epistemic_program_step_intent(current,dc,'FEAS-'+cid,fob(cid),act_ob())
        assert n['status']=='ACTION_INTENT_NOMINATED'
        ec=EpistemicStepExecutionContext(current,feasibility_capability_id='FEAS-'+cid,feasibility_obligation=fob(cid),decision_context=dc)
        ex=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ec); assert ex['status']=='ACTION_EXECUTED'
        xid=ex['execution']['execution_id']
        obs=Observation('OUT-'+cid,'EXT',f'action-execution:{xid}',{'next_state_id':next_state},authority=Authority.OBSERVATION_ONLY)
        out=m.record_bounded_action_outcome(xid,obs,evidence_id=evid); assert out['status']=='ACTION_OUTCOME_OBSERVED'
        current=advance_epistemic_program_trial(current,intent=m.action_closure.intents[n['intent']['intent_id']],execution=m.action_closure.executions[xid],outcome=m.action_closure.outcomes[out['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs))
    assert current.status=='COMPLETE'
    return current

def test_complete_actual_program_evidence_moves_deficit_to_revisit_required_without_answer_authority():
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        done=complete_trial(m,trial,dc)
        r=m.record_completed_epistemic_program_evidence(done,evidence_id='E-PROGRAM')
        assert r['status']=='PROGRAM_EVIDENCE_RECORDED' and r['state']=='REVISIT_REQUIRED'
        assert r['truth_authority']==r['answer_authority']==r['execution_authority']=='NONE'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
    finally: td.cleanup()

def test_revisit_required_blocks_compulsive_reopening_of_same_macro():
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        done=complete_trial(m,trial,dc)
        m.record_completed_epistemic_program_evidence(done,evidence_id='E-PROGRAM')
        st=m.action_closure.current_state
        new=begin_epistemic_program_trial(candidate(),deficit_id='D',discrimination_signature_sha256='d'*64,capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),start_state_id=st.state_id,start_state_evidence_id=st.evidence_id)
        n=m.nominate_endogenous_epistemic_program_step_intent(new,dc,'FEAS-A',fob('A'),act_ob())
        assert n['status']=='ABSTAIN'
        assert n['priority']['commitment'] in {'UNKNOWN','NO'}
        assert calls==['A','B']
    finally: td.cleanup()

def test_forged_complete_trial_step_content_is_rejected_before_revisit():
    from dataclasses import replace
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        done=complete_trial(m,trial,dc)
        badrec=replace(done.step_records[0],actual_next_state_id='FORGED')
        forged=replace(done,step_records=(badrec,)+done.step_records[1:])
        r=m.record_completed_epistemic_program_evidence(forged,evidence_id='E-FORGED')
        assert r['status']=='PROGRAM_EVIDENCE_REJECTED'
        assert m.epistemic_deficits.records['D'].state.value=='ACTION_LIMITED'
    finally: td.cleanup()
