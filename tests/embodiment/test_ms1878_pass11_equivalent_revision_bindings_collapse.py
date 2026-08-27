from microseed import EpistemicStatus
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_multiple_binding_identities_with_same_revision_content_collapse_to_one_surface():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        first=_qualify_revised_surface(m,c)
        candidate=m.action_outcome_learning.projection_routing_candidates[first.candidate_id]
        refs=[]
        for i in range(12):
            bucket='s0' if i%2==0 else 'r';end,effect=('sx',1.0) if bucket=='s0' else ('s2',-1.0)
            refs.append(m.append_evidence(f'ROUTE-HOLDOUT-1878-{i}',{
                'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':candidate.projection_id,'projection_epoch':candidate.projection_epoch,
                'projection_signature_sha256':candidate.projection_signature_sha256,'projection_bucket_id':bucket,'task_id':candidate.task_id,
                'action_id':'B','channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':effect,
            },EpistemicStatus.PRESSURE_SUPPORTED,source='SECOND-INDEPENDENT-HOLDOUT-PATH'))
        ticket=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='HSP-MS1878-SECOND').qualify(
            candidate,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
        out=m.qualify_projection_conditioned_relation_routing(ticket)
        assert out['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        second=m.action_outcome_learning.projection_conditioned_bindings[out['binding']['binding_id']]
        assert second.binding_id!=first.binding_id
        surface=m.derive_current_revisit_hypothesis_revision_surface('D')
        assert surface['status']=='CURRENT_UNIQUE_REVISED_HYPOTHESIS_SURFACE'
        assert set(surface['binding_ids'])=={first.binding_id,second.binding_id}
        accepted=m.accept_revisit_hypothesis_revision('D',second.binding_id)
        assert accepted['status']=='OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        assert set(accepted['equivalent_binding_ids'])=={first.binding_id,second.binding_id}
        assert accepted['model_switch_authority']=='NONE'
    finally: td.cleanup()
