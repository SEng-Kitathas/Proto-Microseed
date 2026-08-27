from microseed import EpistemicStatus, ExternalProjectionQualifier
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def _qualify_conflicting_second_binding(m,c):
    # Reuse the already-admitted revisit projection from the first surface.
    rec=next(r for r in m.epistemic_projections.records.values() if 'DEFICIT:D' in r.assistance_ancestry)
    prop=m.append_evidence('ROUTE-PROP-1876-B',{'kind':'ROUTING_PROPOSAL'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-PROPOSAL')
    route=m.nominate_projection_conditioned_relation_routing(
        projection_id=rec.projection_id,task_id='REVISIT-1868',action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
        default_action_relations=(('B','R-B-SX-1868'),),bucket_action_overrides=(('s0','B','R-B-S2-1868'),),
        source_evidence_ids=(prop.evidence_id,),
    )
    refs=[]
    for i in range(12):
        bucket='s0' if i%2==0 else 'r'; end,effect=('s2',-1.0) if bucket=='s0' else ('sx',1.0)
        refs.append(m.append_evidence(f'ROUTE-HOLDOUT-1876-B-{i}',{
            'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':rec.projection_id,'projection_epoch':rec.epoch,
            'projection_signature_sha256':rec.signature_sha256,'projection_bucket_id':bucket,'task_id':'REVISIT-1868',
            'action_id':'B','channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':effect,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HSP-CONFLICTING-ROUTING-HOLDOUT'))
    t=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='HSP-MS1876-CONFLICT').qualify(
        route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
    out=m.qualify_projection_conditioned_relation_routing(t)
    assert out['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',out
    return m.action_outcome_learning.projection_conditioned_bindings[out['binding']['binding_id']]


def test_two_distinct_current_revision_surfaces_must_not_allow_caller_pick_to_stale_old_deficit():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        first=_qualify_revised_surface(m,c)
        second=_qualify_conflicting_second_binding(m,c)
        assert first.binding_id!=second.binding_id
        d1=m.derive_revisit_hypothesis_revision_candidate('D',first.binding_id)['revised_hypothesis_digest_sha256']
        d2=m.derive_revisit_hypothesis_revision_candidate('D',second.binding_id)['revised_hypothesis_digest_sha256']
        assert d1!=d2
        # Desired behavior: ambiguity must be preserved; caller binding choice must
        # not become model-switch/deficit-transition authority.
        out=m.accept_revisit_hypothesis_revision('D',first.binding_id)
        assert out['status']=='REVISION_AMBIGUOUS'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
    finally: td.cleanup()
