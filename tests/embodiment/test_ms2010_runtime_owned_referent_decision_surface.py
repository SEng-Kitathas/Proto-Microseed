from scratch.ms2010_runtime_owned_referent_decision_surface import run_ms2010

def test_ms2010_runtime_reconstructs_owned_prefix_live_referent_ambiguity_and_decision_surface():
    r=run_ms2010(); assert r["status"]=="PASS"
    assert r["prefix_actions"]==["P0","P1"] and len(r["surviving_buckets"])==2
    assert r["unique_probe"]=="P2" and r["source_relation_digest_count"]==2
    assert r["handler_calls"]==[] and r["execution_authority"]=="NONE"

def test_ms2010_current_discriminator_content_is_rederived_not_copied():
    r=run_ms2010(); assert r["forged_discriminator"]=="CURRENT_REFERENT_DISCRIMINATOR_CONTENT_DRIFT" and r["truth_authority"]=="NONE"
