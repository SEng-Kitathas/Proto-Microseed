import pytest
from microseed import EpistemicStatus, Authority, CapabilityContract, QualificationState
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()

def _successor():
    td,m,calls,c=_qualified_refinement_fixture()
    b=_qualify_revised_surface(m,c);m.accept_revisit_hypothesis_revision('D',b.binding_id)
    fresh=m.append_evidence('E-U-1898',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
    s=m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1898',unknown_evidence_id=fresh.evidence_id)
    return td,m,b,s

@pytest.mark.parametrize('kind',('PROJECTION','EPISODE','FRAME','VALUE','CAPABILITY'))
def test_each_present_discriminator_premise_drift_stales_successor(kind):
    td,m,b,s=_successor()
    try:
        anchors={(a.kind,a.object_id,a.epoch) for a in s.premise_anchors}
        if kind=='PROJECTION':
            assert ('PROJECTION',b.projection_id,0) in anchors
            m.change_epistemic_projection(b.projection_id,new_signature_sha256='9'*64,reason='MS1898_PROJECTION_DRIFT')
        elif kind=='EPISODE':
            assert ('EPISODE','EP',0) in anchors
            m.change_episode_schema('EP',reason='MS1898_EPISODE_DRIFT')
        elif kind=='FRAME':
            assert ('FRAME','F',0) in anchors
            m.change_operational_frame('F',reason='MS1898_FRAME_DRIFT')
        elif kind=='VALUE':
            assert ('VALUE','V',0) in anchors
            m.change_value_variable('V',reason='MS1898_VALUE_DRIFT')
        else:
            assert ('CAPABILITY_PREMISE','B',0) in anchors
            m.change_capability_dependency('B',reason='MS1898_CAPABILITY_DRIFT')
        assert m.epistemic_deficits.records['D-1898'].state.value=='STALE'
    finally:_close(m,td)

def test_unrelated_capability_drift_does_not_stale_successor():
    td,m,b,s=_successor()
    try:
        m.register_capability(CapabilityContract(
            'UNRELATED-MS1898','opaque',{}, {},(),(),Authority.EFFECT,('MS1898',),'CURRENT',{},
            qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:None,operational_scope_id='S'))
        m.change_capability_dependency('UNRELATED-MS1898',reason='UNRELATED_DRIFT')
        assert m.epistemic_deficits.records['D-1898'].state.value=='ACTION_LIMITED'
    finally:_close(m,td)
