import inspect

from microseed import Microseed
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_close


def test_current_structural_segment_state_has_no_existing_reusable_composition_operand_owner():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-GAP')
    try:
        _boundary(m,('R4','T9','R4','K7'),131000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        rows=m.evidence.list()
        assert len([r for r in rows if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE'])==1
        assert not [r for r in rows if (r.get('payload') or {}).get('kind') in {
            'OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_EVIDENCE',
        }]
        recursive=m.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=65536)
        assert recursive['status']=='DEFER_UNKNOWN',recursive
        assert recursive['reason']=='TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED',recursive
        assert recursive['current_distinct_child_count']==0,recursive

        recursive_src=inspect.getsource(Microseed.derive_and_record_current_native_recursive_b2_ordered_composition)
        assert 'OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE' in recursive_src
        assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE' not in recursive_src
        direct_src=inspect.getsource(Microseed.derive_and_record_current_native_bounded_ordered_composition)
        assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE' not in direct_src
        full_src=inspect.getsource(Microseed)
        refs=[line.strip() for line in full_src.splitlines() if 'OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE' in line]
        assert len(refs)==3,refs  # validator kind check, recorder scan, recorder payload creation
    finally:
        _close(m);td.cleanup()
