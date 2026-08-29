from __future__ import annotations

import json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, EpistemicStatus, ExternalProjectionQualifier, Observation,
    ProjectionDiscoveryConfig, RecruitmentOption, RehearsalTransitionObservation,
    FeasibilityState,
)
from scratch.ms1977_raw_coordinate_projection_boundary import act_ob, basis_ob, build, obs_ob
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'raw_coordinate_parity3_world_server.py'
TRIPLES=tuple(tuple(str((n>>shift)&1) for shift in (2,1,0)) for n in range(8))


class World:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT)); assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        row=json.loads(line); assert row.get('status')=='OK',row; return row
    def reset(self,triple): self.call('reset',raw_tokens=list(triple))
    def apply(self,a): return self.call('apply',action_id=a)
    def observe(self):
        row=self.call('observe'); row.pop('status',None); return row
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)


def external_seed(triple,n=12):
    w=World()
    try:
        w.reset(triple); before=w.observe(); w.apply('B'); after=w.observe()
        effect=float(after['observed_value'])-float(before['observed_value'])
        tag=''.join(triple)
        return tuple(RehearsalTransitionObservation(f'S3-{tag}-{i}','ALIAS','B',after['next_state_id'],effect,0,'F',0,'EP',0) for i in range(n))
    finally:w.close()


def proposals(m):
    out={}
    for triple in TRIPLES:
        p=m.nominate_counterfactual_rehearsal(
            external_seed(triple),
            (RecruitmentOption('B',FeasibilityState.FEASIBLE,local_cost=.1),),
            start_state_id='ALIAS',value_id='V'
        )
        assert p is not None and p.sequence==('B',),p
        out[triple]=p
    return out


def execute_owned(m,w,triple,proposal,index):
    w.reset(triple); m.observe_value_state('V',0.0)
    state_eid=f'E3-STATE-{index}'
    m.observe_opaque_control_state(Observation(f'C3-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id=state_eid)
    raw=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E3-RAW-{index}',capture_id=f'RAW3-{index}',max_coordinates=3)
    assert raw['status']=='BOUNDED_RAW_OBSERVATION_RECORDED',raw
    assert raw['control_state_evidence_id']==state_eid and raw['coordinate_count']==3
    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED',ex
    out=m.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E3-OUT-{index}',capture_id=f'CAP3-{index}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out


def external_holdout(candidate):
    pred={(b,a):e for b,a,e in candidate.bucket_action_prediction}; rows=[]
    for triple in TRIPLES:
        for _ in range(2):
            w=World()
            try:w.reset(triple); w.apply('B'); end=w.observe()['next_state_id']
            finally:w.close()
            bucket=candidate.project(triple); assert bucket is not None and pred[(bucket,'B')]==end
            rows.append({'raw_tokens':triple,'bucket':bucket,'actual_end':end})
    return rows


def run_ms1980():
    td=tempfile.TemporaryDirectory(prefix='ms1980-parity3-'); w=World(); m=build(Path(td.name),w)
    try:
        ps=proposals(m)
        for i in range(64):
            triple=TRIPLES[i%8]; execute_owned(m,w,triple,ps[triple],i)
        owned=m.derive_admitted_projection_samples_from_owned_raw_observations()
        assert owned['status']=='ADMITTED_OWNED_RAW_PROJECTION_SAMPLES',owned
        assert owned['sample_count']==64
        assert not owned['receipt_rejections'] and not owned['sample_rejections']
        samples=tuple(owned['samples']); assert {x.raw_tokens for x in samples}==set(TRIPLES)
        training=tuple(samples[:40]); validation=tuple(samples[40:])

        cfg2=ProjectionDiscoveryConfig(max_subset=2,min_train_support=32,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        found2=m.discover_epistemic_projection_candidates(training,validation,cfg2)
        assert found2==[],found2

        cfg3=ProjectionDiscoveryConfig(max_subset=3,min_train_support=32,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        found3=m.discover_epistemic_projection_candidates(training,validation,cfg3); assert found3,found3
        candidates=[m.epistemic_projection_candidates[x['candidate_id']] for x in found3]
        exact=[c for c in candidates if c.input_positions==(0,1,2)]
        assert len(exact)==1,[(c.input_positions,c.validation_accuracy,c.lift) for c in candidates]
        c=exact[0]; assert c.validation_accuracy==1.0 and c.lift>=.49

        holdout=external_holdout(c)
        qe=m.append_evidence('Q-MS1980-EXTERNAL-HOLDOUT',{'kind':'OWNED_RAW_PARITY3_HOLDOUT','candidate_sha256':c.digest(),'rows':holdout},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-PROCESS-MS1980-QUALIFIER')
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-PROCESS-MS1980').qualify(c,qualification_evidence=(qe,))
        rec=m.admit_epistemic_projection_candidate(ticket,projection_id='P-MS1980'); assert rec.current
        return {
            'status':'PASS','owned_sample_count':owned['sample_count'],
            'max_subset_2_candidates':0,'input_positions':list(c.input_positions),
            'validation_accuracy':c.validation_accuracy,'lift':c.lift,
            'external_holdout_count':len(holdout),
            'earned':'OWNED_BOUNDED_RAW_OBSERVATION_BRIDGE_AND_EXISTING_PROJECTION_SEARCH_COMPOSE_TO_THREE_COORDINATE_SUPPORT_WHEN_ALL_LOWER_ARITY_SUBSETS_ARE_INSUFFICIENT',
            'new_projection_search_mechanism_added':'NO',
            'support_ceiling_authority':'SUPPLIED_BOUNDED_SEARCH_GRAMMAR',
            'semantic_coordinate_authority':'NONE','semantic_projection_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:_close(m);w.close();td.cleanup()


def main(): print(json.dumps(run_ms1980(),indent=2,sort_keys=True,default=str))
if __name__=='__main__': main()
