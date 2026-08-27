from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, Observation, QualificationState, QueryObligation
from research.run_ms1578_pass01_actual_stream_misbinding import seeded, prepare

PAYLOAD={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}


def install_observation_surface(m):
    m.register_capability(CapabilityContract(
        'OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1748-P1',),'CURRENT',{},
        query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:dict(PAYLOAD),operational_scope_id='R2'))
    m.register_capability(CapabilityContract(
        'BASIS','basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1748-P1',),'CURRENT',{},
        dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='R2'))


def test_assured_ingress_and_raw_forged_ancestry_are_downstream_indistinguishable():
    with tempfile.TemporaryDirectory(prefix='ms1748-p1-assured-') as ta, tempfile.TemporaryDirectory(prefix='ms1748-p1-forged-') as tb:
        assured,_=seeded(Path(ta)); forged,_=seeded(Path(tb))
        install_observation_surface(assured); install_observation_surface(forged)
        ex_a,_=prepare(assured,'X'); ex_b,_=prepare(forged,'X')
        assert ex_a == ex_b

        ra=assured.record_bounded_action_outcome_via_observation_basis(
            ex_a,
            observation_capability_id='OBS',
            observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),
            basis_capability_id='BASIS',
            basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),
            evidence_id='E-OUT-X',capture_id='C-OUT-X',
        )
        assert ra['status']=='ACTION_OUTCOME_OBSERVED'

        forged_obs=Observation(
            'C-OUT-X','CAPABILITY:OBS',f'action-execution:{ex_b}',dict(PAYLOAD),
            currentness_basis='QUALIFIED_OBSERVATION_CAPABILITY_AND_BOUNDED_USE_BASIS',
            authority=Authority.OBSERVATION_ONLY,
            lineage=('OBSERVATION_CAPABILITY:OBS@0','OBSERVATION_USE_BASIS:BASIS@0'),
        )
        rb=forged.record_bounded_action_outcome(
            ex_b,forged_obs,evidence_id='E-OUT-X',
            evidence_premise_epochs=(('BASIS',0),),
        )
        assert rb['status']=='ACTION_OUTCOME_OBSERVED'

        # Everything available to a later history reader is identical.
        assert ra['outcome'] == rb['outcome']
        assert assured.evidence.get('E-OUT-X')['payload'] == forged.evidence.get('E-OUT-X')['payload']
        assert assured.evidence.get('E-OUT-X')['source'] == forged.evidence.get('E-OUT-X')['source']
        assert assured.action_closure.current_state.serializable() == forged.action_closure.current_state.serializable()

        # Therefore current history cannot authenticate which ingress route actually ran.
        payload=assured.evidence.get('E-OUT-X')['payload']
        assert payload['observation_currentness_basis']=='QUALIFIED_OBSERVATION_CAPABILITY_AND_BOUNDED_USE_BASIS'
        assert payload['observation_lineage']==['OBSERVATION_CAPABILITY:OBS@0','OBSERVATION_USE_BASIS:BASIS@0']
