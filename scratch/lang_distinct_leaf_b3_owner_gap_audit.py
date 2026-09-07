from __future__ import annotations

import inspect
from pathlib import Path

import microseed.runtime.entity as entity
from scratch.lang_recursive_b2_composition_as_operand import run_campaign


def run_audit() -> dict[str,object]:
    recursive=run_campaign('R4','T9')
    assert recursive['status']=='BOUNDED_ONE_EDGE_RECURSIVE_B2_COMPOSITION_AS_OPERAND_EARNED',recursive
    assert recursive['distinct_leaf_b3_arity_generalization']=='NOT_EARNED',recursive
    src=Path(inspect.getsourcefile(entity.Microseed)).read_text(encoding='utf-8')
    direct_b3_markers=[]
    for marker in ('"arity":3','"arity": 3','arity=3','THREE_OPERAND','THREE_LEAF','NARY_ORDERED','N_ARY_ORDERED'):
        if marker in src:
            direct_b3_markers.append(marker)
    methods=[]; current=None; blocks=[]
    for line in src.splitlines():
        if line.startswith('    def '):
            if current is not None: blocks.append(current)
            current=[line]
        elif current is not None:
            current.append(line)
    if current is not None: blocks.append(current)
    for block in blocks:
        text='\n'.join(block)
        if ('ordered_operational_referent_signatures' in text
                or 'RECURSIVE_ORDERED_EVIDENCE_TUPLE' in text):
            methods.append(block[0].strip())
    expected_marker='"arity":3'
    assert expected_marker in direct_b3_markers,direct_b3_markers
    return {
        'status':'CURRENT_DISTINCT_LEAF_B3_OWNER_PRESENT',
        'base_recursive_head':'9c633d096a1f60f4263c10895ed44edd1a6d07bf',
        'existing_grouped_recursive_status':recursive['status'],
        'existing_grouped_recursive_depth':recursive['composition_depth'],
        'existing_grouped_recursive_b3_claim':recursive['distinct_leaf_b3_arity_generalization'],
        'direct_b3_source_markers':tuple(direct_b3_markers),
        'composition_related_methods':tuple(methods),
        'historically_localized_missing_mechanism':'THREE_DISTINCT_CURRENT_GROUNDED_LEAF_OPERAND_CARRIER_AND_ORDERED_B3_OPERATOR',
        'b3_owner_now_embodied':'YES_HARD_BOUNDED_ARITY_3_ONLY',
        'grouped_recursive_parent_counts_as_b3':'NO',
        'flattening_authority':'NONE',
        'associativity_authority':'NONE',
        'generic_nary_systematicity':'NOT_EARNED',
        'semantic_authority':'NONE','grammar_authority':'NONE','truth_authority':'NONE','execution_authority':'NONE',
    }
