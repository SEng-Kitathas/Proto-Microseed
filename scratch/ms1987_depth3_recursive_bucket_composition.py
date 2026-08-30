from __future__ import annotations

import json, subprocess, sys, tempfile
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
SERVER=ROOT/'research'/'substrate_shadow'/'recursive_bucket_composition_world_server.py'
SEXTETS=tuple(tuple(str((n>>shift)&1) for shift in (5,4,3,2,1,0)) for n in range(64))


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
    m.register_operational_frame(OperationalFrameContract('F','recursive bucket composition frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1987',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','regulatory coordinate',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1987',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED)); m.observe_value_state('V',0.0)
    for aid in ('C','E'):
        m.register_capability(CapabilityContract(aid,f'opaque process effect {aid}',{}, {'output':'receipt'},(),(),Authority.EFFECT,('MS1987',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _aid=aid,**_:world.apply(_aid),operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS','raw observation',{}, {'output':'raw-state'},(),(),Authority.OBSERVATION_ONLY,('MS1987',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1987',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('C','E','OBS'): m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','recursive bucket composition episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1987',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m


def process_samples(action:str,repetitions:int=2):
    w=World(); rows=[]
    try:
        i=0
        for _ in range(repetitions):
            for raw in SEXTETS:
                w.reset(raw); out=w.apply(action)
                rows.append(ProjectionSample(f'{action}-SRC-{i}',raw,action,out['next_state_id'],'S','F',0)); i+=1
        return tuple(rows)
    finally:w.close()


def admit_source_projection(m,action,expected_positions,projection_id):
    rows=process_samples(action,2); train=rows[:96]; validation=rows[96:]
    cfg=ProjectionDiscoveryConfig(max_subset=2,min_train_support=64,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=16)
    found=m.discover_epistemic_projection_candidates(train,validation,cfg); assert found,found
    cs=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
    exact=[c for c in cs if c.input_positions==tuple(expected_positions)]
    assert len(exact)==1,[(c.input_positions,c.validation_accuracy,c.lift) for c in cs]
    c=exact[0]; assert c.validation_accuracy==1.0
    q=m.append_evidence(f'Q-{projection_id}',{'kind':'SOURCE_PROJECTION_HOLDOUT','candidate_sha256':c.digest(),'action':action},EpistemicStatus.PRESSURE_SUPPORTED,source=f'EXTERNAL-{projection_id}')
    ticket=ExternalProjectionQualifier(m.evidence,qualifier_id=f'EXTERNAL-{projection_id}').qualify(c,qualification_evidence=(q,))
    rec=m.admit_epistemic_projection_candidate(ticket,projection_id=projection_id); assert rec.current
    return c,rec


def seed_action(action:str,raw=SEXTETS[0],n=12):
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
    state_eid=f'E-MS1987-{action}-STATE-{index}'
    m.observe_opaque_control_state(Observation(f'C-MS1987-{action}-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id=state_eid)
    receipt=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-MS1987-{action}-RAW-{index}',capture_id=f'RAW-MS1987-{action}-{index}',max_coordinates=6)
    assert receipt['status']=='BOUNDED_RAW_OBSERVATION_RECORDED' and tuple(receipt['raw_tokens'])==raw
    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED',ex
    out=m.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-MS1987-{action}-OUT-{index}',capture_id=f'CAP-MS1987-{action}-{index}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    return out


def learn_owned_c(m,world,pa,pb):
    proposal=prepare_proposal(m,'C')
    for i in range(128): execute_owned(m,world,SEXTETS[i%64],proposal,'C',i)
    composed=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=3)
    assert composed['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',composed
    assert composed['source_projection_ids']==('P-MS1987-A','P-MS1987-B','P-MS1987-D')
    rows=tuple(x for x in composed['samples'] if x.action_token=='C'); assert len(rows)==128
    train=rows[:96]; validation=rows[96:]
    cfg1=ProjectionDiscoveryConfig(max_subset=1,min_train_support=64,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=12)
    assert m.discover_epistemic_projection_candidates(train,validation,cfg1)==[]
    cfg2=ProjectionDiscoveryConfig(max_subset=2,min_train_support=64,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=12)
    found=m.discover_epistemic_projection_candidates(train,validation,cfg2); assert found
    cs=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
    cands=[c for c in cs if c.input_positions==(0,1) and c.digest() not in {pa.digest(),pb.digest()}]
    assert cands,[(c.input_positions,c.validation_accuracy,c.lift) for c in cs]
    c=cands[-1]; assert c.validation_accuracy==1.0
    pred={(b,a):e for b,a,e in c.bucket_action_prediction}; hold=[]
    w=World()
    try:
        for raw in SEXTETS:
            w.reset(raw); actual=w.apply('C')['next_state_id']; source=(pa.project(raw),pb.project(raw),m.epistemic_projection_candidates[next(x for x in m.epistemic_projection_candidates if m.epistemic_projection_candidates[x].digest()==m.epistemic_projections.records['P-MS1987-D'].signature_sha256)].project(raw))
            bucket=c.project(source); assert bucket is not None and pred[(bucket,'C')]==actual
            hold.append({'raw':raw,'bucket':bucket,'actual':actual})
    finally:w.close()
    qe=m.append_evidence('Q-MS1987-C',{'kind':'DEPTH2_COMPOSITION_HOLDOUT','candidate_sha256':c.digest(),'rows':hold},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1987-C')
    ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1987-C').qualify(c,qualification_evidence=(qe,))
    rec=m.admit_epistemic_projection_candidate(ticket,projection_id='P-MS1987-C'); assert rec.current
    return c,rec


def _discover_e(m,rows,max_subset):
    cfg=ProjectionDiscoveryConfig(max_subset=max_subset,min_train_support=64,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=16)
    return m.discover_epistemic_projection_candidates(rows[:96],rows[96:],cfg)


def run_ms1987():
    td=tempfile.TemporaryDirectory(prefix='ms1987-depth3-'); world=World(); m=build(Path(td.name),world)
    try:
        pa,_=admit_source_projection(m,'A',(0,1),'P-MS1987-A')
        pb,_=admit_source_projection(m,'B',(2,3),'P-MS1987-B')
        pd,_=admit_source_projection(m,'D',(4,5),'P-MS1987-D')
        c,crec=learn_owned_c(m,world,pa,pb)
        assert m.epistemic_projections.is_current('P-MS1987-C',crec.epoch)

        proposal=prepare_proposal(m,'E')
        for i in range(128): execute_owned(m,world,SEXTETS[i%64],proposal,'E',1000+i)

        # Reproduce the pre-MS1987 boundary under an explicit zero-recursion ceiling.
        flat=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=4,max_projection_depth=0)
        assert flat['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',flat
        assert flat['source_projection_ids']==('P-MS1987-A','P-MS1987-B','P-MS1987-D')
        assert ('P-MS1987-C','SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND') in flat['source_rejections']
        flat_e=tuple(x for x in flat['samples'] if x.action_token=='E'); assert len(flat_e)==128
        assert _discover_e(m,flat_e,2)==[]

        # One recursive edge is enough to evaluate C from its admitted source lineage.
        composed=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=4,max_projection_depth=1)
        assert composed['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',composed
        assert composed['source_projection_ids']==('P-MS1987-A','P-MS1987-B','P-MS1987-C','P-MS1987-D')
        assert composed['source_rejections']==()
        e_rows=tuple(x for x in composed['samples'] if x.action_token=='E'); assert len(e_rows)==128
        assert _discover_e(m,e_rows,1)==[]
        found=_discover_e(m,e_rows,2); assert found
        cs=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
        exact=[x for x in cs if x.input_positions==(2,3)]
        assert len(exact)==1,[(x.input_positions,x.validation_accuracy,x.lift) for x in cs]
        e=exact[0]; assert e.validation_accuracy==1.0 and e.lift>=.49

        # If C's exact candidate content disappears, the bridge refuses C rather than guessing.
        c_key=next(k for k,v in m.epistemic_projection_candidates.items() if v.digest()==c.digest())
        saved=m.epistemic_projection_candidates.pop(c_key)
        missing=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=4,max_projection_depth=1)
        assert ('P-MS1987-C','SOURCE_PROJECTION_CONTENT_NOT_EXACTLY_RECOVERABLE') in missing['source_rejections']
        assert missing['source_projection_ids']==('P-MS1987-A','P-MS1987-B','P-MS1987-D')
        m.epistemic_projection_candidates[c_key]=saved

        pred={(b,a):effect for b,a,effect in e.bucket_action_prediction}; hold=[]
        w=World()
        try:
            for raw in SEXTETS:
                w.reset(raw); actual=w.apply('E')['next_state_id']
                ba=pa.project(raw); bb=pb.project(raw); bd=pd.project(raw); assert None not in (ba,bb,bd)
                bc=c.project((ba,bb,bd)); assert bc is not None
                vector=(ba,bb,bc,bd)
                bucket=e.project(vector); assert bucket is not None and pred[(bucket,'E')]==actual
                hold.append({'raw':raw,'source_buckets':vector,'bucket':bucket,'actual':actual})
        finally:w.close()
        qe=m.append_evidence('Q-MS1987-E',{'kind':'DEPTH3_COMPOSITION_HOLDOUT','candidate_sha256':e.digest(),'rows':hold},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1987-E')
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1987-E').qualify(e,qualification_evidence=(qe,))
        erec=m.admit_epistemic_projection_candidate(ticket,projection_id='P-MS1987-E'); assert erec.current
        assert [x[0] for x in erec.source_projection_epochs]==['P-MS1987-A','P-MS1987-B','P-MS1987-C','P-MS1987-D']
        assert m.epistemic_projections.is_current('P-MS1987-E',erec.epoch)

        # Direct dependent pressure: changing C must stale E.
        m.epistemic_projections.change('P-MS1987-C',new_signature_sha256='c'*64)
        e_after_c=m.epistemic_projections.records['P-MS1987-E']
        assert not e_after_c.current and not m.epistemic_projections.is_current('P-MS1987-E',e_after_c.epoch)

        # Upstream pressure: changing A must stale the current C generation.
        c_after_change=m.epistemic_projections.records['P-MS1987-C']; assert c_after_change.current
        m.epistemic_projections.change('P-MS1987-A',new_signature_sha256='a'*64)
        c_after_a=m.epistemic_projections.records['P-MS1987-C']
        assert not c_after_a.current and not m.epistemic_projections.is_current('P-MS1987-C',c_after_a.epoch)

        return {
            'status':'PASS',
            'flat_source_projection_ids':list(flat['source_projection_ids']),
            'flat_C_rejection':'SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND',
            'flat_depth3_candidates':0,
            'recursive_source_projection_ids':list(composed['source_projection_ids']),
            'recursive_depth':1,
            'single_source_candidates':0,
            'depth3_positions':list(e.input_positions),
            'validation_accuracy':e.validation_accuracy,'lift':e.lift,
            'external_holdout_count':len(hold),
            'C_source_projection_epochs':[list(x) for x in crec.source_projection_epochs],
            'E_source_projection_epochs':[list(x) for x in erec.source_projection_epochs],
            'missing_C_content_refused':True,
            'C_change_staled_E':True,
            'A_change_staled_C':True,
            'earned':'CURRENT_COMPOSED_OPAQUE_PROJECTIONS_CAN_BE_RECURSIVELY_EVALUATED_THROUGH_EXACT_SOURCE_LINEAGE_AND_REUSED_AS_INPUTS_TO_EXISTING_PROJECTION_SEARCH_AT_ONE_ADDITIONAL_DEPTH',
            'new_projection_search_mechanism_added':'NO',
            'new_representation_manager_added':'NO',
            'sample_persistence':'NONE',
            'semantic_recursion_authority':'NONE','semantic_symbol_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:_close(m);world.close();td.cleanup()


def main(): print(json.dumps(run_ms1987(),indent=2,sort_keys=True,default=str))
if __name__=='__main__': main()
