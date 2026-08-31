from scratch.lang_c01_operational_reference_relation import run_campaign

def test_lang_c01_grounded_binding_supports_b1_operational_reference_only_while_hostiles_fail_closed():
    r=run_campaign()
    assert r["status"]=="PASS"
    assert r["positive"]["status"]=="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY"
    assert r["positive"]["semantic_reference_authority"]=="NONE"
    assert r["positive"]["truth_authority"]=="NONE"
    assert r["positive"]["execution_authority"]=="NONE"
    for k in ("wrong_token","stale","convention_reversal","readable_ungrounded"):
        assert r[k]["status"]=="DEFER_UNKNOWN"
