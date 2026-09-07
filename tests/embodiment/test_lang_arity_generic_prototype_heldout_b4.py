from microseed import EpistemicStatus,Microseed
from scratch.lang_arity_four_grounded_referents_fixture import (
    fixture,_close,OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,
)
from scratch.lang_arity_generic_prototype import derive_current_bounded_ordered_composition_prototype
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _boundary(m,eid):
    m.append_evidence(eid,{'kind':'ARITY_GENERALIZATION_REPRESENTED_BOUNDARY','runtime_boot_seq':m._current_runtime_boot_seq()},EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-WORLD')


def _run_once(tokens=('R4','T9','W3','K7'),sensor_transform=None):
    td,m,world,seeded=fixture(tokens=tokens,sensor_transform=sensor_transform)
    try:
        ta,tb,tc,td_token=tokens
        sigs=(seeded['mapping'][ta],seeded['mapping'][tb],seeded['mapping'][tc],seeded['mapping'][td_token])
        _obs(m,tokens,'ARITY4-HELDOUT',10000)
        g4=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        assert g4['status']=='CURRENT_BOUNDED_ORDERED_COMPOSITION_PROTOTYPE' and g4['derived_arity']==4,g4
        assert g4['ordered_operational_referent_signatures']==sigs
        assert g4['caller_supplied_arity']=='NO'
        assert not hasattr(m,'derive_and_record_current_native_b4_ordered_composition')
        digest=str(g4['composition_content_digest_sha256'])
        _boundary(m,'E-ARITY4-ORDER-BOUNDARY')
        _obs(m,(ta,tb,td_token,tc),'ARITY4-HELDOUT-ORDER',10100)
        perm=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        assert perm['status']=='CURRENT_BOUNDED_ORDERED_COMPOSITION_PROTOTYPE',perm
        assert perm['composition_content_digest_sha256']!=digest
        _boundary(m,'E-ARITY4-DUP-BOUNDARY')
        _obs(m,(ta,tb,tc,ta),'ARITY4-DUP',10200)
        dup=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        assert dup['status']=='DEFER_UNKNOWN' and dup['reason']=='ALL_BOUNDED_REFERENT_OPERANDS_MUST_BE_DISTINCT',dup
        _boundary(m,'E-ARITY4-UNSEEN-BOUNDARY')
        _obs(m,(ta,tb,tc,'UNSEEN-ARITY4'),'ARITY4-UNSEEN',10300)
        unseen=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        assert unseen['status']=='DEFER_UNKNOWN' and unseen['reason']=='UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED',unseen
        _boundary(m,'E-ARITY4-DRIFT-BOUNDARY')
        _obs(m,tokens,'ARITY4-DRIFT',10400)
        before_drift=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        assert before_drift['status']=='CURRENT_BOUNDED_ORDERED_COMPOSITION_PROTOTYPE',before_drift
        m.change_capability_dependency('QD',reason='ARITY4-QD-DRIFT')
        drift=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        assert drift['status']=='DEFER_UNKNOWN' and drift['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED',drift
        return {'digest':digest,'order_digest':str(perm['composition_content_digest_sha256']),'sigs':sigs,'records':seeded['records'],'root':str(m.store.path.parent) if hasattr(m.store,'path') else None,'dup':dup,'unseen':unseen,'drift':drift}
    finally:
        _close(m);td.cleanup()


def test_same_generic_prototype_generalizes_from_earned_b2_b3_to_heldout_arity4_without_b4_branch():
    r=_run_once()
    assert r['digest']!=r['order_digest']
    assert r['dup']['reason']=='ALL_BOUNDED_REFERENT_OPERANDS_MUST_BE_DISTINCT'
    assert r['unseen']['reason']=='UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED'
    assert r['drift']['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED'


def test_token_label_and_eight_channel_representation_transforms_preserve_heldout_arity4_identity():
    a=_run_once(('R4','T9','W3','K7'))
    b=_run_once(('K7','R4','T9','W3'))
    p=_run_once(('R4','T9','W3','K7'),lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]))
    inv=_run_once(('R4','T9','W3','K7'),lambda row:tuple(-x for x in row))
    assert a['digest']==b['digest']==p['digest']==inv['digest']
    assert a['order_digest']==b['order_digest']==p['order_digest']==inv['order_digest']
