from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus,
    ExternalProjectionQualifier, FeasibilityState, Microseed, Observation,
    OperationalFrameContract, QualificationState, QueryObligation, RecruitmentOption,
    RehearsalTransitionObservation, ValueVariableContract,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'representation_alias_world_server.py'


class AliasWorld:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n');self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        r=json.loads(line); assert r.get('status')=='OK',r; return r
    def reset(self,context): self.call('reset',context=context)
    def apply(self,action): return self.call('apply',action_id=action)
    def observe(self):
        r=self.call('observe'); r.pop('status',None); return r
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)


def act_ob(): return QueryObligation('ACT','external process effect',Authority.EFFECT,operational_scope_id='S')
def obs_ob(): return QueryObligation('OBS-Q','external process observation',Authority.OBSERVATION_ONLY,operational_scope_id='S')
def basis_ob(): return QueryObligation('BASIS-Q','bounded observation use',Authority.DERIVED_READ_ONLY,operational_scope_id='S')


def build(root: Path, world: AliasWorld):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract('F','process-backed alias frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1972',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','bounded regulatory coordinate',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1972',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')))
    m.observe_value_state('V',0.0)
    for cid in ('PREP','B'):
        m.register_capability(CapabilityContract(cid,'opaque process effect',{}, {'output':'opaque-receipt'},('WORLD_EFFECT != WORLD_MODEL',),(),Authority.EFFECT,('MS1972',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S',assistance_ancestry=('EXTERNAL_PROCESS_EFFECT_CAPABILITY',)))
    m.register_capability(CapabilityContract('OBS','process observation',{}, {'output':'opaque-state'},('OBSERVATION != TRUTH_AUTHORITY',),(),Authority.OBSERVATION_ONLY,('MS1972',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','bounded observation basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1972',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='S'))
    for cid in ('PREP','B','OBS'): m.frames.bind_capability('F',cid)
    m.register_episode_schema(EpisodeSchemaContract('EP','alias episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1972',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    return m


def external_sample(context, action):
    w=AliasWorld()
    try:
        w.reset(context)
        if action=='B': w.apply('PREP')
        before=w.observe(); w.apply(action); after=w.observe()
        return before,after
    finally:w.close()


def seed_rows(context,action,n=12):
    before,after=external_sample(context,action)
    effect=round(float(after['observed_value'])-float(before['observed_value']),3)
    return tuple(RehearsalTransitionObservation(f'SEED-{context}-{action}-{i}',str(before['next_state_id']),action,str(after['next_state_id']),effect,0,'F',0,'EP',0) for i in range(n))


def option(cid): return RecruitmentOption(cid,FeasibilityState.FEASIBLE,local_cost=0.1)


def execute_step(m, proposal, tag):
    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED',ex
    out=m.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-{tag}',capture_id=f'CAP-{tag}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    return out


def prepare_proposals(m):
    proposals={}
    for context in ('s0','r'):
        p=m.nominate_counterfactual_rehearsal(seed_rows(context,'PREP'),(option('PREP'),),start_state_id=context,value_id='V')
        assert p is not None and p.sequence==('PREP',)
        proposals[(context,'PREP')]=p
        b=m.nominate_counterfactual_rehearsal(seed_rows(context,'B'),(option('B'),),start_state_id='s1',value_id='V')
        assert b is not None and b.sequence==('B',)
        proposals[(context,'B')]=b
    return proposals


def run_chain(m,world,proposals,context,index):
    world.reset(context)
    m.observe_value_state('V',0.0)
    start=world.observe()
    m.observe_opaque_control_state(Observation(f'CTX-{context}-{index}','EXTERNAL-PROCESS','opaque-control',context,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-CTX-{context}-{index}')
    prep=execute_step(m,proposals[(context,'PREP')],f'{context}-{index}-PREP')
    assert prep['outcome']['actual_next_state_id']=='s1' and prep['outcome']['observed_value']==1.0
    bout=execute_step(m,proposals[(context,'B')],f'{context}-{index}-B')
    expected='sx' if context=='s0' else 's2'
    assert bout['outcome']['actual_next_state_id']==expected and bout['outcome']['observed_value']==2.2
    return {'context':context,'prep_evidence':prep['outcome']['evidence_id'],'b_evidence':bout['outcome']['evidence_id'],'endpoint':expected}


def external_holdout(candidate):
    rows=[]
    for context in ('s0','r'):
        for i in range(4):
            before,after=external_sample(context,'B')
            rows.append({'context':context,'start':before['next_state_id'],'end':after['next_state_id'],'effect':round(after['observed_value']-before['observed_value'],3)})
    expected={('s0','sx'),('r','s2')}
    observed={(r['context'],r['end']) for r in rows}
    assert observed==expected
    return rows


def run_ms1972():
    td=tempfile.TemporaryDirectory(prefix='ms1972-proc-alias-'); root=Path(td.name); world=AliasWorld(); m=build(root,world)
    try:
        proposals=prepare_proposals(m)
        history=[]
        for context in ('s0','s0','r','r'):
            history.append(run_chain(m,world,proposals,context,len(history)))

        surface=m.derive_admitted_one_step_visible_history_refinements()
        assert surface['status']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENTS_FOUND',surface
        target=[c for c in surface['refinements'] if (c.start_token,c.action_token)==('s1','B')]
        assert len(target)==1,target
        c=target[0]
        assert set(c.context_outcomes)=={('s0','sx',2),('r','s2',2)}

        heldout=external_holdout(c)
        qe=m.append_evidence('Q-MS1972-EXTERNAL-HOLDOUT',{'kind':'PROCESS_ALIAS_REFINEMENT_HOLDOUT','candidate_sha256':c.digest(),'rows':heldout},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-PROCESS-MS1972-QUALIFIER')
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-PROCESS-MS1972').qualify(c,qualification_evidence=(qe,))
        rec=m.admit_one_step_visible_history_refinement_projection(ticket,projection_id='P-MS1972')
        assert rec.current and rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'

        # Restart is intentionally not claimed here; MS1973 will pressure re-entry/currentness.
        return {
            'status':'PASS','history':history,
            'candidate_id':c.candidate_id,'candidate_sha256':c.digest(),'context_outcomes':c.context_outcomes,
            'projection':rec.serializable(),
            'heldout_rows':heldout,
            'live_world_pid':world.proc.pid,
            'earned':'PROCESS_BACKED_ACTUAL_ACTION_HISTORY_CAN_GROW_AND_EXTERNALLY_QUALIFY_A_GENERIC_OPAQUE_PREVIOUS_VISIBLE_STATE_REFINEMENT_WITHOUT_REVISIT_OR_SEMANTIC_CATEGORY',
            'history_acquisition_assistance':'EXTERNALLY_EQUIPPED_REHEARSAL_SEEDS_FROM_SEPARATE_PROCESS_PROBES',
            'truth_authority':'NONE','hidden_state_authority':'NONE','semantic_category_authority':'NONE','language_authority':'NONE',
        }
    finally:
        _close(m); world.close(); td.cleanup()


def main(): print(json.dumps(run_ms1972(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
