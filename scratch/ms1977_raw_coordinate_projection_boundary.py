from __future__ import annotations

import json, random, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus, ExternalProjectionQualifier,
    FeasibilityState, Microseed, Observation, OperationalFrameContract,
    ProjectionDiscoveryConfig, ProjectionSample, QualificationState, QueryObligation,
    RecruitmentOption, RehearsalTransitionObservation, ValueVariableContract,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'raw_coordinate_alias_world_server.py'
PAIRS=(('0','0'),('0','1'),('1','0'),('1','1'))

class World:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT)); assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush(); line=self.proc.stdout.readline(); assert line
        row=json.loads(line); assert row.get('status')=='OK',row; return row
    def reset(self,pair):self.call('reset',raw_tokens=list(pair))
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
    m.register_operational_frame(OperationalFrameContract('F','raw-coordinate alias frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','regulatory coordinate',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED));m.observe_value_state('V',0.0)
    m.register_capability(CapabilityContract('B','opaque effect',{}, {'output':'receipt'},(),(),Authority.EFFECT,('MS1977',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.apply('B'),operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS','raw observation',{}, {'output':'opaque-state-plus-raw'},(),(),Authority.OBSERVATION_ONLY,('MS1977',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1977',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('B','OBS'):m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','raw-coordinate alias episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m

def external_seed(pair,n=12):
    w=World()
    try:
        w.reset(pair);before=w.observe();w.apply('B');after=w.observe();effect=float(after['observed_value'])-float(before['observed_value'])
        return tuple(RehearsalTransitionObservation(f'S-{pair[0]}{pair[1]}-{i}','ALIAS','B',after['next_state_id'],effect,0,'F',0,'EP',0) for i in range(n))
    finally:w.close()

def proposals(m):
    out={}
    for pair in PAIRS:
        p=m.nominate_counterfactual_rehearsal(external_seed(pair),(RecruitmentOption('B',FeasibilityState.FEASIBLE,local_cost=.1),),start_state_id='ALIAS',value_id='V');assert p;out[pair]=p
    return out

def execute(m,w,pair,p,index):
    w.reset(pair);m.observe_value_state('V',0.0)
    pre=w.observe();assert tuple(pre['raw_tokens'])==pair
    m.observe_opaque_control_state(Observation(f'C-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-STATE-{index}')
    i=m.nominate_bounded_action_intent(p.proposal_id,act_ob());assert i['status']=='ACTION_INTENT_NOMINATED'
    x=m.execute_bounded_action(i['intent']['intent_id'],act_ob());assert x['status']=='ACTION_EXECUTED'
    o=m.record_bounded_action_outcome_via_observation_basis(x['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-OUT-{index}',capture_id=f'CAP-{index}');assert o['status']=='ACTION_OUTCOME_OBSERVED'
    ev=m.evidence.get(f'E-OUT-{index}');assert ev is not None
    # Pre-repair boundary: raw_tokens reached the observation handler but are absent
    # from durable action-outcome evidence and generic OBSERVATION events.
    assert 'raw_tokens' not in (ev.get('payload') or {})
    return ProjectionSample(f'HARNESS-{index}',pair,'B',o['outcome']['actual_next_state_id'],'S','F',0)

def external_holdout(candidate):
    rows=[]
    pred={(b,a):e for b,a,e in candidate.bucket_action_prediction}
    for pair in PAIRS:
        for _ in range(4):
            w=World()
            try:w.reset(pair);w.apply('B');end=w.observe()['next_state_id']
            finally:w.close()
            bucket=candidate.project(pair);assert bucket is not None and pred[(bucket,'B')]==end;rows.append({'raw_tokens':pair,'end':end,'bucket':bucket})
    return rows

def run_ms1977():
    td=tempfile.TemporaryDirectory(prefix='ms1977-raw-proj-');w=World();m=build(Path(td.name),w)
    try:
        ps=proposals(m);rows=[]
        for i in range(48):
            pair=PAIRS[i%4];rows.append(execute(m,w,pair,ps[pair],i))
        rr=list(rows);random.Random(1977).shuffle(rr);train=tuple(rr[:28]);validation=tuple(rr[28:])
        cfg1=ProjectionDiscoveryConfig(max_subset=1,min_train_support=20,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=4)
        assert m.discover_epistemic_projection_candidates(train,validation,cfg1)==[]
        cfg2=ProjectionDiscoveryConfig(max_subset=2,min_train_support=20,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=4)
        found=m.discover_epistemic_projection_candidates(train,validation,cfg2);assert found
        candidates=[m.epistemic_projection_candidates[x['candidate_id']] for x in found];c=[x for x in candidates if x.input_positions==(0,1)][0];assert c.validation_accuracy==1.0
        h=external_holdout(c);q=m.append_evidence('Q-MS1977',{'kind':'RAW_COORD_HOLDOUT','candidate_sha256':c.digest(),'rows':h},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1977')
        t=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1977').qualify(c,qualification_evidence=(q,));rec=m.admit_epistemic_projection_candidate(t,projection_id='P-MS1977-SUPPLIED-RAW');assert rec.current
        return {'status':'BOUNDARY_CONFIRMED','single_coordinate_candidates':0,'input_positions':list(c.input_positions),'validation_accuracy':c.validation_accuracy,'external_holdout_count':len(h),'earned':'EXISTING_PROJECTION_SEARCH_CAN_DISCOVER_A_TWO_COORDINATE_XOR_DISCRIMINATOR_WHEN_RAW_COORDINATES_ARE_SUPPLIED','missing_owner':'BOUNDED_DURABLE_OWNED_RAW_OBSERVATION_COORDINATE_INGRESS','ordinary_outcome_evidence_preserves_raw_tokens':'NO','raw_coordinate_authority':'HARNESS_SUPPLIED_ASSISTANCE','semantic_projection_authority':'NONE','language_authority':'NONE'}
    finally:_close(m);w.close();td.cleanup()

def main():print(json.dumps(run_ms1977(),indent=2,sort_keys=True))
if __name__=='__main__':main()
