from microseed import EpistemicStatus, ExternalProjectionQualifier
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from tests.embodiment.test_ms1864_pass17_qualified_refinement_routes_independently_qualified_relations import _add_relation
from tests.embodiment.test_ms1862_pass15_revisit_refinement_reuses_external_projection_admission import _qualified_refinement_fixture


def _qualify_revised_surface(m, c):
    qp=m.append_evidence('Q-PROJ-1868',{'kind':'REFINEMENT_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL')
    pt=ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1868-PROJ').qualify(c,qualification_evidence=(qp,))
    rec=m.admit_revisit_one_step_visible_history_refinement_projection('D',pt,projection_id='P-REF-1868')
    _add_relation(m,'R-B-SX-1868','sx',1.0,'SX1868')
    _add_relation(m,'R-B-S2-1868','s2',-1.0,'S21868')
    prop=m.append_evidence('ROUTE-PROP-1868',{'kind':'ROUTING_PROPOSAL'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-PROPOSAL')
    route=m.nominate_projection_conditioned_relation_routing(
        projection_id=rec.projection_id,task_id='REVISIT-1868',action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
        default_action_relations=(('B','R-B-S2-1868'),),bucket_action_overrides=(('s0','B','R-B-SX-1868'),),source_evidence_ids=(prop.evidence_id,),
    )
    refs=[]
    for i in range(12):
        bucket='s0' if i%2==0 else 'r'; end,effect=('sx',1.0) if bucket=='s0' else ('s2',-1.0)
        refs.append(m.append_evidence(f'ROUTE-HOLDOUT-1868-{i}',{
            'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':rec.projection_id,'projection_epoch':rec.epoch,
            'projection_signature_sha256':rec.signature_sha256,'projection_bucket_id':bucket,'task_id':'REVISIT-1868','action_id':'B',
            'channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':effect,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HSP-ROUTING-HOLDOUT'))
    ticket=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='HSP-MS1868-ROUTE').qualify(
        route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
    admitted=m.qualify_projection_conditioned_relation_routing(ticket)
    assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
    return m.action_outcome_learning.projection_conditioned_bindings[admitted['binding']['binding_id']]


def test_revised_model_does_not_rewrite_old_deficit_and_existing_ms1177_succession_owner_remains_lawful():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        old=m.epistemic_deficits.records['D']
        old_digest=old.hypothesis_digest_sha256
        old_unknown=old.unknown_evidence_id
        old_relevant=tuple(old.relevant_evidence_ids)
        assert old.state.value=='REVISIT_REQUIRED'
        binding=_qualify_revised_surface(m,c)
        assert m._projection_conditioned_binding_current(binding)
        # A qualified revised consequential surface does not silently rewrite/reopen
        # the historical deficit.  MS1177 still owns succession semantics.
        assert old.state.value=='REVISIT_REQUIRED'
        assert old.hypothesis_digest_sha256==old_digest
        m.stale_epistemic_deficit('D',reason='BOUNDED_HYPOTHESIS_SET_CHANGED')
        assert old.state.value=='STALE'
        assert old.hypothesis_digest_sha256==old_digest
        assert old.unknown_evidence_id==old_unknown
        assert tuple(old.relevant_evidence_ids)==old_relevant
        # If a new bounded UNKNOWN is later established, it is a new record with a
        # new content identity; the old UNKNOWN is never rewritten.
        u=m.append_evidence('E-U-REVISED-1868',{'kind':'REVISED_SURFACE_UNKNOWN'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
        new=m.record_action_limited_unknown(
            deficit_id='D-REVISED-1868',question_key=old.question_key,hypothesis_digest_sha256='b'*64,
            unknown_evidence_id=u.evidence_id,missing_discriminator_signature_sha256='c'*64,premise_anchors=old.premise_anchors,
            assistance_ancestry=('MS1868_OWNER_AUDIT_CALLER_SUPPLIED_REVISED_DIGEST_AND_UNKNOWN',),
        )
        assert new.state.value=='ACTION_LIMITED'
        assert new.hypothesis_digest_sha256!=old.hypothesis_digest_sha256
        assert m.epistemic_development_pressure_ids()==('D-REVISED-1868',)
        assert m.epistemic_revisit_required_ids()==()
        # This pass deliberately identifies the remaining assistance rather than
        # pretending the binding itself decides whether a new UNKNOWN exists.
        assert 'CALLER_SUPPLIED_REVISED_DIGEST_AND_UNKNOWN' in new.assistance_ancestry[0]
        assert calls==['A','B']
    finally:
        td.cleanup()
