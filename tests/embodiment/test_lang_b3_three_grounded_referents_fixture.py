from scratch.lang_b3_three_grounded_referents_fixture import fixture,_close


def test_existing_substrate_grounds_and_qualifies_three_distinct_referents_without_b3_operator():
    td,m,world,seeded=fixture()
    try:
        assert set(seeded['profiles'])=={'QX','QY','QZ'}
        assert len(set(seeded['mapping'].values()))==3
        assert set(seeded['mapping'])=={'R4','T9','W3'}
        assert all(m.opaque_evidence_association_status(rid)['status']=='CURRENT_OPAQUE_EVIDENCE_ASSOCIATION' for rid in seeded['records'].values())
        assert not any((row.get('payload') or {}).get('kind')=='OWNED_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE' for row in m.evidence.list())
    finally:
        _close(m);td.cleanup()
