from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture


def _install(m,outcomes):
    m.register_capability(CapabilityContract('P-1856','opaque',{}, {},(),(),Authority.EFFECT,('MS1856',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'receipt':'P'},operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS-1856','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1856',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda execution_id,**_:{'next_state_id':outcomes[execution_id]},operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS-1856','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1856',),'CURRENT',{},dependencies=('OBS-1856',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('P-1856','A','OBS-1856'): m.frames.bind_capability('F',cid)


def _add(m,outcomes,idx,cap,start,end,control_eid):
    cmt=RelationalCommitment(f'C1856-{idx}',f'action:{cap}',TernaryCommitment.YES,reason='OWNED_HISTORY_REFINEMENT_FIXTURE')
    intent=BoundedActionIntent(f'I1856-{idx}',None,None,cmt,cap,0,start,control_eid,None,None,None,'Q','S',basis_kind='EPISTEMIC_PROGRAM_STEP')
    ex=ActionExecutionRecord(f'X1856-{idx}',intent.intent_id,cap,0,start,'a'*64,execution_commitment_id=cmt.commitment_id)
    m.action_closure.add_intent(intent);m.action_closure.add_execution(ex);m.store.append('BOUNDED_ACTION_EXECUTED',ex.serializable());outcomes[ex.execution_id]=end
    r=m.record_bounded_action_outcome_via_observation_basis(ex.execution_id,observation_capability_id='OBS-1856',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),basis_capability_id='BASIS-1856',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),evidence_id=f'E1856-{idx}',capture_id=f'CAP1856-{idx}')
    assert r['status']=='ACTION_OUTCOME_OBSERVED',r
    return ex.execution_id,r['outcome']['evidence_id']


def _pair(m,outcomes,idx,context,end):
    _,eid=_add(m,outcomes,idx*2,'P-1856',context,'q',f'ROOT-{idx}')
    return _add(m,outcomes,idx*2+1,'A','q',end,eid)[0]


def test_owned_admitted_history_derives_refinement_without_caller_pairs_or_persistence():
    td,m,_,_,_,_=fixture()
    try:
        outcomes={};_install(m,outcomes)
        _pair(m,outcomes,0,'p','x');_pair(m,outcomes,1,'p','x');_pair(m,outcomes,2,'r','y');_pair(m,outcomes,3,'r','y')
        result=m.derive_admitted_one_step_visible_history_refinements()
        assert result['status']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENTS_FOUND',result
        assert result['successor_pair_count']==4
        assert len(result['refinements'])==1
        c=result['refinements'][0]
        assert c.context_outcomes==(('p','x',2),('r','y',2))
        assert result['truth_authority']==result['hidden_state_authority']==result['history_depth_extension_authority']=='NONE'
        assert not any(e['kind'].startswith('ONE_STEP_VISIBLE_HISTORY') for e in m.store.events())
    finally:td.cleanup()


def test_missing_exact_successor_evidence_link_blocks_context_support():
    td,m,_,_,_,_=fixture()
    try:
        outcomes={};_install(m,outcomes)
        _pair(m,outcomes,0,'p','x');_pair(m,outcomes,1,'p','x');_pair(m,outcomes,2,'r','y')
        # Fourth current transition has a recurrent y endpoint but no exact predecessor evidence binding.
        _add(m,outcomes,99,'A','q','y','UNRELATED-EVIDENCE')
        result=m.derive_admitted_one_step_visible_history_refinements()
        assert result['status']=='NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT',result
        assert result['refinements']==()
    finally:td.cleanup()
