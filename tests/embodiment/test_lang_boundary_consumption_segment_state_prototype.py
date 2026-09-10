from tempfile import TemporaryDirectory
from pathlib import Path

from microseed import Authority,Microseed,Observation
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_boundary_consumption_segment_state_prototype import derive_current_segment_state_from_unique_boundary


def _setup(tag='BOUNDARY-CONSUME'):
    td=TemporaryDirectory(prefix='boundary-consume-proto-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    attach_four_runtime_surface(m,world,tag)
    seeded=seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
    return td,m,seeded

def _obs(m,seq,base,phase):
    for i,t in enumerate(seq):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _direct_digest(seq,base):
    td,m,seeded=_setup('BOUNDARY-CONSUME-DIRECT')
    try:
        _obs(m,seq,base,'BOUNDARY-CONSUME-DIRECT')
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        return out['composition_content_digest_sha256'],out['ordered_operational_referent_signatures']
    finally:_close(m);td.cleanup()


def test_unique_current_boundary_derives_two_read_only_segment_contents_without_writing_or_reordering_ledger():
    td,m,seeded=_setup()
    try:
        _obs(m,('R4','T9','R4','K7'),91000,'BOUNDARY-CONSUME')
        b=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert b['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b
        before_count=m.evidence.count();before_ids=tuple(r['evidence_id'] for r in m.evidence.list())
        out=derive_current_segment_state_from_unique_boundary(m)
        after_ids=tuple(r['evidence_id'] for r in m.evidence.list())
        assert out['status']=='CURRENT_RETROSPECTIVE_SEGMENT_STATE_PROTOTYPE',out
        assert out['split_index']==2
        assert m.evidence.count()==before_count and before_ids==after_ids
        assert out['caller_supplied_boundary_id']==out['caller_supplied_split']==out['caller_supplied_segment_operands']=='NO'
        assert out['ledger_rewrite_authority']==out['historical_event_authority']==out['effect_authority']==out['execution_authority']==out['semantic_grouping_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_prototype_segment_content_digests_exactly_match_earned_bounded_composition_identity_for_same_grounded_segments():
    left_digest,left_sigs=_direct_digest(('R4','T9'),92000)
    right_digest,right_sigs=_direct_digest(('R4','K7'),93000)
    td,m,seeded=_setup('BOUNDARY-CONSUME-EQUIV')
    try:
        _obs(m,('R4','T9','R4','K7'),94000,'BOUNDARY-CONSUME-EQUIV')
        b=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert b['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b
        out=derive_current_segment_state_from_unique_boundary(m)
        assert out['status']=='CURRENT_RETROSPECTIVE_SEGMENT_STATE_PROTOTYPE',out
        assert out['left_composition_content_digest_sha256']==left_digest
        assert out['right_composition_content_digest_sha256']==right_digest
        assert tuple(out['left_content']['ordered_operational_referent_signatures'])==left_sigs
        assert tuple(out['right_content']['ordered_operational_referent_signatures'])==right_sigs
    finally:_close(m);td.cleanup()


def test_two_current_boundary_witnesses_are_ambiguous_without_a_consumption_marker():
    td,m,seeded=_setup('BOUNDARY-CONSUME-MULTI')
    try:
        _obs(m,('R4','T9','R4','K7'),95000,'BOUNDARY-CONSUME-MULTI-A')
        a=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert a['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',a
        reset=m.observe_opaque_control_state(
            Observation('CAP-BOUNDARY-CONSUME-MULTI-B','EXTERNAL','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-BOUNDARY-CONSUME-MULTI-B-WINDOW',
        )
        assert reset['status']=='CURRENT_OPAQUE_CONTROL_STATE',reset
        _obs(m,('T9','W3','T9','R4'),95100,'BOUNDARY-CONSUME-MULTI-B')
        b=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert b['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b
        out=derive_current_segment_state_from_unique_boundary(m)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='UNIQUE_CURRENT_UNCONSUMED_STRUCTURAL_BOUNDARY_WITNESS_REQUIRED',out
        assert out['current_boundary_count']==2
    finally:_close(m);td.cleanup()
