from __future__ import annotations
import json, hashlib, tempfile
from pathlib import Path
from microseed import (
    Authority, CapabilityContract, CounterfactualRehearsalConfig, EpisodeSchemaContract,
    FeasibilityState, Microseed, Observation, OperationalFrameContract, QualificationState,
    QueryObligation, RecruitmentOption, RehearsalTransitionObservation, ValueVariableContract,
)
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord, ActionOutcomeRecord

SCOPE='AFF-SCOPE'; OBL=QueryObligation('AFF-Q','bounded discriminating probe',required_authority=Authority.EFFECT,operational_scope_id=SCOPE)

def setup():
    td=tempfile.TemporaryDirectory(prefix='ms1679-ctrl-'); m=Microseed(Path(td.name)); calls=[]
    m.register_operational_frame(OperationalFrameContract('F','opaque-frame',hashlib.sha256(b'F').hexdigest(),Authority.DERIVED_READ_ONLY,('MS1679',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','opaque',2,3,hashlib.sha256(b'V').hexdigest(),Authority.DERIVED_READ_ONLY,('MS1679',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')))
    m.register_episode_schema(EpisodeSchemaContract('E','opaque-episode',hashlib.sha256(b'E').hexdigest(),Authority.DERIVED_READ_ONLY,('MS1679',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    for cid in ('A','B'):
        m.register_capability(CapabilityContract(cid,'opaque-primitive',{}, {},(),(),Authority.EFFECT,('MS1679',),'CURRENT',{},query_obligation_id='AFF-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid, **_: calls.append(_cid) or {'receipt':_cid},operational_scope_id=SCOPE))
    m.observe_value_state('V',0.0)
    m.observe_opaque_control_state(Observation('CTRL0','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='ECTRL0')
    rows=[]
    for i in range(8):
        rows.append(RehearsalTransitionObservation(f'A{i}','S0','A','S1',.5,0,'F',0,'E',0))
        rows.append(RehearsalTransitionObservation(f'B{i}','S1','B','S2',2.0,0,'F',0,'E',0))
    opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption('B',FeasibilityState.FEASIBLE,local_cost=.1))
    return td,m,calls,tuple(rows),opts

def run():
    td,m,calls,rows,opts=setup()
    try:
        p=m.nominate_counterfactual_rehearsal(rows,opts,start_state_id='S0',value_id='V',config=CounterfactualRehearsalConfig(max_horizon=2))
        assert p and p.sequence==('A','B')
        i1=m.nominate_bounded_action_intent(p.proposal_id,OBL); assert i1['status']=='ACTION_INTENT_NOMINATED'
        e1=m.execute_bounded_action(i1['intent']['intent_id'],OBL); assert e1['status']=='ACTION_EXECUTED'
        x1=e1['execution']['execution_id']
        o1=m.record_bounded_action_outcome(x1,Observation('O1','EXT',f'action-execution:{x1}',{'next_state_id':'S1','value_id':'V','observed_value':.5},authority=Authority.OBSERVATION_ONLY),evidence_id='EO1')
        assert o1['status']=='ACTION_OUTCOME_OBSERVED' and o1['requires_redeliberation']
        p2=m.nominate_counterfactual_rehearsal(rows,opts,start_state_id='S1',value_id='V',config=CounterfactualRehearsalConfig(max_horizon=2))
        assert p2 and p2.sequence==('B',)
        i2=m.nominate_bounded_action_intent(p2.proposal_id,OBL); e2=m.execute_bounded_action(i2['intent']['intent_id'],OBL); x2=e2['execution']['execution_id']
        o2=m.record_bounded_action_outcome(x2,Observation('O2','EXT',f'action-execution:{x2}',{'next_state_id':'S2','value_id':'V','observed_value':2.5},authority=Authority.OBSERVATION_ONLY),evidence_id='EO2')
        assert o2['status']=='ACTION_OUTCOME_OBSERVED' and calls==['A','B']
        # Native records bind each step to an action intent/proposal, not one epistemic macro trial/discrimination need.
        fields={
          'BoundedActionIntent':sorted(BoundedActionIntent.__dataclass_fields__),
          'ActionExecutionRecord':sorted(ActionExecutionRecord.__dataclass_fields__),
          'ActionOutcomeRecord':sorted(ActionOutcomeRecord.__dataclass_fields__),
        }
        for names in fields.values():
            assert 'program_trial_id' not in names and 'discrimination_need_id' not in names and 'macro_trial_id' not in names
        assert p.proposal_id != p2.proposal_id
        out={
          'MS1679_pass02':{
            'rehearsal_sequence':list(p.sequence),'first_action_only':i1['intent']['capability_id'],
            'requires_redeliberation_after_first_outcome':o1['requires_redeliberation'],
            'record_fields':fields,
            'disposition':'ORDINARY_CONTROL_IS_ONE_STEP_CLOSED_LOOP__NO_NATIVE_EPISTEMIC_PROGRAM_TRIAL_IDENTITY'
          },
          'MS1680_pass03':{
            'physical_handler_calls':calls,'first_proposal_id':p.proposal_id,'second_proposal_id':p2.proposal_id,
            'final_state':m.action_closure.current_state.state_id,'final_value':m.values.latest['V'][1],
            'disposition':'ORDINARY_CONTROL_CAN_REALIZE_PRIMITIVES_OVER_MULTIPLE_TICKS__HARNESS_CURRENTLY_OWNS_MACRO_CONTINUITY',
            'next_discriminator':'CAN_A_TINY_PROPOSAL_ONLY_PROGRAM_TRIAL_CARRIER_BIND_EXISTING_STEP_INTENT_EXECUTION_OUTCOME_RECORDS_WITHOUT_EXECUTING_ANYTHING_ITSELF'
          }
        }
        Path(__file__).with_name('MS1679_1680_PASS02_03_CONTROL_REALIZATION_AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True))
        print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__':run()
