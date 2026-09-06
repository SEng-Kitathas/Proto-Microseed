from scratch.lang_c07_observed_token_relation_binding import run_campaign


def test_c07_observed_opaque_tokens_bind_two_opposing_current_relations_without_new_action_contracts():
    r=run_campaign("K7","M2")
    assert r["status"]=="PASS_BOUNDED_RESEARCH_ONLY"
    assert len(r["bindings"]["bindings"])==2
    assert r["token_a_resolution"]["status"]=="OPAQUE_OBSERVED_TOKEN_RESOLVES_CURRENT_RELATION_RESEARCH_ONLY"
    assert r["token_b_resolution"]["status"]=="OPAQUE_OBSERVED_TOKEN_RESOLVES_CURRENT_RELATION_RESEARCH_ONLY"
    assert r["convention_reversal"]["status"]=="DEFER_UNKNOWN"
    assert r["ambiguous_holdout"]["status"]=="DEFER_UNKNOWN"
    assert r["relation_drift"]["status"]=="DEFER_UNKNOWN"
    assert r["new_microseed_action_contracts_registered"]==[]
    assert r["language_status"]=="DEFERRED_PRELINGUAL_COGNITION_ACTIVE"


def test_c07_token_surface_permutation_has_no_privileged_spelling_or_semantic_alias():
    a=run_campaign("K7","M2")
    b=run_campaign("M2","K7")
    assert a["status"]==b["status"]=="PASS_BOUNDED_RESEARCH_ONLY"
    amap={x["opaque_token"]:tuple(x["relation_order"]) for x in a["bindings"]["bindings"]}
    bmap={x["opaque_token"]:tuple(x["relation_order"]) for x in b["bindings"]["bindings"]}
    assert amap["K7"]==bmap["M2"]
    assert amap["M2"]==bmap["K7"]
    assert a["new_microseed_action_contracts_registered"]==b["new_microseed_action_contracts_registered"]==[]


def test_c07_output_surface_does_not_reify_capability_faculty_or_semantic_roles():
    r=run_campaign("ZQ","17")
    for obj in (r["bindings"],r["token_a_resolution"],r["token_b_resolution"]):
        keys={str(k).lower() for k in obj}
        assert not any("capability" in k or "faculty" in k for k in keys)
        assert not any(k in keys for k in {"predicate","subject","object","agent","patient"})
    assert "NO_GENERIC_CAPABILITY" in r["nonclaim"]
    assert "NO_LANGUAGE_FACULTY" in r["nonclaim"]
