from scratch.lang_recursive_b2_child_currentness_hostile import run_hostile


def test_b2_currentness_false_green_is_exposed_before_recursive_promotion():
    r=run_hostile()
    assert r['status']=='CURRENTNESS_GUARD_PRESENT'
    assert r['before_status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED'
    assert r['drifted_capability_id']=='QX' and r['drifted_capability_current'] is False
    assert r['after_status']=='DEFER_UNKNOWN'
    assert r['after_reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED'
    assert r['after_digest'] is None
    assert r['stale_child_was_accepted'] is False
    assert r['recursive_promotion_allowed']=='NO'


from pathlib import Path
from tempfile import TemporaryDirectory
from microseed import Microseed
from scratch.lang_c08d_postrestart_native_relation_rederivation import OpaqueTwoLocusWorld,_attach_runtime_surface,_close
from scratch.lang_systematic_heldout_native_b2_recombination import _seed_current_native_referent_associations,_observe_sequence


def _sibling_drift(kind: str):
    td=TemporaryDirectory(prefix='recursive-b2-sibling-currentness-'); world=OpaqueTwoLocusWorld(); m=Microseed(Path(td.name))
    try:
        _attach_runtime_surface(m,world,'REC-B2-SIBLING')
        _seed_current_native_referent_associations(m,world,'R4','T9')
        _observe_sequence(m,('R4','T9'),phase='REC-B2-SIBLING',base=9100)
        before=m.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
        assert before['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',before
        if kind=='QY':
            m.change_capability_dependency('QY',reason='RECURSIVE_CHILD_QY_DRIFT')
            assert not m.capabilities.is_current('QY')
        elif kind=='FRAME':
            m.change_operational_frame('F',reason='RECURSIVE_CHILD_FRAME_DRIFT')
            assert not m.frames.is_current('F',0)
        else:
            raise AssertionError(kind)
        after=m.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
        return before,after
    finally:
        _close(m);td.cleanup()


def test_second_operand_capability_drift_removes_b2_support():
    before,after=_sibling_drift('QY')
    assert after['status']=='DEFER_UNKNOWN',after
    assert after['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED',after
    assert after.get('composition_content_digest_sha256') is None


def test_frame_drift_removes_b2_support_even_when_association_record_is_still_current():
    before,after=_sibling_drift('FRAME')
    assert after['status']=='DEFER_UNKNOWN',after
    assert after['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED',after
    assert after.get('composition_content_digest_sha256') is None
