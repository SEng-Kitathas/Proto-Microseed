from pathlib import Path
import json,tempfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from microseed import *
from microseed.runtime.types import EvidenceRef
from microseed.development.action_learning import nominate_action_outcome_candidates


def cap():
 return CapabilityContract('A','opaque',{},{},(),(),Authority.EFFECT,('MS1403-1427',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'receipt':'A'},operational_scope_id='SCOPE')
def setup(m):
 m.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS878-902',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
 m.register_value_variable(ValueVariableContract('V','opaque',8,10,'v'*64,Authority.DERIVED_READ_ONLY,('MS953-977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')));m.observe_value_state('V',0)
 m.register_capability(cap());m.register_episode_schema(EpisodeSchemaContract('E','opaque','e'*64,Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
 m.observe_opaque_control_state(Observation('CS','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS')
def rows():return tuple(RehearsalTransitionObservation(f'P{i}','S0','A','SX',9.0,0,'F',0,'E',0) for i in range(10))
def opts():return (RecruitmentOption('A',FeasibilityState.FEASIBLE),)
def obl():return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='SCOPE')
def experience(m,p,i,ns='S1',post=1.5):
 if i:
  m.observe_value_state('V',0);m.observe_opaque_control_state(Observation(f'R{i}','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-R{i}')
 ii=m.nominate_bounded_action_intent(p.proposal_id,obl());ex=m.execute_bounded_action(ii['intent']['intent_id'],obl());eid=ex['execution']['execution_id']
 return m.record_bounded_action_outcome(eid,Observation(f'O{i}','EXT',f'action-execution:{eid}',{'next_state_id':ns,'value_id':'V','observed_value':post},authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-O{i}')
def holdout(m,c,n=20,ns='S1',eff=1.5,prefix='H'):
 out=[];base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs]}
 for i in range(n):out.append(m.append_evidence(f'{prefix}{i}',{**base,'actual_next_state_id':ns,'actual_value_effect':eff,'i':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT'))
 return tuple(out)

def main():
 checks={}
 with tempfile.TemporaryDirectory() as td:
  m=Microseed(Path(td));setup(m);p=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V');outs=[experience(m,p,i) for i in range(12)]
  c=m.nominate_action_outcome_predictive_candidates()[0]
  checks['failed_intention_can_be_successful_learning_event']=all(o['outcome']['prediction_commitment']['commitment']=='NO' for o in outs) and c.next_state_id=='S1' and c.value_effect==1.5
  ev=m.evidence.get(outs[0]['outcome']['evidence_id'])['payload'];checks['intent_is_provenance_not_learning_label']=ev['intended_next_state_id']=='SX' and ev['next_state_id']=='S1' and c.next_state_id!='SX'
  checks['one_outcome_not_law']=nominate_action_outcome_candidates(m._action_outcome_experiences()[:1])==()
  checks['passive_cooccurrence_not_action_consequence']=not hasattr(m,'nominate_action_law_from_passive_observation')
  checks['candidate_model_output_only']=c.authority=='MODEL_OUTPUT_ONLY' and c.truth_authority==c.causal_theorem_authority==c.qualification_authority=='NONE'
  refs=holdout(m,c);t=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=refs)
  checks['independent_holdout_qualification']=t.state==QualificationState.SHADOW_QUALIFIED and t.holdout_accuracy==1.0
  fake=[EvidenceRef(e,m.evidence.get(e)['sha256'],EpistemicStatus.PRESSURE_SUPPORTED,False) for e in c.source_evidence_ids]
  bad=ActionOutcomeRelationQualificationTicket(c.candidate_id,c.digest(),QualificationState.SHADOW_QUALIFIED,'HSP-EXTERNAL','fake',tuple(fake),len(fake),1.0)
  checks['proposal_evidence_not_qualification_evidence']=m.qualify_action_outcome_predictive_relation(bad)['reason']=='PROPOSAL_QUALIFICATION_EVIDENCE_OVERLAP'
  m.observe_value_state('V',0);m.observe_opaque_control_state(Observation('RESET','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-RESET')
  checks['proposal_only_candidate_not_rehearsal_relation']=m.nominate_counterfactual_rehearsal((),opts(),start_state_id='S0',value_id='V') is None
  q=m.qualify_action_outcome_predictive_relation(t);rid=q['relation']['relation_id'];checks['qualified_relation_is_predictive_not_causal_theorem']=q['status']=='CURRENT_PREDICTIVE_RELATION' and q['truth_authority']=='NONE' and q['causal_theorem_authority']=='NONE'
  rp=m.nominate_counterfactual_rehearsal((),opts(),start_state_id='S0',value_id='V');checks['qualified_relation_reenters_bounded_rehearsal']=rp is not None and rp.predicted_state_path==('S0','S1')
  m.change_capability_dependency('A',reason='DRIFT');checks['drift_stales_current_use_without_erasing_history']=m.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION' and rid in m.action_outcome_learning.relations
  m2=Microseed(Path(td));checks['restart_preserves_history_not_current_runtime_contracts']=rid in m2.action_outcome_learning.relations and m2.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION'
 with tempfile.TemporaryDirectory() as td:
  m=Microseed(Path(td));setup(m);p=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V');[experience(m,p,i,'S1' if i%2==0 else 'S2',1.0 if i%2==0 else -1.0) for i in range(12)]
  checks['hidden_context_mixture_abstains_without_partition']=m.nominate_action_outcome_predictive_candidates()==()
 with tempfile.TemporaryDirectory() as td:
  m=Microseed(Path(td));setup(m);p=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V');[experience(m,p,i) for i in range(12)];c=m.nominate_action_outcome_predictive_candidates()[0]
  decoy=ActionOutcomePredictiveCandidate('DECOY',c.start_state_id,c.capability_id,'SX',9.0,c.support,1.0,c.source_evidence_ids,c.capability_epoch,c.frame_epochs,c.episode_schema_epochs,c.value_epoch,c.topology_epochs,c.coordination_epochs)
  dt=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(decoy,qualification_evidence=holdout(m,decoy,20,'S1',1.5,'D'))
  checks['intention_decoy_rejected_by_reality']=dt.state==QualificationState.REJECTED and dt.holdout_accuracy==0.0
  st=m.status();checks['ms1427_terminal_ms1428_untouched']=st['research_terminal_ms']>=1427 and st['integration_evidence_through_ms']>=1427 and st['next_ms']>=1428 and st['next_started'] is False
  checks['no_general_causal_learner_or_auto_model_switch']=m.action_outcome_learning_status()['general_causal_learner_authority']=='NONE' and not hasattr(m,'rewrite_world_model_from_prediction_error') and not hasattr(m,'auto_switch_predictive_relation')
 out={'checks':checks,'passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values())}
 Path(__file__).resolve().parents[2].joinpath('MS1403_1427_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
