from scratch.lang_segment_state_operand_carrier_prototype import derive_current_structural_segment_side_child_carriers
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_direct_digest,_close


def test_read_only_segment_side_carriers_preserve_exact_composition_identity_and_provenance():
    left_digest,left_sigs=_direct_digest(('R4','T9'),132000)
    right_digest,right_sigs=_direct_digest(('R4','K7'),133000)
    td,m,world,seeded=_setup('SEGMENT-OPERAND-CARRIER')
    try:
        _boundary(m,('R4','T9','R4','K7'),134000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        before=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        out=derive_current_structural_segment_side_child_carriers(m,max_records=65536)
        after=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        assert out['status']=='CURRENT_STRUCTURAL_SEGMENT_SIDE_CHILD_CARRIERS_DERIVED',out
        assert out['carrier_count']==2
        assert before==after
        left,right=out['carriers']
        assert (left['side'],right['side'])==('LEFT','RIGHT')
        assert left['composition_content_digest_sha256']==left_digest
        assert right['composition_content_digest_sha256']==right_digest
        assert tuple(left['ordered_operational_referent_signatures'])==left_sigs
        assert tuple(right['ordered_operational_referent_signatures'])==right_sigs
        for c in (left,right):
            assert c['segment_state_evidence_ref']==[state['segment_state_evidence_id'],state['segment_state_evidence_sha256']]
            assert c['boundary_evidence_ref']==[state['boundary_evidence_id'],state['boundary_evidence_sha256']]
            assert c['historical_event_authority']==c['flattening_authority']==c['associativity_authority']=='NONE'
        assert out['caller_supplied_segment_state_id']==out['caller_supplied_side']==out['caller_supplied_child_order']==out['caller_supplied_grouping']=='NO'
    finally:
        _close(m);td.cleanup()


def test_segment_side_carrier_derivation_is_idempotent_read_only_and_chronology_owned():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-CARRIER-IDEMP')
    try:
        _boundary(m,('R4','T9','R4','K7'),135000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        before=tuple(r['evidence_id'] for r in m.evidence.list())
        a=derive_current_structural_segment_side_child_carriers(m,max_records=65536)
        b=derive_current_structural_segment_side_child_carriers(m,max_records=65536)
        assert a==b
        assert tuple(r['evidence_id'] for r in m.evidence.list())==before
        assert a['selection_basis']=='CURRENT_STRUCTURAL_SEGMENT_STATE_EVIDENCE_APPEND_ORDER_THEN_LEFT_RIGHT'
        assert a['historical_event_authority']==a['ledger_rewrite_authority']==a['semantic_grouping_authority']==a['effect_authority']==a['scheduler_authority']=='NONE'
    finally:
        _close(m);td.cleanup()
