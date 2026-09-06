from scratch.lang_c06_grounded_directional_relation import run_campaign


def test_lang_c06_external_asymmetry_earns_order_without_installing_relation_action_or_faculty():
    r=run_campaign()
    assert r["status"]=="PASS"
    assert r["candidate"]["status"]=="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY"
    assert r["frame"]["status"]=="B2_GROUNDED_DIRECTIONAL_RELATIONAL_REFERENCE_FRAME_RESEARCH_ONLY"
    assert r["reversed_argument_order"]["status"]=="DEFER_UNKNOWN"
    assert r["convention_reversal"]["status"]=="DEFER_UNKNOWN"
    assert r["fresh_same"]["status"]=="CURRENT_DIRECTIONAL_RELATION_REVALIDATED_RESEARCH_ONLY"
    assert r["fresh_reversed"]["status"]=="DEFER_UNKNOWN"
    assert r["new_microseed_action_contracts_registered"]==[]
    assert r["sensor_polarity_inverted"]["status"]=="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY"
    assert r["sensor_polarity_inverted"]["ordered_operational_referent_signatures"]==r["candidate"]["ordered_operational_referent_signatures"]
    assert r["restart_same"]["status"]=="CURRENT_DIRECTIONAL_RELATION_REVALIDATED_RESEARCH_ONLY"
    assert r["restart_reversed"]["status"]=="DEFER_UNKNOWN"
    assert r["restart_new_microseed_action_contracts_registered"]==[]
    assert "relation_signal_id" not in r["candidate"]
    assert r["frame"]["predicate_authority"]==r["frame"]["truth_authority"]==r["frame"]["language_authority"]=="NONE"


def test_lang_c06_no_capability_or_predicate_surface_is_smuggled_into_candidate():
    r=run_campaign(); c=r["candidate"]
    assert "derived_relation_id" in c
    assert all("capability" not in k.lower() for k in c)
    assert "predicate" not in c["relation_form"].lower()
    assert r["new_microseed_action_contracts_registered"]==[]
