from microseed import ExternalProjectionQualifier, EpistemicStatus
from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation, ExternalProjectionConditionedRelationQualifier
from tests.embodiment.test_ms1862_pass15_revisit_refinement_reuses_external_projection_admission import _qualified_refinement_fixture


def _add_relation(m,rid,end,effect,tag):
    train=f'{tag}-TRAIN';qual=f'{tag}-QUAL'
    m.append_evidence(train,{'kind':'RELATION_TRAIN','id':rid},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-REL')
    m.append_evidence(qual,{'kind':'RELATION_QUAL','id':rid},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP-REL')
    r=QualifiedActionOutcomePredictiveRelation(
        relation_id=rid,candidate_id='C-'+rid,candidate_sha256=(('a' if end=='sx' else 'b')*64),
        start_state_id='s1',capability_id='B',next_state_id=end,value_effect=float(effect),
        support=12,consistency=1.0,source_evidence_ids=(train,),qualification_evidence_ids=(qual,),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=0,frame_epochs=(('F',0),),
        episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
    )
    m.action_outcome_learning.add_relation(r);return r


def test_qualified_refinement_plus_independently_qualified_branch_relations_reuses_existing_scoped_routing():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        # Qualify/admit the structural refinement through the existing projection owner.
        qp=m.append_evidence('Q-PROJ-1864',{'kind':'REFINEMENT_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL')
        pt=ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1864-PROJ').qualify(c,qualification_evidence=(qp,))
        rec=m.admit_revisit_one_step_visible_history_refinement_projection('D',pt,projection_id='P-REF-1864')
        assert rec.current

        # Consequential branches are separately already-qualified relations.  The
        # projection does not create or qualify either of them.
        rsx=_add_relation(m,'R-B-SX','sx',1.0,'SX1864')
        rs2=_add_relation(m,'R-B-S2','s2',-1.0,'S21864')
        assert m._action_outcome_relation_current(rsx) and m._action_outcome_relation_current(rs2)

        prop=m.append_evidence('ROUTE-PROP-1864',{'kind':'ROUTING_PROPOSAL'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-PROPOSAL')
        route=m.nominate_projection_conditioned_relation_routing(
            projection_id='P-REF-1864',task_id='REVISIT-1864',action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
            default_action_relations=(('B','R-B-S2'),),bucket_action_overrides=(('s0','B','R-B-SX'),),
            source_evidence_ids=(prop.evidence_id,),
        )
        refs=[]
        for i in range(12):
            bucket='s0' if i%2==0 else 'r';end,effect=('sx',1.0) if bucket=='s0' else ('s2',-1.0)
            refs.append(m.append_evidence(f'ROUTE-HOLDOUT-1864-{i}',{
                'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':'P-REF-1864','projection_epoch':0,
                'projection_signature_sha256':rec.signature_sha256,'projection_bucket_id':bucket,'task_id':'REVISIT-1864',
                'action_id':'B','channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':effect,
            },EpistemicStatus.PRESSURE_SUPPORTED,source='HSP-ROUTING-HOLDOUT'))
        rt=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='HSP-MS1864-ROUTE').qualify(
            route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
        admitted=m.qualify_projection_conditioned_relation_routing(rt)
        assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',admitted
        bid=admitted['binding']['binding_id']
        a=m.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='s0',action_id='B',task_id='REVISIT-1864',channel_id='opaque-control',horizon=1)
        b=m.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='r',action_id='B',task_id='REVISIT-1864',channel_id='opaque-control',horizon=1)
        assert a['status']==b['status']=='CURRENT_PARTITION_SCOPED_RELATION'
        assert a['relation_id']=='R-B-SX' and b['relation_id']=='R-B-S2'
        assert a['truth_authority']==a['model_switch_authority']=='NONE'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
        assert calls==['A','B']
    finally:
        td.cleanup()
