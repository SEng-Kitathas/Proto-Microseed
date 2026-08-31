from scratch.lang_c05_grounded_binary_relation import run_campaign

def test_lang_c05_relation_signal_grounds_binary_relation_over_two_b1_referents_without_predicate_authority():
 r=run_campaign(); assert r["status"]=="PASS"
 assert r["candidate"]["status"]=="GROUNDED_OPERATIONAL_BINARY_RELATION_CANDIDATE_RESEARCH_ONLY"
 assert r["frame"]["status"]=="B2_GROUNDED_BINARY_RELATIONAL_REFERENCE_FRAME_RESEARCH_ONLY"
 assert r["readable_ungrounded"]["status"]=="DEFER_UNKNOWN"
 assert r["stale_relation"]["status"]=="DEFER_UNKNOWN"
 assert r["frame"]["predicate_authority"]==r["frame"]["truth_authority"]=="NONE"
