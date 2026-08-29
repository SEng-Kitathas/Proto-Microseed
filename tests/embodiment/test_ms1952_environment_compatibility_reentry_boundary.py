from scratch.ms1952_cross_world_compatibility_hostile import run_hostile


def test_incompatible_same_id_world_does_not_reactivate_historical_competence():
    result = run_hostile()
    assert result['status'] == 'BLOCKED'
    assert result['relation_after_incompatible_attach']['status'] == 'STALE_PREDICTIVE_RELATION'
    assert result['relation_after_incompatible_attach']['reason'] == 'STRUCTURAL_PREMISE_NOT_CURRENT'
    assert result['proposal_after_incompatible_attach']['status'] == 'UNKNOWN_INCOMPLETE'
    assert result['proposal_after_incompatible_attach']['reason'] == 'REHEARSAL_EVIDENCE_PREMISE_SIGNATURE_DRIFT:SUBSTRATE-ENV-BINDING'
    assert result['old_predicted_final_state'] == 'LEVEL-2'
    assert result['new_world_actual_after_charge'] == 'LEVEL-1'
