from microseed.development.relational_algebra import (
    OpaqueTransitionSample, discover_one_step_visible_history_refinements,
)


def s(i, origin, start, action, end, frame='F'):
    return OpaqueTransitionSample(f'S{i}',origin,start,action,end,frame,0)


def pair(i, context, end, *, prev_action='P', frame='F'):
    prev=s(f'p{i}',f'po{i}',context,prev_action,'q',frame)
    cur=s(f'c{i}',f'co{i}','q','A',end,frame)
    return prev,cur


def test_two_recurrent_previous_visible_state_contexts_earn_bounded_refinement_without_hidden_state_claim():
    pairs=(pair(0,'p','x'),pair(1,'p','x'),pair(2,'r','y'),pair(3,'r','y'))
    out=discover_one_step_visible_history_refinements(pairs)
    assert len(out)==1
    c=out[0]
    assert c.context_outcomes==(('p','x',2),('r','y',2))
    assert c.context_basis=='PREVIOUS_VISIBLE_STATE_ONLY'
    assert c.hidden_state_authority==c.truth_authority==c.causal_explanation_authority=='NONE'
    assert c.previous_action_identity_authority==c.evidence_independence_authority=='NONE'
    assert c.history_depth_extension_authority=='NONE'


def test_one_trajectory_per_context_is_not_refinement_and_within_context_conflict_remains_unresolved():
    assert discover_one_step_visible_history_refinements((pair(0,'p','x'),pair(1,'r','y')))==()
    ambiguous=(pair(0,'p','x'),pair(1,'p','x'),pair(2,'p','y'),pair(3,'p','y'),pair(4,'r','z'),pair(5,'r','z'))
    assert discover_one_step_visible_history_refinements(ambiguous)==()


def test_previous_action_handle_does_not_create_context_and_frames_never_pool():
    # Same previous visible state under two action handles is one context; conflicting
    # endpoints therefore stay unresolved instead of turning actuator names into state.
    alias=(pair(0,'p','x',prev_action='P1'),pair(1,'p','x',prev_action='P1'),pair(2,'p','y',prev_action='P2'),pair(3,'p','y',prev_action='P2'))
    assert discover_one_step_visible_history_refinements(alias)==()
    cross=(pair(0,'p','x',frame='F1'),pair(1,'p','x',frame='F1'),pair(2,'r','y',frame='F2'),pair(3,'r','y',frame='F2'))
    assert discover_one_step_visible_history_refinements(cross)==()
