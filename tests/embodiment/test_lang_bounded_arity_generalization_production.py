from microseed import EpistemicStatus,Microseed
from scratch.lang_b3_three_grounded_referents_fixture import fixture as fixture3,_close as close3
from scratch.lang_arity_four_grounded_referents_fixture import (
    fixture as fixture4,_close as close4,OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_arity_generic_prototype import derive_current_bounded_ordered_composition_prototype


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def _boundary(m,eid):
    m.append_evidence(eid,{'kind':'ARITY_GENERALIZATION_REPRESENTED_BOUNDARY','runtime_boot_seq':m._current_runtime_boot_seq()},EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-WORLD')


def test_one_production_owner_derives_arity2_and_arity3_without_caller_arity_and_matches_legacy_content():
    td,m,world,seeded=fixture3(tokens=('R4','T9','W3'))
    try:
        _obs(m,('R4','T9'),'PROD-GEN-B2',13000)
        proto2=derive_current_bounded_ordered_composition_prototype(m)
        g2=m.derive_and_record_current_native_bounded_ordered_composition(max_records=32768)
        assert g2['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',g2
        assert g2['derived_arity']==2 and g2['caller_supplied_arity']=='NO'
        assert g2['composition_content_digest_sha256']==proto2['composition_content_digest_sha256']
        legacy2=m.derive_and_record_current_native_b2_ordered_composition(max_records=32768)
        assert legacy2['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',legacy2
        assert g2['composition_content_digest_sha256']==legacy2['composition_content_digest_sha256']
        assert g2['ordered_operational_referent_signatures']==legacy2['ordered_operational_referent_signatures']

        _obs(m,('R4','T9','W3'),'PROD-GEN-B3',13100)
        proto3=derive_current_bounded_ordered_composition_prototype(m)
        g3=m.derive_and_record_current_native_bounded_ordered_composition(max_records=32768)
        assert g3['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',g3
        assert g3['derived_arity']==3 and g3['caller_supplied_arity']=='NO'
        assert g3['composition_content_digest_sha256']==proto3['composition_content_digest_sha256']
        legacy3=m.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert legacy3['status']=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',legacy3
        assert g3['composition_content_digest_sha256']==legacy3['composition_content_digest_sha256']
        assert g3['ordered_operational_referent_signatures']==legacy3['ordered_operational_referent_signatures']

        # The generic evidence is itself represented non-token evidence and consumes/closes the current token suffix.
        consumed=m.derive_and_record_current_native_bounded_ordered_composition(max_records=32768)
        assert consumed['status']=='DEFER_UNKNOWN' and consumed['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM' and consumed['derived_arity']==0,consumed
    finally:
        close3(m);td.cleanup()


def test_production_owner_fails_closed_for_below_minimum_and_overlong_window_without_silent_crop():
    td,m,world,seeded=fixture3(tokens=('R4','T9','W3'))
    try:
        _obs(m,('R4',),'PROD-GEN-ONE',13200)
        one=m.derive_and_record_current_native_bounded_ordered_composition(max_records=32768)
        assert one['status']=='DEFER_UNKNOWN' and one['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM' and one['derived_arity']==1,one
        _boundary(m,'E-PROD-GEN-OVERLONG-BOUNDARY')
        _obs(m,('R4','T9','W3','R4','T9'),'PROD-GEN-FIVE',13300)
        five=m.derive_and_record_current_native_bounded_ordered_composition(max_records=32768)
        assert five['status']=='DEFER_UNKNOWN' and five['reason']=='BOUNDED_OPERAND_WINDOW_EXCEEDS_MAXIMUM' and five['derived_arity']==5,five
        assert five['bounded_max_arity']==4
    finally:
        close3(m);td.cleanup()


def _run_arity4_once(tokens=('R4','T9','W3','K7'),sensor_transform=None):
    td,m,world,seeded=fixture4(tokens=tokens,sensor_transform=sensor_transform)
    try:
        ta,tb,tc,td_token=tokens
        sigs=tuple(seeded['mapping'][x] for x in tokens)
        _obs(m,tokens,'PROD-GEN-B4',14000)
        proto=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        g4=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert g4['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',g4
        assert g4['derived_arity']==4 and g4['ordered_operational_referent_signatures']==sigs
        assert g4['composition_content_digest_sha256']==proto['composition_content_digest_sha256']
        assert g4['caller_supplied_arity']==g4['caller_supplied_token_operands']==g4['caller_supplied_operand_order']=='NO'
        assert g4['bounded_min_arity']==2 and g4['bounded_max_arity']==4
        assert g4['arity_basis']=='EXACT_CONTIGUOUS_CURRENT_RUNTIME_TOKEN_SUFFIX_LENGTH'
        assert g4['flattening_authority']==g4['associativity_authority']=='NONE'
        assert not hasattr(m,'derive_and_record_current_native_b4_ordered_composition')
        digest=str(g4['composition_content_digest_sha256'])

        _obs(m,(ta,tb,td_token,tc),'PROD-GEN-B4-ORDER',14100)
        order=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert order['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',order
        assert order['derived_arity']==4 and order['composition_content_digest_sha256']!=digest

        _obs(m,(ta,tb,tc,ta),'PROD-GEN-B4-DUP',14200)
        dup=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert dup['status']=='DEFER_UNKNOWN' and dup['reason']=='ALL_BOUNDED_REFERENT_OPERANDS_MUST_BE_DISTINCT',dup
        _boundary(m,'E-PROD-GEN-B4-UNSEEN-BOUNDARY')
        _obs(m,(ta,tb,tc,'UNSEEN-ARITY4'),'PROD-GEN-B4-UNSEEN',14300)
        unseen=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert unseen['status']=='DEFER_UNKNOWN' and unseen['reason']=='UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED',unseen
        _boundary(m,'E-PROD-GEN-B4-DRIFT-BOUNDARY')
        _obs(m,tokens,'PROD-GEN-B4-DRIFT',14400)
        before=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert before['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',before
        # re-present after output boundary, then stale one leaf before derivation
        _obs(m,tokens,'PROD-GEN-B4-DRIFT2',14500)
        m.change_capability_dependency('QD',reason='PROD-GEN-B4-QD-DRIFT')
        drift=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert drift['status']=='DEFER_UNKNOWN' and drift['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED',drift
        return {'digest':digest,'order_digest':str(order['composition_content_digest_sha256']),'records':seeded['records'],'mapping':seeded['mapping'],'root':m.store.path.parent if hasattr(m.store,'path') else None}
    finally:
        close4(m);td.cleanup()


def test_same_production_owner_handles_heldout_arity4_without_b4_specific_branch():
    r=_run_arity4_once()
    assert r['digest']!=r['order_digest']


def test_token_label_and_eight_channel_representation_transforms_preserve_production_arity4_identity():
    a=_run_arity4_once(('R4','T9','W3','K7'))
    b=_run_arity4_once(('K7','R4','T9','W3'))
    p=_run_arity4_once(('R4','T9','W3','K7'),lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]))
    inv=_run_arity4_once(('R4','T9','W3','K7'),lambda row:tuple(-x for x in row))
    assert a['digest']==b['digest']==p['digest']==inv['digest']
    assert a['order_digest']==b['order_digest']==p['order_digest']==inv['order_digest']
