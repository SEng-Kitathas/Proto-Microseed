from scratch.lang_recursive_b2_child_currentness_hostile import run_hostile


def test_b2_currentness_false_green_is_exposed_before_recursive_promotion():
    r=run_hostile()
    assert r['status']=='VIOLATION_B2_PROFILE_CURRENTNESS_NOT_RECHECKED'
    assert r['before_status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED'
    assert r['drifted_capability_id']=='QX' and r['drifted_capability_current'] is False
    assert r['after_status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED'
    assert r['after_digest']==r['before_digest']
    assert r['stale_child_was_accepted'] is True
    assert r['recursive_promotion_allowed']=='NO'
