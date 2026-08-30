from scratch.ms2003_owned_raw_referent_boundary_derivation import run_ms2003_owned_raw_boundary
from scratch.ms2003_operational_referent_class_set_routing import run_ms2003_routing
from scratch.ms2003_operational_referent_context_changes_action_intent import run_ms2003_action_intent


def test_ms2003_owned_raw_trace_derives_operational_referent_classes_without_identity_authority():
    r=run_ms2003_owned_raw_boundary()
    assert r["status"]=="PASS"
    assert r["perfect_copy_operationally_indistinguishable"] is True
    assert r["numerical_identity_authority"]=="NONE"
    assert r["semantic_reference_authority"]=="NONE"
    assert r["new_referent_manager_required"]=="NO"


def test_ms2003_class_set_context_routes_existing_qualified_relations_and_fails_closed():
    r=run_ms2003_routing()
    assert r["status"]=="PASS"
    assert r["context_a_bucket"]!=r["context_b_bucket"]
    assert r["context_a_relation"]!=r["context_b_relation"]
    assert r["caller_supplied_projection_bucket"]=="NO"
    assert r["caller_supplied_referent_class"]=="NO"
    assert r["referent_witness_selection"]=="NONE__CLASS_SET_ONLY"
    assert r["unknown_context"]["status"]=="DEFER_UNKNOWN"
    assert r["aliased"]["status"]=="DEFER_UNKNOWN"
    assert r["budget_exhaustion"]["status"]=="DEFER_UNKNOWN"
    assert r["wrong_coordinate"]["reason"]=="OPERATIONAL_REFERENT_CLASS_SET_COORDINATE_MISMATCH"


def test_ms2003_owned_referent_context_changes_zero_row_action_intent_without_policy_manager():
    r=run_ms2003_action_intent()
    assert r["status"]=="PASS"
    assert r["context_a_intent"]=="X"
    assert r["context_b_intent"]=="Y"
    assert r["context_a_rehearsal"]==["X"]
    assert r["context_b_rehearsal"]==["Y"]
    assert r["supplied_rehearsal_rows"]==0
    assert r["caller_supplied_projection_bucket"]=="NO"
    assert r["caller_supplied_referent_class"]=="NO"
    assert r["caller_supplied_preferred_action"]=="NO"
    assert r["unknown_context_rehearsal"]=="NONE"
    assert r["aliased_context_rehearsal"]=="NONE"
    assert r["new_policy_manager_required"]=="NO"
    assert r["new_referent_manager_required"]=="NO"
    assert r["identity_authority"]=="NONE"
    assert r["semantic_reference_authority"]=="NONE"
    assert r["execution_authority"]=="NONE"
