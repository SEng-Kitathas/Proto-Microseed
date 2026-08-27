from microseed.development.epistemic_action import EpistemicDecisionBearingContext,search_represented_discriminating_programs
from tests.embodiment.test_ms1808_pass01_discriminator_beyond_native_two_step_grammar import rel


def test_same_current_start_mapping_does_not_collapse_distinct_handles_into_generator_identity():
    # X and Y are observationally identical at the query start: each maps the two live
    # alternatives to exactly the same split. Elsewhere in the represented frame they
    # differ, so current-start equality is only a local edge fact, not a complete
    # primitive transformation identity.
    model0=(rel('S0','X','A'),rel('S0','Y','A'),rel('S9','X','P'),rel('S9','Y','Q'))
    model1=(rel('S0','X','B'),rel('S0','Y','B'),rel('S9','X','R'),rel('S9','Y','S'))
    dc=EpistemicDecisionBearingContext((model0,model1),())
    result=search_represented_discriminating_programs(decision_context=dc,start_state_id='S0',action_tokens=('X','Y'))
    assert result['status']=='REPRESENTED_INFORMATIVE_PROGRAMS_FOUND'
    assert set(result['programs'])=={('X',),('Y',)}
    assert result['generator_equivalence_authority']=='NONE'
    assert result['physical_affordance_closure_authority']=='NONE'
    # Search may have exhausted this query-local represented start surface; that still
    # says nothing about complete extensional generator identity across the frame.
    assert result['closure_authority']=='REPRESENTED_QUERY_LOCAL_ONLY'
