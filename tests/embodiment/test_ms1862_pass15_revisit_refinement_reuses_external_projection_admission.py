import pytest
from microseed import ExternalProjectionQualifier, EpistemicStatus
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1858_pass11_live_second_step_challenge_participates_in_owned_history_refinement import _install,_run_step,_add_history_pair


def _qualified_refinement_fixture():
    td,m,calls,trial,dc=_generated_fixture(); outcomes={};_install(m,outcomes)
    t1,b1=_run_step(m,outcomes,trial,dc,'A','s1','LIVE-A'); assert b1['status']=='CONSENSUS_NONDISCRIMINATING'
    _,b2=_run_step(m,outcomes,t1,dc,'B','sx','LIVE-B'); assert b2['status']=='MODEL_SPACE_CHALLENGE'
    _add_history_pair(m,outcomes,0,'s0','sx');_add_history_pair(m,outcomes,1,'r','s2');_add_history_pair(m,outcomes,2,'r','s2')
    derived=m.derive_revisit_one_step_visible_history_refinement('D');assert derived['status']=='REVISIT_ONE_STEP_VISIBLE_HISTORY_REFINEMENT_CANDIDATE'
    return td,m,calls,derived['refinement']


def test_revisit_refinement_uses_existing_external_projection_qualification_boundary():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        qualifier=ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1862')
        bad=qualifier.qualify(c,qualification_evidence=())
        with pytest.raises(ValueError,match='INVALID_EXTERNAL_REVISIT_REFINEMENT_QUALIFICATION'):
            m.admit_revisit_one_step_visible_history_refinement_projection('D',bad,projection_id='P-REF')
        assert 'P-REF' not in m.epistemic_projections.records

        q=m.append_evidence('Q-MS1862',{'kind':'REVISIT_REFINEMENT_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL')
        ticket=qualifier.qualify(c,qualification_evidence=(q,))
        rec=m.admit_revisit_one_step_visible_history_refinement_projection('D',ticket,projection_id='P-REF')
        assert rec.projection_id=='P-REF'
        assert rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'
        assert rec.proposal_candidate_sha256==c.digest()==rec.signature_sha256
        assert rec.qualification_evidence_ids==('Q-MS1862',)
        assert rec.frame_epochs==(c.frame_epoch,)
        assert rec.semantic_projection_authority==rec.discovery_authority=='NONE'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
        assert calls==['A','B']
    finally:
        td.cleanup()
