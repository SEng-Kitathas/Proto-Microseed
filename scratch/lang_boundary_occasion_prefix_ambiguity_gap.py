from __future__ import annotations

from microseed.runtime.entity import action_result_digest
from scratch.lang_arity_four_grounded_referents_fixture import fixture,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase)
        assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def _prefix_snapshot(m,start_seq):
    current=[]
    for e in m.store.events():
        if int(e.get('seq',-1))<=int(start_seq): continue
        current.append({'kind':e.get('kind'),'payload':e.get('payload')})
    return action_result_digest(current),tuple(e['kind'] for e in current)


def _run(final_arity:int,base:int):
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        start_seq=max(int(e.get('seq',-1)) for e in m.store.events())
        _obs(m,('R4','T9'),'PREFIX-AMBIG',base)
        snap,kinds=_prefix_snapshot(m,start_seq)
        auto_boundary=[e for e in m.store.events() if int(e.get('seq',-1))>start_seq and e.get('kind') in ('BOUNDED_ACTION_EXECUTED','OWNED_COMPOSITION_WINDOW_BOUNDARY','OPERAND_WINDOW_BOUNDARY')]
        assert not auto_boundary,auto_boundary
        if final_arity>=3:_obs(m,('W3',),'PREFIX-AMBIG',base+2)
        if final_arity>=4:_obs(m,('K7',),'PREFIX-AMBIG',base+3)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        assert out['derived_arity']==final_arity,out
        return {'prefix_digest':snap,'prefix_kinds':kinds,'final_arity':out['derived_arity'],'composition_digest':out['composition_content_digest_sha256']}
    finally:
        _close(m);td.cleanup()


def run_gap()->dict[str,object]:
    a2=_run(2,42000);a3=_run(3,42000);a4=_run(4,42000)
    assert a2['prefix_digest']==a3['prefix_digest']==a4['prefix_digest']
    return {
        'status':'STOP_VALID_COMPOSITION_PREFIX_DOES_NOT_OWN_BOUNDARY_OCCASION',
        'shared_two_token_prefix_digest':a2['prefix_digest'],
        'shared_prefix_store_kinds':a2['prefix_kinds'],
        'lawful_final_arities':(a2['final_arity'],a3['final_arity'],a4['final_arity']),
        'same_owned_prefix_supports_multiple_lawful_continuations':'YES',
        'automatic_boundary_event_after_two_tokens':'NO',
        'caller_invocation_timing_currently_selects_when_composition_evidence_closes_window':'YES',
        'valid_prefix_boundary_authority':'NONE',
        'localized_gap':'OWNED_NONSEMANTIC_BOUNDARY_OCCASION_DISCRIMINATOR_MISSING',
    }
