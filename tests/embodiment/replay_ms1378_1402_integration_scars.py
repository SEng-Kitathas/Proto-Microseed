from pathlib import Path
import json,tempfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from microseed import *

def cap(cid,effect=False,handler=None):
 return CapabilityContract(cid,'opaque',{},{},(),(),Authority.EFFECT if effect else Authority.DERIVED_READ_ONLY,('MS1378-1402',),'CURRENT',{},query_obligation_id='ACT' if effect else None,qualification=QualificationState.SHADOW_QUALIFIED,handler=handler,operational_scope_id='SCOPE' if effect else None)
def setup(m):
 f=OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS878-902',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED);m.register_operational_frame(f)
 v=ValueVariableContract('V','opaque',2,3,'v'*64,Authority.DERIVED_READ_ONLY,('MS953-977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'));m.register_value_variable(v);m.observe_value_state('V',0)
 for cid in ('A','B','C'):m.register_capability(cap(cid,True,handler=lambda **_: {'receipt':'ok'}))
 e=EpisodeSchemaContract('E','opaque','e'*64,Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),));m.register_episode_schema(e)
 m.observe_opaque_control_state(Observation('CS','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS')
def rows():
 out=[];k=0
 for s,a,n,e in (('S0','A','SA',.8),('S0','B','S1',-.4),('S1','C','S2',2.6)):
  for _ in range(10):k+=1;out.append(RehearsalTransitionObservation(f'E{k}',s,a,n,e,0,'F',0,'E',0))
 return out
def opts():return tuple(RecruitmentOption(x,FeasibilityState.FEASIBLE) for x in ('A','B','C'))
def obl():return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='SCOPE')

def main():
 checks={}
 with tempfile.TemporaryDirectory() as td:
  m=Microseed(Path(td));setup(m)
  p=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V')
  checks['stepwise_prediction_ancestry_present']=p.predicted_state_path==('S0','S1','S2') and tuple(round(x,1) for x in p.predicted_step_value_effects)==(-.4,2.6)
  c=m.derive_bounded_action_commitment(p.proposal_id)
  checks['trch_yes_is_premise_licensing_only']=c.licenses_yes() and c.qualifier('execution_authority')=='NONE' and c.qualifier('truth_authority')=='NONE'
  ir=m.nominate_bounded_action_intent(p.proposal_id,obl()); checks['one_next_action_intent_only']=ir['status']=='ACTION_INTENT_NOMINATED' and ir['intent']['capability_id']=='B' and ir['execution_authority']=='NONE'
  er=m.execute_bounded_action(ir['intent']['intent_id'],obl()); eid=er['execution']['execution_id']
  checks['execution_authority_comes_from_effect_capability']=er['status']=='ACTION_EXECUTED' and er['execution']['authority']=='EFFECT'
  checks['handler_result_is_not_observation']=er['observation_recorded'] is False and m.action_closure.current_state.state_id=='S0' and m.values.latest['V'][1]==0
  out=m.record_bounded_action_outcome(eid,Observation('O1','EXT',f'action-execution:{eid}',{'next_state_id':'S1','value_id':'V','observed_value':-.4},authority=Authority.OBSERVATION_ONLY),evidence_id='EO1')
  checks['external_outcome_updates_reality']=out['status']=='ACTION_OUTCOME_OBSERVED' and m.action_closure.current_state.state_id=='S1' and m.values.latest['V'][1]==-.4
  checks['matching_prediction_is_commitment_not_truth']=out['outcome']['prediction_commitment']['commitment']=='YES' and ['truth_authority','NONE'] in out['outcome']['prediction_commitment']['qualifiers']
  checks['old_plan_cannot_open_loop_continue']=m.derive_bounded_action_commitment(p.proposal_id).applicability==TernaryCommitment.NO
  p2=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S1',value_id='V'); checks['fresh_redeliberation_selects_next_action']=p2.sequence==('C',)
  i2=m.nominate_bounded_action_intent(p2.proposal_id,obl()); e2=m.execute_bounded_action(i2['intent']['intent_id'],obl()); x=e2['execution']['execution_id'];m.record_bounded_action_outcome(x,Observation('O2','EXT',f'action-execution:{x}',{'next_state_id':'S2','value_id':'V','observed_value':2.2},authority=Authority.OBSERVATION_ONLY),evidence_id='EO2')
  checks['closed_loop_can_reach_viability']=m.value_pressure('V')['pressure_magnitude']==0
  checks['duplicate_outcome_rejected']=m.record_bounded_action_outcome(x,Observation('O3','EXT',f'action-execution:{x}',{'next_state_id':'S2','value_id':'V','observed_value':2.2},authority=Authority.OBSERVATION_ONLY),evidence_id='EO3')['reason']=='EXECUTION_ALREADY_HAS_OUTCOME'
  # separate wrong-model specimen
 with tempfile.TemporaryDirectory() as td:
  m=Microseed(Path(td));setup(m);p=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V');i=m.nominate_bounded_action_intent(p.proposal_id,obl());e=m.execute_bounded_action(i['intent']['intent_id'],obl());x=e['execution']['execution_id'];o=m.record_bounded_action_outcome(x,Observation('OW','EXT',f'action-execution:{x}',{'next_state_id':'BAD','value_id':'V','observed_value':-1.0},authority=Authority.OBSERVATION_ONLY),evidence_id='EW')
  checks['wrong_model_preserved_as_prediction_violation']=o['outcome']['prediction_commitment']['commitment']=='NO' and m.action_closure.current_state.state_id=='BAD'
  checks['wrong_model_does_not_auto_continue']=m.derive_bounded_action_commitment(p.proposal_id).applicability==TernaryCommitment.NO
  st=m.status();checks['ms1402_terminal_ms1403_untouched']=st['research_terminal_ms']>=1402 and st['integration_evidence_through_ms']>=1402 and st['next_ms']>=1403
  checks['no_general_policy_or_semantic_intention']=st['general_action_policy_authority']=='NONE' and st['semantic_intention_authority']=='NONE' and not hasattr(m,'execute_plan')
  # restart does not recreate handlers/qualified action access
  m2=Microseed(Path(td));checks['restart_history_not_execution_access']=m2.bounded_control_loop_status()['outcome_count']==1 and m2.derive_bounded_action_commitment(p.proposal_id).commitment==TernaryCommitment.UNKNOWN
 out={'checks':checks,'passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values())}
 Path(__file__).resolve().parents[2].joinpath('MS1378_1402_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2)); return 0 if out['all_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
