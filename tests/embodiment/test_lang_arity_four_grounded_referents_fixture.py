from scratch.lang_arity_four_grounded_referents_fixture import fixture,_close

def test_existing_grounding_and_qualification_substrate_scales_to_four_distinct_referents_independently_of_generalized_operator():
    td,m,world,seeded=fixture()
    try:
        assert set(seeded['profiles'])=={'QA','QB','QC','QD'}
        assert len(set(seeded['mapping'].values()))==4
        assert set(seeded['mapping'])=={'R4','T9','W3','K7'}
        assert all(m.opaque_evidence_association_status(rid)['status']=='CURRENT_OPAQUE_EVIDENCE_ASSOCIATION' for rid in seeded['records'].values())
        assert hasattr(m,'derive_and_record_current_native_bounded_ordered_composition')
        assert set(seeded['profiles'])=={'QA','QB','QC','QD'}  # substrate proof remains independent of invoking it
    finally:
        _close(m);td.cleanup()
