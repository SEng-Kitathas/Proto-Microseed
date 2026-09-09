import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _setup():
    td=TemporaryDirectory(prefix='boundary-consume-ceiling-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    attach_four_runtime_surface(m,world,'BOUNDARY-CONSUME-CEILING');seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
    for i,t in enumerate(('R4','T9','R4','K7')):
        r=observe_opaque_token(m,t,127000+i,phase='BOUNDARY-CONSUME-CEILING');assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
    b=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536);assert b['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b
    s=m.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
    return td,m,s


def test_structural_segment_state_consumer_is_not_endogenously_scheduled_by_any_current_runtime_path():
    method='derive_and_record_current_native_structural_segment_state';hits=[]
    for p in Path('microseed').rglob('*.py'):
        for i,l in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
            if method in l:hits.append((str(p),i,l.strip()))
    assert len(hits)==1,hits
    assert hits[0][2].startswith('def derive_and_record_current_native_structural_segment_state(')
    parent='derive_and_record_current_native_structural_segment_b2_recursive_composition';parent_hits=[]
    for p in Path('microseed').rglob('*.py'):
        for i,l in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
            if parent in l:parent_hits.append((str(p),i,l.strip()))
    assert len(parent_hits)==1,parent_hits
    assert parent_hits[0][2].startswith('def derive_and_record_current_native_structural_segment_b2_recursive_composition(')


def test_segment_state_reuse_is_now_explicitly_b2_compatible_only_not_generic_recursive_flattening_or_associativity():
    td,m,s=_setup()
    try:
        out=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['admitted_child_arity']==2 and out['recursive_depth_limit']==1
        assert out['flattening_authority']==out['associativity_authority']=='NONE'
        assert out['semantic_composition_authority']==out['grammar_authority']=='NONE'
        src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_b2_recursive_composition)
        assert 'SEGMENT_STATE_SIDE_NOT_B2_COMPATIBLE_FOR_RECURSIVE_REUSE' in inspect.getsource(Microseed._native_structural_segment_b2_child_carriers)
        assert 'MIXED' not in src.upper() or 'B2_COMPATIBLE' in src.upper()
        old_recursive=inspect.getsource(Microseed.derive_and_record_current_native_recursive_b2_ordered_composition)
        assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE' not in old_recursive
    finally:_close(m);td.cleanup()


def test_earned_claim_is_current_retrospective_operand_reuse_not_historical_event_or_effectful_backfill():
    td,m,s=_setup()
    try:
        parent=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert parent['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',parent
        row=m.evidence.get(parent['composition_state_evidence_id']);assert row is not None
        p=row['payload']
        assert p['temporality']=='CURRENT_RETROSPECTIVE_DERIVATION_APPENDED_AFTER_SEGMENT_STATE'
        assert p['ledger_rewrite_authority']==p['historical_event_authority']==p['effect_authority']==p['execution_authority']=='NONE'
        assert p['flattening_authority']==p['associativity_authority']==p['semantic_composition_authority']==p['grammar_authority']=='NONE'
        assert p['scheduler_authority']==p['authority_gain']=='NONE'
        ordinary=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind') in {
            'OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_EVIDENCE',
        }]
        assert ordinary==[]
    finally:_close(m);td.cleanup()
