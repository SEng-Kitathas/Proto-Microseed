import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _run(phases,base):
    td=TemporaryDirectory(prefix='boundary-occasion-phase-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-OCCASION-PHASE')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        for i,(t,phase) in enumerate(zip(('R4','T9','R4','K7'),phases)):
            r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
        out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',out
        return out['boundary_content_digest_sha256'],out['split_index'],out['ordered_operational_referent_signatures']
    finally:_close(m);td.cleanup()


def test_phase_labels_do_not_change_structural_boundary_content():
    a=_run(('A','A','A','A'),80000)
    b=_run(('LEFT','LEFT','RIGHT','RIGHT'),81000)
    c=_run(('NONSENSE-1','NONSENSE-2','NONSENSE-3','NONSENSE-4'),82000)
    assert a==b==c


def test_production_owner_contains_no_clock_pause_phase_semantics_planner_or_action_creation_path():
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_boundary_occasion)
    lower=src.lower()
    for forbidden in ('time.time','monotonic','sleep(','timeout','pause','phase','punctuation','grammar','semantic_role','planner','scheduler','execute_bounded_action(','nominate_bounded_action_intent(','register_capability('):
        assert forbidden not in lower
    assert 'selection_authority":"content_uniqueness_only"' in lower.replace(' ', '')
    assert 'retroactive_composition_rewrite_authority":"none"' in lower.replace(' ', '')
    assert 'effect_authority":"none"' in lower.replace(' ', '')
