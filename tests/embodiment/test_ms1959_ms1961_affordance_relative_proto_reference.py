from microseed.cognition.referents import derive_affordance_relative_referent_signature
from scratch.ms1959_cross_session_operational_referent_signature import run_cross_session_signature
from scratch.ms1960_affordance_relative_proto_referent import run_affordance_relative
from scratch.ms1961_joint_sensor_actuator_symmetry import run_joint_symmetry


def test_cross_session_boundary_content_reassociates_sensor_permuted_partitions_without_identity_authority():
    result = run_cross_session_signature()
    assert result['status'] == 'PASS'
    assert len(result['shared_operational_signatures']) == 2
    assert result['identity_authority'] == 'NONE'
    assert result['semantic_reference_authority'] == 'NONE'
    assert result['remaining_boundary'] == 'PROTOCOL_RELATIVE_OPERATIONAL_SIGNATURE != GENERAL_REFERENT_IDENTITY'


def test_integrated_affordance_relative_signature_survives_sensor_and_protocol_order_changes():
    result = run_affordance_relative()
    assert result['status'] == 'PASS'
    assert len(result['shared_affordance_signatures']) == 2
    assert result['identity_authority'] == 'NONE'
    assert result['semantic_reference_authority'] == 'NONE'
    assert result['remaining_boundary'] == 'AFFORDANCE_RELATIVE_OPERATIONAL_REFERENT != NUMERICAL_OBJECT_IDENTITY'


def test_joint_sensor_and_actuator_alias_symmetry_refuses_numerical_identity():
    result = run_joint_symmetry()
    assert result['status'] == 'PASS'
    assert result['identity_authority'] == 'NONE'
    assert result['semantic_reference_authority'] == 'NONE'
    assert result['required_breaker'] == 'ADDITIONAL_CONTINUITY_OR_ASYMMETRIC_EVIDENCE_REQUIRED'
    assert result['session_a_alignment'] != result['session_b_alignment_after_joint_alias_swap']


def test_integrated_signature_rejects_noncoherent_or_empty_inputs():
    empty = derive_affordance_relative_referent_signature(((1,2),(1,2)),(),('A',))
    assert empty.status == 'UNKNOWN_INCOMPLETE'
    assert empty.reason == 'EMPTY_REFERENT_GROUP'
    assert empty.signature_sha256 is None

    noncoherent = derive_affordance_relative_referent_signature(((1,2),(2,3)),(0,1),('A','B','A'))
    assert noncoherent.status == 'UNKNOWN_INCOMPLETE'
    assert noncoherent.reason == 'GROUP_NOT_BOUNDARY_COHERENT'
    assert noncoherent.identity_authority == 'NONE'
    assert noncoherent.semantic_reference_authority == 'NONE'
