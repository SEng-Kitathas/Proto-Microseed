from __future__ import annotations
import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, EpistemicStatus, QualificationState, QueryObligation
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier
from research.run_ms1578_pass01_actual_stream_misbinding import seeded, prepare

TRUE={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}


def install(m):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1620',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(TRUE),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1620',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_ADMISSION_VALIDITY'},operational_scope_id='R2'))


def close(m,eid,i):
    return m.record_bounded_action_outcome_via_observation_basis(
        eid,
        observation_capability_id='OBS',
        observation_obligation=QueryObligation('OBS-Q','observe',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id='R2'),
        basis_capability_id='BASIS',
        basis_obligation=QueryObligation('BASIS-Q','basis',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),
        evidence_id=f'E-O-{i}',capture_id=f'C-{i}',
    )


def holdout(m,c,n=12):
    refs=[]
    base={
        'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,
        'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],
        'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),
        'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],
        'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs],
    }
    for i in range(n):
        refs.append(m.append_evidence(f'H-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT'))
    return tuple(refs)


def established():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1620-')
    m,_=seeded(Path(td.name)); install(m)
    for i in range(12):
        eid,_=prepare(m,f'P{i}')
        assert close(m,eid,i)['status']=='ACTION_OUTCOME_OBSERVED'
    c=next(c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY')
    t=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=holdout(m,c))
    r=m.qualify_action_outcome_predictive_relation(t)
    assert r['status']=='CURRENT_PREDICTIVE_RELATION'
    return td,m,c,r['relation']['relation_id']


def test_basis_epoch_reaches_candidate_and_relation():
    td,m,c,rid=established()
    try:
        assert c.evidence_premise_epochs==(('BASIS',0),)
        r=m.action_outcome_learning.relations[rid]
        assert r.evidence_premise_epochs==(('BASIS',0),)
    finally: td.cleanup()


def test_basis_challenge_stales_downstream_relation():
    td,m,c,rid=established()
    try:
        assert m.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        m.invalidate_capability('BASIS',reason='HISTORICAL_ADMISSION_BASIS_CHALLENGED')
        assert m.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()


def test_raw_legacy_outcomes_keep_empty_evidence_premise_ancestry():
    td,m,c,rid=established()
    try:
        # Legacy/raw path remains an explicit assistance bypass and does not invent a premise.
        # The established candidate came from assured ingress, so inspect an independent raw entity.
        m2,_=seeded(Path(td.name)/'raw')
        for i in range(8):
            eid,_=prepare(m2,f'R{i}')
            from microseed import Observation
            r=m2.record_bounded_action_outcome(eid,Observation(f'RAW{i}','RAW',f'action-execution:{eid}',TRUE,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-R-{i}')
            assert r['status']=='ACTION_OUTCOME_OBSERVED'
        rc=next(c for c in m2.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY')
        assert rc.evidence_premise_epochs==()
    finally: td.cleanup()


def test_rehearsal_conversion_preserves_evidence_premise_ancestry_after_ms1941_bridge():
    td,m,c,rid=established()
    try:
        # MS1620 originally refused ordinary conversion because the durable
        # rehearsal proposal could not carry this ancestry. MS1941 supersedes
        # that enforcement only after the durable proposal itself preserves and
        # rechecks the exact premise epochs/signatures.
        relation=m.action_outcome_learning.relations[rid]
        rr=relation.as_rehearsal_relation()
        assert rr is not None
        assert rr.evidence_premise_epochs==relation.evidence_premise_epochs
        assert rr.evidence_premise_signatures==relation.evidence_premise_signatures
        assert rr.value_epoch==relation.value_epoch
    finally: td.cleanup()

def test_holdout_without_matching_evidence_premise_does_not_qualify_assured_candidate():
    td,m,c,rid=established()
    try:
        # established() already qualified one relation. Build a fresh candidate-shaped copy is unnecessary;
        # directly verify evaluator support goes to zero when the holdout omits the premise ancestry.
        from microseed.development.action_learning import evaluate_action_outcome_holdout
        refs=[]
        base={
            'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,
            'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],
            'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),
            'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],
        }
        for i in range(12):
            refs.append(m.append_evidence(f'HM-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT'))
        support,acc=evaluate_action_outcome_holdout(c,tuple(refs),m.evidence)
        assert support==0 and acc==0.0
    finally: td.cleanup()


def test_basis_stale_before_relation_admission_blocks_admission():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1620-prestale-')
    try:
        m,_=seeded(Path(td.name));install(m)
        for i in range(12):
            eid,_=prepare(m,f'S{i}'); assert close(m,eid,i)['status']=='ACTION_OUTCOME_OBSERVED'
        c=next(c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY')
        t=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=holdout(m,c))
        m.invalidate_capability('BASIS',reason='BASIS_CHALLENGED_BEFORE_ADMISSION')
        r=m.qualify_action_outcome_predictive_relation(t)
        assert r=={'status':'RELATION_REJECTED','reason':'RELATION_PREMISE_NOT_CURRENT'}
    finally: td.cleanup()
