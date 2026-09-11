from __future__ import annotations

import inspect
from pathlib import Path
import microseed.runtime.entity as entity
from scratch.lang_c08g_native_b2_ordered_composition import run_campaign


def run_audit() -> dict[str,object]:
    c08g=run_campaign('R4','T9')
    assert c08g['status']=='C08G_NATIVE_B2_ORDERED_COMPOSITION_REEMBODIED',c08g
    src=Path(inspect.getsourcefile(entity.Microseed)).read_text(encoding='utf-8')
    owned_methods=[]
    current=None; blocks=[]
    for line in src.splitlines():
        if line.startswith('    def '):
            if current is not None: blocks.append(current)
            current=[line]
        elif current is not None:
            current.append(line)
    if current is not None: blocks.append(current)
    for block in blocks:
        text='\n'.join(block)
        if ('ORDERED_EVIDENCE_TUPLE' in text or 'composition_operator' in text or 'composition_content_digest_sha256' in text):
            owned_methods.append(block[0].strip())
    expected=(
        'def derive_and_record_current_native_b2_ordered_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
        'def derive_and_record_current_native_b3_ordered_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
        'def derive_and_record_current_native_bounded_ordered_composition(',
        'def _native_structural_segment_state_content_from_boundary(',
        'def _validate_current_native_structural_segment_state(',
        'def derive_and_record_current_native_structural_segment_state(',
        'def _native_structural_segment_b2_child_carriers(',
        'def _validate_current_native_structural_segment_b2_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_b2_recursive_composition(',
        'def _native_structural_segment_bounded_child_carriers(',
        'def _validate_current_native_structural_segment_bounded_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_bounded_recursive_composition(',
        'def _native_depth_one_structural_segment_parent_child_carrier(',
        'def _validate_current_native_structural_segment_depth_two_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_depth_two_recursive_composition(',
        'def _native_depth_two_structural_segment_parent_child_carrier(',
        'def _validate_current_native_structural_segment_depth_three_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_depth_three_recursive_composition(',
        'def _native_depth_three_structural_segment_parent_child_carrier(',
        'def _validate_current_native_structural_segment_depth_four_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_depth_four_recursive_composition(',
        'def derive_and_record_current_native_recursive_b2_ordered_composition(',
    )
    assert tuple(owned_methods)==expected,owned_methods
    return {
        'status':'CURRENT_BOUNDED_COMPOSITION_OWNERS_PRESENT',
        'c08g_xy_available_in_research_helper':c08g['xy_composition_digest_sha256'],
        'c08g_yx_available_in_research_helper':c08g['yx_composition_digest_sha256'],
        'c08g_order_sensitive':c08g['order_sensitive'],
        'production_owned_composition_methods':owned_methods,
        'historically_localized_missing_mechanism':'MICROSEED_OWNED_BOUNDED_ORDERED_COMPOSITION_OPERATOR',
        'binding_now_embodied':'YES_BOUNDED_B2_PLUS_DIRECT_B3_PLUS_BOUNDED_ARITY_2_TO_4_PLUS_FIXED_DEPTH_ONE_SEGMENT_REUSE_PLUS_ONE_EXPLICIT_DEPTH_TWO_EDGE_PLUS_ONE_EXPLICIT_MIXED_DEPTH_THREE_EDGE_PLUS_ONE_EXPLICIT_MIXED_DEPTH_FOUR_EDGE',
        'structural_segment_operand_scope':'BOUNDED_DEPTH_ONE_TO_DEPTH_TWO_PLUS_MIXED_DEPTH_THREE_PLUS_MIXED_DEPTH_FOUR_WITH_FULL_ANCESTRY_EXCLUSION',
        'generic_unbounded_structural_segment_operand':'NOT_EARNED',
        'recursive_depth':'4_FIXED_MIXED_EDGE_ONLY',
        'direct_b3_arity':'3_ONLY',
        'bounded_generalized_arity':'2_TO_4_ONLY',
        'generic_unbounded_systematicity':'NOT_EARNED',
        'generic_recursive_closure':'NOT_EARNED',
        'depth_three_reuse':'ONE_EXPLICIT_MIXED_DEPTH_EDGE_ONLY',
        'depth_four_reuse':'ONE_EXPLICIT_MIXED_DEPTH_EDGE_ONLY',
        'new_planner_required':'NO',
        'grammar_authority':'NONE','semantic_authority':'NONE','truth_authority':'NONE','execution_authority':'NONE',
    }
