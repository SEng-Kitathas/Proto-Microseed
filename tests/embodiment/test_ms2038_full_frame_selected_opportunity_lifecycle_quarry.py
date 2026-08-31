from scratch.ms2038_full_frame_selected_opportunity_lifecycle_quarry import run_ms2038


def test_ms2038_full_frame_selected_opportunity_lifecycle_is_bounded_and_idempotent():
    r=run_ms2038()
    assert r["status"]=="FULL_FRAME_SELECTED_OPPORTUNITY_LIFECYCLE_EARNED_RESEARCH_ONLY"
    assert r["tradeoff"]["result"]["status"]=="ABSTAIN"
    d=r["dominance"]["result"]
    assert d["status"]=="SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED"
    assert d["selected_probe_action_id"]=="P2"
    assert d["deficit_delta"]==1 and d["intent_delta"]==1 and d["execution_delta"]==0
    assert r["idempotent"]["second"]["reason"]=="SELECTED_EPISTEMIC_DEFICIT_ALREADY_PERSISTED"
    assert r["idempotent"]["second"]["deficit_delta"]==0
    assert r["idempotent"]["second"]["intent_delta"]==0
    assert r["idempotent"]["second"]["execution_delta"]==0
    assert r["incomplete_frame"]["result"]["reason"]=="CURRENT_VALUE_FRAME_OBSERVATION_MISSING:X"
    assert r["runtime_promotion_authorized"]=="NO"
    assert r["execution_authority"]=="NONE"
