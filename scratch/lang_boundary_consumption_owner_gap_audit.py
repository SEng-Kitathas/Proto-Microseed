from __future__ import annotations
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def run_audit():
    source=Path('microseed/runtime/entity.py').read_text(encoding='utf-8')
    consumer_markers=('SEGMENTED_COMPOSITION_STATE','consume_current_native_structural_boundary','derive_and_record_current_native_segmented')
    hits={m:(m in source) for m in consumer_markers}
    td=TemporaryDirectory(prefix='boundary-consumer-gap-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-CONSUMER-GAP')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        for i,t in enumerate(('R4','T9','R4','K7')):
            r=observe_opaque_token(m,t,90000+i,phase='BOUNDARY-CONSUMER-GAP');assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
        before=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        b=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert b['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b
        after=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        comp=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        return {
            'status':'STOP_STRUCTURAL_BOUNDARY_WITNESS_CONSUMER_OWNER_MISSING',
            'consumer_markers_present':hits,
            'boundary_status':b['status'],'split_index':b['split_index'],
            'bounded_composition_count_before':len(before),'bounded_composition_count_after_boundary':len(after),
            'generic_composition_after_boundary_status':comp['status'],'generic_composition_after_boundary_reason':comp.get('reason'),
            'localized_missing_mechanism':'CURRENT_STRUCTURAL_BOUNDARY_WITNESS_TO_RETROSPECTIVE_SEGMENT_COMPOSITION_STATE_OWNER',
            'ledger_rewrite_authority':'NONE','caller_grouping_authority':'NONE','effect_authority':'NONE',
        }
    finally:_close(m);td.cleanup()
