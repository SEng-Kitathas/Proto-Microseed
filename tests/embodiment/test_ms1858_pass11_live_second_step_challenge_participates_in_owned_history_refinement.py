from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture


def _install(m,outcomes):
    m.register_capability(CapabilityContract('P-1858','opaque',{}, {},(),(),Authority.EFFECT,('MS1858',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'receipt':'P'},operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS-1858','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1858',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda execution_id,**_:{'next_state_id':outcomes[execution_id]},operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS-1858','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1858',),'CURRENT',{},dependencies=('OBS-1858',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('P-1858','A','B','OBS-1858'): m.frames.bind_capability('F',cid)


def _close(m,outcomes,xid,end,tag):
    outcomes[xid]=end
    return m.record_bounded_action_outcome_via_observation_basis(
        xid,observation_capability_id='OBS-1858',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
        basis_capability_id='BASIS-1858',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
        evidence_id=f'E1858-{tag}',capture_id=f'C1858-{tag}')


def _add_history_pair(m,outcomes,idx,context,end):
    c1=RelationalCommitment(f'P-C-{idx}','action:P',TernaryCommitment.YES,reason='HISTORY_CONTEXT')
    i1=BoundedActionIntent(f'P-I-{idx}',None,None,c1,'P-1858',0,context,f'ROOT-{idx}',None,None,None,'Q','S',basis_kind='EPISTEMIC_PROGRAM_STEP')
    x1=ActionExecutionRecord(f'P-X-{idx}',i1.intent_id,'P-1858',0,context,'p'*64,execution_commitment_id=c1.commitment_id)
    m.action_closure.add_intent(i1);m.action_closure.add_execution(x1);m.store.append('BOUNDED_ACTION_EXECUTED',x1.serializable())
    o1=_close(m,outcomes,x1.execution_id,'s1',f'P{idx}');assert o1['status']=='ACTION_OUTCOME_OBSERVED',o1
    c2=RelationalCommitment(f'B-C-{idx}','action:B',TernaryCommitment.YES,reason='HISTORY_CURRENT')
    i2=BoundedActionIntent(f'B-I-{idx}',None,None,c2,'B',0,'s1',o1['outcome']['evidence_id'],None,None,None,'Q','S',basis_kind='EPISTEMIC_PROGRAM_STEP')
    x2=ActionExecutionRecord(f'B-X-{idx}',i2.intent_id,'B',0,'s1','b'*64,execution_commitment_id=c2.commitment_id)
    m.action_closure.add_intent(i2);m.action_closure.add_execution(x2);m.store.append('BOUNDED_ACTION_EXECUTED',x2.serializable())
    o2=_close(m,outcomes,x2.execution_id,end,f'B{idx}');assert o2['status']=='ACTION_OUTCOME_OBSERVED',o2


def _run_step(m,outcomes,trial,dc,cap,end,tag):
    n=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial,dc,act_ob());assert n['status']=='ACTION_INTENT_NOMINATED',n;assert n['intent']['capability_id']==cap
    ctx=EpistemicStepExecutionContext(trial,decision_context=dc)
    ex=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx);assert ex['status']=='ACTION_EXECUTED',ex
    xid=ex['execution']['execution_id'];out=_close(m,outcomes,xid,end,tag);assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    adv=advance_epistemic_program_trial(trial,intent=m.action_closure.intents[n['intent']['intent_id']],execution=m.action_closure.executions[xid],outcome=m.action_closure.outcomes[out['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs))
    bearing=m.assess_epistemic_program_step_outcome_bearing(trial,adv,dc)
    return adv,bearing


def test_live_second_step_model_challenge_joins_recurrent_visible_history_refinement():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        outcomes={};_install(m,outcomes)
        t1,b1=_run_step(m,outcomes,trial,dc,'A','s1','LIVE-A')
        assert b1['status']=='CONSENSUS_NONDISCRIMINATING',b1
        t2,b2=_run_step(m,outcomes,t1,dc,'B','sx','LIVE-B')
        assert b2['status']=='MODEL_SPACE_CHALLENGE' and b2['revisit_status']=='REVISIT_REQUIRED',b2
        # Same previous-visible-state context s0 recurs once more through a different
        # previous action handle; action identity is intentionally ignored by refinement.
        _add_history_pair(m,outcomes,0,'s0','sx')
        _add_history_pair(m,outcomes,1,'r','s2')
        _add_history_pair(m,outcomes,2,'r','s2')
        result=m.derive_admitted_one_step_visible_history_refinements()
        assert result['status']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENTS_FOUND',result
        target=[c for c in result['refinements'] if (c.start_token,c.action_token)==('s1','B')]
        assert len(target)==1
        assert set(target[0].context_outcomes)=={('s0','sx',2),('r','s2',2)}
        assert target[0].previous_action_identity_authority=='NONE'
        assert target[0].hidden_state_authority==target[0].history_depth_extension_authority=='NONE'
        assert calls==['A','B']
    finally:td.cleanup()
