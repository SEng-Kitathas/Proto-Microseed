from scratch.lang_c02_multi_token_restart_revalidation import run_campaign

def test_lang_c02_two_independent_b1_relations_survive_restart_only_by_current_revalidation_and_drift_localizes():
 r=run_campaign(); assert r["status"]=="PASS" and r["two_independent_relations"] and r["distinct_operational_referents"]
 assert r["restart_requires_explicit_revalidation"]
 assert r["localized_drift"]["sig_y"]["status"]=="DEFER_UNKNOWN"
 assert r["localized_drift"]["sig_x"]["status"]=="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY"
