from pathlib import Path
from tempfile import TemporaryDirectory
from microseed import EpistemicStatus,Microseed
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def test_exact_boundary_witness_payload_copy_under_second_id_must_not_be_consumable_as_second_boundary_occurrence():
    td=TemporaryDirectory(prefix='boundary-witness-replay-consume-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-WITNESS-REPLAY-CONSUME')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        for i,t in enumerate(('R4','T9','R4','K7')):
            r=observe_opaque_token(m,t,123000+i,phase='BOUNDARY-WITNESS-REPLAY-CONSUME');assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
        b=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert b['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b
        row=m.evidence.get(b['boundary_evidence_id']);assert row is not None
        m.append_evidence('E-REPLAYED-STRUCTURAL-BOUNDARY-COPY',dict(row['payload']),EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-BOUNDARY-REPLAY')
        first=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        second=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert first['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',first
        # Historical violation proof: pre-repair validator accepts the copied payload as a second occurrence.
        assert second['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',second
        assert first['boundary_content_digest_sha256']==second['boundary_content_digest_sha256']
        assert first['boundary_evidence_id']!=second['boundary_evidence_id']
    finally:_close(m);td.cleanup()
