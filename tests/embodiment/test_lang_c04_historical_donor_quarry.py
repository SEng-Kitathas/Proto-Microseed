from scratch.lang_c04_historical_donor_quarry import run_campaign

def test_lang_c04_c2_quarry_strips_algorithms_from_supplied_semantic_assistance():
 r=run_campaign(); assert r["status"]=="PASS"
 assert "EXTENSIONAL_COMPOSITION_AS_PURE_ALGORITHMIC_INVARIANT" in r["admissible_parts"]
 assert "MULTIPLE_LAWFUL_SEGMENTATIONS_REQUIRE_UNKNOWN" in r["admissible_parts"]
 assert "SUPPLIED_STATE_IDENTITY" in r["quarantined_assumptions"]
 assert r["event_frame_ambiguous"]=="UNKNOWN_INCOMPLETE"
