from __future__ import annotations

import pytest

from microseed import EpistemicStatus, ExternalProjectionQualifier
from microseed.development.action_closure import OpaqueControlStateWitness
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1858_pass11_live_second_step_challenge_participates_in_owned_history_refinement import _install, _add_history_pair
from tests.embodiment.test_ms1864_pass17_qualified_refinement_routes_independently_qualified_relations import _add_relation


def _fixture():
    td,m,calls,trial,dc=_generated_fixture()
    outcomes={}; _install(m,outcomes)
    _add_history_pair(m,outcomes,0,'s0','sx')
    _add_history_pair(m,outcomes,1,'s0','sx')
    _add_history_pair(m,outcomes,2,'r','s2')
    _add_history_pair(m,outcomes,3,'r','s2')
    surface=m.derive_admitted_one_step_visible_history_refinements()
    assert surface['status']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENTS_FOUND',surface
    target=[c for c in surface['refinements'] if (c.start_token,c.action_token)==('s1','B')]
    assert len(target)==1
    return td,m,calls,outcomes,target[0]


def _ticket(m,c,eid='Q-MS1971'):
    q=m.append_evidence(eid,{'kind':'REFINEMENT_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1971')
    return ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1971-PROJECTION').qualify(c,qualification_evidence=(q,))


def _close(td,m):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()


def test_owned_history_refinement_generically_admits_and_routes_without_revisit_authority():
    td,m,calls,outcomes,c=_fixture()
    try:
        ticket=_ticket(m,c)
        rec=m.admit_one_step_visible_history_refinement_projection(ticket,projection_id='P-MS1971')
        assert rec.current
        assert rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'
        assert rec.signature_sha256==c.digest()
        assert rec.frame_epochs==(c.frame_epoch,)
        assert all(not x.startswith('DEFICIT:') for x in rec.assistance_ancestry)

        rsx=_add_relation(m,'R-MS1971-SX','sx',1.0,'MS1971-SX')
        rs2=_add_relation(m,'R-MS1971-S2','s2',-1.0,'MS1971-S2')
        assert m._action_outcome_relation_current(rsx) and m._action_outcome_relation_current(rs2)

        prop=m.append_evidence('ROUTE-PROP-MS1971',{'kind':'ROUTING_PROPOSAL'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-PROPOSAL')
        route=m.nominate_projection_conditioned_relation_routing(
            projection_id='P-MS1971',task_id='GENERIC-MS1971',action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
            default_action_relations=(('B','R-MS1971-S2'),),bucket_action_overrides=(('s0','B','R-MS1971-SX'),),
            source_evidence_ids=(prop.evidence_id,),
        )
        refs=[]
        for i in range(12):
            bucket='s0' if i%2==0 else 'r'; end,effect=('sx',1.0) if bucket=='s0' else ('s2',-1.0)
            refs.append(m.append_evidence(f'ROUTE-HOLDOUT-MS1971-{i}',{
                'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':'P-MS1971','projection_epoch':0,
                'projection_signature_sha256':rec.signature_sha256,'projection_bucket_id':bucket,'task_id':'GENERIC-MS1971',
                'action_id':'B','channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':effect,
            },EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1971-ROUTING-HOLDOUT'))
        rt=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='EXTERNAL-MS1971-ROUTE').qualify(
            route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
        admitted=m.qualify_projection_conditioned_relation_routing(rt)
        assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',admitted
        bid=admitted['binding']['binding_id']

        chosen=None
        for outcome in m.action_closure.outcomes.values():
            projected=m.derive_admitted_opaque_transition_sample(outcome.execution_id)
            if projected.get('status')!='ADMITTED_OPAQUE_TRANSITION_SAMPLE': continue
            row=projected['sample']
            if row.sample_id in c.source_sample_ids and row.start_token=='s0' and row.end_token=='s1':
                chosen=outcome;break
        assert chosen is not None
        m.action_closure.set_state(OpaqueControlStateWitness('s1',chosen.evidence_id))
        resolved=m.resolve_current_one_step_visible_history_projection_conditioned_relation(
            bid,action_id='B',task_id='GENERIC-MS1971',channel_id='opaque-control',horizon=1)
        assert resolved['status']=='CURRENT_PARTITION_SCOPED_RELATION',resolved
        assert resolved['projection_bucket_id']=='s0'
        assert resolved['relation_id']=='R-MS1971-SX'
        assert resolved['bucket_derivation_basis']=='CURRENT_ADMITTED_PREDECESSOR_VISIBLE_STATE'
        assert resolved['bucket_selection_authority']==resolved['hidden_state_authority']==resolved['history_depth_extension_authority']=='NONE'

        events=[e['payload'] for e in m.store.events() if e['kind']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENT_PROJECTION_ADMITTED']
        assert len(events)==1
        assert events[0]['semantic_category_authority']==events[0]['truth_authority']==events[0]['execution_authority']=='NONE'
    finally:_close(td,m)


def test_generic_history_refinement_admission_rejects_zero_evidence_ticket():
    td,m,calls,outcomes,c=_fixture()
    try:
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1971-PROJECTION').qualify(c,qualification_evidence=())
        with pytest.raises(ValueError,match='INVALID_EXTERNAL_HISTORY_REFINEMENT_QUALIFICATION'):
            m.admit_one_step_visible_history_refinement_projection(ticket)
        assert not m.epistemic_projections.records
    finally:_close(td,m)


def test_generic_history_refinement_admission_rejects_ticket_after_frame_stales():
    td,m,calls,outcomes,c=_fixture()
    try:
        ticket=_ticket(m,c,'Q-MS1971-DRIFT')
        m.frames.change('F',reason='MS1971-FRAME-DRIFT')
        with pytest.raises(ValueError,match='CURRENT_HISTORY_REFINEMENT_FOR_TICKET_NOT_FOUND|HISTORY_REFINEMENT_FRAME_DRIFT_AFTER_NOMINATION'):
            m.admit_one_step_visible_history_refinement_projection(ticket)
        assert not m.epistemic_projections.records
    finally:_close(td,m)
