from microseed import EpistemicStatus
from scratch.lang_b3_three_grounded_referents_fixture import fixture as fixture3,_close as close3
from scratch.lang_arity_four_grounded_referents_fixture import fixture as fixture4,_close as close4
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_operand_window_store_aware_prototype import derive_store_aware_bounded_composition_prototype


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def test_store_aware_selector_matches_current_generalized_content_for_no_action_arity2_and_arity3():
    td,m,world,seeded=fixture3(tokens=('R4','T9','W3'))
    try:
        _obs(m,('R4','T9'),'STORE-EQUIV-B2',22000)
        proto2=derive_store_aware_bounded_composition_prototype(m)
        prod2=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert proto2['status']=='CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE',proto2
        assert prod2['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',prod2
        assert proto2['composition_content_digest_sha256']==prod2['composition_content_digest_sha256']
        _obs(m,('R4','T9','W3'),'STORE-EQUIV-B3',22100)
        proto3=derive_store_aware_bounded_composition_prototype(m)
        prod3=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert proto3['status']=='CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE',proto3
        assert prod3['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',prod3
        assert proto3['composition_content_digest_sha256']==prod3['composition_content_digest_sha256']
    finally:close3(m);td.cleanup()


def test_store_aware_selector_matches_current_generalized_content_for_no_action_arity4():
    td,m,world,seeded=fixture4(tokens=('R4','T9','W3','K7'))
    try:
        _obs(m,('R4','T9','W3','K7'),'STORE-EQUIV-B4',22200)
        proto=derive_store_aware_bounded_composition_prototype(m)
        prod=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert proto['status']=='CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE',proto
        assert prod['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',prod
        assert proto['derived_arity']==prod['derived_arity']==4
        assert proto['composition_content_digest_sha256']==prod['composition_content_digest_sha256']
    finally:close4(m);td.cleanup()


def test_existing_represented_non_token_evidence_delimiter_semantics_are_preserved():
    td,m,world,seeded=fixture4(tokens=('R4','T9','W3','K7'))
    try:
        _obs(m,('R4','T9'),'STORE-EQUIV-EVIDENCE-PRE',22300)
        m.append_evidence('E-STORE-EQUIV-BOUNDARY',{'kind':'REPRESENTED_NON_TOKEN_BOUNDARY_TEST','runtime_boot_seq':m._current_runtime_boot_seq()},EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-WORLD')
        _obs(m,('W3','K7'),'STORE-EQUIV-EVIDENCE-POST',22400)
        proto=derive_store_aware_bounded_composition_prototype(m)
        prod=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert proto['status']=='CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE',proto
        assert prod['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',prod
        assert proto['derived_arity']==prod['derived_arity']==2
        assert proto['composition_content_digest_sha256']==prod['composition_content_digest_sha256']
        assert proto['last_boundary']['kind']=='REPRESENTED_NON_TOKEN_EVIDENCE'
    finally:close4(m);td.cleanup()
