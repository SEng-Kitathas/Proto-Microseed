from pathlib import Path
from tempfile import TemporaryDirectory
import inspect

from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _setup(tag):
    td=TemporaryDirectory(prefix='boundary-consume-invocation-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    attach_four_runtime_surface(m,world,tag);seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
    return td,m

def _obs(m,seq,base,phase):
    for i,t in enumerate(seq):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _boundary(m,seq,base,phase):
    _obs(m,seq,base,phase)
    b=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
    assert b['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b
    return b


def _run(delayed:bool,base:int):
    td,m=_setup('BOUNDARY-CONSUME-INVOCATION')
    try:
        a=_boundary(m,('R4','T9','R4','K7'),base,'FIRST')
        states=[]
        if not delayed:
            s=m.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s;states.append(s)
        b=_boundary(m,('T9','W3','T9','R4'),base+100,'SECOND')
        while len(states)<2:
            s=m.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s;states.append(s)
        ordinary=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        return [(x['boundary_content_digest_sha256'],x['segment_state_content_digest_sha256']) for x in states],len(ordinary)
    finally:_close(m);td.cleanup()


def test_immediate_vs_delayed_consumption_converges_on_same_ordered_segment_state_contents():
    immediate,oi=_run(False,124000)
    delayed,od=_run(True,125000)
    assert immediate==delayed
    assert oi==od==0


def test_segment_state_evidence_budget_fails_closed_before_partial_selection_or_write():
    td,m=_setup('BOUNDARY-CONSUME-BUDGET')
    try:
        _boundary(m,('R4','T9','R4','K7'),126000,'BUDGET')
        total=m.evidence.count();before=tuple(r['evidence_id'] for r in m.evidence.list())
        out=m.derive_and_record_current_native_structural_segment_state(max_records=total-1)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED',out
        assert out['reason']=='SEGMENT_STATE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET'
        assert tuple(r['evidence_id'] for r in m.evidence.list())==before
    finally:_close(m);td.cleanup()


def test_production_consumer_contains_no_clock_phase_scheduler_planner_action_creation_or_historical_composition_backfill_path():
    names=['_native_structural_segment_state_content_from_boundary','_validate_current_native_structural_segment_state','derive_and_record_current_native_structural_segment_state']
    src='\n'.join(inspect.getsource(getattr(Microseed,n)) for n in names).lower()
    for forbidden in ('time.time','monotonic','sleep(','timeout','pause','phase','punctuation','grammar','semantic_role','planner','scheduler','execute_bounded_action(','nominate_bounded_action_intent(','register_capability('):
        assert forbidden not in src
    assert 'owned_native_bounded_ordered_operational_reference_composition_evidence' not in inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_state).lower()
    assert 'current_retrospective_derivation_appended_after_boundary' in src
    assert 'ledger_rewrite_authority":"none"' in src.replace(' ','')
    assert 'historical_event_authority":"none"' in src.replace(' ','')
    assert 'effect_authority":"none"' in src.replace(' ','')
    assert 'semantic_grouping_authority":"none"' in src.replace(' ','')
