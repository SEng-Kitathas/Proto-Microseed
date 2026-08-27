from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext,
    derive_current_program_discrimination_commitment,
    derive_program_observable_partition,
)
from microseed.development.epistemic_program import EpistemicProgramTrial
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment


def rel(state, action, nxt):
    return RehearsalTransitionRelation(
        state_id=state, capability_id=action, next_state_id=nxt,
        value_effect=0.0, support=2, consistency=1.0,
        source_evidence_ids=(f'E-{state}-{action}-{nxt}',), capability_epoch=0,
        frame_epoch=('F',0), episode_schema_epoch=('EP',0),
        value_epoch=('V',0),
    )


def trial(steps):
    return EpistemicProgramTrial(
        trial_id='T-'+'-'.join(steps), deficit_id='D',
        discrimination_signature_sha256='a'*64,
        relation_candidate_id='R', relation_candidate_sha256='b'*64,
        steps=tuple(steps), capability_epochs=tuple((s,0) for s in steps),
        capability_signatures=tuple((s,'c'*64) for s in steps),
        frame_epochs=(('F',0),), obligation_id='Q', operational_scope_id='S',
        start_state_id='S0', start_state_evidence_id='E0',
    )


def test_existing_information_owner_can_locate_discriminator_beyond_native_two_step_program_grammar():
    # Both live alternatives make the exact same observations for A then B.
    # Only a third already-represented primitive C exposes the live discriminator.
    common=(rel('S0','A','S1'), rel('S1','B','S2'))
    dc=EpistemicDecisionBearingContext((
        common+(rel('S2','C','P'),),
        common+(rel('S2','C','Q'),),
    ),())
    priority=RelationalCommitment('PRIORITY','decision-bearing',TernaryCommitment.YES,reason='FIXTURE_ALREADY_EARNED_DECISION_BEARING')

    two=trial(('A','B'))
    three=trial(('A','B','C'))

    two_info=derive_current_program_discrimination_commitment(
        trial=two,decision_context=dc,decision_bearing_commitment=priority,
    )
    three_info=derive_current_program_discrimination_commitment(
        trial=three,decision_context=dc,decision_bearing_commitment=priority,
    )

    assert two_info.commitment is TernaryCommitment.NO
    assert two_info.reason=='PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE'
    assert derive_program_observable_partition(trial=two,decision_context=dc)==((0,1),)

    assert three_info.commitment is TernaryCommitment.YES
    assert three_info.reason=='PROGRAM_CAN_CHANGE_OBSERVABLE_EVIDENCE'
    assert derive_program_observable_partition(trial=three,decision_context=dc)==((0,),(1,))

    # This localizes a grammar/reach seam only. It does not establish search exhaustion,
    # generated closure saturation, execution permission, or a generic depth increase.
    assert three.proposal_authority==three.execution_authority==three.truth_authority=='NONE'
