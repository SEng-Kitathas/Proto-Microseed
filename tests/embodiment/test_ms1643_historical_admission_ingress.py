from __future__ import annotations
import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, EpistemicStatus, QualificationState, QueryObligation
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier
from research.run_ms1578_pass01_actual_stream_misbinding import seeded, prepare

TRUE={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}

def install(m, *, hist_authority=Authority.DERIVED_READ_ONLY):
    obs=CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1643',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(TRUE),operational_scope_id='R2')
    m.register_capability(obs)
    m.register_capability(CapabilityContract('LIVE-BASIS','live-use',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1643',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='LIVE-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE'},operational_scope_id='R2'))
    hist_boundary={'basis':'A','admission_premise_signatures':[['OBS',obs.computed_signature_sha256()]]}
    m.register_capability(CapabilityContract('HIST-ADMIT','historical-admission',hist_boundary, {},('HISTORICAL_ONLY','NO_TRUTH_AUTHORITY'),(),hist_authority,('MS1643',),'CURRENT',{},query_obligation_id='HIST-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'ADMITTED_AT_ACQUISITION'},operational_scope_id='R2'))

def call(m,eid,tag='X', *, hist_obligation=True):
    return m.record_bounded_action_outcome_via_observation_basis(
        eid,
        observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),
        basis_capability_id='LIVE-BASIS',basis_obligation=QueryObligation('LIVE-Q','live',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),
        admission_basis_capability_id='HIST-ADMIT',admission_basis_obligation=QueryObligation('HIST-Q','historical admission',Authority.DERIVED_READ_ONLY,operational_scope_id='R2') if hist_obligation else None,
        evidence_id=f'E-{tag}',capture_id=f'C-{tag}',
    )

def holdout(m,c):
    refs=[]
    base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs],'evidence_premise_signatures':[list(x) for x in c.evidence_premise_signatures]}
    for i in range(12): refs.append(m.append_evidence(f'H-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='HOLDOUT'))
    return tuple(refs)

def established():
    td=tempfile.TemporaryDirectory(prefix='ms1643-');m,_=seeded(Path(td.name));install(m)
    for i in range(12):
        eid,_=prepare(m,f'P{i}'); assert call(m,eid,str(i))['status']=='ACTION_OUTCOME_OBSERVED'
    c=next(c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY' and c.evidence_premise_signatures)
    rr=m.qualify_action_outcome_predictive_relation(ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=holdout(m,c)))
    assert rr['status']=='CURRENT_PREDICTIVE_RELATION'
    return td,m,c,rr['relation']['relation_id']

def test_split_ingress_persists_historical_basis_epoch_and_content_signature():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td));install(m);eid,_=prepare(m,'ONE');r=call(m,eid,'ONE');assert r['status']=='ACTION_OUTCOME_OBSERVED'
        p=m.evidence.get('E-ONE')['payload']
        assert p['evidence_premise_epochs']==[['HIST-ADMIT',0]]
        assert p['evidence_premise_signatures']==[['HIST-ADMIT',m.capabilities.contracts['HIST-ADMIT'].computed_signature_sha256()]]
        assert p['observation_currentness_basis']=='QUALIFIED_OBSERVATION_CAPABILITY_AND_LIVE_USE_PLUS_HISTORICAL_ADMISSION_BASIS'

def test_temporary_live_channel_loss_does_not_stale_historical_relation():
    td,m,c,rid=established()
    try:
        m.invalidate_capability('OBS',reason='TEMP_ACCESS_LOSS')
        assert m.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert m.capabilities.contracts['LIVE-BASIS'].qualification==QualificationState.STALE
    finally: td.cleanup()

def test_retrospective_basis_failure_must_advance_epoch_and_stays_stale_after_requalification():
    td,m,c,rid=established()
    try:
        m.change_capability_dependency('HIST-ADMIT',reason='RETROSPECTIVE_ADMISSION_FALSE')
        h=m.capabilities.contracts['HIST-ADMIT'];h.qualification=QualificationState.SHADOW_QUALIFIED;h.currentness='CURRENT'
        assert m.capabilities.epochs['HIST-ADMIT']==1
        assert m.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()

def test_same_id_epoch_but_changed_basis_content_stales_relation():
    td,m,c,rid=established()
    try:
        assert m.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        m.capabilities.contracts['HIST-ADMIT'].boundary={'basis':'ALTERED'}
        assert m.capabilities.epochs['HIST-ADMIT']==0
        assert m.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()

def test_prospective_live_mapping_change_does_not_retroactively_stale_history():
    td,m,c,rid=established()
    try:
        m.change_capability_dependency('OBS',reason='NEW_LIVE_MAPPING')
        assert m.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert m.capabilities.contracts['LIVE-BASIS'].qualification==QualificationState.STALE
    finally: td.cleanup()

def test_historical_admission_obligation_is_required_when_split_basis_requested():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td));install(m);eid,_=prepare(m,'NOOB');r=call(m,eid,'NOOB',hist_obligation=False)
        assert r=={'status':'OUTCOME_REJECTED','reason':'HISTORICAL_ADMISSION_BASIS_OBLIGATION_REQUIRED'}

def test_historical_admission_basis_requires_derived_read_only_authority():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td));install(m,hist_authority=Authority.OBSERVATION_ONLY);eid,_=prepare(m,'BADAUTH');r=call(m,eid,'BADAUTH')
        assert r['status']=='OUTCOME_REJECTED';assert r['reason']=='HISTORICAL_ADMISSION_BASIS_NOT_CURRENT'

def test_old_historical_basis_cannot_admit_new_evidence_after_mapping_content_change():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td));install(m)
        e0,_=prepare(m,'OLD');assert call(m,e0,'OLD')['status']=='ACTION_OUTCOME_OBSERVED'
        m.change_capability_dependency('OBS',reason='NEW_MAPPING')
        obs=m.capabilities.contracts['OBS'];obs.purpose='new mapping';obs.boundary={'mapping':'V2'};obs.qualification=QualificationState.SHADOW_QUALIFIED;obs.currentness='CURRENT'
        m.change_capability_dependency('LIVE-BASIS',reason='NEW_MAPPING')
        live=m.capabilities.contracts['LIVE-BASIS'];live.qualification=QualificationState.SHADOW_QUALIFIED;live.currentness='CURRENT'
        e1,_=prepare(m,'NEW');r=call(m,e1,'NEW')
        assert r=={'status':'OUTCOME_REJECTED','reason':'HISTORICAL_ADMISSION_BASIS_NOT_APPLICABLE_TO_CURRENT_PREMISES'}


def test_same_mapping_content_new_runtime_epoch_can_reuse_applicable_historical_basis():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td));install(m)
        m.change_capability_dependency('OBS',reason='TEMP_RUNTIME_EPOCH')
        obs=m.capabilities.contracts['OBS'];obs.qualification=QualificationState.SHADOW_QUALIFIED;obs.currentness='CURRENT'
        m.change_capability_dependency('LIVE-BASIS',reason='TEMP_RUNTIME_EPOCH')
        live=m.capabilities.contracts['LIVE-BASIS'];live.qualification=QualificationState.SHADOW_QUALIFIED;live.currentness='CURRENT'
        eid,_=prepare(m,'SAME');assert call(m,eid,'SAME')['status']=='ACTION_OUTCOME_OBSERVED'


def test_split_historical_basis_requires_snapshot_bound_acquisition_premise():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td));install(m)
        m.capabilities.contracts['HIST-ADMIT'].boundary={'basis':'A'}
        eid,_=prepare(m,'NOSNAP');r=call(m,eid,'NOSNAP')
        assert r=={'status':'OUTCOME_REJECTED','reason':'HISTORICAL_ADMISSION_PREMISE_SIGNATURES_REQUIRED'}


def test_snapshot_binding_does_not_turn_false_but_current_mapping_into_truth():
    with tempfile.TemporaryDirectory() as td:
        m,_=seeded(Path(td));install(m)
        # Handler implementation is deliberately false while immutable contract metadata stays unchanged.
        m.capabilities.contracts['OBS'].handler=lambda **_:{'next_state_id':'S1','observed_values':{'ENERGY':99.0,'THERMAL':99.0,'INTEGRITY':99.0}}
        eid,_=prepare(m,'FALSECURRENT');r=call(m,eid,'FALSECURRENT')
        assert r['status']=='ACTION_OUTCOME_OBSERVED'
        assert m.evidence.get('E-FALSECURRENT')['payload']['observed_values']['ENERGY']==99.0

def test_historical_signature_reaches_candidate_and_qualified_relation():
    td,m,c,rid=established()
    try:
        assert c.evidence_premise_signatures
        r=m.action_outcome_learning.relations[rid]
        assert r.evidence_premise_signatures==c.evidence_premise_signatures
        assert r.evidence_premise_signatures[0][0]=='HIST-ADMIT'
    finally: td.cleanup()


def test_holdout_without_matching_historical_signature_does_not_qualify_candidate():
    td,m,c,_=established()
    try:
        refs=[]
        base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs],'evidence_premise_signatures':[['HIST-ADMIT','0'*64]]}
        for i in range(12):
            refs.append(m.append_evidence(f'BAD-HSIG-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='MISMATCHED-HIST-SIG-HOLDOUT'))
        ticket=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=tuple(refs))
        assert ticket.state==QualificationState.REJECTED
        assert ticket.holdout_support==0
    finally: td.cleanup()
