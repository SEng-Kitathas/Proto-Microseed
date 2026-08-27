from microseed.development.epistemic import EpistemicContrastBinding, EpistemicContrastRow
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound,_close
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob


def _trial_and_requirement(m):
    formed=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())
    assert formed['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
    reqs=[x for x in m.epistemic_contrasts.bindings.values() if x.deficit_id=='D-1904' and x.binding_origin=='DERIVED_CURRENT_REVISED_SURFACE_CONTRAST']
    assert len(reqs)==1
    return formed['trial'],reqs[0]


def test_content_equivalent_registered_requirement_paths_collapse_instead_of_creating_false_ambiguity():
    td,m,calls,b,s=_bound()
    try:
        trial,req=_trial_and_requirement(m)
        duplicate=EpistemicContrastBinding(
            binding_id='DERIVED-EQUIVALENT-MS1911',deficit_id=req.deficit_id,
            hypothesis_digest_sha256=req.hypothesis_digest_sha256,rows=req.rows,
            binding_origin='DERIVED_CURRENT_REVISED_SURFACE_CONTRAST',
            assistance_ancestry=('EQUIVALENT_PROVENANCE_PATH_MS1911',),
        )
        m.register_epistemic_contrast(duplicate)
        out=m.derive_current_program_discriminator_satisfaction(trial)
        assert out.licenses_yes(),out.serializable()
    finally:_close(m,td)


def test_genuinely_distinct_current_registered_requirements_preserve_ambiguity():
    td,m,calls,b,s=_bound()
    try:
        trial,req=_trial_and_requirement(m)
        row=req.rows[0]
        changed=EpistemicContrastRow(
            projection_id=row.projection_id,projection_epoch=row.projection_epoch,
            candidate_outcome_digests=tuple((cid, ('e'*64 if i==0 else digest)) for i,(cid,digest) in enumerate(row.candidate_outcome_digests)),
            condition_signature_sha256=row.condition_signature_sha256,
        )
        distinct=EpistemicContrastBinding(
            binding_id='DERIVED-DISTINCT-MS1911',deficit_id=req.deficit_id,
            hypothesis_digest_sha256=req.hypothesis_digest_sha256,rows=(changed,),
            binding_origin='DERIVED_CURRENT_REVISED_SURFACE_CONTRAST',
            assistance_ancestry=('DISTINCT_PROVENANCE_PATH_MS1911',),
        )
        m.register_epistemic_contrast(distinct)
        out=m.derive_current_program_discriminator_satisfaction(trial)
        assert not out.licenses_yes(),out.serializable()
        assert out.reason=='UNIQUE_CURRENT_REGISTERED_DISCRIMINATOR_REQUIRED'
    finally:_close(m,td)
