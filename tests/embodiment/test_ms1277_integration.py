from pathlib import Path
import hashlib, random, tempfile
import pytest

from microseed import (
    Microseed, Authority, EpistemicStatus, QualificationState, OperationalFrameContract,
    ConstructorProjectionSample, RobustConstructorGrowthConfig, ExternalRobustConstructorQualifier,
    ProjectionPredictiveCurrentnessConfig,
)


def H(x): return hashlib.sha256(x.encode()).hexdigest()

def new():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1277-')
    m=Microseed(Path(td.name))
    m.register_operational_frame(OperationalFrameContract(
        frame_id='F',purpose='opaque-raw-action-effect-boundary',signature_sha256=H('frame-v0'),
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS1253-1277',),currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNAL_FRAME_QUALIFICATION',),
        invariants=('NO_SEMANTIC_FEATURE_AUTHORITY',),
    ))
    return td,m

def rows(prefix,n=2400,*,causal=(2,11,19),noise=.02,seed=1,start=0,structured=False):
    r=random.Random(seed);out=[]
    for i in range(n):
        raw=tuple(str(r.randrange(2)) for _ in range(24));ai=r.randrange(2);y=ai
        for j in causal:y^=int(raw[j])
        if structured and raw[7]=='1':y^=1
        elif r.random()<noise:y^=1
        out.append(ConstructorProjectionSample(f'{prefix}-{i}',(raw,),f'a{ai}',f'e{y}',None,'F',0))
    return out

def split3(xs):
    n=len(xs);a=n//2;b=3*n//4;return xs[:a],xs[a:b],xs[b:]

def cfg(**kw):
    base=dict(max_support_ceiling=4,max_lag_ceiling=0,top_supports_per_order=16,min_train_support=100,
              min_validation_accuracy=.90,min_lift_over_action_baseline=.30,min_scope_accuracy=.90,
              max_conflict_edges=5000,combination_budget=20000,max_candidates=8)
    base.update(kw);return RobustConstructorGrowthConfig(**base)

def discover(m,xs,**kw):
    tr,pr,va=split3(xs);return m.discover_robust_epistemic_constructor_candidates(tr,pr,va,cfg(**kw))

def ticket(m,cid,eid='Q'):
    ev=m.append_evidence(eid,{'heldout':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1277')
    return ExternalRobustConstructorQualifier(m.evidence,qualifier_id='HSP-MS1277').qualify(
        m.robust_epistemic_constructor_candidates[cid],qualification_evidence=(ev,))

def support(m,found):
    c=m.robust_epistemic_constructor_candidates[found[0]['candidate_id']]
    return tuple((a.lag,a.position) for a in c.atoms),c


def test_two_percent_noise_recovers_true_triple_without_noise_rate_model():
    td,m=new()
    try:
        f=discover(m,rows('n2',noise=.02,seed=11)); s,c=support(m,f)
        assert s==((0,2),(0,11),(0,19))
        assert c.validation_accuracy>=.96 and c.observed_conflict_coverage>.94
        assert 'NO_NOISE_RATE_MODEL' in c.assistance_ancestry
        assert not any('NOISE_0.02' in x for x in c.assistance_ancestry)
    finally:td.cleanup()


def test_eight_percent_noise_still_recovers_same_support_inside_looser_qualification_bounds():
    td,m=new()
    try:
        f=discover(m,rows('n8',noise=.08,seed=12),min_validation_accuracy=.84,min_lift_over_action_baseline=.25,min_scope_accuracy=.84)
        s,c=support(m,f);assert s==((0,2),(0,11),(0,19));assert c.validation_accuracy>=.88
    finally:td.cleanup()


def test_support_ceiling_and_combination_budget_abstain():
    td,m=new()
    try:
        assert discover(m,rows('ceil',seed=13),max_support_ceiling=2)==[]
        assert discover(m,rows('budget',seed=14),combination_budget=100)==[]
    finally:td.cleanup()


def test_structured_corruption_is_absorbed_as_operational_coordinate_not_declared_noise():
    td,m=new()
    try:
        f=discover(m,rows('struct',seed=15,structured=True,noise=0),min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95)
        s,c=support(m,f);assert s==((0,2),(0,7),(0,11),(0,19));assert c.validation_accuracy==1.0
    finally:td.cleanup()


def test_simultaneous_hidden_regime_mixture_abstains():
    td,m=new()
    try:
        r=random.Random(16);xs=[]
        for i in range(2800):
            raw=tuple(str(r.randrange(2)) for _ in range(24));ai=r.randrange(2);causal=(2,11,19) if r.randrange(2)==0 else (2,11,20);y=ai
            for j in causal:y^=int(raw[j])
            if r.random()<.02:y^=1
            xs.append(ConstructorProjectionSample(f'mix-{i}',(raw,),f'a{ai}',f'e{y}',None,'F',0))
        assert discover(m,xs,min_validation_accuracy=.82,min_lift_over_action_baseline=.20,min_scope_accuracy=.82)==[]
    finally:td.cleanup()


def test_external_qualification_is_still_required_for_robust_candidate_admission():
    td,m=new()
    try:
        f=discover(m,rows('q',seed=17));cid=f[0]['candidate_id'];c=m.robust_epistemic_constructor_candidates[cid]
        bad=ExternalRobustConstructorQualifier(m.evidence,qualifier_id='HSP-MS1277').qualify(c,qualification_evidence=())
        with pytest.raises(ValueError,match='NOT_ADMISSIBLE|NO_QUALIFICATION_EVIDENCE'):
            m.admit_robust_epistemic_constructor_candidate(bad,projection_id='P')
        rec=m.admit_robust_epistemic_constructor_candidate(ticket(m,cid),projection_id='P')
        assert rec.projection_origin=='ENDOGENOUS_ROBUST_CONSTRUCTOR_GROWTH_EXTERNALLY_QUALIFIED'
        assert rec.proposal_candidate_sha256==c.digest() and rec.qualification_evidence_ids==('Q',)
        assert rec.semantic_projection_authority==rec.discovery_authority=='NONE'
    finally:td.cleanup()


def test_robust_candidate_restart_preserves_proposal_without_qualification_gain():
    td,m=new()
    try:
        f=discover(m,rows('restart',seed=18));cid=f[0]['candidate_id'];sig=m.robust_epistemic_constructor_candidates[cid].digest();root=Path(td.name);del m
        m2=Microseed(root);assert cid in m2.robust_epistemic_constructor_candidates;assert m2.robust_epistemic_constructor_candidates[cid].digest()==sig;assert cid not in m2.epistemic_projections.records
    finally:td.cleanup()


def _admitted_old(m):
    f=discover(m,rows('old',n=3000,causal=(2,11,19),noise=.02,seed=19));cid=f[0]['candidate_id'];m.admit_robust_epistemic_constructor_candidate(ticket(m,cid,'QOLD'),projection_id='P');return cid

def current_stream(pre=1024,post=1024,*,post_causal=(2,11,20),post_noise=.02):
    return rows('pre',pre,causal=(2,11,19),noise=.02,seed=20)+rows('post',post,causal=post_causal,noise=post_noise,seed=21)


def test_stable_noisy_law_does_not_false_stale_projection():
    td,m=new()
    try:
        _admitted_old(m);w=m.assess_epistemic_projection_predictive_currentness('P',rows('stable',2048,causal=(2,11,19),noise=.02,seed=22),ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2))
        assert w['status']=='CURRENT_WITHIN_BOUNDS' and w['projection_current'] is True and m.epistemic_projections.records['P'].current
    finally:td.cleanup()


def test_sequential_law_switch_stales_projection_and_recent_data_nominates_new_support():
    td,m=new()
    try:
        _admitted_old(m);stream=current_stream();w=m.assess_epistemic_projection_predictive_currentness('P',stream,ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2))
        assert w['status']=='DRIFT_WITNESS' and w['drift_cause_authority']=='NONE' and not m.epistemic_projections.records['P'].current
        recent=rows('recent',2400,causal=(2,11,20),noise=.02,seed=23);f=discover(m,recent);s,_=support(m,f);assert s==((0,2),(0,11),(0,20))
    finally:td.cleanup()


def test_noise_rate_shift_produces_same_drift_kind_without_cause_authority():
    td,m=new()
    try:
        _admitted_old(m);stream=current_stream(post_causal=(2,11,19),post_noise=.24);w=m.assess_epistemic_projection_predictive_currentness('P',stream,ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2))
        assert w['status']=='DRIFT_WITNESS';assert w['drift_cause_authority']=='NONE';assert w['regime_identity_authority']=='NONE'
    finally:td.cleanup()


def test_frame_drift_invalidates_admitted_robust_projection_independently_of_predictive_monitor():
    td,m=new()
    try:
        f=discover(m,rows('frame',seed=24));cid=f[0]['candidate_id'];m.admit_robust_epistemic_constructor_candidate(ticket(m,cid,'QF'),projection_id='P');m.change_operational_frame('F',reason='RAW_BOUNDARY_CHANGED');assert m.epistemic_projections.records['P'].current is False
    finally:td.cleanup()


def test_status_hard_stop_and_nonpromotions():
    td,m=new()
    try:
        s=m.status();assert s['research_terminal_ms']>=1277 and s['integration_evidence_through_ms']>=1277 and s['next_ms']>=1278
        assert 'NO_EFFECT_METRIC_OR_NOISE_RATE_MODEL' in s['projection_constructor_growth'];assert 'NO_DRIFT_CAUSE_OR_REGIME_IDENTITY_AUTHORITY' in s['projection_predictive_currentness']
        assert not hasattr(m,'discover_regime_identity') and not hasattr(m,'infer_noise_model')
    finally:td.cleanup()
