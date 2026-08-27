import pytest
from microseed.development.epistemic import EpistemicProjectionRecord
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1858_pass11_live_second_step_challenge_participates_in_owned_history_refinement import _install,_run_step,_add_history_pair


def test_revisit_refinement_cannot_self_admit_as_consequential_projection():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        outcomes={};_install(m,outcomes)
        t1,b1=_run_step(m,outcomes,trial,dc,'A','s1','LIVE-A')
        assert b1['status']=='CONSENSUS_NONDISCRIMINATING'
        _,b2=_run_step(m,outcomes,t1,dc,'B','sx','LIVE-B')
        assert b2['status']=='MODEL_SPACE_CHALLENGE'
        _add_history_pair(m,outcomes,0,'s0','sx')
        _add_history_pair(m,outcomes,1,'r','s2')
        _add_history_pair(m,outcomes,2,'r','s2')
        result=m.derive_revisit_one_step_visible_history_refinement('D')
        assert result['status']=='REVISIT_ONE_STEP_VISIBLE_HISTORY_REFINEMENT_CANDIDATE',result
        c=result['refinement']

        # Structural refinement is not already an admitted current projection.
        assert c.refinement_id not in m.epistemic_projections.records
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'

        # The existing consequential routing owner refuses to consume it until an
        # actual current EpistemicProjectionRecord exists.  No implicit conversion.
        with pytest.raises(ValueError,match='PROJECTION_ROUTING_REQUIRES_CURRENT_EPISTEMIC_PROJECTION'):
            m.nominate_projection_conditioned_relation_routing(
                projection_id=c.refinement_id,task_id='REVISIT-REFINEMENT',
                action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
                default_action_relations=(('B','NONEXISTENT'),),
                bucket_action_overrides=(),source_evidence_ids=tuple(m.epistemic_deficits.records['D'].relevant_evidence_ids),
            )

        # Existing projection semantics also refuse an endogenous-qualified label
        # with no qualification ancestry.  Candidate existence cannot self-qualify.
        with pytest.raises(ValueError,match='DISCOVERED_EPISTEMIC_PROJECTION_REQUIRES_EXTERNAL_QUALIFICATION_ANCESTRY'):
            EpistemicProjectionRecord(
                projection_id=c.refinement_id,signature_sha256='a'*64,
                projection_origin='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED',
                proposal_candidate_sha256='b'*64,qualification_evidence_ids=(),
                frame_epochs=(c.frame_epoch,),
            )

        assert c.truth_authority==c.hidden_state_authority=='NONE'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
        assert calls==['A','B']
    finally:
        td.cleanup()
