from scratch.ms2029_promote_selected_opportunity_persistence_nomination import run_ms2029


def test_ms2029_runtime_nomination_persists_only_strict_selected_opportunity_and_is_idempotent():
    r = run_ms2029()
    assert r["status"] == "PASS"
    sym = r["symmetric"]
    assert sym["result"]["status"] == "ABSTAIN"
    assert sym["before"] == sym["after"]
    asym = r["asymmetric_idempotent"]
    assert asym["first"]["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED"
    assert asym["first"]["selected_probe_action_id"] == "P2"
    assert asym["first"]["deficit_delta"] == 1 and asym["first"]["intent_delta"] == 1 and asym["first"]["execution_delta"] == 0
    assert asym["second"]["reason"] == "SELECTED_EPISTEMIC_DEFICIT_ALREADY_PERSISTED"
    assert asym["mid"] == asym["after"]
    assert asym["calls"] == []


def test_ms2029_value_drift_before_nomination_creates_no_durable_state_or_effect():
    r = run_ms2029()
    d = r["value_drift"]
    assert d["result"]["status"] == "ABSTAIN"
    assert d["before"] == d["after"]
    assert d["calls"] == []
    assert r["new_scheduler_required"] == r["persistent_opportunity_registry_required"] == "NO"
    assert r["execution_authority"] == "NONE"
