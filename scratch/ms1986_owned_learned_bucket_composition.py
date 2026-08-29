from __future__ import annotations

import json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus,
    ExternalProjectionQualifier, FeasibilityState, Microseed, Observation,
    OperationalFrameContract, ProjectionDiscoveryConfig, QualificationState,
    QueryObligation, RecruitmentOption, RehearsalTransitionObservation,
    ValueVariableContract,
)
from scratch.ms1985_two_learned_bucket_composition_boundary import (
    QUADS, admit_source_projection,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'owned_bucket_composition_world_server.py'


class World:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT)); assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        row=json.loads(line); assert row.get('status')=='OK',row; return row
    def reset(self,raw): self.call('reset',raw_tokens=list(raw))
    def apply(self,a): return self.call('apply',action_id=a)
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
    m.register_operational_frame(OperationalFrameContract('F','owned bucket composition frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1986',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','regulatory coordinate',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1986',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED)); m.observe_value_state('V',0.0)
    m.register_capability(CapabilityContract('Z','opaque process effect',{}, {'output':'receipt'},(),(),Authority.EFFECT,('MS1986',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.apply('Z'),operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS','raw observation',{}, {'output':'raw-state'},(),(),Authority.OBSERVATION_ONLY,('MS1986',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1986',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('Z','OBS'): m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','owned bucket composition episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1986',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m


def external_seed_z(raw,n=12):
    w=World()
    try:
        w.reset(raw); before=w.observe(); w.apply('Z'); after=w.observe(); effect=float(after['observed_value'])-float(before['observed_value'])
        tag=''.join(raw)
        return tuple(RehearsalTransitionObservation(f'Z-SEED-{tag}-{i}','ALIAS','Z',after['next_state_id'],effect,0,'F',0,'EP',0) for i in range(n))
    finally:w.close()


def prepare_z_proposals(m):
    out={}
    for raw in QUADS:
        p=m.nominate_counterfactual_rehearsal(external_seed_z(raw),(RecruitmentOption('Z',FeasibilityState.FEASIBLE,local_cost=.1),),start_state_id='ALIAS',value_id='V')
        assert p is not None and p.sequence==('Z',),p
        out[raw]=p
    return out


def execute_z(m,world,raw,proposal,index):
    world.reset(raw);m.observe_value_state('V',0.0)
    state_eid=f'E-MS1986-STATE-{index}'
    m.observe_opaque_control_state(Observation(f'C-MS1986-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id=state_eid)
    receipt=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-MS1986-RAW-{index}',capture_id=f'RAW-MS1986-{index}',max_coordinates=4)
    assert receipt['status']=='BOUNDED_RAW_OBSERVATION_RECORDED' and tuple(receipt['raw_tokens'])==raw
    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED',ex
    out=m.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-MS1986-OUT-{index}',capture_id=f'CAP-MS1986-{index}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    return out


def external_holdout(candidate,pa,pb):
    w=World(); rows=[];pred={(b,a):e for b,a,e in candidate.bucket_action_prediction}
    try:
        for raw in QUADS:
            w.reset(raw);w.apply('Z');end=w.observe()['next_state_id']
            source=(pa.project(raw),pb.project(raw)); assert None not in source
            bucket=candidate.project(source); assert bucket is not None and pred[(bucket,'Z')]==end
            rows.append({'raw':raw,'source_buckets':source,'bucket':bucket,'actual_end':end})
        return rows
    finally:w.close()


def run_ms1986():
    td=tempfile.TemporaryDirectory(prefix='ms1986-owned-bucket-compose-'); world=World(); m=build(Path(td.name),world)
    try:
        pa,_=admit_source_projection(m,'A',(0,1),'P-MS1986-A')
        pb,_=admit_source_projection(m,'B',(2,3),'P-MS1986-B')
        ps=prepare_z_proposals(m)
        for i in range(64):
            raw=QUADS[i%16]; execute_z(m,world,raw,ps[raw],i)

        composed=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=2)
        assert composed['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',composed
        assert composed['source_projection_ids']==('P-MS1986-A','P-MS1986-B')
        assert composed['source_projection_count']==2 and composed['sample_count']==64
        samples=tuple(composed['samples'])
        assert len({x.raw_tokens[0] for x in samples})==2 and len({x.raw_tokens[1] for x in samples})==2
        train=samples[:48];validation=samples[48:]

        cfg1=ProjectionDiscoveryConfig(max_subset=1,min_train_support=32,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        assert m.discover_epistemic_projection_candidates(train,validation,cfg1)==[]
        cfg2=ProjectionDiscoveryConfig(max_subset=2,min_train_support=32,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        found=m.discover_epistemic_projection_candidates(train,validation,cfg2); assert found
        cs=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
        exact=[c for c in cs if c.input_positions==(0,1) and c.digest() not in {pa.digest(),pb.digest()}]
        assert exact,[(c.input_positions,c.validation_accuracy,c.lift) for c in cs]
        c=exact[-1]; assert c.validation_accuracy==1.0 and c.lift>=.49
        holdout=external_holdout(c,pa,pb)
        qe=m.append_evidence('Q-MS1986-SECOND',{'kind':'OWNED_BUCKET_COMPOSITION_HOLDOUT','candidate_sha256':c.digest(),'rows':holdout},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1986-SECOND')
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1986-SECOND').qualify(c,qualification_evidence=(qe,))
        rec=m.admit_epistemic_projection_candidate(ticket,projection_id='P-MS1986-SECOND'); assert rec.current
        expected_source_lineage=tuple((pid,m.epistemic_projections.records[pid].epoch,m.epistemic_projections.records[pid].signature_sha256) for pid in ('P-MS1986-A','P-MS1986-B'))
        assert rec.source_projection_epochs==expected_source_lineage
        assert c.source_projection_epochs==expected_source_lineage
        return {
            'status':'PASS','source_projection_ids':list(composed['source_projection_ids']),
            'source_projection_count':composed['source_projection_count'],'owned_second_stage_sample_count':composed['sample_count'],
            'source_projection_epochs':[list(x) for x in rec.source_projection_epochs],
            'coordinate_order_basis':composed['coordinate_order_basis'],'composition_basis':composed['composition_basis'],
            'single_source_candidates':0,'second_stage_positions':list(c.input_positions),'validation_accuracy':c.validation_accuracy,'lift':c.lift,
            'external_holdout_count':len(holdout),'second_stage_projection_id':rec.projection_id,
            'earned':'CURRENT_EXACT_ADMITTED_RAW_PROJECTIONS_CAN_AUTOMATICALLY_SUPPLY_AN_OPAQUE_BUCKET_VECTOR_OVER_OWNED_ACTION_HISTORY_TO_FEED_EXISTING_SECOND_STAGE_PROJECTION_GROWTH',
            'new_projection_search_mechanism_added':'NO','sample_persistence':'NONE',
            'source_selection_authority':composed['source_selection_authority'],
            'semantic_symbol_authority':'NONE','semantic_composition_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:_close(m);world.close();td.cleanup()


def main():print(json.dumps(run_ms1986(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
