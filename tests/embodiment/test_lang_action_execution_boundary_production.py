from scratch.lang_arity_four_grounded_referents_fixture import fixture,_close,_observe_s0
from scratch.lang_c08c_native_owned_affordance_relation import ACT,_proposal
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _bare_exec(m,cid,serial):
    p=_proposal(m,cid,serial);n=m.nominate_bounded_action_intent(p.proposal_id,ACT);assert n['status']=='ACTION_INTENT_NOMINATED',n
    x=m.execute_bounded_action(n['intent']['intent_id'],ACT);assert x['status']=='ACTION_EXECUTED',x
    return x


def test_production_generalized_owner_recognizes_authenticated_bare_action_execution_as_window_boundary():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _observe_s0(m,'PROD-BOUNDARY-RESET')
        _obs(m,('R4','T9'),'PROD-BOUNDARY-PRE',27000)
        x=_bare_exec(m,'QA',270)
        _obs(m,('W3','K7'),'PROD-BOUNDARY-POST',27100)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        assert out['derived_arity']==2
        assert out['ordered_operational_referent_signatures']==(seeded['mapping']['W3'],seeded['mapping']['K7'])
        assert out['last_window_boundary']['kind']=='BOUNDED_ACTION_EXECUTED'
        assert out['last_window_boundary']['execution_id']==x['execution']['execution_id']
        assert out['window_chronology_basis']=='AUTHENTICATED_DURABLE_STORE_EVENT_CHRONOLOGY'
        assert out['action_execution_boundary_recognition']=='AUTHENTICATED_CURRENT_RUNTIME_ONLY'
        assert out['action_execution_boundary_creation_authority']=='NONE'
        assert out['caller_supplied_boundary']=='NO'
        row=m.evidence.get(out['composition_evidence_id'])
        assert row is not None
        payload=row['payload']
        assert payload['last_window_boundary']['execution_id']==x['execution']['execution_id']
        assert payload['action_execution_boundary_creation_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_rejected_action_and_unrelated_store_event_do_not_delimit_production_window():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _observe_s0(m,'PROD-BOUNDARY-NOEXEC-RESET')
        _obs(m,('R4','T9'),'PROD-BOUNDARY-NOEXEC-PRE',27200)
        bad=m.execute_bounded_action('NO-SUCH-INTENT',ACT)
        assert bad['status']=='NO_EXECUTION'
        m.store.append('OPAQUE_EVIDENCE_ASSOCIATION_REGISTERED',{'noise':'not-boundary'})
        _obs(m,('W3','K7'),'PROD-BOUNDARY-NOEXEC-POST',27300)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        assert out['derived_arity']==4
    finally:_close(m);td.cleanup()


def test_forged_action_execution_store_event_blocks_production_window_instead_of_delimiting_it():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _obs(m,('R4','T9'),'PROD-BOUNDARY-FORGE-PRE',27400)
        m.store.append('BOUNDED_ACTION_EXECUTED',{'execution_id':'FORGED','intent_id':'FORGED','capability_id':'QA'})
        _obs(m,('W3','K7'),'PROD-BOUNDARY-FORGE-POST',27500)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='ACTION_EXECUTION_BOUNDARY_NOT_AUTHENTICATED',out
    finally:_close(m);td.cleanup()
