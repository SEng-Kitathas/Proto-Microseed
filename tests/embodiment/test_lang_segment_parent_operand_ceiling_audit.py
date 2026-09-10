import inspect

from microseed import Microseed
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent,_mixed_parent


def test_depth_two_is_earned_but_depth_three_and_generic_recursive_closure_are_explicitly_none():
    td,m,world,seeded=_setup('SEGMENT-PARENT-CEILING')
    try:
        _b2_parent(m,360000); _mixed_parent(m,(3,4),361000)
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['input_parent_depth']==1 and out['composition_depth']==2 and out['child_arity']==2
        assert out['recursive_depth_limit']==2
        assert out['generic_recursive_closure_authority']==out['depth_three_authority']=='NONE'
        assert out['flattening_authority']==out['associativity_authority']=='NONE'
        assert out['historical_event_authority']==out['scheduler_authority']==out['effect_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_new_owner_accepts_only_the_two_earned_depth_one_parent_kinds_not_its_own_depth_two_output():
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_two_recursive_composition)
    accepted=src[src.index('accepted={'):src.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE' in accepted
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE' in accepted
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' not in accepted
    assert '"composition_depth":2' in src
    assert '"depth_three_authority":"NONE"' in src


def test_depth_two_top_level_identity_has_two_parent_digests_not_flattened_grandchildren():
    td,m,world,seeded=_setup('SEGMENT-PARENT-CEILING-NEST')
    try:
        _b2_parent(m,362000); _mixed_parent(m,(2,4),363000)
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536); assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        row=m.evidence.get(out['composition_state_evidence_id']); assert row is not None
        payload=row['payload']
        assert len(payload['ordered_child_composition_content_digests'])==2
        assert len(payload['children'])==2
        assert all(len(c['nested_child_content_digests'])==2 for c in payload['children'])
        top={'operator':payload['composition_operator'],'children':payload['ordered_child_composition_content_digests'],'depth':payload['composition_depth'],'child_arity':payload['child_arity']}
        assert 'ordered_operational_referent_signatures' not in top
        assert payload['flattening_authority']==payload['associativity_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_depth_two_surface_has_budget_only_no_caller_parent_order_grouping_depth_or_output_id():
    sig=inspect.signature(Microseed.derive_and_record_current_native_structural_segment_depth_two_recursive_composition)
    assert tuple(sig.parameters)==('self','max_records')
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_two_recursive_composition).lower()
    assert 'latest_two_distinct_current_depth_one_retrospective_segment_parent_contents_in_evidence_order' in src
    for forbidden in ('parent_ids:', 'parent_order:', 'grouping:', 'depth:', 'output_evidence_id:', 'execute_bounded_action(', 'scheduler(', 'planner('):
        assert forbidden not in str(sig).lower()
