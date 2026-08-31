from scratch.lang_c03_b2_ordered_reference_composition import run_campaign

def test_lang_c03_two_independent_b1_relations_compose_order_sensitively_and_fail_if_component_stale():
 r=run_campaign(); assert r["status"]=="PASS"
 assert r["xy"]["status"]=="B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RESEARCH_ONLY"
 assert r["xy"]["components"]!=r["yx"]["components"]
 assert r["duplicate"]["status"]=="DEFER_UNKNOWN"
 assert r["stale_component"]["status"]=="DEFER_UNKNOWN"
 assert r["xy"]["predicate_authority"]=="NONE"
