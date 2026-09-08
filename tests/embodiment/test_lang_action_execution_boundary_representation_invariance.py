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


def _run(boundary_action='QA',tokens=('R4','T9','W3','K7'),sensor_transform=None,base=29000):
    td,m,world,seeded=fixture(tokens=tokens,sensor_transform=sensor_transform)
    try:
        _observe_s0(m,f'BOUNDARY-INVAR-{boundary_action}-RESET')
        _obs(m,tokens[:2],f'BOUNDARY-INVAR-{boundary_action}-PRE',base)
        x=_bare_exec(m,boundary_action,base)
        _obs(m,tokens[2:],f'BOUNDARY-INVAR-{boundary_action}-POST',base+100)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        assert out['derived_arity']==2
        assert out['last_window_boundary']['execution_id']==x['execution']['execution_id']
        assert out['last_window_boundary']['capability_id']==boundary_action
        return {'digest':out['composition_content_digest_sha256'],'ordered':out['ordered_operational_referent_signatures'],'boundary_capability':out['last_window_boundary']['capability_id']}
    finally:_close(m);td.cleanup()


def test_boundary_action_identity_changes_witness_ancestry_not_composition_content():
    qa=_run('QA',base=29000)
    qb=_run('QB',base=30000)
    assert qa['boundary_capability']!=qb['boundary_capability']
    assert qa['digest']==qb['digest']
    assert qa['ordered']==qb['ordered']


def test_action_boundary_composition_content_is_invariant_to_token_labels_and_sensor_representation():
    base=_run('QA',('R4','T9','W3','K7'),base=31000)
    labels=_run('QA',('K7','R4','T9','W3'),base=32000)
    perm=_run('QA',('R4','T9','W3','K7'),lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]),33000)
    inv=_run('QA',('R4','T9','W3','K7'),lambda row:tuple(-x for x in row),34000)
    assert base['digest']==labels['digest']==perm['digest']==inv['digest']
    assert base['ordered']==labels['ordered']==perm['ordered']==inv['ordered']


def test_action_after_token_window_closes_it_instead_of_becoming_semantic_separator_token():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _observe_s0(m,'BOUNDARY-AFTER-RESET')
        _obs(m,('W3','K7'),'BOUNDARY-AFTER-TOKENS',35000)
        _bare_exec(m,'QA',350)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM',out
        assert out['derived_arity']==0
        assert out['last_boundary']['kind']=='BOUNDED_ACTION_EXECUTED'
    finally:_close(m);td.cleanup()
