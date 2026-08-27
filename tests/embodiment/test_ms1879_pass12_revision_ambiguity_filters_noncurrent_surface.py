from microseed import EpistemicStatus, ExternalProjectionQualifier
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def _qualify_distinct_second_projection_binding(m,c):
    q=m.append_evidence('Q-PROJ-1879-B',{'kind':'REFINEMENT_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP-ALT-PROJ')
    pt=ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1879-ALT-PROJ').qualify(c,qualification_evidence=(q,))
    rec=m.admit_revisit_one_step_visible_history_refinement_projection('D',pt,projection_id='P-REF-1879-B')
    prop=m.append_evidence('ROUTE-PROP-1879-B',{'kind':'ROUTING_PROPOSAL'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-PROPOSAL')
    route=m.nominate_projection_conditioned_relation_routing(
        projection_id=rec.projection_id,task_id='REVISIT-1868',action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
        default_action_relations=(('B','R-B-SX-1868'),),bucket_action_overrides=(('s0','B','R-B-S2-1868'),),source_evidence_ids=(prop.evidence_id,),
    )
    refs=[]
    for i in range(12):
        bucket='s0' if i%2==0 else 'r';end,effect=('s2',-1.0) if bucket=='s0' else ('sx',1.0)
        refs.append(m.append_evidence(f'ROUTE-HOLDOUT-1879-B-{i}',{
            'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':rec.projection_id,'projection_epoch':rec.epoch,
            'projection_signature_sha256':rec.signature_sha256,'projection_bucket_id':bucket,'task_id':'REVISIT-1868',
            'action_id':'B','channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':effect,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HSP-ALT-ROUTE'))
    t=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='HSP-MS1879-ALT-ROUTE').qualify(route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
    out=m.qualify_projection_conditioned_relation_routing(t); assert out['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
    return m.action_outcome_learning.projection_conditioned_bindings[out['binding']['binding_id']]


def test_noncurrent_rival_revision_drops_out_without_deleting_history_or_selecting_it():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        first=_qualify_revised_surface(m,c)
        rival=_qualify_distinct_second_projection_binding(m,c)
        amb=m.derive_current_revisit_hypothesis_revision_surface('D')
        assert amb['status']=='REVISION_AMBIGUOUS'
        historical_rival_id=rival.binding_id
        stale=m.epistemic_projections.invalidate(rival.projection_id)
        assert not stale.current
        assert historical_rival_id in m.action_outcome_learning.projection_conditioned_bindings
        now=m.derive_current_revisit_hypothesis_revision_surface('D')
        assert now['status']=='CURRENT_UNIQUE_REVISED_HYPOTHESIS_SURFACE'
        assert now['binding_ids']==(first.binding_id,)
        accepted=m.accept_revisit_hypothesis_revision('D',first.binding_id)
        assert accepted['status']=='OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        assert accepted['model_switch_authority']=='NONE'
    finally: td.cleanup()
