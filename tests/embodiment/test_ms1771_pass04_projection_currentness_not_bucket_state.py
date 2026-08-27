from microseed.development.epistemic import EpistemicProjectionRecord


def test_projection_record_owns_projection_identity_currentness_not_current_bucket_or_outcome_state():
    rec = EpistemicProjectionRecord(
        projection_id='P', signature_sha256='a'*64, epoch=3,
        projection_origin='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED',
        proposal_candidate_sha256='b'*64, qualification_evidence_ids=('E-Q',),
        frame_epochs=(('F',1),), episode_schema_epochs=(('EP',2),), current=True,
    )
    p = rec.serializable()
    assert p['projection_id'] == 'P' and p['epoch'] == 3 and p['current'] is True
    for forbidden in ('projection_bucket_id','current_bucket_id','outcome_digest_sha256','possible_bucket_ids','live_bucket_ids'):
        assert forbidden not in p
    assert rec.discovery_authority == rec.semantic_projection_authority == 'NONE'
