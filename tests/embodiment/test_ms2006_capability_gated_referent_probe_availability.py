from scratch.ms2006_capability_gated_referent_probe_availability import run_ms2006


def test_ms2006_information_value_does_not_create_capability_availability():
    r=run_ms2006(); assert r["status"]=="PASS"
    assert r["cases"]["no_capability"]["reason"]=="INFORMATIVE_PROBE_CAPABILITY_NOT_FOUND"
    assert r["cases"]["wrong_authority"]["reason"]=="INFORMATIVE_PROBE_CAPABILITY_NOT_EFFECT"
    assert r["cases"]["wrong_scope"]["reason"]=="INFORMATIVE_PROBE_OPERATIONAL_SCOPE_MISMATCH"


def test_ms2006_exact_current_effect_capability_yields_inert_availability_and_stales_on_drift():
    r=run_ms2006(); c=r["cases"]["current_available"]; a=r["cases"]["after_drift"]
    assert c["status"]=="CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE_CAPABILITY_AVAILABLE"
    assert c["capability_id"]=="P2" and c["capability_epoch"]==0
    assert c["invoked"]=="NO" and r["cases"]["handler_calls_during_availability"]==[]
    assert a["reason"]=="INFORMATIVE_PROBE_CAPABILITY_NOT_CURRENT"
    assert r["cases"]["unrelated_alias_present"]=="P2-ALT"
    assert r["selection_authority"]==r["execution_authority"]==r["truth_authority"]=="NONE"
