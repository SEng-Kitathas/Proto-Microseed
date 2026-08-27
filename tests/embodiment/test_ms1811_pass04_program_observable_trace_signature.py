from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext, derive_program_observable_partition,
    derive_program_observable_trace_signature,
)
from microseed.development.epistemic_program import EpistemicProgramTrial
from microseed.development.rehearsal import RehearsalTransitionRelation


def rel(s,a,n):
    return RehearsalTransitionRelation(state_id=s, capability_id=a, next_state_id=n, value_effect=0.0,
        support=2, consistency=1.0, source_evidence_ids=(f'E-{s}-{a}-{n}',), capability_epoch=0,
        frame_epoch=('F',0), episode_schema_epoch=('EP',0), value_epoch=('V',0))


def trial(steps):
    return EpistemicProgramTrial(trial_id='T-'+'-'.join(steps), deficit_id='D',
        discrimination_signature_sha256='a'*64, relation_candidate_id='R', relation_candidate_sha256='b'*64,
        steps=tuple(steps), capability_epochs=tuple((s,0) for s in steps),
        capability_signatures=tuple((s,'c'*64) for s in steps), frame_epochs=(('F',0),),
        obligation_id='Q', operational_scope_id='S', start_state_id='S0', start_state_evidence_id='E0')


def test_existing_information_owner_exposes_trace_signature_without_authority_gain():
    a0=(rel('S0','A','S1'),rel('S1','B','S2'),rel('S2','C','P'))
    a1=(rel('S0','A','S1'),rel('S1','B','S2'),rel('S2','C','Q'))
    dc=EpistemicDecisionBearingContext((a0,a1),())
    t=trial(('A','B','C'))
    sig=derive_program_observable_trace_signature(trial=t,decision_context=dc)
    assert sig==(('S1','S2','P'),('S1','S2','Q'))
    assert derive_program_observable_partition(trial=t,decision_context=dc)==((0,),(1,))
    assert t.truth_authority==t.execution_authority==t.qualification_authority=='NONE'


def test_missing_represented_transition_leaves_trace_identity_unresolved():
    dc=EpistemicDecisionBearingContext(((rel('S0','A','S1'),),(rel('S0','A','S1'),)),())
    assert derive_program_observable_trace_signature(trial=trial(('A','B')),decision_context=dc) is None
