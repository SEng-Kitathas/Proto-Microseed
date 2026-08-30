from scratch.ms2024_selected_opportunity_persistence_and_nomination import run_ms2024


def test_ms2024_tie_persists_nothing_and_nominates_nothing():
    r = run_ms2024()
    x = r["symmetric"]["result"]
    assert x["status"] == "ABSTAIN"
    assert x["reason"] == "WORST_RESIDUAL_PRESSURE_TIE"
    assert x["deficit_delta"] == x["intent_delta"] == x["execution_delta"] == 0
    assert r["symmetric"]["calls"] == []


def test_ms2024_strict_selected_opportunity_alone_enters_existing_durable_nomination_path():
    r = run_ms2024()
    x = r["asymmetric"]["result"]
    assert x["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED"
    assert x["selected_probe_action_id"] == "P2"
    assert x["deficit_delta"] == 1 and x["intent_delta"] == 1 and x["execution_delta"] == 0
    assert x["nomination"]["status"] == "ACTION_INTENT_NOMINATED"
    assert x["nomination"]["intent"]["capability_id"] == "P2"
    assert x["execution_authority"] == "NONE"
    assert r["asymmetric"]["calls"] == []


def test_ms2024_value_drift_before_selection_abstains_without_durable_state():
    r = run_ms2024()
    x = r["value_drift_before_selection"]["result"]
    assert x["status"] == "ABSTAIN"
    assert x["deficit_delta"] == x["intent_delta"] == x["execution_delta"] == 0
    assert r["value_drift_before_selection"]["calls"] == []
    assert r["new_scheduler_required"] == r["persistent_opportunity_registry_required"] == "NO"
