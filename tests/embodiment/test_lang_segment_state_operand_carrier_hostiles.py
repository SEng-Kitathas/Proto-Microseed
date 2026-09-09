from microseed import EpistemicStatus
from scratch.lang_segment_state_operand_carrier_prototype import derive_current_structural_segment_side_child_carriers
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_close


def test_segment_side_carrier_fails_closed_on_copied_valid_segment_payload_under_new_id():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-CARRIER-FORGE')
    try:
        _boundary(m,('R4','T9','R4','K7'),136000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        row=m.evidence.get(state['segment_state_evidence_id']);assert row is not None
        m.append_evidence('E-FORGED-SEGMENT-OPERAND-COPY',dict(row['payload']),EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE_COPY')
        out=derive_current_structural_segment_side_child_carriers(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='SEGMENT_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT',out
    finally:_close(m);td.cleanup()


def test_segment_side_carrier_fails_closed_after_underlying_currentness_drift():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-CARRIER-DRIFT')
    try:
        _boundary(m,('R4','T9','R4','K7'),137000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        m.change_capability_dependency('QA',reason='SEGMENT-OPERAND-CARRIER-QA-DRIFT')
        out=derive_current_structural_segment_side_child_carriers(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason'] in {'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE','STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'},out
    finally:_close(m);td.cleanup()


def test_segment_side_carrier_budget_exhaustion_is_not_false_saturation():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-CARRIER-BUDGET')
    try:
        _boundary(m,('R4','T9','R4','K7'),138000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        total=m.evidence.count();assert total>0
        out=derive_current_structural_segment_side_child_carriers(m,max_records=total-1)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED',out
        assert out['total_records']==total and out['max_records']==total-1
    finally:_close(m);td.cleanup()


def test_multiple_segment_states_emit_children_in_persisted_state_order_then_left_right_without_caller_choice():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-CARRIER-MULTI')
    try:
        a=_boundary(m,('R4','T9','R4','K7'),139000)
        b=_boundary(m,('T9','W3','T9','R4'),139100)
        s1=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        s2=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert s1['boundary_evidence_id']==a['boundary_evidence_id']
        assert s2['boundary_evidence_id']==b['boundary_evidence_id']
        out=derive_current_structural_segment_side_child_carriers(m,max_records=65536)
        assert out['status']=='CURRENT_STRUCTURAL_SEGMENT_SIDE_CHILD_CARRIERS_DERIVED',out
        assert out['carrier_count']==4
        carriers=out['carriers']
        assert [(c['segment_state_evidence_ref'][0],c['side']) for c in carriers]==[
            (s1['segment_state_evidence_id'],'LEFT'),(s1['segment_state_evidence_id'],'RIGHT'),
            (s2['segment_state_evidence_id'],'LEFT'),(s2['segment_state_evidence_id'],'RIGHT'),
        ]
        assert out['caller_supplied_segment_state_id']==out['caller_supplied_side']==out['caller_supplied_child_order']==out['caller_supplied_grouping']=='NO'
    finally:_close(m);td.cleanup()


def test_carrier_derivation_does_not_backfill_historical_composition_or_recursive_rows():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-CARRIER-NOBACKFILL')
    try:
        _boundary(m,('R4','T9','R4','K7'),140000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        before=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        out=derive_current_structural_segment_side_child_carriers(m,max_records=65536)
        after=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        assert out['status']=='CURRENT_STRUCTURAL_SEGMENT_SIDE_CHILD_CARRIERS_DERIVED',out
        assert before==after
        forbidden={
            'OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_EVIDENCE',
        }
        assert not [r for r in m.evidence.list() if (r.get('payload') or {}).get('kind') in forbidden]
        assert out['historical_event_authority']==out['ledger_rewrite_authority']==out['flattening_authority']==out['associativity_authority']=='NONE'
    finally:_close(m);td.cleanup()
