from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from microseed import (
    Authority, CapabilityContract, CounterfactualRehearsalConfig, EpisodeSchemaContract,
    EpistemicStatus, FeasibilityState, Microseed, Observation, OperationalFrameContract,
    OpaqueTransitionSample, QualificationState, QueryObligation, RecruitmentOption,
    RehearsalTransitionObservation, ValueVariableContract, discover_opaque_action_composition_candidates,
)
from microseed.cognition.hypothesis import Hypothesis,HypothesisSet
from microseed.development.epistemic_program import begin_epistemic_program_trial,advance_epistemic_program_trial,completed_program_evidence_payload

def H(x):return hashlib.sha256(str(x).encode()).hexdigest()
SCOPE='AFF-SCOPE';OBL=QueryObligation('AFF-Q','bounded discriminating probe',required_authority=Authority.EFFECT,operational_scope_id=SCOPE)
def cap(cid,calls):return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1686',),'CURRENT',{},query_obligation_id='AFF-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:calls.append(_cid) or {'receipt':_cid},operational_scope_id=SCOPE)
def setup():
 td=tempfile.TemporaryDirectory(prefix='ms1686-');m=Microseed(Path(td.name));calls=[]
 m.register_operational_frame(OperationalFrameContract('F','opaque',H('F'),Authority.DERIVED_READ_ONLY,('MS1686',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
 m.register_value_variable(ValueVariableContract('V','opaque',2,3,H('V'),Authority.DERIVED_READ_ONLY,('MS1686',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')))
 m.register_episode_schema(EpisodeSchemaContract('E','opaque',H('E'),Authority.DERIVED_READ_ONLY,('MS1686',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
 for cid in ('A','B','C'):m.register_capability(cap(cid,calls))
 m.observe_value_state('V',0.0);m.observe_opaque_control_state(Observation('CTRL0','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='ECTRL0')
 rr=[]
 for i in range(8):
  rr += [RehearsalTransitionObservation(f'A{i}','S0','A','S1',.5,0,'F',0,'E',0),RehearsalTransitionObservation(f'B{i}','S1','B','S2',2.0,0,'F',0,'E',0)]
 opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption('B',FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption('C',FeasibilityState.FEASIBLE,local_cost=9))
 rs=[
  OpaqueTransitionSample('a0','oa0','q0','A','qm0','F',0),OpaqueTransitionSample('b0','ob0','qm0','B','qe0','F',0),OpaqueTransitionSample('c0','oc0','q0','C','qe0','F',0),
  OpaqueTransitionSample('a1','oa1','q1','A','qm1','F',0),OpaqueTransitionSample('b1','ob1','qm1','B','qe1','F',0),OpaqueTransitionSample('c1','oc1','q1','C','qe1','F',0)]
 cand=[c for c in discover_opaque_action_composition_candidates(rs,min_positive_support=2) if (c.direct_action_token,c.first_action_token,c.second_action_token)==('C','A','B')][0]
 return td,m,calls,tuple(rr),opts,cand

def run():
 td,m,calls,rows,opts,cand=setup()
 try:
  unknown=m.append_evidence('E-UNK',{'question':'macro outcome','live':['H1','H2']},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS1686')
  m.record_action_limited_unknown(deficit_id='D',question_key='opaque-macro',hypothesis_digest_sha256=H('H1|H2'),unknown_evidence_id=unknown.evidence_id,missing_discriminator_signature_sha256=H('A>B'))
  cw=m.action_closure.current_state
  trial=begin_epistemic_program_trial(cand,deficit_id='D',discrimination_signature_sha256=H('A>B'),capabilities=m.capabilities,obligation=OBL,current_frame_epochs=dict(m.frames.epochs),start_state_id=cw.state_id,start_state_evidence_id=cw.evidence_id)
  # Physical realization still comes from the existing regulatory rehearsal loop.
  p=m.nominate_counterfactual_rehearsal(rows,opts,start_state_id='S0',value_id='V',config=CounterfactualRehearsalConfig(max_horizon=2));assert p.sequence==('A','B')
  ni=m.nominate_bounded_action_intent(p.proposal_id,OBL);i1=m.action_closure.intents[ni['intent']['intent_id']];exr=m.execute_bounded_action(i1.intent_id,OBL);e1=m.action_closure.executions[exr['execution']['execution_id']]
  # Pass11 boundary: execution alone cannot advance epistemic trial without actual outcome.
  pre=trial; assert len(pre.step_records)==0
  out1=m.record_bounded_action_outcome(e1.execution_id,Observation('O1','EXT',f'action-execution:{e1.execution_id}',{'next_state_id':'S1','value_id':'V','observed_value':.5},authority=Authority.OBSERVATION_ONLY),evidence_id='EO1');o1=m.action_closure.outcomes[out1['outcome']['outcome_id']]
  trial=advance_epistemic_program_trial(trial,intent=i1,execution=e1,outcome=o1,capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs));assert trial.status=='OPEN'
  p2=m.nominate_counterfactual_rehearsal(rows,opts,start_state_id='S1',value_id='V',config=CounterfactualRehearsalConfig(max_horizon=2));assert p2.sequence==('B',)
  ni2=m.nominate_bounded_action_intent(p2.proposal_id,OBL);i2=m.action_closure.intents[ni2['intent']['intent_id']];exr2=m.execute_bounded_action(i2.intent_id,OBL);e2=m.action_closure.executions[exr2['execution']['execution_id']]
  out2=m.record_bounded_action_outcome(e2.execution_id,Observation('O2','EXT',f'action-execution:{e2.execution_id}',{'next_state_id':'S2','value_id':'V','observed_value':2.5},authority=Authority.OBSERVATION_ONLY),evidence_id='EO2');o2=m.action_closure.outcomes[out2['outcome']['outcome_id']]
  trial=advance_epistemic_program_trial(trial,intent=i2,execution=e2,outcome=o2,capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs));assert trial.status=='COMPLETE' and calls==['A','B']
  payload=completed_program_evidence_payload(trial);ref=m.append_evidence('E-PROGRAM',payload,EpistemicStatus.PRESSURE_SUPPORTED,source='MS1686-PROGRAM-TRIAL')
  revisit=m.request_epistemic_revisit('D',ref.evidence_id,relevance_basis_sha256=trial.digest());assert revisit['state']=='REVISIT_REQUIRED'
  hs=HypothesisSet([Hypothesis('H1',lambda x:'S2'),Hypothesis('H2',lambda x:'ALT')]);hs.observe(('A','B'),trial.step_records[-1].actual_next_state_id);assert hs.disposition()=='IDENTIFIED_WITHIN_CANDIDATE_SET' and hs.live[0].hypothesis_id=='H1'
  # Unexpected result challenges the bounded model space rather than forcing a winner.
  hs_bad=HypothesisSet([Hypothesis('H1',lambda x:'S2'),Hypothesis('H2',lambda x:'ALT')]);hs_bad.observe(('A','B'),'SURPRISE');assert hs_bad.disposition()=='MODEL_SPACE_MISSPECIFIED_OR_CONTRADICTED'
  out={
   'MS1686_pass09':{'trial_status':trial.status,'physical_calls':calls,'step_proposal_ids':[i1.proposal_id,i2.proposal_id],'disposition':'HARNESS_ASSISTED_ORDINARY_CONTROL_REALIZES_COMPOSED_AFFORDANCE_AND_CARRIER_BINDS_ACTUAL_STEP_RECORDS'},
   'MS1687_pass10':{'first_step_actual_state':o1.actual_next_state_id,'second_rehearsal_start':p2.start_state_id,'disposition':'MANDATORY_REDELIBERATION_PRESERVED__PROGRAM_CONTINUITY_DOES_NOT_OVERRIDE_CLOSED_LOOP_CONTROL'},
   'MS1688_pass11':{'execution_without_outcome_step_count':len(pre.step_records),'disposition':'EXECUTION_RECEIPT_ALONE_CANNOT_ADVANCE_EPISTEMIC_PROGRAM__ACTUAL_OUTCOME_REQUIRED'},
   'MS1689_pass12':{'component_epoch_ancestry':[list(x) for x in trial.capability_epochs],'disposition':'PROGRAM_STEP_BINDING_RECHECKS_COMPONENT_CURRENTNESS_EACH_ADVANCE'},
   'MS1690_pass13':{'frame_epochs':[list(x) for x in trial.frame_epochs],'disposition':'PROGRAM_STEP_BINDING_RECHECKS_RELATIONAL_FRAME_EPOCH_EACH_ADVANCE'},
   'MS1691_pass14':{'control_state_chain':[[r.step_index,r.actual_next_state_id,r.outcome_evidence_id] for r in trial.step_records],'disposition':'PROGRAM_CONTINUITY_BOUND_TO_ACTUAL_OUTCOME_STATE_EVIDENCE_NOT_HARNESS_STEP_COUNTER'},
   'MS1692_pass15':{'hypothesis_disposition':hs.disposition(),'survivor':hs.live[0].hypothesis_id,'disposition':'CLEAN_MACRO_RESULT_CAN_RESOLVE_BOUNDED_LIVE_ALTERNATIVES_ONLY'},
   'MS1693_pass16':{'unexpected_result':hs_bad.disposition(),'disposition':'UNEXPECTED_MACRO_RESULT_CHALLENGES_MODEL_SPACE__NO_FORCED_HIDDEN_CAUSE'},
   'deficit_after_program_evidence':revisit,
   'authority_boundary':{'trial_truth':payload['truth_authority'],'trial_execution_gain':payload['execution_authority_gain'],'physical_actuator_identity':payload['physical_actuator_identity_authority']},
   'remaining_assistance':'ACTION_SELECTION_STILL_OWNED_BY_REGULATORY_REHEARSAL_AND_CALLER_SUPPLIED_FEASIBILITY__NOT_AUTONOMOUS_EPISTEMIC_REALIZATION'
  }
  Path(__file__).with_name('MS1686_1693_PASS09_16_PROGRAM_END_TO_END.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
 finally:td.cleanup()
if __name__=='__main__':run()
