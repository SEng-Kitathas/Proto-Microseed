from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, Observation, OperationalFrameContract, QualificationState, QueryObligation
from research.run_ms1578_pass01_actual_stream_misbinding import EFFECTS, seeded, prepare

PAYLOAD={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}


def install(m):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1750',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(PAYLOAD),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1750',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='R2'))


def bind_frame(m, frame='F'):
    for cid in EFFECTS:
        m.frames.bind_capability(frame,cid)
    m.frames.bind_capability(frame,'OBS')


def close(m,eid,tag='X'):
    return m.record_bounded_action_outcome_via_observation_basis(
        eid,observation_capability_id='OBS',
        observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),
        basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),
        evidence_id=f'E-OUT-{tag}',capture_id=f'C-OUT-{tag}')


def test_existing_execution_observation_and_frame_owners_project_one_ephemeral_sample():
    with tempfile.TemporaryDirectory(prefix='ms1750-good-') as td:
        m,_=seeded(Path(td)); install(m); bind_frame(m); eid,_=prepare(m,'G')
        r=close(m,eid,'G'); assert r['status']=='ACTION_OUTCOME_OBSERVED'
        p=m.derive_admitted_opaque_transition_sample(eid)
        assert p['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        s=p['sample']
        assert s.origin_id==eid
        assert s.start_token==m.action_closure.executions[eid].start_state_id
        assert s.action_token==m.action_closure.executions[eid].capability_id
        assert s.end_token==r['outcome']['actual_next_state_id']
        assert (s.frame_id,s.frame_epoch)==('F',0)
        assert p['truth_authority']==p['qualification_authority']==p['execution_authority']==p['evidence_independence_authority']=='NONE'
        assert not any(e['kind']=='OPAQUE_TRANSITION_SAMPLE' for e in m.store.events())


def test_no_common_action_observation_frame_abstains():
    with tempfile.TemporaryDirectory(prefix='ms1750-noframe-') as td:
        m,_=seeded(Path(td)); install(m); eid,_=prepare(m,'N')
        close(m,eid,'N')
        p=m.derive_admitted_opaque_transition_sample(eid)
        assert p=={'status':'ABSTAIN','reason':'UNIQUE_COMMON_OPERATIONAL_FRAME_REQUIRED','authority':'NONE'}


def test_two_common_frames_preserve_frame_ambiguity():
    with tempfile.TemporaryDirectory(prefix='ms1750-multi-') as td:
        m,_=seeded(Path(td)); install(m)
        m.register_operational_frame(OperationalFrameContract('F2','opaque-2','2'*64,Authority.DERIVED_READ_ONLY,('MS1750',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
        bind_frame(m,'F'); bind_frame(m,'F2')
        eid,_=prepare(m,'M'); close(m,eid,'M')
        p=m.derive_admitted_opaque_transition_sample(eid)
        assert p=={'status':'ABSTAIN','reason':'UNIQUE_COMMON_OPERATIONAL_FRAME_REQUIRED','authority':'NONE'}


def test_forged_raw_lineage_without_receipt_cannot_project_sample():
    with tempfile.TemporaryDirectory(prefix='ms1750-raw-') as td:
        m,_=seeded(Path(td)); install(m); bind_frame(m); eid,_=prepare(m,'R')
        obs=Observation('C-OUT-R','CAPABILITY:OBS',f'action-execution:{eid}',dict(PAYLOAD),
            currentness_basis='QUALIFIED_OBSERVATION_CAPABILITY_AND_BOUNDED_USE_BASIS',authority=Authority.OBSERVATION_ONLY,
            lineage=('OBSERVATION_CAPABILITY:OBS@0','OBSERVATION_USE_BASIS:BASIS@0'))
        r=m.record_bounded_action_outcome(eid,obs,evidence_id='E-OUT-R',evidence_premise_epochs=(('BASIS',0),))
        assert r['status']=='ACTION_OUTCOME_OBSERVED'
        p=m.derive_admitted_opaque_transition_sample(eid)
        assert p=={'status':'ABSTAIN','reason':'AUTHENTICATED_OBSERVATION_INGRESS_REQUIRED','authority':'NONE'}
