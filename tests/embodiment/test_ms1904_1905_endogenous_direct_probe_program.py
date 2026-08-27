from microseed import EpistemicStatus
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()

def _bound():
    td,m,calls,c=_qualified_refinement_fixture();b=_qualify_revised_surface(m,c);m.accept_revisit_hypothesis_revision('D',b.binding_id)
    fresh=m.append_evidence('E-U-1904',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
    s=m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1904',unknown_evidence_id=fresh.evidence_id)
    assert m.bind_current_revised_surface_direct_probe(old_deficit_id='D',successor_deficit_id='D-1904')['status']=='PROBE_AVAILABLE'
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


def test_current_direct_probe_candidate_reuses_existing_inert_trial_owner_without_action_side_effect():
    td,m,calls,b,s=_bound()
    try:
        before=len(m.action_closure.executions)
        out=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())
        assert out['status']=='EPISTEMIC_TRIAL_INSTANTIATED',out
        t=out['trial']; assert t.steps==('B',) and t.status=='OPEN'
        assert t.discrimination_signature_sha256==s.missing_discriminator_signature_sha256
        assert t.source_relation_digests==out['candidate'].source_relation_digests
        assert t.execution_authority==t.truth_authority=='NONE'
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)
