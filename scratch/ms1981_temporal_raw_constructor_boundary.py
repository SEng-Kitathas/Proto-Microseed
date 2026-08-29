from __future__ import annotations

import json, random, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, ConstructorGrowthConfig, ConstructorProjectionSample,
    EpisodeSchemaContract, EpistemicStatus, ExternalConstructorQualifier, FeasibilityState,
    Microseed, Observation, OperationalFrameContract, QualificationState, QueryObligation,
    RecruitmentOption, RehearsalTransitionObservation, ValueVariableContract,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'temporal_raw_relation_world_server.py'
BITS=(('0','0'),('0','1'),('1','0'),('1','1'))


class World:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT)); assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        row=json.loads(line); assert row.get('status')=='OK',row; return row
    def reset(self,bits):self.call('reset',bits=list(bits))
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
    m.register_operational_frame(OperationalFrameContract('F','temporal raw relation frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1981',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','regulatory coordinate',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1981',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED));m.observe_value_state('V',0.0)
    for cid in ('PREP','B'):
        m.register_capability(CapabilityContract(cid,'opaque effect',{}, {'output':'receipt'},(),(),Authority.EFFECT,('MS1981',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS','raw observation',{}, {'output':'raw'},(),(),Authority.OBSERVATION_ONLY,('MS1981',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1981',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('PREP','B','OBS'):m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','temporal raw episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1981',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m


def external_seed(bits,action,n=12):
    w=World()
    try:
        w.reset(bits)
        if action=='B':w.apply('PREP')
        before=w.observe();w.apply(action);after=w.observe();effect=float(after['observed_value'])-float(before['observed_value'])
        start='ALIAS0' if action=='PREP' else 'ALIAS1'
        return tuple(RehearsalTransitionObservation(f'S-{bits[0]}{bits[1]}-{action}-{i}',start,action,after['next_state_id'],effect,0,'F',0,'EP',0) for i in range(n))
    finally:w.close()


def proposals(m):
    prep=m.nominate_counterfactual_rehearsal(external_seed(('0','0'),'PREP'),(RecruitmentOption('PREP',FeasibilityState.FEASIBLE,local_cost=.1),),start_state_id='ALIAS0',value_id='V');assert prep
    out={'PREP':prep}
    for bits in BITS:
        p=m.nominate_counterfactual_rehearsal(external_seed(bits,'B'),(RecruitmentOption('B',FeasibilityState.FEASIBLE,local_cost=.1),),start_state_id='ALIAS1',value_id='V');assert p;out[bits]=p
    return out


def step(m,proposal,tag):
    i=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob());assert i['status']=='ACTION_INTENT_NOMINATED',i
    x=m.execute_bounded_action(i['intent']['intent_id'],act_ob());assert x['status']=='ACTION_EXECUTED',x
    o=m.record_bounded_action_outcome_via_observation_basis(x['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-OUT-{tag}',capture_id=f'CAP-{tag}');assert o['status']=='ACTION_OUTCOME_OBSERVED',o
    return o


def chain(m,w,ps,bits,index):
    w.reset(bits);m.observe_value_state('V',0.0)
    m.observe_opaque_control_state(Observation(f'C0-{index}','EXTERNAL','opaque-control','ALIAS0',authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-STATE0-{index}')
    r0=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-RAW0-{index}',capture_id=f'RAW0-{index}',max_coordinates=1);assert r0['status']=='BOUNDED_RAW_OBSERVATION_RECORDED' and tuple(r0['raw_tokens'])==(bits[0],)
    a=step(m,ps['PREP'],f'{index}-PREP');assert a['outcome']['actual_next_state_id']=='ALIAS1'
    r1=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-RAW1-{index}',capture_id=f'RAW1-{index}',max_coordinates=1);assert r1['status']=='BOUNDED_RAW_OBSERVATION_RECORDED' and tuple(r1['raw_tokens'])==(bits[1],)
    b=step(m,ps[bits],f'{index}-B');expected='SAME' if bits[0]==bits[1] else 'DIFF';assert b['outcome']['actual_next_state_id']==expected
    return {'bits':bits,'end':expected}


def supplied_rows(history,prefix):
    return tuple(ConstructorProjectionSample(f'{prefix}-{i}',((row['bits'][1],),(row['bits'][0],)),'B',row['end'],'S','F',0,'EP',0) for i,row in enumerate(history))


def external_holdout(candidate):
    pred={(b,a):e for b,a,e in candidate.bucket_action_prediction};rows=[]
    for bits in BITS:
        for _ in range(4):
            w=World()
            try:w.reset(bits);w.apply('PREP');w.apply('B');end=w.observe()['next_state_id']
            finally:w.close()
            raw=((bits[1],),(bits[0],));bucket=candidate.project(raw);assert bucket is not None and pred[(bucket,'B')]==end;rows.append({'raw_history':raw,'bucket':bucket,'end':end})
    return rows


def run_ms1981():
    td=tempfile.TemporaryDirectory(prefix='ms1981-temporal-raw-');w=World();m=build(Path(td.name),w)
    try:
        ps=proposals(m);history=[]
        for i in range(40):history.append(chain(m,w,ps,BITS[i%4],i))
        train=supplied_rows(history[:24],'TRAIN');pressure=supplied_rows(history[24:32],'PRESS');validation=supplied_rows(history[32:],'VALID')
        cfg0=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=0,min_train_support=16,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        assert m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg0)==[]
        cfg1=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=1,min_train_support=16,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        found=m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg1);assert found
        cs=[m.epistemic_constructor_candidates[x['candidate_id']] for x in found]
        exact=[c for c in cs if set(a.token() for a in c.atoms)=={'L0:P0','L1:P0'}]
        assert len(exact)==1,[(tuple(a.token() for a in c.atoms),c.validation_accuracy,c.lift) for c in cs]
        c=exact[0];assert c.validation_accuracy==1.0
        h=external_holdout(c);q=m.append_evidence('Q-MS1981',{'kind':'TEMPORAL_RAW_HOLDOUT','candidate_sha256':c.digest(),'rows':h},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1981')
        t=ExternalConstructorQualifier(m.evidence,qualifier_id='EXTERNAL-MS1981').qualify(c,qualification_evidence=(q,));rec=m.admit_epistemic_constructor_candidate(t,projection_id='P-MS1981-SUPPLIED-RAW-HISTORY');assert rec.current
        return {'status':'BOUNDARY_CONFIRMED','current_raw_only_candidates':0,'atoms':[a.token() for a in c.atoms],'validation_accuracy':c.validation_accuracy,'external_holdout_count':len(h),'earned':'EXISTING_CONSTRUCTOR_CAN_RESOLVE_A_TEMPORAL_RAW_RELATION_WHEN_RAW_OBSERVATION_HISTORY_SLICES_ARE_SUPPLIED','missing_owner':'ENTITY_OWNED_RAW_OBSERVATION_PREDECESSOR_CHAIN_TO_CONSTRUCTOR_SAMPLE','raw_history_authority':'HARNESS_SUPPLIED_ASSISTANCE','new_constructor_mechanism_required':'NO','semantic_coordinate_authority':'NONE','semantic_projection_authority':'NONE','language_authority':'NONE'}
    finally:_close(m);w.close();td.cleanup()


def main():print(json.dumps(run_ms1981(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
