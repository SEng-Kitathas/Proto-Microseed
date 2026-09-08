from scratch.lang_arity_four_grounded_referents_fixture import fixture,_close,_observe_s0
from scratch.lang_c08c_native_owned_affordance_relation import ACT,_proposal
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_operand_window_store_aware_prototype import derive_store_aware_bounded_composition_prototype,derive_store_aware_operand_window


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _bare_exec(m,cid,serial):
    p=_proposal(m,cid,serial);n=m.nominate_bounded_action_intent(p.proposal_id,ACT);assert n['status']=='ACTION_INTENT_NOMINATED',n
    x=m.execute_bounded_action(n['intent']['intent_id'],ACT);assert x['status']=='ACTION_EXECUTED',x
    return x


def test_authenticated_bare_action_execution_delimits_post_action_token_window_without_outcome_evidence():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _observe_s0(m,'STORE-AWARE-RESET')
        _obs(m,('R4','T9'),'STORE-AWARE-PRE',21000)
        x=_bare_exec(m,'QA',210)
        _obs(m,('W3','K7'),'STORE-AWARE-POST',21100)
        out=derive_store_aware_bounded_composition_prototype(m)
        assert out['status']=='CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE',out
        assert out['derived_arity']==2
        assert out['ordered_operational_referent_signatures']==(seeded['mapping']['W3'],seeded['mapping']['K7'])
        assert out['last_boundary']['kind']=='BOUNDED_ACTION_EXECUTED'
        assert out['last_boundary']['execution_id']==x['execution']['execution_id']
        assert out['caller_supplied_boundary']==out['caller_supplied_arity']=='NO'
        assert out['execution_authority_gain']==out['semantic_grouping_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_rejected_action_attempt_creates_no_boundary_and_unrelated_store_event_has_no_grouping_authority():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _observe_s0(m,'STORE-AWARE-NOEXEC-RESET')
        _obs(m,('R4','T9'),'STORE-AWARE-NOEXEC-PRE',21200)
        bad=m.execute_bounded_action('NO-SUCH-INTENT',ACT)
        assert bad['status']=='NO_EXECUTION'
        m.store.append('OPAQUE_EVIDENCE_ASSOCIATION_REGISTERED',{'noise':'not-a-boundary'})
        _obs(m,('W3','K7'),'STORE-AWARE-NOEXEC-POST',21300)
        out=derive_store_aware_bounded_composition_prototype(m)
        assert out['status']=='CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE',out
        assert out['derived_arity']==4
    finally:_close(m);td.cleanup()


def test_forged_action_execution_store_event_is_refused_not_promoted_to_boundary():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _obs(m,('R4','T9'),'STORE-AWARE-FORGE-PRE',21400)
        m.store.append('BOUNDED_ACTION_EXECUTED',{'execution_id':'FORGED','intent_id':'FORGED','capability_id':'QA'})
        _obs(m,('W3','K7'),'STORE-AWARE-FORGE-POST',21500)
        out=derive_store_aware_operand_window(m)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='ACTION_EXECUTION_BOUNDARY_NOT_AUTHENTICATED',out
    finally:_close(m);td.cleanup()
