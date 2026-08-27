from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, Observation, QualificationState, QueryObligation
from research.run_ms1578_pass01_actual_stream_misbinding import seeded, prepare

PAYLOAD={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}


def install(m):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1749',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(PAYLOAD),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1749',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='R2'))


def assured(m,eid):
    return m.record_bounded_action_outcome_via_observation_basis(
        eid,
        observation_capability_id='OBS',
        observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),
        basis_capability_id='BASIS',
        basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),
        evidence_id='E-OUT',capture_id='C-OUT')


def test_assured_wrapper_stamps_content_bound_zero_authority_route_receipt_only():
    with tempfile.TemporaryDirectory(prefix='ms1749-a-') as ta, tempfile.TemporaryDirectory(prefix='ms1749-b-') as tb:
        a,_=seeded(Path(ta)); b,_=seeded(Path(tb)); install(a); install(b)
        exa,_=prepare(a,'X'); exb,_=prepare(b,'X'); assert exa==exb
        ra=assured(a,exa); assert ra['status']=='ACTION_OUTCOME_OBSERVED'
        receipt=ra['observation_admission_receipt']
        assert receipt['execution_id']==exa
        assert receipt['outcome_evidence_id']=='E-OUT'
        assert receipt['route_kind']=='BOUNDED_OBSERVATION_USE_BASIS'
        assert receipt['truth_authority']==receipt['evidence_independence_authority']==receipt['execution_authority']=='NONE'
        assert receipt['observation_capability_signature_sha256']==a.capabilities.contracts['OBS'].computed_signature_sha256()
        assert receipt['observation_basis_capability_signature_sha256']==a.capabilities.contracts['BASIS'].computed_signature_sha256()
        stored=[e['payload'] for e in a.store.events() if e['kind']=='OBSERVATION_ADMISSION_RECEIPT']
        assert stored==[receipt]

        # Same forged Observation claims through the raw public ingress do not create the route receipt.
        forged=Observation(
            'C-OUT','CAPABILITY:OBS',f'action-execution:{exb}',dict(PAYLOAD),
            currentness_basis='QUALIFIED_OBSERVATION_CAPABILITY_AND_BOUNDED_USE_BASIS',
            authority=Authority.OBSERVATION_ONLY,
            lineage=('OBSERVATION_CAPABILITY:OBS@0','OBSERVATION_USE_BASIS:BASIS@0'))
        rb=b.record_bounded_action_outcome(exb,forged,evidence_id='E-OUT',evidence_premise_epochs=(('BASIS',0),))
        assert rb['status']=='ACTION_OUTCOME_OBSERVED'
        assert 'observation_admission_receipt' not in rb
        assert not [e for e in b.store.events() if e['kind']=='OBSERVATION_ADMISSION_RECEIPT']
