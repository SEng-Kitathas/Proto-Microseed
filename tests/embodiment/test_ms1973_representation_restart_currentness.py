from scratch.ms1973_representation_restart_currentness import run_ms1973


def test_history_refinement_requires_exact_current_premises_after_restart():
    result=run_ms1973()
    assert result['status']=='PASS'
    assert result['no_attachment']['derived_surface_status']=='NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT'
    assert 'CURRENT_HISTORY_REFINEMENT_FOR_TICKET_NOT_FOUND' in result['no_attachment']['admission_error']
    assert result['incompatible_same_id_frame']['rejected_reasons']==['OPERATIONAL_FRAME_CONTENT_DRIFT']
    recovered=result['compatible_reattachment']
    assert recovered['derived_surface_status']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENTS_FOUND'
    assert recovered['persisted_projection_signature_matches_rederived_content'] is True
    assert result['registry_current_flag_authority']=='INSUFFICIENT_ALONE'
    assert result['semantic_category_authority']==result['hidden_state_authority']==result['language_authority']=='NONE'
