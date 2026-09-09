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


def test_segment_state_is_not_yet_consumed_as_reusable_composition_operand_by_any_other_production_owner():
    marker='OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE';hits=[]
    for p in Path('microseed').rglob('*.py'):
        for i,l in enumerate(p.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
            if marker in l:hits.append((str(p),i,l.strip()))
    # Current occurrences are confined to validator + producer branch; no downstream owner exists.
    assert hits,hits
    entity=Path(inspect.getsourcefile(Microseed)).read_text(encoding='utf-8')
    consumer_start=entity.index('    def _validate_current_native_structural_segment_state(')
    recursive_start=entity.index('    def derive_and_record_current_native_recursive_b2_ordered_composition(')
    before=entity[:consumer_start];after=entity[recursive_start:]
    assert marker not in before
    assert marker not in after


def test_earned_claim_is_current_derived_state_not_historical_event_or_effectful_composition_backfill():
    td,m,s=_setup()
    try:
        row=m.evidence.get(s['segment_state_evidence_id']);assert row is not None
        p=row['payload']
        assert p['temporality']=='CURRENT_RETROSPECTIVE_DERIVATION_APPENDED_AFTER_BOUNDARY'
        assert p['ledger_rewrite_authority']==p['historical_event_authority']==p['effect_authority']==p['execution_authority']==p['semantic_grouping_authority']=='NONE'
        ordinary=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        assert ordinary==[]
    finally:_close(m);td.cleanup()
