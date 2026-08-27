from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, Microseed, OperationalFrameContract, QualificationState, QueryObligation
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment


def build_world(root: Path):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS1754',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    for cid in ('A','B','C'):
        m.register_capability(CapabilityContract(cid,'opaque-action',{}, {},(),(),Authority.EFFECT,('MS1754',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:{'receipt':_cid},operational_scope_id='S'))
        m.frames.bind_capability('F',cid)
    outcomes={}
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1754',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda execution_id,**_: {'next_state_id':outcomes[execution_id]},operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1754',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE_USE'},operational_scope_id='S'))
    m.frames.bind_capability('F','OBS')
    return m,outcomes


def add_transition(m,outcomes,idx,start,action,end, *, authenticated_execution=False):
    cmt=RelationalCommitment(f'CM-{idx}',f'action:{action}',TernaryCommitment.YES,reason='FIXTURE_CURRENT_EFFECT')
    intent=BoundedActionIntent(
        intent_id=f'I-{idx}',proposal_id=f'T-{idx}',proposal_digest='d'*64,action_commitment=cmt,
        capability_id=action,capability_epoch=0,start_state_id=start,control_state_evidence_id=f'CS-{idx}',
        expected_next_state_id=None,expected_value_effect=None,value_epoch=None,obligation_id='Q',operational_scope_id='S',
        basis_kind='EPISTEMIC_PROGRAM_STEP')
    ex=ActionExecutionRecord(f'X-{idx}',intent.intent_id,action,0,start,'h'*64,execution_commitment_id=cmt.commitment_id)
    m.action_closure.add_intent(intent); m.action_closure.add_execution(ex)
    if authenticated_execution:
        m.store.append('BOUNDED_ACTION_EXECUTED',ex.serializable())
    outcomes[ex.execution_id]=end
    r=m.record_bounded_action_outcome_via_observation_basis(
        ex.execution_id,observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
        basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
        evidence_id=f'E-{idx}',capture_id=f'C-{idx}')
    assert r['status']=='ACTION_OUTCOME_OBSERVED'


def test_existing_relational_algebra_discovers_candidate_directly_from_admitted_history():
    with tempfile.TemporaryDirectory(prefix='ms1754-') as td:
        m,outcomes=build_world(Path(td))
        rows=[
            ('s0','A','m0'),('m0','B','e0'),('s0','C','e0'),
            ('s1','A','m1'),('m1','B','e1'),('s1','C','e1'),
        ]
        for idx,row in enumerate(rows): add_transition(m,outcomes,idx,*row,authenticated_execution=True)
        r=m.discover_admitted_opaque_action_composition_candidates()
        assert r['status']=='ADMITTED_RELATIONAL_CANDIDATE_SURFACE'
        assert r['admitted_sample_count']==6
        target=[c for c in r['candidates'] if (c.direct_action_token,c.first_action_token,c.second_action_token)==('C','A','B')]
        assert len(target)==1 and target[0].positive_support==2
        assert r['sample_persistence']==r['candidate_persistence']=='NONE'
        assert r['truth_authority']==r['execution_authority']==r['evidence_independence_authority']=='NONE'
