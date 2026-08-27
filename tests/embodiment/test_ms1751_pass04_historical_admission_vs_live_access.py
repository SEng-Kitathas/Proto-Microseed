from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from research.run_ms1578_pass01_actual_stream_misbinding import EFFECTS, seeded, prepare

PAYLOAD={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}


def install(m, *, historical: bool):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1751',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(PAYLOAD),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1751',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE_USE'},operational_scope_id='R2'))
    if historical:
        sig=m.capabilities.contracts['OBS'].computed_signature_sha256()
        m.register_capability(CapabilityContract('HIST','historical-admission',{'admission_premise_signatures':(('OBS',sig),)}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1751',),'CURRENT',{},query_obligation_id='HIST-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'HISTORICAL_ADMISSION_VALID'},operational_scope_id='R2'))
    for cid in EFFECTS: m.frames.bind_capability('F',cid)
    m.frames.bind_capability('F','OBS')


def close(m,eid,*,historical: bool):
    kwargs={}
    if historical:
        kwargs.update(admission_basis_capability_id='HIST', admission_basis_obligation=QueryObligation('HIST-Q','historical-admission',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'))
    return m.record_bounded_action_outcome_via_observation_basis(
        eid,observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),
        basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),
        evidence_id='E-OUT',capture_id='C-OUT',**kwargs)


def test_historical_admission_basis_preserves_old_sample_across_live_channel_outage():
    with tempfile.TemporaryDirectory(prefix='ms1751-hist-') as td:
        m,_=seeded(Path(td)); install(m,historical=True); eid,_=prepare(m,'H'); assert close(m,eid,historical=True)['status']=='ACTION_OUTCOME_OBSERVED'
        assert m.derive_admitted_opaque_transition_sample(eid)['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        stale=m.invalidate_capability('OBS',reason='TEMPORARY_LIVE_ACCESS_LOSS')
        assert {'OBS','BASIS'}.issubset(stale) and 'HIST' not in stale
        assert m.derive_admitted_opaque_transition_sample(eid)['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'


def test_without_separate_historical_basis_live_access_loss_blocks_reuse():
    with tempfile.TemporaryDirectory(prefix='ms1751-live-') as td:
        m,_=seeded(Path(td)); install(m,historical=False); eid,_=prepare(m,'L'); assert close(m,eid,historical=False)['status']=='ACTION_OUTCOME_OBSERVED'
        m.invalidate_capability('OBS',reason='TEMPORARY_LIVE_ACCESS_LOSS')
        p=m.derive_admitted_opaque_transition_sample(eid)
        assert p=={'status':'ABSTAIN','reason':'LIVE_OBSERVATION_ADMISSION_NOT_CURRENT','authority':'NONE'}


def test_retrospective_historical_admission_failure_blocks_old_sample():
    with tempfile.TemporaryDirectory(prefix='ms1751-invalid-') as td:
        m,_=seeded(Path(td)); install(m,historical=True); eid,_=prepare(m,'I'); assert close(m,eid,historical=True)['status']=='ACTION_OUTCOME_OBSERVED'
        m.invalidate_capability('HIST',reason='RETROSPECTIVE_ADMISSION_INVALIDATION')
        p=m.derive_admitted_opaque_transition_sample(eid)
        assert p=={'status':'ABSTAIN','reason':'HISTORICAL_OBSERVATION_ADMISSION_NOT_CURRENT','authority':'NONE'}
