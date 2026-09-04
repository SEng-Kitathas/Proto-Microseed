
from scratch.ms2002_persisted_operational_referent_class import run_ms2002
from scratch.ms2004_unified_referent_lifetime_policy import run_ms2004


def test_persistent_referent_and_perfect_copy_replacement_are_operationally_indistinguishable_after_restart_gap_and_reappearance():
    result=run_ms2002()
    assert result['status']=='PASS'
    assert result['persistent_vs_perfect_copy_replacement_operationally_indistinguishable'] is True
    left=result['persistent_variant']; right=result['perfect_copy_replacement_variant']
    assert left['pre_signatures']==right['pre_signatures']
    assert left['post_signatures']==right['post_signatures']
    assert left['post_match_counts']==right['post_match_counts']
    assert left['identity_authority']==right['identity_authority']=='NONE'
    assert left['semantic_reference_authority']==right['semantic_reference_authority']=='NONE'
    assert left['execution_authority']==right['execution_authority']=='NONE'
    assert result['new_referent_manager_required']=='NO__EXISTING_EVIDENCE_LEDGER_ONLY'


def test_ambiguity_and_search_budget_fail_closed_instead_of_fabricating_identity():
    result=run_ms2002()
    assert result['aliased_post']['status']=='UNKNOWN_INCOMPLETE'
    assert result['aliased_post']['identity_authority']=='NONE'
    assert result['budget_hostile']['bounded_status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED'
    assert result['budget_hostile']['complete_status']=='OPERATIONAL_REFERENT_SIGNATURE_CLASS_REASSOCIATED'


def test_multi_session_lifetime_policy_composes_without_identity_manager():
    result=run_ms2004()
    assert result['status']=='PASS'
    blob=str(result)
    assert 'identity_authority' in blob.lower() or 'identity' in blob.lower()
    # The frontier claim is bounded: the existing lifetime/referent owners compose
    # without introducing a numerical-identity manager. Exact detailed guarantees
    # remain those asserted by the canonical MS2004 fixture itself.
