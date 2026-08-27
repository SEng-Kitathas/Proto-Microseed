from microseed.development.epistemic import EpistemicContrastRow, derive_pre_evidence_discriminator_signature


def test_content_only_discriminator_signature_is_stable_across_projection_identity_epoch_and_row_order():
    rows_a=(
        EpistemicContrastRow('P-A',3,(('ctx-b','b'*64),('ctx-a','a'*64)),'c'*64),
        EpistemicContrastRow('P-C',9,(('ctx-a','e'*64),('ctx-b','f'*64))),
    )
    rows_b=(
        EpistemicContrastRow('P-DIFFERENT',101,(('ctx-b','f'*64),('ctx-a','e'*64))),
        EpistemicContrastRow('P-B',44,(('ctx-a','a'*64),('ctx-b','b'*64)),'c'*64),
    )
    sig_a=derive_pre_evidence_discriminator_signature(
        hypothesis_digest_sha256='d'*64, rows=rows_a,
        projection_content_signatures={'P-A':'1'*64,'P-C':'2'*64},
    )
    sig_b=derive_pre_evidence_discriminator_signature(
        hypothesis_digest_sha256='d'*64, rows=rows_b,
        projection_content_signatures={'P-B':'1'*64,'P-DIFFERENT':'2'*64},
    )
    assert sig_a==sig_b


def test_content_only_discriminator_changes_with_hypothesis_partition_condition_or_projection_content():
    base=EpistemicContrastRow('P',0,(('a','1'*64),('b','2'*64)),'3'*64)
    def sig(h='4'*64,row=base,ps='5'*64):
        return derive_pre_evidence_discriminator_signature(hypothesis_digest_sha256=h,rows=(row,),projection_content_signatures={row.projection_id:ps})
    s=sig()
    assert sig(h='6'*64)!=s
    assert sig(row=EpistemicContrastRow('P',0,(('a','1'*64),('b','7'*64)),'3'*64))!=s
    assert sig(row=EpistemicContrastRow('P',0,(('a','1'*64),('b','2'*64)),'8'*64))!=s
    assert sig(ps='9'*64)!=s
