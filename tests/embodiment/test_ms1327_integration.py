from pathlib import Path
import hashlib, random, tempfile
import pytest

from microseed import (
    Microseed, Authority, EpistemicStatus, QualificationState, OperationalFrameContract,
    CapabilityContract, ConstructorProjectionSample, RobustConstructorGrowthConfig,
    ExternalRobustConstructorQualifier, ProjectionPredictiveCurrentnessConfig,
    DriftInterventionConfig, DriftInterventionProbe,
)


def H(x): return hashlib.sha256(x.encode()).hexdigest()

def new():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1327-')
    m=Microseed(Path(td.name))
    m.register_operational_frame(OperationalFrameContract(
        frame_id='F',purpose='opaque-raw-action-effect-boundary',signature_sha256=H('frame-v0'),
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS1303-1327',),currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNAL_FRAME_QUALIFICATION',),
        invariants=('NO_SEMANTIC_FEATURE_AUTHORITY',),
    ))
    return td,m

def rows(prefix,n=2400,*,causal=(2,11,19),noise=.02,seed=1):
    r=random.Random(seed);out=[]
    for i in range(n):
        raw=tuple(str(r.randrange(2)) for _ in range(24));ai=r.randrange(2);y=ai
        for j in causal:y^=int(raw[j])
        if r.random()<noise:y^=1
        out.append(ConstructorProjectionSample(f'{prefix}-{i}',(raw,),f'a{ai}',f'e{y}',None,'F',0))
    return out

def cfg(**kw):
    b=dict(max_support_ceiling=4,max_lag_ceiling=0,top_supports_per_order=16,min_train_support=100,
           min_validation_accuracy=.90,min_lift_over_action_baseline=.30,min_scope_accuracy=.90,
           max_conflict_edges=5000,combination_budget=20000,max_candidates=8)
    b.update(kw);return RobustConstructorGrowthConfig(**b)

def discover(m,xs,**kw):
    n=len(xs);return m.discover_robust_epistemic_constructor_candidates(xs[:n//2],xs[n//2:3*n//4],xs[3*n//4:],cfg(**kw))

def robust_ticket(m,cid,eid):
    ev=m.append_evidence(eid,{'heldout':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1327')
    return ExternalRobustConstructorQualifier(m.evidence,qualifier_id='HSP-MS1327').qualify(
        m.robust_epistemic_constructor_candidates[cid],qualification_evidence=(ev,))

def add_probe_cap(m,cid):
    m.register_capability(CapabilityContract(
        capability_id=cid,purpose='opaque intervention access',boundary={},interface={},
        invariants=('NO_SEMANTIC_INTERVENTION_AUTHORITY',),hazards=('NO_EFFECT_AUTHORITY',),
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS1303-1327',),currentness='CURRENT',resources={},
        qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNALLY_QUALIFIED_PROBE_ACCESS',),
    ))

def setup_pair(m):
    A=rows('A',3000,seed=1); fa=discover(m,A); old_cid=fa[0]['candidate_id']
    m.admit_robust_epistemic_constructor_candidate(robust_ticket(m,old_cid,'QA'),projection_id='P')
    B=rows('B',1800,causal=(2,11,20),seed=2)
    w=m.assess_epistemic_projection_predictive_currentness(
        'P',B,ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2))
    assert w['status']=='DRIFT_WITNESS'
    fb=discover(m,B); alt_cid=fb[0]['candidate_id']; ticket=robust_ticket(m,alt_cid,'QB')
    old=m.robust_epistemic_constructor_candidates[old_cid];alt=m.robust_epistemic_constructor_candidates[alt_cid]
    rr=random.Random(3);probes=[]
    for i in range(64):
        raw=tuple(str(rr.randrange(2)) for _ in range(24));action=f'a{rr.randrange(2)}';cap=f'CAP-P{i}'
        add_probe_cap(m,cap)
        probes.append(DriftInterventionProbe(f'P{i}',cap,0,(raw,),action,'F',0,assistance_ancestry=('SUPPLIED_OPAQUE_TEMPLATE',)))
    return old,alt,ticket,probes

def selected(m):
    old,alt,ticket,probes=setup_pair(m)
    p=m.plan_epistemic_projection_drift_intervention('P',ticket,probes,DriftInterventionConfig(repeats=31,min_agreement=.65,min_margin=.20,max_probe_pool=64))
    assert p['status']=='PROBE_SELECTED'
    return old,alt,ticket,probes,p

def token_for(packet,csha):
    for outcome,cands in packet['prediction_partition']:
        if csha in cands:return outcome
    raise AssertionError('candidate not in partition')

def add_batch(m,p,eid,outcomes):
    return m.append_evidence(eid,{'kind':'DRIFT_INTERVENTION_OUTCOME_BATCH','plan_id':p['plan_id'],'probe_id':p['probe']['probe_id'],'outcomes':list(outcomes)},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL_PROBE_EXECUTION')


def test_current_disagreement_probe_is_selected_without_truth_or_switch_authority():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m)
        assert p['disagreement_entropy']>0 and p['truth_authority']=='NONE'
        assert p['drift_cause_semantic_authority']==p['model_switch_authority']==p['scheduling_authority']=='NONE'
        assert m.epistemic_projections.records['P'].current is False
    finally:td.cleanup()


def test_zero_disagreement_pool_does_not_advertise_probe_access():
    td,m=new()
    try:
        old,alt,ticket,probes=setup_pair(m)
        same=[]
        for p in probes:
            po=old.project(p.raw_history);pa=alt.project(p.raw_history)
            op={(b,a):e for b,a,e in old.bucket_action_prediction}.get((po,p.action_token)) if po else None
            ap={(b,a):e for b,a,e in alt.bucket_action_prediction}.get((pa,p.action_token)) if pa else None
            if op==ap:same.append(p)
        out=m.plan_epistemic_projection_drift_intervention('P',ticket,same,DriftInterventionConfig(max_probe_pool=64))
        assert out['status']=='NO_DISCRIMINATING_INTERVENTION_WITHIN_QUALIFIED_SET' and out['plan_id'] is None
    finally:td.cleanup()


def test_discriminating_but_stale_probe_access_is_action_limited():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m)
        # invalidate every qualified probe capability before replanning
        for q in probes:m.invalidate_capability(q.capability_id,reason='ACCESS_LOST')
        out=m.plan_epistemic_projection_drift_intervention('P',ticket,probes,DriftInterventionConfig(max_probe_pool=64))
        assert out['status']=='ACTION_LIMITED' and out['plan_id'] is None
    finally:td.cleanup()


def test_repeated_probe_evidence_narrows_to_alternative_predictive_candidate_only():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m);tok=token_for(p,alt.digest())
        add_batch(m,p,'E1',[tok]*31)
        w=m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E1')
        assert w['status']=='NARROWED_TO_SINGLE_OPAQUE_PREDICTIVE_CANDIDATE' and w['supported_candidate_sha256']==alt.digest()
        assert w['drift_cause_semantic_authority']==w['truth_authority']==w['model_switch_authority']=='NONE'
        assert m.epistemic_projections.records['P'].current is False
    finally:td.cleanup()


def test_high_nuisance_batch_can_support_historical_predictive_law_without_noise_identity():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m);ot=token_for(p,old.digest());at=token_for(p,alt.digest())
        outcomes=[ot]*25+[at]*6;add_batch(m,p,'E2',outcomes)
        w=m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E2')
        assert w['status']=='NARROWED_TO_SINGLE_OPAQUE_PREDICTIVE_CANDIDATE' and w['supported_candidate_sha256']==old.digest()
        assert not hasattr(m,'infer_noise_model') and w['drift_cause_semantic_authority']=='NONE'
    finally:td.cleanup()


def test_hidden_mixture_remains_unresolved_within_finite_probe_bounds():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m);ot=token_for(p,old.digest());at=token_for(p,alt.digest())
        outcomes=[ot]*16+[at]*15;add_batch(m,p,'E3',outcomes)
        w=m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E3')
        assert w['status']=='UNRESOLVED_WITHIN_BOUNDS' and w['supported_candidate_sha256'] is None
    finally:td.cleanup()


def test_unpredicted_probe_outcomes_are_model_space_challenge_not_new_cause():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m);add_batch(m,p,'E4',['eX']*31)
        w=m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E4')
        assert w['status']=='MODEL_SPACE_CHALLENGE' and w['supported_candidate_sha256'] is None
        assert w['qualification_authority']==w['drift_cause_semantic_authority']=='NONE'
    finally:td.cleanup()


def test_probe_capability_drift_after_plan_blocks_evidence_consumption():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m);tok=token_for(p,alt.digest());add_batch(m,p,'E5',[tok]*31)
        m.invalidate_capability(p['probe']['capability_id'],reason='ACCESS_DRIFT')
        with pytest.raises(ValueError,match='STALE_DRIFT_INTERVENTION_PLAN_CAPABILITY'):
            m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E5')
    finally:td.cleanup()


def test_frame_drift_after_plan_blocks_evidence_consumption():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m);tok=token_for(p,alt.digest());add_batch(m,p,'E6',[tok]*31)
        m.change_operational_frame('F',reason='RAW_BOUNDARY_CHANGED')
        with pytest.raises(ValueError,match='STALE_DRIFT_INTERVENTION_PLAN_ALTERNATIVE_FRAME|STALE_DRIFT_INTERVENTION_PLAN_FRAME|STALE_DRIFT_INTERVENTION_PLAN_PROJECTION_STATE'):
            m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E6')
    finally:td.cleanup()


def test_probe_evidence_is_content_bound_and_cannot_be_replayed_twice():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m);tok=token_for(p,alt.digest())
        m.append_evidence('BAD',{'kind':'DRIFT_INTERVENTION_OUTCOME_BATCH','plan_id':'wrong','probe_id':p['probe']['probe_id'],'outcomes':[tok]*31},EpistemicStatus.PRESSURE_SUPPORTED)
        with pytest.raises(ValueError,match='EVIDENCE_CONTENT_MISMATCH'):
            m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'BAD')
        add_batch(m,p,'E7',[tok]*31);m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E7')
        with pytest.raises(ValueError,match='EVIDENCE_ALREADY_CONSUMED'):
            m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E7')
    finally:td.cleanup()


def test_plan_and_witness_replay_as_history_without_restoring_probe_access():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m);tok=token_for(p,alt.digest());add_batch(m,p,'E8',[tok]*31)
        w=m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E8');root=Path(td.name);del m
        m2=Microseed(root)
        assert p['plan_id'] in m2.epistemic_drift_intervention_plans and w['witness_id'] in m2.epistemic_drift_intervention_witnesses
        m2.append_evidence('E9',{'kind':'DRIFT_INTERVENTION_OUTCOME_BATCH','plan_id':p['plan_id'],'probe_id':p['probe']['probe_id'],'outcomes':[tok]*31},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL_PROBE_EXECUTION')
        with pytest.raises(ValueError,match='STALE_DRIFT_INTERVENTION_PLAN_ALTERNATIVE_FRAME'):
            m2.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'E9')
    finally:td.cleanup()


def test_finite_evidence_gates_are_part_of_plan_and_cannot_be_changed_at_consumption():
    td,m=new()
    try:
        old,alt,ticket,probes,p=selected(m)
        assert p['repeats']==31 and p['min_agreement']==.65 and p['min_margin']==.20
        tok=token_for(p,alt.digest())
        m.append_evidence('SHORT',{'kind':'DRIFT_INTERVENTION_OUTCOME_BATCH','plan_id':p['plan_id'],'probe_id':p['probe']['probe_id'],'outcomes':[tok]*7},EpistemicStatus.PRESSURE_SUPPORTED)
        with pytest.raises(ValueError,match='OUTCOME_COUNT_MISMATCH'):
            m.record_epistemic_projection_drift_intervention_evidence(p['plan_id'],'SHORT')
    finally:td.cleanup()
