from scratch.naked_c01_explicit_experimental_warrant_quarry import run_campaign

def test_naked_c01_exact_one_shot_warrant_fails_closed_under_scope_and_currentness_hostiles():
    r=run_campaign()
    assert r["status"]=="PASS"
    assert r["positive"]["status"]=="AUTHORIZED_ONCE"
    assert all(v["status"]=="ABSTAIN" for v in r["hostiles"].values())
    assert r["positive"]["information_value_authority"]=="NONE"
    assert r["positive"]["general_action_authority"]=="NONE"
