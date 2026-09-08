from __future__ import annotations

from scratch.lang_arity_four_grounded_referents_fixture import fixture,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase)
        assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def _run(inject_bookkeeping: bool,base: int) -> dict[str,object]:
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _obs(m,('R4','T9'),'BOUNDARY-BOOKKEEP-PRE',base)
        bookkeeping_event=None
        if inject_bookkeeping:
            token='R4'; key='QA'
            before=len(m.store.events())
            cur=m.assess_opaque_evidence_association_currentness(
                seeded['records'][token],witness_evidence_id=str(seeded['profiles'][key]['evidence_id']))
            assert cur['status']=='CURRENTNESS_CONFIRMED',cur
            after_events=m.store.events()[before:]
            matches=[e for e in after_events if e.get('kind')=='OPAQUE_EVIDENCE_ASSOCIATION_CURRENTNESS_WITNESS']
            assert len(matches)==1,matches
            bookkeeping_event=matches[0]
        _obs(m,('W3','K7'),'BOUNDARY-BOOKKEEP-POST',base+100)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        return {
            'derived_arity':out['derived_arity'],
            'digest':out['composition_content_digest_sha256'],
            'ordered':out['ordered_operational_referent_signatures'],
            'bookkeeping_event_seq':None if bookkeeping_event is None else int(bookkeeping_event['seq']),
            'bookkeeping_kind':None if bookkeeping_event is None else bookkeeping_event['kind'],
            'last_boundary':out.get('last_window_boundary'),
        }
    finally:
        _close(m);td.cleanup()


def run_gap() -> dict[str,object]:
    plain=_run(False,40000)
    with_bookkeeping=_run(True,41000)
    assert plain['derived_arity']==with_bookkeeping['derived_arity']==4
    assert plain['digest']==with_bookkeeping['digest']
    assert plain['ordered']==with_bookkeeping['ordered']
    return {
        'status':'STOP_INTERNAL_BOOKKEEPING_EVENT_CANNOT_OWN_TOKEN_GROUPING_BOUNDARY',
        'plain':plain,
        'with_bookkeeping':with_bookkeeping,
        'same_external_token_sequence':'YES',
        'bookkeeping_optional_without_world_change':'YES',
        'bookkeeping_grouping_authority':'NONE',
        'localized_gap':'NO_LAWFUL_PASSIVE_TOKEN_ONLY_BOUNDARY_OCCASION_PRESENT',
    }
