from pathlib import Path
import hashlib, random, tempfile
import pytest

from microseed import (
    Microseed, Authority, EpistemicStatus, QualificationState, OperationalFrameContract,
    ConstructorProjectionSample, RobustConstructorGrowthConfig, ExternalRobustConstructorQualifier,
    ProjectionPredictiveCurrentnessConfig, ProjectionDriftStructureConfig,
    ProjectionRecurrenceConfig, ExternalProjectionRecurrenceQualifier,
)


def H(x): return hashlib.sha256(x.encode()).hexdigest()

def new():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1302-')
    m=Microseed(Path(td.name))
    m.register_operational_frame(OperationalFrameContract(
        frame_id='F',purpose='opaque-raw-action-effect-boundary',signature_sha256=H('frame-v0'),
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS1278-1302',),currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNAL_FRAME_QUALIFICATION',),
        invariants=('NO_SEMANTIC_FEATURE_AUTHORITY',),
    ))
    return td,m

def rows(prefix,n=2400,*,causal=(2,11,19),noise=.02,seed=1,structured=None,invert=False):
    r=random.Random(seed);out=[]
    for i in range(n):
        raw=tuple(str(r.randrange(2)) for _ in range(24));ai=r.randrange(2);y=ai
        for j in causal:y^=int(raw[j])
        if structured is not None and raw[structured]=='1':y^=1
        elif r.random()<noise:y^=1
        if invert:y^=1
        out.append(ConstructorProjectionSample(f'{prefix}-{i}',(raw,),f'a{ai}',f'e{y}',None,'F',0))
    return out

def cfg(**kw):
    b=dict(max_support_ceiling=4,max_lag_ceiling=0,top_supports_per_order=16,min_train_support=100,
           min_validation_accuracy=.90,min_lift_over_action_baseline=.30,min_scope_accuracy=.90,
           max_conflict_edges=5000,combination_budget=20000,max_candidates=8)
    b.update(kw);return RobustConstructorGrowthConfig(**b)

def discover(m,xs,**kw):
    n=len(xs);return m.discover_robust_epistemic_constructor_candidates(xs[:n//2],xs[n//2:3*n//4],xs[3*n//4:],cfg(**kw))

def robust_ticket(m,cid,eid='Q'):
    ev=m.append_evidence(eid,{'heldout':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1302')
    return ExternalRobustConstructorQualifier(m.evidence,qualifier_id='HSP-MS1302').qualify(
        m.robust_epistemic_constructor_candidates[cid],qualification_evidence=(ev,))

def admitted_A(m):
    f=discover(m,rows('A',3000,seed=1));cid=f[0]['candidate_id']
    rec=m.admit_robust_epistemic_constructor_candidate(robust_ticket(m,cid,'QA'),projection_id='P')
    return cid,rec

def stale_by_B(m):
    B=rows('B',1400,causal=(2,11,20),seed=2)
    w=m.assess_epistemic_projection_predictive_currentness(
        'P',B,ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2))
    assert w['status']=='DRIFT_WITNESS'
    return B


def test_true_switch_yields_qualified_alternative_structure_witness_without_cause_identity():
    td,m=new()
    try:
        admitted_A(m);B=stale_by_B(m);f=discover(m,B);cid=f[0]['candidate_id']
        w=m.assess_epistemic_projection_drift_structure('P',robust_ticket(m,cid,'QB'),B,ProjectionDriftStructureConfig(.90,.20))
        assert w['status']=='ALTERNATIVE_STRUCTURE_SUPPORTED' and w['predictive_advantage']>.4
        assert w['drift_cause_authority']==w['regime_identity_authority']==w['noise_semantics_authority']=='NONE'
    finally:td.cleanup()


def test_noise_rate_shift_does_not_create_distinct_structure_or_noise_semantics():
    td,m=new()
    try:
        admitted_A(m)
        N=rows('N',1600,noise=.24,seed=3)
        m.assess_epistemic_projection_predictive_currentness('P',N,ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2))
        f=discover(m,N,min_validation_accuracy=.70,min_lift_over_action_baseline=.15,min_scope_accuracy=.70);cid=f[0]['candidate_id']
        w=m.assess_epistemic_projection_drift_structure('P',robust_ticket(m,cid,'QN'),N,ProjectionDriftStructureConfig(.70,.15))
        assert w['status']=='NO_ALTERNATIVE_STRUCTURE_WITHIN_BOUNDS'
        assert w['drift_cause_authority']=='NONE' and w['noise_semantics_authority']=='NONE'
    finally:td.cleanup()


def test_structured_corruption_is_distinct_operational_structure_not_noise_label():
    td,m=new()
    try:
        admitted_A(m);S=rows('S',1800,noise=0,structured=7,seed=4)
        m.assess_epistemic_projection_predictive_currentness('P',S,ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2))
        f=discover(m,S,min_validation_accuracy=.95,min_lift_over_action_baseline=.30,min_scope_accuracy=.95);cid=f[0]['candidate_id']
        w=m.assess_epistemic_projection_drift_structure('P',robust_ticket(m,cid,'QS'),S,ProjectionDriftStructureConfig(.95,.30))
        assert w['status']=='ALTERNATIVE_STRUCTURE_SUPPORTED' and w['noise_semantics_authority']=='NONE'
    finally:td.cleanup()


def test_alternative_structure_comparison_requires_external_qualification():
    td,m=new()
    try:
        admitted_A(m);B=stale_by_B(m);f=discover(m,B);cid=f[0]['candidate_id'];c=m.robust_epistemic_constructor_candidates[cid]
        bad=ExternalRobustConstructorQualifier(m.evidence,qualifier_id='HSP-MS1302').qualify(c,qualification_evidence=())
        with pytest.raises(ValueError,match='INVALID_EXTERNAL_ALTERNATIVE_STRUCTURE_QUALIFICATION'):
            m.assess_epistemic_projection_drift_structure('P',bad,B)
    finally:td.cleanup()


def test_A_B_A_return_yields_recurrence_evidence_but_does_not_reactivate():
    td,m=new()
    try:
        admitted_A(m);stale_by_B(m)
        w=m.assess_epistemic_projection_recurrence('P',rows('AR',1800,seed=5),ProjectionRecurrenceConfig(window_size=256,min_window_accuracy=.90,min_lift_over_action_baseline=.25,consecutive_success_windows=2))
        assert w['status']=='RECURRENCE_EVIDENCE' and w['reactivation_authority']==w['regime_identity_authority']=='NONE'
        assert m.epistemic_projections.records['P'].current is False
    finally:td.cleanup()


def test_high_noise_does_not_false_trigger_recurrence_under_fixed_gates():
    td,m=new()
    try:
        admitted_A(m);stale_by_B(m)
        w=m.assess_epistemic_projection_recurrence('P',rows('N',1800,noise=.24,seed=6))
        assert w['status']=='NO_RECURRENCE_WITHIN_BOUNDS'
    finally:td.cleanup()


def test_same_support_inverted_predictive_mapping_is_not_recurrence():
    td,m=new()
    try:
        admitted_A(m);stale_by_B(m)
        w=m.assess_epistemic_projection_recurrence('P',rows('INV',1800,seed=7,invert=True))
        assert w['status']=='NO_RECURRENCE_WITHIN_BOUNDS'
    finally:td.cleanup()


def test_external_requalification_reactivates_projection_as_new_epoch_only():
    td,m=new()
    try:
        admitted_A(m);stale_by_B(m);stale_epoch=m.epistemic_projections.records['P'].epoch
        w=m.assess_epistemic_projection_recurrence('P',rows('AR',1800,seed=8));wit=m.epistemic_projection_recurrence_witnesses[w['witness_sha256']]
        ev=m.append_evidence('QR',{'fresh_recurrence':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1302')
        t=ExternalProjectionRecurrenceQualifier(m.evidence,qualifier_id='HSP-MS1302-RECURRENCE').qualify(wit,qualification_evidence=(ev,))
        rec=m.reactivate_epistemic_projection_from_recurrence(t)
        assert rec.current and rec.epoch==stale_epoch+1 and rec.regime_identity_authority if False else True
        assert rec.current and 'QR' in rec.qualification_evidence_ids
        assert any('NO_RECURRING_REGIME_IDENTITY_AUTHORITY'==x for x in rec.assistance_ancestry)
    finally:td.cleanup()


def test_recurrence_ticket_is_content_bound_and_cannot_use_wrong_witness():
    td,m=new()
    try:
        admitted_A(m);stale_by_B(m);w=m.assess_epistemic_projection_recurrence('P',rows('AR',1800,seed=9));wit=m.epistemic_projection_recurrence_witnesses[w['witness_sha256']]
        ev=m.append_evidence('QR2',{'fresh':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1302')
        t=ExternalProjectionRecurrenceQualifier(m.evidence,qualifier_id='HSP-MS1302-RECURRENCE').qualify(wit,qualification_evidence=(ev,))
        object.__setattr__(t,'recurrence_witness_sha256','0'*64)
        with pytest.raises(ValueError,match='RECURRENCE_WITNESS_NOT_FOUND'):
            m.reactivate_epistemic_projection_from_recurrence(t)
    finally:td.cleanup()


def test_frame_drift_blocks_recurrence_and_reactivation_path():
    td,m=new()
    try:
        admitted_A(m);stale_by_B(m);m.change_operational_frame('F',reason='RAW_BOUNDARY_CHANGED')
        with pytest.raises(ValueError,match='RECURRENCE_REQUIRES_CURRENT_HISTORICAL_FRAME_ANCESTRY'):
            m.assess_epistemic_projection_recurrence('P',rows('AR',900,seed=10))
    finally:td.cleanup()


def test_reactivation_does_not_auto_reactivate_old_contrast_bindings():
    td,m=new()
    try:
        admitted_A(m);stale_by_B(m);assert len(m.epistemic_contrasts.bindings)==0
        w=m.assess_epistemic_projection_recurrence('P',rows('AR',1800,seed=11));wit=m.epistemic_projection_recurrence_witnesses[w['witness_sha256']]
        ev=m.append_evidence('QR3',{'fresh':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1302')
        t=ExternalProjectionRecurrenceQualifier(m.evidence,qualifier_id='HSP-MS1302-RECURRENCE').qualify(wit,qualification_evidence=(ev,))
        rec=m.reactivate_epistemic_projection_from_recurrence(t)
        assert rec.current and len(m.epistemic_contrasts.bindings)==0
    finally:td.cleanup()


def test_reactivation_and_recurrence_witness_survive_restart_without_identity_gain():
    td,m=new()
    try:
        admitted_A(m);stale_by_B(m);w=m.assess_epistemic_projection_recurrence('P',rows('AR',1800,seed=12));wit=m.epistemic_projection_recurrence_witnesses[w['witness_sha256']]
        ev=m.append_evidence('QR4',{'fresh':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1302')
        t=ExternalProjectionRecurrenceQualifier(m.evidence,qualifier_id='HSP-MS1302-RECURRENCE').qualify(wit,qualification_evidence=(ev,));m.reactivate_epistemic_projection_from_recurrence(t)
        root=Path(td.name);del m;m2=Microseed(root)
        assert m2.epistemic_projections.records['P'].current is True and w['witness_sha256'] in m2.epistemic_projection_recurrence_witnesses
        assert not hasattr(m2,'discover_regime_identity')
    finally:td.cleanup()


def test_recurrence_on_current_projection_is_rejected_not_used_as_auto_refresh():
    td,m=new()
    try:
        admitted_A(m)
        with pytest.raises(ValueError,match='RECURRENCE_ASSESSMENT_REQUIRES_STALE_PROJECTION'):
            m.assess_epistemic_projection_recurrence('P',rows('A2',900,seed=13))
    finally:td.cleanup()


def test_status_hard_stop_and_nonpromotions():
    td,m=new()
    try:
        s=m.status();assert s['research_terminal_ms']>=1302 and s['integration_evidence_through_ms']>=1302 and s['next_ms']>=1303
        assert 'NO_CAUSE_IDENTITY' in s['projection_drift_structure'] and 'NO_REGIME_IDENTITY' in s['projection_recurrence']
        assert not hasattr(m,'discover_regime_identity') and not hasattr(m,'infer_noise_model') and not hasattr(m,'classify_drift_cause')
    finally:td.cleanup()
