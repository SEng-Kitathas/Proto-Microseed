from __future__ import annotations
import json, tempfile
from pathlib import Path
from microseed import Authority, CapabilityContract, EpistemicStatus, Microseed, Observation, OperationalFrameContract, QualificationState, QueryObligation
from microseed.development.epistemic_program import begin_epistemic_program_trial
from microseed.development.relational_algebra import OpaqueTransitionSample, discover_opaque_action_composition_candidates


def cand():
 r=(OpaqueTransitionSample('a0','o1','s0','A','m0','F',0),OpaqueTransitionSample('b0','o2','m0','B','e0','F',0),OpaqueTransitionSample('c0','o3','s0','C','e0','F',0),OpaqueTransitionSample('a1','o4','s1','A','m1','F',0),OpaqueTransitionSample('b1','o5','m1','B','e1','F',0),OpaqueTransitionSample('c1','o6','s1','C','e1','F',0))
 return [x for x in discover_opaque_action_composition_candidates(r,min_positive_support=2) if (x.direct_action_token,x.first_action_token,x.second_action_token)==('C','A','B')][0]

def run():
 td=tempfile.TemporaryDirectory(prefix='ms1708-')
 try:
  m=Microseed(Path(td.name));calls=[];world={'state':'FEASIBLE'}
  for cid in ('A','B'):
   m.register_capability(CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1708',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:calls.append(_cid),operational_scope_id='S'))
  m.register_capability(CapabilityContract('FEAS-A','feas',{'target_capability_id':'A'},{},(),(),Authority.DERIVED_READ_ONLY,('MS1708',),'CURRENT',{},dependencies=('A',),query_obligation_id='QF',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'feasibility':world['state']},operational_scope_id='S'))
  m.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS1708',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
  m.observe_opaque_control_state(Observation('CS','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS')
  m.append_evidence('E-U',{'unknown':'x'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS1708')
  m.record_action_limited_unknown(deficit_id='D',question_key='QX',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U',missing_discriminator_signature_sha256='d'*64)
  ob=QueryObligation('Q','probe',required_authority=Authority.EFFECT,operational_scope_id='S');fb=QueryObligation('QF','feas',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='S')
  t=begin_epistemic_program_trial(cand(),deficit_id='D',discrimination_signature_sha256='d'*64,capabilities=m.capabilities,obligation=ob,current_frame_epochs=dict(m.frames.epochs),start_state_id='s0',start_state_evidence_id='E-CS')
  n=m.nominate_grounded_epistemic_program_step_intent(t,'FEAS-A',fb,ob)
  assert n['status']=='ACTION_INTENT_NOMINATED' and calls==[]
  out={'pass':'MS1708_PASS06','current_adapter_nominates_without_any_normative_priority_premise':True,'effect_calls':calls,
       'disposition':'NARROWED_NEGATIVE__ACTION_LIMITED_PLUS_CURRENT_FEASIBILITY_STILL_FALSE_NOMINATES_WITHOUT_DECISION_BEARING_NORMATIVE_PRESSURE',
       'scar':'ACTION_LIMITED_UNKNOWN + FEASIBLE_ROUTE != LAWFUL_EPISTEMIC_INITIATION'}
  Path(__file__).with_name('MS1708_PASS06_INITIATION_PRIORITY_GAP.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2))
 finally:td.cleanup()
if __name__=='__main__':run()
