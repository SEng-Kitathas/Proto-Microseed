import pytest
from microseed import ExternalProjectionQualifier, EpistemicStatus
from tests.embodiment.test_ms1862_pass15_revisit_refinement_reuses_external_projection_admission import _qualified_refinement_fixture


def test_qualified_refinement_projection_does_not_manufacture_value_bearing_branch_relation():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        before_ids=set(m.action_outcome_learning.relations)
        before_sx=[r.relation_id for r in m.action_outcome_learning.relations.values() if r.capability_id=='B' and r.next_state_id=='sx']
        assert before_sx==[]

        q=m.append_evidence('Q-MS1863',{'kind':'REVISIT_REFINEMENT_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL')
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1863').qualify(c,qualification_evidence=(q,))
        rec=m.admit_revisit_one_step_visible_history_refinement_projection('D',ticket,projection_id='P-REF-1863')
        assert rec.current

        # Qualifying the representation changes no consequential relation state.
        assert set(m.action_outcome_learning.relations)==before_ids
        assert [r.relation_id for r in m.action_outcome_learning.relations.values() if r.capability_id=='B' and r.next_state_id=='sx']==[]

        # Existing projection-conditioned routing refuses a fabricated branch relation.
        with pytest.raises(ValueError,match='PROJECTION_ROUTING_RELATION_NOT_FOUND'):
            m.nominate_projection_conditioned_relation_routing(
                projection_id='P-REF-1863',task_id='REVISIT-1863',
                action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
                default_action_relations=(('B','FAKE-B-SX-RELATION'),),
                bucket_action_overrides=(),source_evidence_ids=('Q-MS1863',),
            )
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
        assert calls==['A','B']
    finally:
        td.cleanup()
