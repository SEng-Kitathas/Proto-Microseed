from scratch.lang_arity_four_grounded_referents_fixture import fixture,_close,_observe_s0
from scratch.lang_c08c_native_owned_affordance_relation import ACT,_proposal
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,tokens,phase,base):
    rows=[]
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
        rows.append(r)
    return rows

def _bare_exec(m,cid,serial):
    p=_proposal(m,cid,serial);n=m.nominate_bounded_action_intent(p.proposal_id,ACT);assert n['status']=='ACTION_INTENT_NOMINATED',n
    x=m.execute_bounded_action(n['intent']['intent_id'],ACT);assert x['status']=='ACTION_EXECUTED',x
    return x


def test_exact_action_execution_event_replay_is_detected_not_reused_as_second_boundary():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _observe_s0(m,'REPLAY-ACTION-RESET')
        _obs(m,('R4','T9'),'REPLAY-ACTION-PRE',28000)
        x=_bare_exec(m,'QA',280)
        eid=x['execution']['execution_id']
        event=[row for row in m.store.events() if row.get('kind')=='BOUNDED_ACTION_EXECUTED' and (row.get('payload') or {}).get('execution_id')==eid][-1]
        m.store.append('BOUNDED_ACTION_EXECUTED',dict(event['payload']))
        _obs(m,('W3','K7'),'REPLAY-ACTION-POST',28100)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='ACTION_EXECUTION_BOUNDARY_REPLAY_DETECTED',out
        assert out['execution_id']==eid
    finally:_close(m);td.cleanup()


def test_exact_evidence_store_event_replay_is_detected_not_reused_as_operand_or_boundary():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        rows=_obs(m,('R4','T9'),'REPLAY-EVIDENCE',28200)
        eid=rows[-1]['evidence_id']
        event=[row for row in m.store.events() if row.get('kind')=='EVIDENCE' and (row.get('payload') or {}).get('evidence_id')==eid][-1]
        m.store.append('EVIDENCE',dict(event['payload']))
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='OPERAND_WINDOW_EVIDENCE_EVENT_REPLAY_DETECTED',out
        assert out['evidence_id']==eid
    finally:_close(m);td.cleanup()


def test_post_execution_capability_drift_does_not_erase_historical_action_boundary_or_create_effect_authority():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _observe_s0(m,'BOUNDARY-HISTORY-RESET')
        _obs(m,('R4','T9'),'BOUNDARY-HISTORY-PRE',28300)
        x=_bare_exec(m,'QA',283)
        m.change_capability_dependency('QA',reason='BOUNDARY-HISTORY-QA-DRIFT')
        _obs(m,('W3','K7'),'BOUNDARY-HISTORY-POST',28400)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        assert out['derived_arity']==2
        assert out['last_window_boundary']['execution_id']==x['execution']['execution_id']
        assert out['action_execution_boundary_creation_authority']=='NONE'
        assert out['execution_authority']=='NONE'
    finally:_close(m);td.cleanup()
