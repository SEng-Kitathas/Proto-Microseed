from microseed import ExternalProjectionQualifier, EpistemicStatus
from microseed.development.action_closure import OpaqueControlStateWitness
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from tests.embodiment.test_ms1862_pass15_revisit_refinement_reuses_external_projection_admission import _qualified_refinement_fixture
from tests.embodiment.test_ms1864_pass17_qualified_refinement_routes_independently_qualified_relations import _add_relation


def _install_routing(m,c):
    qp=m.append_evidence('Q-PROJ-1865',{'kind':'REFINEMENT_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL')
    pt=ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1865-PROJ').qualify(c,qualification_evidence=(qp,))
    rec=m.admit_revisit_one_step_visible_history_refinement_projection('D',pt,projection_id='P-REF-1865')
    _add_relation(m,'R-B-SX-1865','sx',1.0,'SX1865')
    _add_relation(m,'R-B-S2-1865','s2',-1.0,'S21865')
    prop=m.append_evidence('ROUTE-PROP-1865',{'kind':'ROUTING_PROPOSAL'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-PROPOSAL')
    route=m.nominate_projection_conditioned_relation_routing(
        projection_id='P-REF-1865',task_id='REVISIT-1865',action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
        default_action_relations=(('B','R-B-S2-1865'),),bucket_action_overrides=(('s0','B','R-B-SX-1865'),),
        source_evidence_ids=(prop.evidence_id,),
    )
    refs=[]
    for i in range(12):
        bucket='s0' if i%2==0 else 'r';end,effect=('sx',1.0) if bucket=='s0' else ('s2',-1.0)
        refs.append(m.append_evidence(f'ROUTE-HOLDOUT-1865-{i}',{
            'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':'P-REF-1865','projection_epoch':0,
            'projection_signature_sha256':rec.signature_sha256,'projection_bucket_id':bucket,'task_id':'REVISIT-1865',
            'action_id':'B','channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':effect,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HSP-ROUTING-HOLDOUT'))
    ticket=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='HSP-MS1865-ROUTE').qualify(
        route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
    admitted=m.qualify_projection_conditioned_relation_routing(ticket);assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
    return admitted['binding']['binding_id']


def test_current_admitted_predecessor_visible_state_derives_bucket_without_caller_bucket_label():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        bid=_install_routing(m,c)
        # Find one exact admitted predecessor transition s0 -> s1 already in the
        # refinement's owned support and make that evidence the current state witness.
        chosen=None
        for outcome in m.action_closure.outcomes.values():
            projected=m.derive_admitted_opaque_transition_sample(outcome.execution_id)
            if projected.get('status')!='ADMITTED_OPAQUE_TRANSITION_SAMPLE': continue
            row=projected['sample']
            if row.sample_id in c.source_sample_ids and row.start_token=='s0' and row.end_token=='s1':
                chosen=outcome;break
        assert chosen is not None
        m.action_closure.set_state(OpaqueControlStateWitness('s1',chosen.evidence_id))
        out=m.resolve_current_one_step_visible_history_projection_conditioned_relation(
            bid,action_id='B',task_id='REVISIT-1865',channel_id='opaque-control',horizon=1)
        assert out['status']=='CURRENT_PARTITION_SCOPED_RELATION',out
        assert out['relation_id']=='R-B-SX-1865'
        assert out['projection_bucket_id']=='s0'
        assert out['bucket_derivation_basis']=='CURRENT_ADMITTED_PREDECESSOR_VISIBLE_STATE'
        assert out['bucket_selection_authority']==out['hidden_state_authority']==out['history_depth_extension_authority']=='NONE'

        # Same visible current state with no exact admitted predecessor ancestry
        # cannot be assigned a bucket by name or nearest match.
        m.action_closure.set_state(OpaqueControlStateWitness('s1','UNRELATED-CURRENT-EVIDENCE'))
        no=m.resolve_current_one_step_visible_history_projection_conditioned_relation(
            bid,action_id='B',task_id='REVISIT-1865',channel_id='opaque-control',horizon=1)
        assert no['status']=='DEFER_UNKNOWN' and no['reason']=='CURRENT_STATE_PREDECESSOR_OUTCOME_NOT_UNIQUE',no
        assert calls==['A','B']
    finally:
        td.cleanup()
