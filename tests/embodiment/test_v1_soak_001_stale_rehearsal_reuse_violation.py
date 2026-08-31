from scratch.v1_soak_001_stale_rehearsal_reuse_violation import run

def test_v1_soak_001_reproduces_stale_predictive_relation_reuse_violation_before_repair():
    r=run()
    assert r["sign_flip_guard"]["status"]=="BLOCKED_AS_EXPECTED"
    assert r["terminal_only_drift"]["status"]=="VIOLATED"
    assert r["terminal_only_drift"]["relation_status"]["R-41"]["status"]=="STALE_PREDICTIVE_RELATION"
    assert r["terminal_only_drift"]["proposal_status"]["s2"]["status"]=="CURRENT_REHEARSAL_PROPOSAL"
    assert r["terminal_only_drift"]["post_drift_r_commitment"]["commitment"]=="YES"
    assert r["terminal_only_drift"]["post_drift_r_intent"]["status"]=="ACTION_INTENT_NOMINATED"
