from microseed import EpistemicStatus, Observation, Authority
from microseed.development.epistemic_program import begin_generated_epistemic_program_trial
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()



def _scaffold_direct_probe_trial(m, *, successor_deficit_id='D-1904'):
    """Zero-authority historical branch-locus trial for downstream-owner tests only.

    This does not claim the branch locus is the organism's current control state.
    Production trial formation remains owned by the locus-gated Microseed API.
    """
    formed=m.derive_current_revised_surface_direct_probe_program_candidate(
        old_deficit_id='D',successor_deficit_id=successor_deficit_id)
    assert formed['status']=='CURRENT_DIRECT_PROBE_PROGRAM_CANDIDATE',formed
    loci={m.action_outcome_learning.relations[rid].start_state_id for rid in formed['source_relation_ids']}
    assert len(loci)==1,loci
    locus=next(iter(loci))
    deficit=m.epistemic_deficits.records[successor_deficit_id]
    trial=begin_generated_epistemic_program_trial(
        formed['candidate'],deficit_id=deficit.deficit_id,
        discrimination_signature_sha256=deficit.missing_discriminator_signature_sha256,
        capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),
        start_state_id=locus,start_state_evidence_id='TEST_SCAFFOLD_BRANCH_LOCUS_NOT_CURRENT_OBSERVATION',
    )
    assert trial.execution_authority==trial.truth_authority=='NONE'
    return trial

def _bound():
    td,m,calls,c=_qualified_refinement_fixture();b=_qualify_revised_surface(m,c);m.accept_revisit_hypothesis_revision('D',b.binding_id)
    fresh=m.append_evidence('E-U-1904',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
    s=m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1904',unknown_evidence_id=fresh.evidence_id)
    assert m.bind_current_revised_surface_direct_probe(old_deficit_id='D',successor_deficit_id='D-1904')['status']=='PROBE_AVAILABLE'
    return td,m,calls,b,s




def _bound_at_probe_locus():
    """Rebuild the same revised successor with the live control state already at s1."""
    td,m,calls,c=_qualified_refinement_fixture()
    b=_qualify_revised_surface(m,c);m.accept_revisit_hypothesis_revision('D',b.binding_id)
    m.observe_opaque_control_state(
        Observation('MS1904-PROBE-LOCUS-S1','EXT','opaque-control','s1',authority=Authority.OBSERVATION_ONLY),
        evidence_id='E-MS1904-PROBE-LOCUS-S1')
    fresh=m.append_evidence('E-U-1904-LOCUS',{'kind':'FRESH_UNKNOWN_AT_DIRECT_PROBE_LOCUS'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
    s=m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1904',unknown_evidence_id=fresh.evidence_id)
    assert m.bind_current_revised_surface_direct_probe(old_deficit_id='D',successor_deficit_id='D-1904')['status']=='PROBE_AVAILABLE'
    assert m.action_closure.current_state.state_id=='s1'
    return td,m,calls,b,s

def test_unique_direct_probe_forms_one_step_candidate_from_exact_qualified_branch_relation_digests():
    td,m,calls,b,s=_bound()
    try:
        before=len(m.action_closure.executions)
        out=m.derive_current_revised_surface_direct_probe_program_candidate(old_deficit_id='D',successor_deficit_id='D-1904')
        assert out['status']=='CURRENT_DIRECT_PROBE_PROGRAM_CANDIDATE',out
        c=out['candidate']; assert c.steps==('B',)
        expected_ids=tuple(sorted({b.relation_id_for(bucket,'B') for bucket in b.qualified_bucket_ids}))
        assert out['source_relation_ids']==expected_ids
        expected_digests=tuple(sorted(m.action_outcome_learning.relations[rid].as_epistemic_alternative_relation().digest() for rid in expected_ids))
        assert c.source_relation_digests==expected_digests
        assert c.frame_epochs==( ('F',0), )
        assert c.proposal_authority==c.execution_authority==c.truth_authority=='NONE'
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_current_direct_probe_candidate_does_not_become_trial_when_live_state_is_not_branch_locus():
    td,m,calls,b,s=_bound()
    try:
        before=len(m.action_closure.executions)
        candidate=m.derive_current_revised_surface_direct_probe_program_candidate(old_deficit_id='D',successor_deficit_id='D-1904')
        assert candidate['status']=='CURRENT_DIRECT_PROBE_PROGRAM_CANDIDATE',candidate
        out=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())
        assert out['status']=='ABSTAIN',out
        assert out['reason']=='CURRENT_CONTROL_STATE_NOT_DIRECT_PROBE_LOCUS'
        assert out['decision_surface']['direct_probe_locus_state_id']=='s1'
        assert out['decision_surface']['current_control_state_id']=='s2'
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)
