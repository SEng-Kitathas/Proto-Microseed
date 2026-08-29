from __future__ import annotations

import json, random, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, ConstructorGrowthConfig, EpisodeSchemaContract,
    EpistemicStatus, ExternalConstructorQualifier, FeasibilityState, Microseed,
    Observation, OperationalFrameContract, QualificationState, QueryObligation,
    RecruitmentOption, RehearsalTransitionObservation, ValueVariableContract,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'lag3_representation_alias_world_server.py'

class World:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT)); assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n');self.proc.stdin.flush();line=self.proc.stdout.readline();assert line
        row=json.loads(line);assert row.get('status')=='OK',row;return row
    def reset(self,c):self.call('reset',context=c)
    def apply(self,a):return self.call('apply',action_id=a)
    def observe(self):
        r=self.call('observe');r.pop('status',None);return r
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)

def act_ob():return QueryObligation('ACT','effect',Authority.EFFECT,operational_scope_id='S')
def obs_ob():return QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S')
def basis_ob():return QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S')

def build(root,world):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract('F','lag3 alias frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1976',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','regulatory coordinate',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1976',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')));m.observe_value_state('V',0.0)
    for cid in ('P1','P2','P3','B'):
        m.register_capability(CapabilityContract(cid,'opaque process effect',{}, {'output':'receipt'},(),(),Authority.EFFECT,('MS1976',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS','observe',{}, {'output':'state'},(),(),Authority.OBSERVATION_ONLY,('MS1976',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1976',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('P1','P2','P3','B','OBS'):m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','lag3 episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1976',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m

def ext_sample(context,action):
    w=World()
    try:
        w.reset(context)
        for a in ('P1','P2','P3'):
            if action==a:break
            w.apply(a)
        before=w.observe();w.apply(action);after=w.observe();return before,after
    finally:w.close()

def seed(context,action,n=12):
    before,after=ext_sample(context,action);effect=float(after['observed_value'])-float(before['observed_value'])
    return tuple(RehearsalTransitionObservation(f'S-{context}-{action}-{i}',before['next_state_id'],action,after['next_state_id'],effect,0,'F',0,'EP',0) for i in range(n))
def option(a):return RecruitmentOption(a,FeasibilityState.FEASIBLE,local_cost=.1)
def proposals(m):
    out={};starts={'P1':lambda c:c,'P2':lambda c:'s1','P3':lambda c:'s2','B':lambda c:'s3'}
    for c in ('s0','r'):
        for a in ('P1','P2','P3','B'):
            p=m.nominate_counterfactual_rehearsal(seed(c,a),(option(a),),start_state_id=starts[a](c),value_id='V');assert p and p.sequence==(a,);out[(c,a)]=p
    return out

def step(m,p,tag):
    i=m.nominate_bounded_action_intent(p.proposal_id,act_ob());assert i['status']=='ACTION_INTENT_NOMINATED';x=m.execute_bounded_action(i['intent']['intent_id'],act_ob());assert x['status']=='ACTION_EXECUTED'
    o=m.record_bounded_action_outcome_via_observation_basis(x['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-{tag}',capture_id=f'C-{tag}');assert o['status']=='ACTION_OUTCOME_OBSERVED';return o

def chain(m,w,ps,c,i):
    w.reset(c);m.observe_value_state('V',0.0);m.observe_opaque_control_state(Observation(f'C-{c}-{i}','EXT','opaque-control',c,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-C-{c}-{i}')
    for a,end in [('P1','s1'),('P2','s2'),('P3','s3')]:assert step(m,ps[(c,a)],f'{c}-{i}-{a}')['outcome']['actual_next_state_id']==end
    end='sx' if c=='s0' else 'sy';assert step(m,ps[(c,'B')],f'{c}-{i}-B')['outcome']['actual_next_state_id']==end

def heldout(candidate):
    rows=[]
    for c in ('s0','r'):
        for _ in range(8):
            _,after=ext_sample(c,'B');raw=(('s3',),('s2',),('s1',),(c,));bucket=candidate.project(raw);rows.append((bucket,after['next_state_id']))
    pred={(b,a):e for b,a,e in candidate.bucket_action_prediction};assert all(b is not None and pred[(b,'B')]==e for b,e in rows);return rows

def run_ms1976():
    td=tempfile.TemporaryDirectory(prefix='ms1976-lag3-');w=World();m=build(Path(td.name),w)
    try:
        ps=proposals(m)
        for i in range(40):chain(m,w,ps,'s0' if i%2==0 else 'r',i)
        owned=m.derive_admitted_constructor_projection_samples(max_lag=3);rows=[x for x in owned['samples'] if x.action_token=='B' and len(x.raw_history)==4];assert len(rows)==40
        assert {x.raw_history for x in rows}=={(('s3',),('s2',),('s1',),('s0',)),(('s3',),('s2',),('s1',),('r',))}
        rr=list(rows);random.Random(1976).shuffle(rr);train=tuple(rr[:20]);pressure=tuple(rr[20:30]);validation=tuple(rr[30:])
        cfg2=ConstructorGrowthConfig(max_support_ceiling=3,max_lag_ceiling=2,min_train_support=12,min_validation_accuracy=.95,min_lift_over_action_baseline=.4,min_scope_accuracy=.95,max_candidates=4)
        assert m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg2)==[]
        cfg3=ConstructorGrowthConfig(max_support_ceiling=3,max_lag_ceiling=3,min_train_support=12,min_validation_accuracy=.95,min_lift_over_action_baseline=.4,min_scope_accuracy=.95,max_candidates=4)
        found=m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg3);assert found
        cs=[m.epistemic_constructor_candidates[x['candidate_id']] for x in found];cs=[c for c in cs if c.lag_depth_used==3];assert cs;c=cs[0];assert [a.token() for a in c.atoms]==['L3:P0'];assert c.validation_accuracy==1.0
        h=heldout(c);q=m.append_evidence('Q-MS1976',{'kind':'LAG3_HOLDOUT','candidate_sha256':c.digest(),'rows':h},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1976')
        t=ExternalConstructorQualifier(m.evidence,qualifier_id='EXTERNAL-MS1976').qualify(c,qualification_evidence=(q,));rec=m.admit_epistemic_constructor_candidate(t,projection_id='P-MS1976');assert rec.current
        return {'status':'PASS','max_lag_2_candidates':0,'atoms':[a.token() for a in c.atoms],'lag_depth_used':c.lag_depth_used,'validation_accuracy':c.validation_accuracy,'external_holdout_count':len(h),'earned':'OWNED_AUTHENTICATED_HISTORY_BRIDGE_AND_EXISTING_CONSTRUCTOR_GROWTH_COMPOSE_TO_LAG3_WITHOUT_NEW_REPRESENTATION_MECHANISM','history_window_authority':'SUPPLIED_BOUNDED_CEILING','semantic_projection_authority':'NONE','language_authority':'NONE'}
    finally:_close(m);w.close();td.cleanup()

def main():print(json.dumps(run_ms1976(),indent=2,sort_keys=True))
if __name__=='__main__':main()
