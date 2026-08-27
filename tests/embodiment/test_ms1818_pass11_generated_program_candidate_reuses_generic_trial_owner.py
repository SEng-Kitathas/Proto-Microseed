import pytest
from microseed.development.epistemic_program import GeneratedEpistemicProgramCandidate, begin_generated_epistemic_program_trial
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.types import Authority, CapabilityContract, QualificationState, QueryObligation


def cap(cid):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1818',),'CURRENT',{},
        query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:None,operational_scope_id='S')


def test_generated_three_step_candidate_enters_existing_length_generic_inert_trial_owner():
    reg=CapabilityRegistry()
    for cid in ('A','B','C'): reg.register(cap(cid))
    c=GeneratedEpistemicProgramCandidate('G-ABC',('A','B','C'),('a'*64,'b'*64,'c'*64),(('F',0),))
    t=begin_generated_epistemic_program_trial(c,deficit_id='D',discrimination_signature_sha256='d'*64,
        capabilities=reg,obligation=QueryObligation('Q','probe',required_authority=Authority.EFFECT,operational_scope_id='S'),
        current_frame_epochs={'F':0},start_state_id='S0',start_state_evidence_id='E0')
    assert t.steps==('A','B','C')
    assert t.relation_candidate_id=='G-ABC' and t.relation_candidate_sha256==c.digest()
    assert t.proposal_authority==t.qualification_authority==t.truth_authority==t.execution_authority=='NONE'


def test_generated_program_candidate_rejects_authority_escalation():
    with pytest.raises(ValueError,match='AUTHORITY_ESCALATION'):
        GeneratedEpistemicProgramCandidate('G',('A','B','C'),('a'*64,),(('F',0),),truth_authority='YES')
