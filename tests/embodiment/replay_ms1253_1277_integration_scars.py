from __future__ import annotations
from pathlib import Path
import hashlib,json,random,tempfile
from microseed import (
    Microseed, Authority, EpistemicStatus, QualificationState, OperationalFrameContract,
    ConstructorProjectionSample, RobustConstructorGrowthConfig, ExternalRobustConstructorQualifier,
    ProjectionPredictiveCurrentnessConfig,
)

def H(x): return hashlib.sha256(x.encode()).hexdigest()

def setup(root):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract(
        frame_id='F',purpose='opaque-raw-action-effect-boundary',signature_sha256=H('frame-v0'),
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS1253-1277',),currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNAL_FRAME_QUALIFICATION',),
        invariants=('NO_SEMANTIC_FEATURE_AUTHORITY',),
    ))
    return m

def rows(prefix,n=2400,*,causal=(2,11,19),noise=.02,seed=1,structured=False):
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

def support(m,found):
    c=m.robust_epistemic_constructor_candidates[found[0]['candidate_id']]
    return tuple((a.lag,a.position) for a in c.atoms),c

def ticket(m,cid,eid):
    ev=m.append_evidence(eid,{'heldout':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1277')
    return ExternalRobustConstructorQualifier(m.evidence,qualifier_id='HSP-MS1277').qualify(
        m.robust_epistemic_constructor_candidates[cid],qualification_evidence=(ev,))

def admitted(m):
    f=discover(m,rows('old',3000,seed=41));cid=f[0]['candidate_id']
    m.admit_robust_epistemic_constructor_candidate(ticket(m,cid,'QOLD'),projection_id='P')
    return cid

def current_stream(*,post_causal=(2,11,20),post_noise=.02):
    return rows('pre',1024,causal=(2,11,19),noise=.02,seed=42)+rows('post',1024,causal=post_causal,noise=post_noise,seed=43)

def main():
    checks={}
    with tempfile.TemporaryDirectory(prefix='ms1277-replay-a-') as td:
        m=setup(Path(td))
        f=discover(m,rows('n2',noise=.02,seed=31));s,c=support(m,f)
        checks['two_percent_noise_recovers_true_triple']=s==((0,2),(0,11),(0,19)) and c.validation_accuracy>=.96
        checks['no_noise_rate_or_effect_metric_assistance']='NO_NOISE_RATE_MODEL' in c.assistance_ancestry and 'NO_EFFECT_DISTANCE_METRIC' in c.assistance_ancestry
        checks['support_ceiling_exhaustion_abstains']=discover(m,rows('ceil',seed=32),max_support_ceiling=2)==[]
        checks['combination_budget_exhaustion_abstains']=discover(m,rows('budget',seed=33),combination_budget=100)==[]
        sf,sc=support(m,discover(m,rows('struct',seed=34,structured=True,noise=0),min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95))
        checks['structured_corruption_becomes_operational_coordinate']=sf==((0,2),(0,7),(0,11),(0,19)) and sc.validation_accuracy==1.0
        bad=ExternalRobustConstructorQualifier(m.evidence,qualifier_id='HSP-MS1277').qualify(c,qualification_evidence=())
        try:
            m.admit_robust_epistemic_constructor_candidate(bad,projection_id='BAD')
            checks['external_qualification_boundary']=False
        except ValueError:
            checks['external_qualification_boundary']=True
    with tempfile.TemporaryDirectory(prefix='ms1277-replay-mix-') as td:
        m=setup(Path(td));r=random.Random(35);xs=[]
        for i in range(2800):
            raw=tuple(str(r.randrange(2)) for _ in range(24));ai=r.randrange(2);causal=(2,11,19) if r.randrange(2)==0 else (2,11,20);y=ai
            for j in causal:y^=int(raw[j])
            if r.random()<.02:y^=1
            xs.append(ConstructorProjectionSample(f'mix-{i}',(raw,),f'a{ai}',f'e{y}',None,'F',0))
        checks['simultaneous_hidden_regime_mixture_abstains']=discover(m,xs,min_validation_accuracy=.82,min_lift_over_action_baseline=.20,min_scope_accuracy=.82)==[]
    with tempfile.TemporaryDirectory(prefix='ms1277-replay-restart-') as td:
        root=Path(td);m=setup(root);f=discover(m,rows('restart',seed=36));cid=f[0]['candidate_id'];sig=m.robust_epistemic_constructor_candidates[cid].digest();del m
        m2=Microseed(root);checks['candidate_restart_preserves_proposal_without_qualification_gain']=cid in m2.robust_epistemic_constructor_candidates and m2.robust_epistemic_constructor_candidates[cid].digest()==sig and cid not in m2.epistemic_projections.records
    with tempfile.TemporaryDirectory(prefix='ms1277-replay-current-') as td:
        m=setup(Path(td));admitted(m);pc=ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2)
        stable=m.assess_epistemic_projection_predictive_currentness('P',rows('stable',2048,seed=37),pc)
        checks['stable_noisy_law_remains_current']=stable['status']=='CURRENT_WITHIN_BOUNDS' and stable['projection_current'] is True
        sw=m.assess_epistemic_projection_predictive_currentness('P',current_stream(),pc)
        checks['law_switch_yields_cause_free_drift_witness']=sw['status']=='DRIFT_WITNESS' and sw['drift_cause_authority']=='NONE' and sw['regime_identity_authority']=='NONE'
        checks['drift_witness_stales_projection']=m.epistemic_projections.records['P'].current is False
        nf=discover(m,rows('recent',2400,causal=(2,11,20),noise=.02,seed=38));ns,_=support(m,nf)
        checks['recent_data_nominates_replacement_support']=ns==((0,2),(0,11),(0,20))
    with tempfile.TemporaryDirectory(prefix='ms1277-replay-noise-') as td:
        m=setup(Path(td));admitted(m);pc=ProjectionPredictiveCurrentnessConfig(window_size=256,min_window_accuracy=.82,consecutive_failure_windows=2)
        nw=m.assess_epistemic_projection_predictive_currentness('P',current_stream(post_causal=(2,11,19),post_noise=.24),pc)
        checks['noise_rate_shift_has_same_drift_kind_without_cause_identity']=nw['status']=='DRIFT_WITNESS' and nw['drift_cause_authority']=='NONE' and nw['regime_identity_authority']=='NONE'
    with tempfile.TemporaryDirectory(prefix='ms1277-replay-frame-') as td:
        m=setup(Path(td));admitted(m);m.change_operational_frame('F',reason='RAW_BOUNDARY_CHANGED')
        checks['frame_drift_invalidates_robust_projection']=m.epistemic_projections.records['P'].current is False
        root=Path(td);del m;m2=Microseed(root)
        checks['predictive_or_frame_invalidation_survives_restart']=m2.epistemic_projections.records['P'].current is False
        s=m2.status();checks['ms1277_preserved_as_ancestral_floor']=s['research_terminal_ms']>=1277 and s['integration_evidence_through_ms']>=1277 and s['next_ms']>=1278
        checks['no_noise_model_regime_identity_or_self_qualification_api']=not hasattr(m2,'infer_noise_model') and not hasattr(m2,'discover_regime_identity') and not hasattr(m2,'self_qualify_projection')
    out={'schema':'microseed.ms1253-1277-integration-scar-replay.v1','checks':checks,'passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values())}
    print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
