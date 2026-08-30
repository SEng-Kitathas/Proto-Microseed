from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
from typing import Any
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
 Authority,CapabilityContract,EpisodeSchemaContract,EpistemicStatus,FeasibilityState,Microseed,Observation,
 OperationalFrameContract,QualificationState,QueryObligation,RecruitmentOption,RehearsalTransitionObservation,ValueVariableContract,
)
from scratch.ms2005_bounded_referent_probe_reconstruction import UNIQUE_A

class World:
    def __init__(self): self.index=0;self.value=0.0
    def reset(self): self.index=0;self.value=0.0
    def apply(self,action):
        expected=('P0','P1')[self.index]
        if action!=expected: raise AssertionError((action,expected,self.index))
        self.index+=1;self.value+=1.0
        return {'receipt':action}
    def observe(self):
        row=UNIQUE_A[self.index]
        return {'next_state_id':f's{self.index}','value_id':'V','observed_value':self.value,'raw_tokens':[str(x) for x in row]}

def act_ob():return QueryObligation('MS2009-ACT','effect',Authority.EFFECT,operational_scope_id='S')
def obs_ob():return QueryObligation('MS2009-OBS','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S')
def basis_ob():return QueryObligation('MS2009-BASIS','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S')

def build(root:Path,world:World)->Microseed:
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract('F','opaque probe frame','f'*64,Authority.DERIVED_READ_ONLY,('MS2009',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','reg',2.0,3.0,'v'*64,Authority.REFERENCE_ONLY,('MS2009',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    for cid in ('P0','P1'):
        m.register_capability(CapabilityContract(cid,'opaque probe prefix effect',{}, {'output':'receipt'},(),(),Authority.EFFECT,('MS2009',),'CURRENT',{},query_obligation_id='MS2009-ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS','raw observation',{}, {'output':'raw'},(),(),Authority.OBSERVATION_ONLY,('MS2009',),'CURRENT',{},query_obligation_id='MS2009-OBS',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','observation use basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS2009',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='MS2009-BASIS',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('P0','P1','OBS'):m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','opaque probe episode','e'*64,Authority.DERIVED_READ_ONLY,('MS2009',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m

def proposal(m:Microseed,cid,start,next_state):
    rows=tuple(RehearsalTransitionObservation(f'E-SEED-{cid}-{i}',start,cid,next_state,1.0,0,'F',0,'EP',0) for i in range(8))
    p=m.nominate_counterfactual_rehearsal(rows,(RecruitmentOption(cid,FeasibilityState.FEASIBLE,local_cost=.1),),start_state_id=start,value_id='V')
    assert p is not None,p;return p

def record_raw(m:Microseed,tag:str):
    r=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-RAW-'+tag,capture_id='RAW-'+tag,max_coordinates=8)
    assert r['status']=='BOUNDED_RAW_OBSERVATION_RECORDED',r;return r

def execute_step(m:Microseed,cid,proposal,tag):
    n=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob());assert n['status']=='ACTION_INTENT_NOMINATED',n
    x=m.execute_bounded_action(n['intent']['intent_id'],act_ob());assert x['status']=='ACTION_EXECUTED',x
    o=m.record_bounded_action_outcome_via_observation_basis(x['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id='E-OUT-'+tag,capture_id='CAP-'+tag)
    assert o['status']=='ACTION_OUTCOME_OBSERVED',o;return o

def derive_current_owned_probe_prefix(m:Microseed,*,max_steps:int=4)->dict[str,Any]:
    base={'semantic_coordinate_authority':'NONE','semantic_referent_authority':'NONE','truth_authority':'NONE','selection_authority':'NONE','execution_authority':'NONE'}
    depth=int(max_steps)
    if depth<0 or depth>8:raise ValueError('BOUNDED_CURRENT_PROBE_PREFIX_DEPTH_REQUIRED')
    cw=m.action_closure.current_state
    if cw is None:return {**base,'status':'DEFER_UNKNOWN','reason':'NO_CURRENT_OPAQUE_CONTROL_STATE'}
    current_frames={(fid,m.frames.epochs[fid]) for fid in m.frames.frames if m.frames.is_current(fid)}
    matches,rejections=m._current_bounded_raw_receipts_for_control_state(control_state_id=cw.state_id,control_state_evidence_id=cw.evidence_id,allowed_frames=current_frames)
    if len(matches)!=1:return {**base,'status':'DEFER_UNKNOWN','reason':'EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_PROBE_PREFIX_REQUIRED','matching_receipt_count':len(matches),'receipt_rejections':rejections}
    current_row,current_payload=matches[0]
    frame=(str(current_payload['frame_id']),int(current_payload['frame_epoch']))
    raw_rev=[tuple(str(x) for x in current_payload['raw_tokens'])];raw_eids=[str(current_row['evidence_id'])];actions_rev=[];execution_ids=[]
    cursor_state=cw.state_id;cursor_evidence=cw.evidence_id
    for lag in range(depth):
        predecessors=[o for o in m.action_closure.outcomes.values() if o.evidence_id==cursor_evidence]
        if not predecessors: break
        if len(predecessors)!=1:return {**base,'status':'DEFER_UNKNOWN','reason':'PROBE_PREFIX_PREDECESSOR_OUTCOME_NOT_UNIQUE','lag':lag,'count':len(predecessors)}
        out=predecessors[0]; projected=m.derive_admitted_opaque_transition_sample(out.execution_id)
        if projected.get('status')!='ADMITTED_OPAQUE_TRANSITION_SAMPLE':return {**base,'status':'DEFER_UNKNOWN','reason':'PROBE_PREFIX_PREDECESSOR_TRANSITION_NOT_ADMITTED','lag':lag}
        sample=projected['sample'];ex=m.action_closure.executions.get(out.execution_id);intent=None if ex is None else m.action_closure.intents.get(ex.intent_id)
        if ex is None or intent is None:return {**base,'status':'DEFER_UNKNOWN','reason':'PROBE_PREFIX_PREDECESSOR_ACTION_NOT_OWNED','lag':lag}
        if sample.end_token!=cursor_state or (sample.frame_id,sample.frame_epoch)!=frame:return {**base,'status':'DEFER_UNKNOWN','reason':'PROBE_PREFIX_PREDECESSOR_STATE_OR_FRAME_MISMATCH','lag':lag}
        pmatches,prej=m._current_bounded_raw_receipts_for_control_state(control_state_id=intent.start_state_id,control_state_evidence_id=intent.control_state_evidence_id,allowed_frames={frame})
        if len(pmatches)!=1:return {**base,'status':'DEFER_UNKNOWN','reason':'EXACT_SINGLE_PREDECESSOR_RAW_OBSERVATION_FOR_PROBE_PREFIX_REQUIRED','lag':lag,'matching_receipt_count':len(pmatches),'receipt_rejections':prej}
        prow,ppayload=pmatches[0]
        actions_rev.append(str(ex.capability_id));execution_ids.append(str(ex.execution_id));raw_rev.append(tuple(str(x) for x in ppayload['raw_tokens']));raw_eids.append(str(prow['evidence_id']))
        cursor_state=intent.start_state_id;cursor_evidence=intent.control_state_evidence_id
    if len(raw_rev)>1:
        episodes=[(eid,m.episodes.epochs[eid]) for eid,s in m.episodes.schemas.items() if m.episodes.is_current(eid) and frame in tuple(s.frame_epochs)]
        if len(episodes)!=1:return {**base,'status':'DEFER_UNKNOWN','reason':'EXACT_SINGLE_CURRENT_EPISODE_FOR_PROBE_PREFIX_REQUIRED','episode_matches':episodes}
    return {**base,'status':'CURRENT_OWNED_OPAQUE_PROBE_PREFIX','raw_samples':tuple(reversed(raw_rev)),'opaque_action_sequence':tuple(reversed(actions_rev)),'raw_observation_evidence_ids':tuple(reversed(raw_eids)),'execution_ids':tuple(reversed(execution_ids)),'frame_epoch':frame,'step_count':len(actions_rev),'depth_ceiling':depth,'history_basis':'AUTHENTICATED_CURRENT_RAW_RECEIPTS_PLUS_ACTION_OUTCOME_PREDECESSOR_CHAIN'}

def produce_prefix(root:Path,world:World):
    m=build(root,world);world.reset();m.observe_value_state('V',0.0);m.observe_opaque_control_state(Observation('C0','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS0');record_raw(m,'0')
    p0=proposal(m,'P0','s0','s1');execute_step(m,'P0',p0,'0');record_raw(m,'1')
    p1=proposal(m,'P1','s1','s2');execute_step(m,'P1',p1,'1');record_raw(m,'2')
    return m

def run_ms2009()->dict[str,Any]:
    td=tempfile.TemporaryDirectory(prefix='ms2009-prefix-');root=Path(td.name);world=World();m=produce_prefix(root,world)
    try:
        first=derive_current_owned_probe_prefix(m,max_steps=2);assert first['status']=='CURRENT_OWNED_OPAQUE_PROBE_PREFIX',first
        assert first['opaque_action_sequence']==('P0','P1'),first
        assert first['raw_samples']==tuple(tuple(str(x) for x in row) for row in UNIQUE_A[:3]),first
    finally:
        m.biography.close();m.evidence.conn.close();m.store.conn.close()
    # Reattach exact runtime contracts; durable raw/action/outcome history must recover.
    world2=World();world2.index=2;world2.value=2.0;m2=build(root,world2)
    try:
        recovered=derive_current_owned_probe_prefix(m2,max_steps=2);assert recovered['status']=='CURRENT_OWNED_OPAQUE_PROBE_PREFIX',recovered
        assert recovered['raw_samples']==first['raw_samples'] and recovered['opaque_action_sequence']==first['opaque_action_sequence']
        # Duplicate current receipt: no arbitrary winner.
        dup=m2.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-RAW-DUP',capture_id='RAW-DUP',max_coordinates=8);assert dup['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        ambiguous=derive_current_owned_probe_prefix(m2,max_steps=2);assert ambiguous['status']=='DEFER_UNKNOWN' and ambiguous['reason']=='EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_PROBE_PREFIX_REQUIRED',ambiguous
    finally:m2.biography.close();m2.evidence.conn.close();m2.store.conn.close()
    # Separate replay for frame-drift hostile.
    world3=World();world3.index=2;world3.value=2.0;m3=build(root,world3)
    try:
        # duplicate durable receipt is still present from previous hostile, so establish drift diagnostic via rejection set.
        m3.frames.change('F',reason='MS2009-FRAME-DRIFT')
        drift=derive_current_owned_probe_prefix(m3,max_steps=2);assert drift['status']=='DEFER_UNKNOWN',drift
        reasons={reason for _,reason in drift.get('receipt_rejections',())};assert 'RAW_OBSERVATION_FRAME_NOT_CURRENT' in reasons,drift
    finally:m3.biography.close();m3.evidence.conn.close();m3.store.conn.close();td.cleanup()
    return {'status':'PASS','raw_samples':[list(x) for x in first['raw_samples']],'opaque_action_sequence':list(first['opaque_action_sequence']),'restart_reconstruction':'PASS','duplicate_receipt':'DEFER_UNKNOWN','frame_drift':'DEFER_UNKNOWN','caller_supplied_raw_trace':'NO','caller_supplied_action_sequence':'NO','history_basis':first['history_basis'],'truth_authority':'NONE','selection_authority':'NONE','execution_authority':'NONE'}

def main():print(json.dumps(run_ms2009(),indent=2,sort_keys=True))
if __name__=='__main__':main()
