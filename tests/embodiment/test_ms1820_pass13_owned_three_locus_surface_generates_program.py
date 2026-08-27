from microseed import Authority, CapabilityContract, EpistemicStatus, Observation, QualificationState
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord, ActionOutcomeCoordinate, ActionOutcomeRecord
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, act_ob


def _add_effect_c(m, calls):
    m.register_capability(CapabilityContract(
        'C','opaque',{}, {},(),(),Authority.EFFECT,('T',),'CURRENT',{},query_obligation_id='Q',
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: calls.append('C') or {'receipt':'C'}, operational_scope_id='S',
    ))


def _add_value_step(m, *, xid, action, start, end, effect, control_evidence):
    cmt=RelationalCommitment(f'CM-{xid}',f'action:{action}',TernaryCommitment.YES,reason='MS1820_OWNED_HISTORY_FIXTURE')
    intent=BoundedActionIntent(
        intent_id=f'I-{xid}', proposal_id=None, proposal_digest=None, action_commitment=cmt,
        capability_id=action, capability_epoch=0, start_state_id=start,
        control_state_evidence_id=control_evidence, expected_next_state_id=None, expected_value_effect=None,
        value_epoch=('V',0), obligation_id='Q', operational_scope_id='S', basis_kind='MULTI_VALUE_LICENSE',
        required_value_epochs=(('V',0),),
    )
    ex=ActionExecutionRecord(f'X-{xid}',intent.intent_id,action,0,start,(action.lower()*64)[:64],execution_commitment_id=cmt.commitment_id)
    m.action_closure.add_intent(intent); m.action_closure.add_execution(ex)
    evidence_id=f'E-{xid}'
    m.append_evidence(evidence_id,{'kind':'MS1820_OWNED_VALUE_HISTORY'},EpistemicStatus.PRESSURE_SUPPORTED,source='TEST')
    coord=ActionOutcomeCoordinate('V',0,float(effect),float(effect),frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),))
    m.action_closure.add_outcome(ActionOutcomeRecord(f'O-{xid}',ex.execution_id,evidence_id,end,None,None,cmt,value_outcomes=(coord,)))
    return evidence_id


def _add_recurrent_chain(m, prefix, effect, final_state):
    ea=_add_value_step(m,xid=f'{prefix}-A',action='A',start='s0',end='s1',effect=effect,control_evidence=f'E-ROOT-{prefix}')
    eb=_add_value_step(m,xid=f'{prefix}-B',action='B',start='s1',end='s2',effect=effect,control_evidence=ea)
    _add_value_step(m,xid=f'{prefix}-C',action='C',start='s2',end=final_state,effect=effect,control_evidence=eb)


def test_owned_three_locus_history_directly_generates_three_step_candidate_without_external_relation_sets():
    td,m,calls,_,_,_=fixture()
    try:
        _add_effect_c(m,calls)
        _add_recurrent_chain(m,'P1',+1.0,'u')
        _add_recurrent_chain(m,'P2',+1.0,'u')
        _add_recurrent_chain(m,'N1',-1.0,'v')
        _add_recurrent_chain(m,'N2',-1.0,'v')
        # Ensure the current represented starting point is exactly the chain root.
        m.observe_opaque_control_state(Observation('CS-1820','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-1820')

        surface=m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        assert surface['status']=='THREE_LOCUS_CHAIN_MODEL_SURFACE', surface
        assert len(surface['relation_sets'])==2 and all(len(x)==3 for x in surface['relation_sets'])

        result=m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(obligation=act_ob())
        assert result['status']=='REPRESENTED_INFORMATIVE_PROGRAMS_FOUND', result
        assert any(c.steps==('A','B','C') for c in result['candidates'])
        abc=[c for c in result['candidates'] if c.steps==('A','B','C')][0]
        assert abc.truth_authority==abc.execution_authority==abc.qualification_authority==abc.closure_authority=='NONE'
        assert result['alternative_model_set_authority']=='PROPOSAL_ONLY_EPHEMERAL'
        assert result['world_model_authority']==result['causal_explanation_authority']==result['evidence_independence_authority']=='NONE'
        assert calls==[]
    finally:
        td.cleanup()
