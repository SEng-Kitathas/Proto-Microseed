from scratch.naked_c03_unique_eligible_subject import run_campaign

def test_naked_c03_unique_eligibility_nominates_without_hidden_ranking_and_multi_candidate_abstains():
 r=run_campaign(); assert r["status"]=="PASS"
 assert r["single"]["status"]=="UNIQUE_EXPERIMENT_SUBJECT_NOMINATED"
 assert r["multiple"]["status"]=="ABSTAIN" and r["multiple"]["reason"]=="UNIQUE_EXPERIMENT_SUBJECT_REQUIRED"
 assert r["narrowed"]["capability_id"]=="B"
