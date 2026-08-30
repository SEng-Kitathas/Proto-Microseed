from __future__ import annotations

import itertools, json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus,
    ExternalProjectionQualifier, FeasibilityState, Microseed, Observation,
    OperationalFrameContract, ProjectionDiscoveryConfig, ProjectionSample,
    QualificationState, QueryObligation, RecruitmentOption,
    RehearsalTransitionObservation, ValueVariableContract,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'depth4_recursive_bucket_world_server.py'


def _pair(parity:int,toggle:int) -> tuple[str,str]:
    return str(toggle),str(toggle^parity)


OCTETS=[]
for parities in itertools.product((0,1),repeat=4):
    for toggles in ((0,0,0,0),(0,1,1,0),(1,0,0,1),(1,1,1,1)):
        raw=[]
        for p,t in zip(parities,toggles): raw.extend(_pair(p,t))
        OCTETS.append(tuple(raw))
OCTETS=tuple(OCTETS)
assert len(OCTETS)==64 and len(set(OCTETS))==64


class World:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT)); assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        row=json.loads(line); assert row.get('status')=='OK',row; return row
    def reset(self,raw): self.call('reset',raw_tokens=list(raw))
    def apply(self,action): return self.call('apply',action_id=action)
    def observe(self):
        row=self.call('observe'); row.pop('status',None); return row
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)


def act_ob(): return QueryObligation('ACT','effect',Authority.EFFECT,operational_scope_id='S')
def obs_ob(): return QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S')
def basis_ob(): return QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S')


def build(root:Path,world:World):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract('F','depth4 recursive bucket frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1988',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','regulatory coordinate',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1988',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED)); m.observe_value_state('V',0.0)
    for aid in ('C','E','G'):
        m.register_capability(CapabilityContract(aid,f'opaque process effect {aid}',{}, {'output':'receipt'},(),(),Authority.EFFECT,('MS1988',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _aid=aid,**_:world.apply(_aid),operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS','raw observation',{}, {'output':'raw-state'},(),(),Authority.OBSERVATION_ONLY,('MS1988',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1988',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('C','E','G','OBS'): m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','depth4 recursive bucket episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1988',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m


def process_samples(action:str,repetitions:int=2):
    w=World(); rows=[]
    try:
        i=0
        for _ in range(repetitions):
            for raw in OCTETS:
                w.reset(raw); out=w.apply(action)
                rows.append(ProjectionSample(f'{action}-SRC-{i}',raw,action,out['next_state_id'],'S','F',0)); i+=1
        return tuple(rows)
    finally:w.close()


def discover_exact(m,rows,expected_positions,max_subset=2):
    cfg=ProjectionDiscoveryConfig(max_subset=max_subset,min_train_support=64,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=24)
    found=m.discover_epistemic_projection_candidates(rows[:96],rows[96:],cfg); assert found
    cs=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
    exact=[c for c in cs if c.input_positions==tuple(expected_positions)]
    assert exact,[(c.input_positions,c.validation_accuracy,c.lift) for c in cs]
    return exact[-1],cs


def admit_source_projection(m,action,expected_positions,projection_id):
    rows=process_samples(action,2)
    c,_=discover_exact(m,rows,expected_positions,2); assert c.validation_accuracy==1.0
    q=m.append_evidence(f'Q-{projection_id}',{'kind':'SOURCE_PROJECTION_HOLDOUT','candidate_sha256':c.digest(),'action':action},EpistemicStatus.PRESSURE_SUPPORTED,source=f'EXTERNAL-{projection_id}')
    ticket=ExternalProjectionQualifier(m.evidence,qualifier_id=f'EXTERNAL-{projection_id}').qualify(c,qualification_evidence=(q,))
    rec=m.admit_epistemic_projection_candidate(ticket,projection_id=projection_id); assert rec.current
    return c,rec


def seed_action(action:str,raw=OCTETS[0],n=12):
    w=World()
    try:
        w.reset(raw); before=w.observe(); w.apply(action); after=w.observe(); effect=float(after['observed_value'])-float(before['observed_value'])
        return tuple(RehearsalTransitionObservation(f'{action}-SEED-{i}','ALIAS',action,after['next_state_id'],effect,0,'F',0,'EP',0) for i in range(n))
    finally:w.close()


def prepare_proposal(m,action):
    p=m.nominate_counterfactual_rehearsal(seed_action(action),(RecruitmentOption(action,FeasibilityState.FEASIBLE,local_cost=.1),),start_state_id='ALIAS',value_id='V')
    assert p is not None and p.sequence==(action,),p
    return p


def execute_owned(m,world,raw,proposal,action,index):
    world.reset(raw); m.observe_value_state('V',0.0)
    state_eid=f'E-MS1988-{action}-STATE-{index}'
    m.observe_opaque_control_state(Observation(f'C-MS1988-{action}-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id=state_eid)
    receipt=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-MS1988-{action}-RAW-{index}',capture_id=f'RAW-MS1988-{action}-{index}',max_coordinates=8)
    assert receipt['status']=='BOUNDED_RAW_OBSERVATION_RECORDED' and tuple(receipt['raw_tokens'])==raw
    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED',ex
    out=m.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-MS1988-{action}-OUT-{index}',capture_id=f'CAP-MS1988-{action}-{index}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out


def run_owned_action(m,world,action,index_base):
    proposal=prepare_proposal(m,action)
    for i in range(128): execute_owned(m,world,OCTETS[i%64],proposal,action,index_base+i)


def qualify_candidate(m,candidate,projection_id,kind,holdout):
    qe=m.append_evidence(f'Q-{projection_id}',{'kind':kind,'candidate_sha256':candidate.digest(),'rows':holdout},EpistemicStatus.PRESSURE_SUPPORTED,source=f'EXTERNAL-{projection_id}')
    ticket=ExternalProjectionQualifier(m.evidence,qualifier_id=f'EXTERNAL-{projection_id}').qualify(candidate,qualification_evidence=(qe,))
    rec=m.admit_epistemic_projection_candidate(ticket,projection_id=projection_id); assert rec.current
    return rec


def learn_composed(m,action,projection_id,expected_positions,max_sources,depth):
    composed=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=max_sources,max_projection_depth=depth)
    assert composed['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',composed
    rows=tuple(x for x in composed['samples'] if x.action_token==action); assert len(rows)==128
    cfg1=ProjectionDiscoveryConfig(max_subset=1,min_train_support=64,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=24)
    assert m.discover_epistemic_projection_candidates(rows[:96],rows[96:],cfg1)==[]
    c,_=discover_exact(m,rows,expected_positions,2); assert c.validation_accuracy==1.0
    return composed,c


def candidate_for_record(m,projection_id):
    rec=m.epistemic_projections.records[projection_id]
    matches=[c for c in m.epistemic_projection_candidates.values() if c.digest()==rec.signature_sha256]
    assert len(matches)==1
    return matches[0]


def external_holdout_g(candidate,pa,pb,pd,pf,c,e):
    w=World(); rows=[]; pred={(b,a):effect for b,a,effect in candidate.bucket_action_prediction}
    try:
        for raw in OCTETS:
            w.reset(raw); actual=w.apply('G')['next_state_id']
            ba=pa.project(raw); bb=pb.project(raw); bd=pd.project(raw); bf=pf.project(raw); assert None not in (ba,bb,bd,bf)
            bc=c.project((ba,bb,bd,bf)); assert bc is not None
            be=e.project((ba,bb,bc,bd,bf)); assert be is not None
            vector=(ba,bb,bc,bd,be,bf)
            bucket=candidate.project(vector); assert bucket is not None and pred[(bucket,'G')]==actual
            rows.append({'raw':raw,'source_buckets':vector,'bucket':bucket,'actual':actual})
        return rows
    finally:w.close()


def run_ms1988():
    td=tempfile.TemporaryDirectory(prefix='ms1988-depth4-'); world=World(); m=build(Path(td.name),world)
    try:
        pa,_=admit_source_projection(m,'A',(0,1),'P-MS1988-A')
        pb,_=admit_source_projection(m,'B',(2,3),'P-MS1988-B')
        pd,_=admit_source_projection(m,'D',(4,5),'P-MS1988-D')
        pf,_=admit_source_projection(m,'F',(6,7),'P-MS1988-F')

        run_owned_action(m,world,'C',0)
        c_basis,c=learn_composed(m,'C','P-MS1988-C',(0,1),4,0)
        assert c_basis['source_projection_ids']==('P-MS1988-A','P-MS1988-B','P-MS1988-D','P-MS1988-F')
        c_hold=[{'source_count':4,'candidate_sha256':c.digest()}]
        crec=qualify_candidate(m,c,'P-MS1988-C','DEPTH2_COMPOSITION_HOLDOUT',c_hold)

        run_owned_action(m,world,'E',1000)
        e_basis,e=learn_composed(m,'E','P-MS1988-E',(2,3),5,1)
        assert e_basis['source_projection_ids']==('P-MS1988-A','P-MS1988-B','P-MS1988-C','P-MS1988-D','P-MS1988-F')
        e_hold=[{'source_count':5,'candidate_sha256':e.digest()}]
        erec=qualify_candidate(m,e,'P-MS1988-E','DEPTH3_COMPOSITION_HOLDOUT',e_hold)

        run_owned_action(m,world,'G',2000)

        shallow=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=6,max_projection_depth=1)
        assert shallow['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',shallow
        assert shallow['source_projection_ids']==('P-MS1988-A','P-MS1988-B','P-MS1988-C','P-MS1988-D','P-MS1988-F')
        assert ('P-MS1988-E','SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND') in shallow['source_rejections']
        shallow_g=tuple(x for x in shallow['samples'] if x.action_token=='G'); assert len(shallow_g)==128
        shallow_cfg=ProjectionDiscoveryConfig(max_subset=2,min_train_support=64,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=24)
        assert m.discover_epistemic_projection_candidates(shallow_g[:96],shallow_g[96:],shallow_cfg)==[]

        deep=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=6,max_projection_depth=2)
        assert deep['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',deep
        assert deep['source_projection_ids']==('P-MS1988-A','P-MS1988-B','P-MS1988-C','P-MS1988-D','P-MS1988-E','P-MS1988-F')
        g_rows=tuple(x for x in deep['samples'] if x.action_token=='G'); assert len(g_rows)==128
        one_cfg=ProjectionDiscoveryConfig(max_subset=1,min_train_support=64,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=24)
        assert m.discover_epistemic_projection_candidates(g_rows[:96],g_rows[96:],one_cfg)==[]
        g,_=discover_exact(m,g_rows,(4,5),2); assert g.validation_accuracy==1.0 and g.lift>=.49

        hold=external_holdout_g(g,pa,pb,pd,pf,c,e); assert len(hold)==64
        grec=qualify_candidate(m,g,'P-MS1988-G','DEPTH4_COMPOSITION_HOLDOUT',hold)
        assert [x[0] for x in grec.source_projection_epochs]==['P-MS1988-A','P-MS1988-B','P-MS1988-C','P-MS1988-D','P-MS1988-E','P-MS1988-F']
        assert m.epistemic_projections.is_current('P-MS1988-G',grec.epoch)

        m.epistemic_projections.change('P-MS1988-E',new_signature_sha256='e'*64)
        g_after=m.epistemic_projections.records['P-MS1988-G']
        assert not g_after.current and not m.epistemic_projections.is_current('P-MS1988-G',g_after.epoch)
        e_after=m.epistemic_projections.records['P-MS1988-E']; assert e_after.current
        m.epistemic_projections.change('P-MS1988-C',new_signature_sha256='c'*64)
        e_after_c=m.epistemic_projections.records['P-MS1988-E']
        assert not e_after_c.current and not m.epistemic_projections.is_current('P-MS1988-E',e_after_c.epoch)

        return {
            'status':'PASS',
            'shallow_source_projection_ids':list(shallow['source_projection_ids']),
            'shallow_E_rejection':'SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND',
            'shallow_G_candidates':0,
            'deep_source_projection_ids':list(deep['source_projection_ids']),
            'deep_recursive_depth':2,
            'single_source_G_candidates':0,
            'depth4_positions':list(g.input_positions),
            'validation_accuracy':g.validation_accuracy,'lift':g.lift,
            'external_holdout_count':len(hold),
            'C_source_projection_count':len(crec.source_projection_epochs),
            'E_source_projection_count':len(erec.source_projection_epochs),
            'G_source_projection_count':len(grec.source_projection_epochs),
            'E_change_staled_G':True,'C_change_staled_E':True,
            'earned':'THE_SAME_BOUNDED_SOURCE_LINEAGE_EVALUATOR_SUPPORTS_ONE_MORE_LEVEL_OF_OPAQUE_REPRESENTATION_COMPOSITION_WITHOUT_CORE_MECHANISM_CHANGE',
            'core_mechanism_change':'NO','new_projection_search_mechanism':'NO','new_representation_manager':'NO',
            'semantic_recursion_authority':'NONE','semantic_symbol_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:_close(m);world.close();td.cleanup()


def main(): print(json.dumps(run_ms1988(),indent=2,sort_keys=True,default=str))
if __name__=='__main__': main()
