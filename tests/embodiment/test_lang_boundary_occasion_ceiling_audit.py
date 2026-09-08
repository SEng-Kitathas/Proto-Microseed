import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _setup():
    td=TemporaryDirectory(prefix='boundary-occasion-ceiling-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    attach_four_runtime_surface(m,world,'BOUNDARY-OCCASION-CEILING')
    seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
    for i,t in enumerate(('R4','T9','R4','K7')):
        r=observe_opaque_token(m,t,83000+i,phase='BOUNDARY-OCCASION-CEILING');assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
    return td,m


def test_structural_boundary_owner_is_not_endogenously_scheduled_by_any_current_microseed_runtime_path():
    method='derive_and_record_current_native_structural_boundary_occasion'
    hits=[]
    for p in Path('microseed').rglob('*.py'):
        txt=p.read_text(encoding='utf-8',errors='ignore')
        for i,l in enumerate(txt.splitlines(),1):
            if method in l:hits.append((str(p),i,l.strip()))
    assert len(hits)==1,hits
    assert hits[0][2].startswith('def derive_and_record_current_native_structural_boundary_occasion(')


def test_durable_structural_boundary_witness_does_not_materialize_left_or_right_composition_evidence():
    td,m=_setup()
    try:
        before=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',out
        after=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        assert len(after)==len(before)
        assert out['retroactive_composition_rewrite_authority']=='NONE'
        assert out['selection_authority']=='CONTENT_UNIQUENESS_ONLY'
    finally:_close(m);td.cleanup()


def test_owner_claim_is_retrospective_structural_not_prospective_semantic_or_effectful():
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_boundary_occasion)
    lower=src.lower()
    assert 'retrospective_recognition_after_extension_conflict' in lower
    assert 'retroactive_composition_rewrite_authority":"none"' in lower.replace(' ','')
    assert 'effect_authority":"none"' in lower.replace(' ','')
    assert 'semantic_grouping_authority":"none"' in lower.replace(' ','')
    assert 'prospective' not in lower
