from __future__ import annotations
import tempfile
from pathlib import Path
from microseed import Authority, CapabilityContract, Observation, QualificationState, QueryObligation
from research.run_ms1578_pass01_actual_stream_misbinding import seeded, prepare

TRUE={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}
FALSE={"next_state_id":"FALSE","observed_values":{"ENERGY":4.6,"THERMAL":8.3,"INTEGRITY":5.1}}

def install(m,payload=TRUE,*,basis_dep=True,obs_authority=Authority.OBSERVATION_ONLY):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),obs_authority,('MS1598',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(payload),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1598',),'CURRENT',{},dependencies=('OBS',) if basis_dep else (),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='R2'))

def call(m,eid,tag='X',scope='R2'):
    return m.record_bounded_action_outcome_via_observation_basis(eid,observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id=scope),basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id=scope),evidence_id='E-'+tag,capture_id='C-'+tag)

def test_current_basis_and_channel_close_outcome_and_preserve_ancestry():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td)); install(m); eid,_=prepare(m,'GOOD'); r=call(m,eid,'GOOD')
        assert r['status']=='ACTION_OUTCOME_OBSERVED'
        ev=m.evidence.get('E-GOOD')['payload']
        assert ev['observation_currentness_basis']=='QUALIFIED_OBSERVATION_CAPABILITY_AND_BOUNDED_USE_BASIS'
        assert ev['observation_lineage']==['OBSERVATION_CAPABILITY:OBS@0','OBSERVATION_USE_BASIS:BASIS@0']

def test_stale_channel_transitively_stales_basis_and_rejects_ingress():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td)); install(m); eid,_=prepare(m,'STALE'); stale=m.invalidate_capability('OBS',reason='MAP_STALE'); r=call(m,eid,'STALE')
        assert stale=={'OBS','BASIS'}; assert r['status']=='OUTCOME_REJECTED'; assert r['reason']=='OBSERVATION_BASIS_NOT_CURRENT'
        assert not m.action_closure.outcomes

def test_wrong_scope_rejects_before_outcome():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td)); install(m); eid,_=prepare(m,'SCOPE'); r=call(m,eid,'SCOPE',scope='OTHER')
        assert r['status']=='OUTCOME_REJECTED'; assert not m.action_closure.outcomes

def test_basis_must_depend_on_selected_observation_channel():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td)); install(m,basis_dep=False); eid,_=prepare(m,'DEP'); r=call(m,eid,'DEP')
        assert r=={'status':'OUTCOME_REJECTED','reason':'OBSERVATION_BASIS_DOES_NOT_BIND_CHANNEL'}

def test_observation_capability_must_carry_observation_only_authority():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td)); install(m,obs_authority=Authority.DERIVED_READ_ONLY); eid,_=prepare(m,'AUTH'); r=call(m,eid,'AUTH')
        assert r['status']=='OUTCOME_REJECTED'; assert r['reason']=='OBSERVATION_CAPABILITY_NOT_CURRENT'

def test_false_but_current_mapping_remains_explicit_grounding_boundary():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td)); install(m,payload=FALSE); eid,_=prepare(m,'FALSE'); r=call(m,eid,'FALSE')
        assert r['status']=='ACTION_OUTCOME_OBSERVED'
        effects={x['value_id']:x['actual_value_effect'] for x in r['outcome']['value_outcomes']}
        assert effects=={'ENERGY':1.4,'THERMAL':0.7,'INTEGRITY':-0.9}

def test_legacy_raw_ingress_remains_explicit_assistance_bypass():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td)); eid,_=prepare(m,'RAW')
        r=m.record_bounded_action_outcome(eid,Observation('RAW','RAW',f'action-execution:{eid}',FALSE,authority=Authority.OBSERVATION_ONLY),evidence_id='E-RAW')
        assert r['status']=='ACTION_OUTCOME_OBSERVED'

def test_basis_capability_must_carry_derived_read_only_authority():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td))
        m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1598',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(TRUE),operational_scope_id='R2'))
        m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1598',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'WRONG_AUTHORITY'},operational_scope_id='R2'))
        eid,_=prepare(m,'BAUTH'); r=call(m,eid,'BAUTH')
        assert r['status']=='OUTCOME_REJECTED'; assert r['reason']=='OBSERVATION_BASIS_NOT_CURRENT'

def test_observation_channel_currentness_is_checked_even_if_basis_metadata_is_still_current():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td)); install(m); eid,_=prepare(m,'DESYNC')
        # Hostile metadata desynchronization: the basis still says current, but the
        # channel itself is stale. The ingress must check both owners independently.
        m.capabilities.contracts['OBS'].qualification=QualificationState.STALE
        m.capabilities.contracts['OBS'].currentness='STALE'
        assert m.capabilities.contracts['BASIS'].qualification==QualificationState.SHADOW_QUALIFIED
        r=call(m,eid,'DESYNC')
        assert r['status']=='OUTCOME_REJECTED'; assert r['reason']=='OBSERVATION_CAPABILITY_NOT_CURRENT'
        assert not m.action_closure.outcomes
