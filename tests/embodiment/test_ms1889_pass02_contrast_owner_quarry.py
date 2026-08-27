from microseed.development.epistemic import EpistemicContrastBinding, EpistemicContrastRow


def test_contrast_row_is_pre_evidence_partition_carrier_while_binding_signature_is_provenance_heavy():
    row=EpistemicContrastRow('P',7,(('ctx-a','a'*64),('ctx-b','b'*64)),'c'*64)
    a=EpistemicContrastBinding('B-A','D','d'*64,(row,),assistance_ancestry=('PATH-A',))
    b=EpistemicContrastBinding('B-B','D','d'*64,(row,),assistance_ancestry=('PATH-B',))
    assert row.candidate_outcome_digests==(('ctx-a','a'*64),('ctx-b','b'*64))
    assert a.computed_signature_sha256()!=b.computed_signature_sha256()
    assert a.truth_authority==b.truth_authority=='NONE'
