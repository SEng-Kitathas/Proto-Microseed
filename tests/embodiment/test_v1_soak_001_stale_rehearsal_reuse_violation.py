from scratch.v1_soak_001_stale_rehearsal_reuse_violation import run

def test_v1_soak_001_repair_blocks_stale_predictive_relation_through_durable_rehearsal_reuse():
    r=run()
    assert r["sign_flip_guard"]["status"]=="BLOCKED_AS_EXPECTED"
    t=r["terminal_only_drift"]
    assert t["status"]=="BLOCKED"
    assert t["relation_status"]["K-17"]["status"]=="CURRENT_PREDICTIVE_RELATION"
    assert t["relation_status"]["M-23"]["status"]=="CURRENT_PREDICTIVE_RELATION"
    assert t["relation_status"]["R-41"]["status"]=="STALE_PREDICTIVE_RELATION"
    assert t["proposal_status"]["s2"]["status"]=="UNKNOWN_INCOMPLETE"
    assert t["proposal_status"]["s2"]["reason"].startswith("REHEARSAL_LEARNED_RELATION_NOT_CURRENT:ACTION-LAW-")
    assert t["post_drift_r_commitment"]["commitment"]=="UNKNOWN"
    assert t["post_drift_r_intent"]["status"]=="ABSTAIN"
