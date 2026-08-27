from microseed.development.epistemic_action import EpistemicDecisionBearingContext, derive_program_observable_partition
from microseed.development.epistemic_program import EpistemicProgramTrial
from microseed.development.rehearsal import RehearsalTransitionRelation


def rel(s,a,n):
    return RehearsalTransitionRelation(
        state_id=s, capability_id=a, next_state_id=n, value_effect=0.0,
        support=2, consistency=1.0, source_evidence_ids=(f'E-{s}-{a}-{n}',),
        capability_epoch=0, frame_epoch=('F',0), episode_schema_epoch=('EP',0), value_epoch=('V',0),
    )


def trial(steps):
    return EpistemicProgramTrial(
        trial_id='T-'+'-'.join(steps), deficit_id='D', discrimination_signature_sha256='a'*64,
        relation_candidate_id='R', relation_candidate_sha256='b'*64, steps=tuple(steps),
        capability_epochs=tuple((s,0) for s in steps), capability_signatures=tuple((s,'c'*64) for s in steps),
        frame_epochs=(('F',0),), obligation_id='Q', operational_scope_id='S',
        start_state_id='S0', start_state_evidence_id='E0',
    )


def trace(steps, rows):
    lookup={(r.state_id,r.capability_id):r for r in rows}
    cur='S0'; out=[]
    for action in steps:
        cur=lookup[(cur,action)].next_state_id; out.append(cur)
    return tuple(out)


def test_information_partition_is_too_coarse_to_be_program_transformation_identity():
    # Two different programs both perfectly separate the two alternatives, so the
    # existing information partition is identical, while their predicted observable
    # traces are extensionally different.
    a0=(rel('S0','A','A1'),rel('A1','B','A2'),rel('A2','C','P'),
        rel('S0','X','X1'),rel('X1','Y','X2'),rel('X2','Z','R'))
    a1=(rel('S0','A','A1'),rel('A1','B','A2'),rel('A2','C','Q'),
        rel('S0','X','X1'),rel('X1','Y','X2'),rel('X2','Z','S'))
    dc=EpistemicDecisionBearingContext((a0,a1),())
    p_abc=derive_program_observable_partition(trial=trial(('A','B','C')),decision_context=dc)
    p_xyz=derive_program_observable_partition(trial=trial(('X','Y','Z')),decision_context=dc)
    assert p_abc==p_xyz==((0,),(1,))
    assert (trace(('A','B','C'),a0),trace(('A','B','C'),a1)) != (trace(('X','Y','Z'),a0),trace(('X','Y','Z'),a1))
    # Therefore partition identity is useful for current information value, but is
    # not lawful evidence that the two programs are the same represented transformation.
