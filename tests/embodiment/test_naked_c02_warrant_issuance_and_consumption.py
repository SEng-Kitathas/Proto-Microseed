from scratch.naked_c02_warrant_issuance_and_consumption import run_campaign

def test_naked_c02_unknownness_not_generic_issuance_and_consumption_is_pre_effect_crash_safe():
 r=run_campaign(); assert r["status"]=="PASS"
 assert r["broad_auto_issue_count"]==20
 assert r["explicit_nomination"]=="ONE_EXACT_SUBJECT_ONLY"
 assert r["crash"]["effect_calls"]==r["retry"]["effect_calls"]==0
 assert r["normal_first"]["effect_calls"]==1 and r["normal_second"]["effect_calls"]==0
