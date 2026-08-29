from scratch.ms1958_proto_referent_boundary_coherence import run_proto_reference


def test_boundary_coherence_recovers_within_session_source_partitions_without_identity_authority():
    result = run_proto_reference()
    assert result['status'] == 'PASS'
    assert result['world_a']['nomination']['status'] == 'REFERENT_PARTITION_NOMINATED'
    assert result['world_b_permuted_channels']['nomination']['status'] == 'REFERENT_PARTITION_NOMINATED'
    assert result['world_a']['nomination']['groups'] != result['world_b_permuted_channels']['nomination']['groups']
    assert result['world_a']['nomination']['identity_authority'] == 'NONE'
    assert result['world_b_permuted_channels']['nomination']['identity_authority'] == 'NONE'
    hostile = result['symmetric_hostile']['nomination']
    assert hostile['status'] == 'UNKNOWN_INCOMPLETE'
    assert hostile['reason'] == 'BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS'
    assert hostile['identity_authority'] == 'NONE'
    assert result['remaining_boundary'] == 'WITHIN_SESSION_PARTITION != CROSS_SESSION_REFERENT_IDENTITY'
