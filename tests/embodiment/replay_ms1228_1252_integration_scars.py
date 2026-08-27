from __future__ import annotations
from pathlib import Path
import hashlib,itertools,json,tempfile
from microseed import (
    Microseed,Authority,EpistemicStatus,QualificationState,OperationalFrameContract,EpisodeSchemaContract,
    ConstructorProjectionSample,ConstructorGrowthConfig,ExternalConstructorQualifier,
)

def H(x): return hashlib.sha256(x.encode()).hexdigest()

def setup(root,episode=True):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract(
        'F','opaque-boundary',H('frame'),Authority.DERIVED_READ_ONLY,('MS1228-1252',),'CURRENT',
        QualificationState.SHADOW_QUALIFIED,('EXTERNAL_FRAME_QUALIFICATION',),('NO_SEMANTIC_FEATURE_AUTHORITY',),()
    ))
    if episode:
        m.register_episode_schema(EpisodeSchemaContract(
            'EPS','opaque-history',H('eps'),Authority.DERIVED_READ_ONLY,('MS1228-1252',),'CURRENT',
            QualificationState.SHADOW_QUALIFIED,('EXTERNAL_EPISODE_SCHEMA_QUALIFICATION',),(('F',0),),(),('NO_SEMANTIC_TIME_AUTHORITY',),()
        ))
    return m

def triple(prefix):
    out=[];i=0
    for bits in itertools.product('01',repeat=8):
        for a in ('a0','a1'):
            y=int(bits[1])^int(bits[4])^int(bits[6])^(a=='a1')
            out.append(ConstructorProjectionSample(f'{prefix}-{i}',(tuple(bits),),a,f'e{int(y)}',None,'F',0));i+=1
    return out

def temporal(prefix):
    out=[];i=0
    for now in itertools.product('01',repeat=4):
        for old in itertools.product('01',repeat=4):
            for a in ('a0','a1'):
                y=int(now[2])^int(old[1])^(a=='a1')
                out.append(ConstructorProjectionSample(f'{prefix}-{i}',(tuple(now),tuple(old)),a,f'e{int(y)}',None,'F',0,'EPS',0));i+=1
    return out

def discover(m, rows_fn, *, support=4, lag=0, budget=20000):
    cfg=ConstructorGrowthConfig(max_support_ceiling=support,max_lag_ceiling=lag,min_train_support=100,
        min_validation_accuracy=.99,min_lift_over_action_baseline=.40,min_scope_accuracy=.99,node_budget=budget)
    return m.discover_epistemic_constructor_candidates(rows_fn('tr'),rows_fn('pr'),rows_fn('va'),cfg)

def ticket(m,cid,eid):
    ev=m.append_evidence(eid,{'heldout':1.0},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL_MS1252')
    return ExternalConstructorQualifier(m.evidence,qualifier_id='HSP-MS1252').qualify(m.epistemic_constructor_candidates[cid],qualification_evidence=(ev,))

def main():
    checks={}
    with tempfile.TemporaryDirectory(prefix='ms1252-replay-a-') as td:
        root=Path(td);m=setup(root)
        f=discover(m,triple);c=m.epistemic_constructor_candidates[f[0]['candidate_id']]
        checks['triple_support_reached_without_exact_degree']=tuple((x.lag,x.position) for x in c.atoms)==((0,1),(0,4),(0,6))
        checks['triple_validation_exact']=c.validation_accuracy==1.0
        checks['no_semantic_operator_in_assistance']=not any('XOR' in x or 'PARITY' in x for x in c.assistance_ancestry)
        checks['support_ceiling_two_abstains']=discover(m,triple,support=2)==[]
        checks['budget_exhaustion_abstains']=discover(m,triple,budget=2)==[]
        checks['candidate_has_zero_authority']=all(getattr(c,k)=='NONE' for k in ('proposal_authority','qualification_authority','semantic_projection_authority','truth_authority'))
        cid=c.candidate_id
        rec=m.admit_epistemic_constructor_candidate(ticket(m,cid,'QA'),projection_id='P')
        checks['external_qualification_is_admission_boundary']=rec.projection_origin=='ENDOGENOUS_CONSTRUCTOR_GROWTH_EXTERNALLY_QUALIFIED' and rec.qualification_evidence_ids==('QA',)
        m.change_operational_frame('F',reason='RAW_BOUNDARY_CHANGED')
        checks['post_admission_frame_drift_invalidates_projection']=m.epistemic_projections.records['P'].current is False

    with tempfile.TemporaryDirectory(prefix='ms1252-replay-restart-') as td:
        root=Path(td);m=setup(root)
        f=discover(m,triple);cid=f[0]['candidate_id'];sig=m.epistemic_constructor_candidates[cid].digest();del m
        m2=Microseed(root);rc=m2.epistemic_constructor_candidates[cid]
        checks['restart_preserves_proposal_without_qualification_gain']=rc.digest()==sig and cid not in m2.epistemic_projections.records and rc.qualification_authority=='NONE'

    with tempfile.TemporaryDirectory(prefix='ms1252-replay-b-') as td:
        m=setup(Path(td))
        checks['present_state_fails_temporal_world']=discover(m,temporal,support=3,lag=0)==[]
        ft=discover(m,temporal,support=3,lag=1);ct=m.epistemic_constructor_candidates[ft[0]['candidate_id']]
        checks['minimal_temporal_support_reached']=tuple((x.lag,x.position) for x in ct.atoms)==((0,2),(1,1))
        checks['temporal_candidate_preserves_episode_ancestry']=ct.episode_schema_epochs==(('EPS',0),)
        m.admit_epistemic_constructor_candidate(ticket(m,ct.candidate_id,'QB'),projection_id='TP')
        m.change_episode_schema('EPS',reason='GROUPING_CHANGED')
        checks['post_admission_episode_drift_invalidates_projection']=m.epistemic_projections.records['TP'].current is False
        s=m.status()
        checks['hard_stop_and_noise_ceiling_preserved']=s['research_terminal_ms']>=1252 and s['next_ms']>=1253 and s.get(f"ms{s['next_ms']}_started") is False and 'EXACT_HYPERGRAPH_PATH' in s['projection_constructor_growth'] and not hasattr(m,'infer_noise_model')
    out={'schema':'microseed.ms1228-1252-integration-scar-replay.v1','checks':checks,'passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values())}
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if out['all_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
