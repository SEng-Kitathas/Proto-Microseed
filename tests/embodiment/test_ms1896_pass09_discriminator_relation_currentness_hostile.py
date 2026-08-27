from microseed import EpistemicStatus
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()


def test_episode_premise_drift_must_stale_successor_whose_discriminator_depended_on_routed_relation():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        m.accept_revisit_hypothesis_revision('D',b.binding_id)
        fresh=m.append_evidence('E-U-1896',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
        successor=m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1896',unknown_evidence_id=fresh.evidence_id)
        assert successor.state.value=='ACTION_LIMITED'
        assert any(a.kind=='EPISODE' and a.object_id=='EP' and a.epoch==0 for a in successor.premise_anchors), successor.premise_anchors
        m.change_episode_schema('EP',reason='MS1896_HOSTILE_EPISODE_DRIFT')
        assert m.epistemic_deficits.records['D-1896'].state.value=='STALE'
    finally:_close(m,td)
