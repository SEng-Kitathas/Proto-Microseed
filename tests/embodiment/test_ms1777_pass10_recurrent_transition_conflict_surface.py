from microseed.development.relational_algebra import OpaqueTransitionSample, discover_opaque_transition_conflicts


def s(i, origin, end, frame='F'):
    return OpaqueTransitionSample(f'S{i}',origin,'q','A',end,frame,0)


def test_one_surprise_does_not_earn_conflict_but_two_recurrent_endpoints_do():
    weak=(s(0,'o0','x'),s(1,'o1','x'),s(2,'o2','y'))
    assert discover_opaque_transition_conflicts(weak)==()
    strong=weak+(s(3,'o3','y'),)
    out=discover_opaque_transition_conflicts(strong)
    assert len(out)==1
    c=out[0]
    assert c.outcome_supports==(('x',2),('y',2))
    assert c.frame_epoch==('F',0)
    assert c.truth_authority==c.causal_explanation_authority=='NONE'
    assert c.state_alias_authority==c.generator_authority=='NONE'
    assert c.evidence_independence_authority=='NONE'


def test_duplicate_origin_cannot_inflate_recurrence_and_frames_never_pool():
    dup=(s(0,'o0','x'),s(1,'o1','x'),s(2,'o2','y'),s(3,'o2','y'))
    assert discover_opaque_transition_conflicts(dup)==()
    cross=(s(0,'o0','x','F1'),s(1,'o1','x','F1'),s(2,'o2','y','F2'),s(3,'o3','y','F2'))
    assert discover_opaque_transition_conflicts(cross)==()
