from __future__ import annotations
import tempfile
from pathlib import Path
from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from research.run_ms1578_pass01_actual_stream_misbinding import EFFECTS, seeded, prepare

PAYLOAD={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}

def install(m):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1753',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(PAYLOAD),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1753',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE'},operational_scope_id='R2'))
    for cid in EFFECTS: m.frames.bind_capability('F',cid)
    m.frames.bind_capability('F','OBS')

def close(m,eid):
    return m.record_bounded_action_outcome_via_observation_basis(eid,observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),evidence_id='E-OUT',capture_id='C-OUT')

def test_same_content_frame_signature_survives():
    with tempfile.TemporaryDirectory(prefix='ms1753-good-') as td:
        m,_=seeded(Path(td)); install(m); eid,_=prepare(m,'G'); assert close(m,eid)['status']=='ACTION_OUTCOME_OBSERVED'
        assert m.derive_admitted_opaque_transition_sample(eid)['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'

def test_same_id_epoch_changed_frame_content_is_rejected():
    with tempfile.TemporaryDirectory(prefix='ms1753-alias-') as td:
        m,_=seeded(Path(td)); install(m); eid,_=prepare(m,'A'); assert close(m,eid)['status']=='ACTION_OUTCOME_OBSERVED'
        m.frames.frames['F'].signature_sha256='2'*64
        assert m.frames.is_current('F',0)
        assert m.derive_admitted_opaque_transition_sample(eid)=={'status':'ABSTAIN','reason':'OPERATIONAL_FRAME_CONTENT_DRIFT','authority':'NONE'}
