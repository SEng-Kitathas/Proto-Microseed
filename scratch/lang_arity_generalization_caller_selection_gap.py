from __future__ import annotations

from scratch.lang_b3_three_grounded_referents_fixture import fixture,_close
from scratch.lang_distinct_leaf_b3_ordered_composition import _observe_sequence


def run_audit() -> dict[str,object]:
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        sx=seeded['mapping']['R4']; sy=seeded['mapping']['T9']; sz=seeded['mapping']['W3']
        _observe_sequence(m,('R4','T9','W3'),phase='ARITY-GAP',base=7000)
        before=m.evidence.count()
        b2=m.derive_and_record_current_native_b2_ordered_composition(max_records=32768)
        assert b2['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',b2
        assert b2['ordered_operational_referent_signatures']==(sy,sz),b2
        # Re-present the exact same three-token operand surface because the B2 output itself is a non-token evidence delimiter.
        _observe_sequence(m,('R4','T9','W3'),phase='ARITY-GAP-B3',base=7100)
        b3=m.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert b3['status']=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',b3
        assert b3['ordered_operational_referent_signatures']==(sx,sy,sz),b3
        return {
            'status':'STOP_ARITY_CURRENTLY_CALLER_SELECTED_BY_METHOD',
            'same_grounded_leaf_set':['R4','T9','W3'],
            'b2_method':'derive_and_record_current_native_b2_ordered_composition',
            'b2_result_arity':2,
            'b2_content':list(b2['ordered_operational_referent_signatures']),
            'b3_method':'derive_and_record_current_native_b3_ordered_composition',
            'b3_result_arity':3,
            'b3_content':list(b3['ordered_operational_referent_signatures']),
            'organism_owned_arity_carrier':'ABSENT',
            'caller_method_choice_changes_arity':'YES',
            'localized_missing_mechanism':'ORGANISM_OWNED_BOUNDED_OPERAND_WINDOW_OR_ARITY_CARRIER',
            'generic_nary':'NOT_EARNED',
            'semantic_authority':'NONE','execution_authority':'NONE',
        }
    finally:
        _close(m);td.cleanup()
