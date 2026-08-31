from scratch.naked_c04_residual_risk_boundary import run_campaign

def test_naked_c04_bounded_exposure_is_not_bounded_downstream_risk():
 r=run_campaign(); assert r["status"]=="PASS"
 assert r["exposure"]["status"]=="BOUNDED_EXPERIMENTAL_EXPOSURE"
 assert r["naked_risk"]["status"]=="UNKNOWN_INCOMPLETE"
 assert r["equipped_risk"]["status"]=="BOUNDED_DOWNSTREAM_RISK_BY_SEPARATE_PREMISE"
 assert r["operator_authority_required"]
