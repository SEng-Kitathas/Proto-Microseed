from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from microseed import Microseed
from scratch.lang_c08d_postrestart_native_relation_rederivation import OpaqueTwoLocusWorld,_attach_runtime_surface,_close
from scratch.lang_systematic_heldout_native_b2_recombination import _seed_current_native_referent_associations,_observe_sequence


def run_hostile() -> dict[str,object]:
    td=TemporaryDirectory(prefix='recursive-b2-child-currentness-'); world=OpaqueTwoLocusWorld(); m=Microseed(Path(td.name))
    try:
        _attach_runtime_surface(m,world,'REC-B2-CURR')
        _seed_current_native_referent_associations(m,world,'R4','T9')
        _observe_sequence(m,('R4','T9'),phase='REC-B2-CURR',base=9000)
        before=m.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
        assert before['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',before
        m.change_capability_dependency('QX',reason='RECURSIVE_CHILD_QX_DRIFT')
        assert not m.capabilities.is_current('QX')
        after=m.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
        violation=(after.get('status')=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED')
        return {
            'status':'VIOLATION_B2_PROFILE_CURRENTNESS_NOT_RECHECKED' if violation else 'CURRENTNESS_GUARD_PRESENT',
            'before_status':before['status'],
            'before_digest':before.get('composition_content_digest_sha256'),
            'drifted_capability_id':'QX',
            'drifted_capability_current':m.capabilities.is_current('QX'),
            'after_status':after.get('status'),
            'after_reason':after.get('reason'),
            'after_digest':after.get('composition_content_digest_sha256'),
            'stale_child_was_accepted':violation,
            'recursive_promotion_allowed':'NO',
        }
    finally:
        _close(m);td.cleanup()
