from __future__ import annotations

import json
import subprocess
import sys
import tempfile
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
SERVER=ROOT/'research'/'substrate_shadow'/'deep_representation_alias_world_server.py'


class DeepAliasWorld:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        row=json.loads(line); assert row.get('status')=='OK',row; return row
    def reset(self,context): self.call('reset',context=context)
    def apply(self,action): return self.call('apply',action_id=action)
    def observe(self):
        row=self.call('observe'); row.pop('status',None); return row
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)


def act_ob(): return QueryObligation('ACT','external process effect',Authority.EFFECT,operational_scope_id='S')
def obs_ob(): return QueryObligation('OBS-Q','external process observation',Authority.OBSERVATION_ONLY,operational_scope_id='S')
def basis_ob(): return QueryObligation('BASIS-Q','bounded observation use',Authority.DERIVED_READ_ONLY,operational_scope_id='S')


def build(root:Path,world:DeepAliasWorld):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract('F','deep alias frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1974',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','bounded regulatory coordinate',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1974',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')))
    m.observe_value_state('V',0.0)
    for cid in ('P1','P2','B'):
        m.register_capability(CapabilityContract(cid,'opaque process effect',{}, {'output':'opaque-receipt'},('WORLD_EFFECT != WORLD_MODEL',),(),Authority.EFFECT,('MS1974',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S',assistance_ancestry=('EXTERNAL_PROCESS_EFFECT_CAPABILITY',)))
    m.register_capability(CapabilityContract('OBS','process observation',{}, {'output':'opaque-state'},('OBSERVATION != TRUTH_AUTHORITY',),(),Authority.OBSERVATION_ONLY,('MS1974',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','bounded observation basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1974',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='S'))
    for cid in ('P1','P2','B','OBS'): m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','deep alias episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1974',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m


def external_sample(context,action):
    w=DeepAliasWorld()
    try:
        w.reset(context)
        if action in {'P2','B'}: w.apply('P1')
        if action=='B': w.apply('P2')
        before=w.observe(); w.apply(action); after=w.observe()
        return before,after
    finally:w.close()


def seed_rows(context,action,n=12):
    before,after=external_sample(context,action)
    effect=round(float(after['observed_value'])-float(before['observed_value']),3)
    return tuple(RehearsalTransitionObservation(f'SEED-{context}-{action}-{i}',str(before['next_state_id']),action,str(after['next_state_id']),effect,0,'F',0,'EP',0) for i in range(n))


def option(cid): return RecruitmentOption(cid,FeasibilityState.FEASIBLE,local_cost=0.1)


def prepare_proposals(m):
    out={}
    for context in ('s0','r'):
        for action,start in (('P1',context),('P2','s1'),('B','s2')):
            p=m.nominate_counterfactual_rehearsal(seed_rows(context,action),(option(action),),start_state_id=start,value_id='V')
            assert p is not None and p.sequence==(action,)
            out[(context,action)]=p
    return out


def execute_step(m,proposal,tag):
    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED',ex
    out=m.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-{tag}',capture_id=f'CAP-{tag}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    return out


def run_chain(m,world,proposals,context,index):
    world.reset(context);m.observe_value_state('V',0.0)
    m.observe_opaque_control_state(Observation(f'CTX-{context}-{index}','EXTERNAL-PROCESS','opaque-control',context,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-CTX-{context}-{index}')
    a=execute_step(m,proposals[(context,'P1')],f'{context}-{index}-P1'); assert a['outcome']['actual_next_state_id']=='s1'
    b=execute_step(m,proposals[(context,'P2')],f'{context}-{index}-P2'); assert b['outcome']['actual_next_state_id']=='s2'
    c=execute_step(m,proposals[(context,'B')],f'{context}-{index}-B'); expected='sx' if context=='s0' else 'sy'; assert c['outcome']['actual_next_state_id']==expected
    return {'context':context,'endpoint':expected,'b_execution_id':c['outcome']['execution_id']}


def supplied_constructor_rows(history,prefix):
    # This is deliberately harness-side. It exposes the exact assistance denominator:
    # ordered history slicing is not yet re-derived by an entity-owned bridge.
    rows=[]
    for i,row in enumerate(history):
        rows.append(ConstructorProjectionSample(
            sample_id=f'{prefix}-{i}',
            raw_history=(('s2',),('s1',),(row['context'],)),
            action_token='B',effect_token=row['endpoint'],operational_scope_id='S',
            frame_id='F',frame_epoch=0,episode_schema_id='EP',episode_schema_epoch=0,
        ))
    return tuple(rows)


def run_ms1974():
    td=tempfile.TemporaryDirectory(prefix='ms1974-deep-alias-');root=Path(td.name);world=DeepAliasWorld();m=build(root,world)
    try:
        proposals=prepare_proposals(m)
        history=[]
        for context in ('s0','r')*12:
            history.append(run_chain(m,world,proposals,context,len(history)))

        one=m.derive_admitted_one_step_visible_history_refinements()
        target=[c for c in one.get('refinements',()) if (c.start_token,c.action_token)==('s2','B')]
        assert not target,target

        # The existing constructor can solve the deeper alias once ordered history is supplied.
        train=supplied_constructor_rows(history[:12],'TRAIN')
        pressure=supplied_constructor_rows(history[12:18],'PRESS')
        validation=supplied_constructor_rows(history[18:24],'VALID')
        cfg=ConstructorGrowthConfig(max_support_ceiling=3,max_lag_ceiling=2,min_train_support=8,min_validation_accuracy=0.95,min_lift_over_action_baseline=0.40,min_scope_accuracy=0.95,max_candidates=4)
        found=m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg)
        assert found,found
        candidates=[m.epistemic_constructor_candidates[x['candidate_id']] for x in found]
        candidates=[c for c in candidates if c.lag_depth_used==2]
        assert candidates,candidates
        c=candidates[0]
        assert any(a.lag==2 for a in c.atoms),c.atoms
        assert c.validation_accuracy==1.0 and c.lift>=0.49

        q=m.append_evidence('Q-MS1974-CONSTRUCTOR',{'kind':'DEEP_ALIAS_CONSTRUCTOR_HOLDOUT','candidate_sha256':c.digest(),'validation_accuracy':c.validation_accuracy},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1974-CONSTRUCTOR-QUALIFIER')
        ticket=ExternalConstructorQualifier(m.evidence,qualifier_id='EXTERNAL-MS1974-CONSTRUCTOR').qualify(c,qualification_evidence=(q,))
        rec=m.admit_epistemic_constructor_candidate(ticket,projection_id='P-MS1974-SUPPLIED-HISTORY')
        assert rec.current

        return {
            'status':'BOUNDARY_CONFIRMED',
            'one_step_target_count':len(target),
            'constructor_candidate_id':c.candidate_id,
            'constructor_candidate_sha256':c.digest(),
            'atoms':[a.token() for a in c.atoms],
            'lag_depth_used':c.lag_depth_used,
            'validation_accuracy':c.validation_accuracy,
            'lift':c.lift,
            'projection':rec.serializable(),
            'earned':'EXISTING_BOUNDED_LAG2_CONSTRUCTOR_CAN_RESOLVE_A_PROCESS_BACKED_DEEP_ALIAS_WHEN_ORDERED_HISTORY_SLICES_ARE_SUPPLIED',
            'missing_owner':'ENTITY_OWNED_AUTHENTICATED_HISTORY_TO_CONSTRUCTOR_SAMPLE_DERIVATION',
            'new_constructor_mechanism_required':'NO',
            'history_slice_authority':'HARNESS_SUPPLIED_ASSISTANCE',
            'semantic_projection_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:
        _close(m);world.close();td.cleanup()


def main(): print(json.dumps(run_ms1974(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
