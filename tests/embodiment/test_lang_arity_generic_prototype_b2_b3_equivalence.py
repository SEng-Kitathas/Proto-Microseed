from microseed import EpistemicStatus
from scratch.lang_b3_three_grounded_referents_fixture import fixture,_close
from scratch.lang_distinct_leaf_b3_ordered_composition import _observe_sequence
from scratch.lang_arity_generic_prototype import derive_current_bounded_ordered_composition_prototype


def test_one_arity_agnostic_prototype_reproduces_earned_b2_and_b3_content_identities():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        # arity 2
        _observe_sequence(m,('R4','T9'),phase='ARITY-GEN-B2',base=9000)
        g2=derive_current_bounded_ordered_composition_prototype(m)
        assert g2['status']=='CURRENT_BOUNDED_ORDERED_COMPOSITION_PROTOTYPE' and g2['derived_arity']==2,g2
        b2=m.derive_and_record_current_native_b2_ordered_composition(max_records=32768)
        assert b2['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',b2
        assert g2['composition_content_digest_sha256']==b2['composition_content_digest_sha256']
        assert g2['ordered_operational_referent_signatures']==b2['ordered_operational_referent_signatures']
        # B2 evidence delimits the next contiguous operand run.
        _observe_sequence(m,('R4','T9','W3'),phase='ARITY-GEN-B3',base=9100)
        g3=derive_current_bounded_ordered_composition_prototype(m)
        assert g3['status']=='CURRENT_BOUNDED_ORDERED_COMPOSITION_PROTOTYPE' and g3['derived_arity']==3,g3
        b3=m.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert b3['status']=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',b3
        assert g3['composition_content_digest_sha256']==b3['composition_content_digest_sha256']
        assert g3['ordered_operational_referent_signatures']==b3['ordered_operational_referent_signatures']
        assert g2['caller_supplied_arity']==g3['caller_supplied_arity']=='NO'
        assert g2['arity_basis']==g3['arity_basis']=='EXACT_CONTIGUOUS_CURRENT_RUNTIME_TOKEN_SUFFIX_LENGTH'
    finally:
        _close(m);td.cleanup()


def test_prototype_fails_closed_below_minimum_and_above_explicit_maximum():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        _observe_sequence(m,('R4',),phase='ARITY-GEN-ONE',base=9200)
        one=derive_current_bounded_ordered_composition_prototype(m)
        assert one=={'status':'DEFER_UNKNOWN','reason':'BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM','derived_arity':1}
        # Delimit then present 5 current tokens; max=4 must reject rather than crop to 4.
        m.derive_and_record_current_native_b2_ordered_composition(max_records=32768)  # refuses but does not delimit; add a known non-token via B3? one token insufficient.
        m.append_evidence('E-ARITY-GEN-BOUNDARY',{'kind':'ARITY_PROTOTYPE_TEST_BOUNDARY','runtime_boot_seq':m._current_runtime_boot_seq()},EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-WORLD')
        _observe_sequence(m,('R4','T9','W3','R4','T9'),phase='ARITY-GEN-FIVE',base=9300)
        five=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        assert five['status']=='DEFER_UNKNOWN' and five['reason']=='BOUNDED_OPERAND_WINDOW_EXCEEDS_MAXIMUM' and five['derived_arity']==5
    finally:
        _close(m);td.cleanup()
