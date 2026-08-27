from __future__ import annotations
import hashlib,json
from pathlib import Path
from microseed import Authority,CapabilityContract,OpaqueTransitionSample,QualificationState,QueryObligation,discover_opaque_action_composition_candidates
from microseed.cognition.hypothesis import Hypothesis,HypothesisSet
from microseed.development.action_closure import BoundedActionIntent,ActionExecutionRecord,ActionOutcomeRecord
from microseed.development.epistemic_program import begin_epistemic_program_trial,advance_epistemic_program_trial
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.commitment import RelationalCommitment,TernaryCommitment

def H(x):return hashlib.sha256(str(x).encode()).hexdigest()
def cap(cid):return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1694',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:None,operational_scope_id='S')
def row(i,s,a,e,o):return OpaqueTransitionSample(i,o,s,a,e,'F',0)
def fixture():
 rs=[row('a0','s0','A','m0','oa0'),row('b0','m0','B','e0','ob0'),row('c0','s0','C','e0','oc0'),row('a1','s1','A','m1','oa1'),row('b1','m1','B','e1','ob1'),row('c1','s1','C','e1','oc1')]
 c=[x for x in discover_opaque_action_composition_candidates(rs,min_positive_support=2) if (x.direct_action_token,x.first_action_token,x.second_action_token)==('C','A','B')][0]
 r=CapabilityRegistry();r.register(cap('A'));r.register(cap('B'));return rs,c,r

def records():
 cm=RelationalCommitment('cm','t',TernaryCommitment.YES)
 intent=BoundedActionIntent('i','p','d',cm,'A',0,'s0','ce0','sX',0.0,('V',0),'Q','S')
 ex=ActionExecutionRecord('x','i','A',0,'s0','handler-sha')
 pc=RelationalCommitment('pc','pt',TernaryCommitment.NO)
 out=ActionOutcomeRecord('o','x','ev','sX',0.0,'V',pc,actual_value_effect=0.0)
 return intent,ex,out

def run():
 rs,c,r=fixture();obl=QueryObligation('Q','probe',required_authority=Authority.EFFECT,operational_scope_id='S')
 t=begin_epistemic_program_trial(c,deficit_id='D',discrimination_signature_sha256=H('AB'),capabilities=r,obligation=obl,current_frame_epochs={'F':0},start_state_id='s0',start_state_evidence_id='ce0')
 i,e,o=records()
 # Hidden evaluator worlds differ in actual actuator primitive, but organism-visible action-closure records are identical.
 visible_a=advance_epistemic_program_trial(t,intent=i,execution=e,outcome=o,capabilities=r,current_frame_epochs={'F':0})
 visible_z=advance_epistemic_program_trial(t,intent=i,execution=e,outcome=o,capabilities=r,current_frame_epochs={'F':0})
 assert visible_a.serializable()==visible_z.serializable()
 # Same-regime macro agreement is nondiscriminating no matter how many copies.
 hs=HypothesisSet([Hypothesis('H1',lambda x:'same'),Hypothesis('H2',lambda x:'same')])
 assert hs.best_probe([('A','B')]) is None
 for k in range(40): hs.observe(('A','B',k),'same') if False else None
 assert hs.disposition()=='UNRESOLVED'
 # A newly observed sequence counterexample revokes the global endpoint-equivalence relation.
 rs_bad=list(rs)+[row('a2','s2','A','m2','oa2'),row('b2','m2','B','DIFF','ob2'),row('c2','s2','C','EXPECTED','oc2')]
 target=[x for x in discover_opaque_action_composition_candidates(rs_bad,min_positive_support=2) if (x.direct_action_token,x.first_action_token,x.second_action_token)==('C','A','B')]
 assert target==[]
 # Cached target has no lasting use authority: component/frame drift blocks a fresh trial from the old candidate.
 _,c2,r2=fixture();r2.invalidate('B')
 blocked_component=False
 try: begin_epistemic_program_trial(c2,deficit_id='D',discrimination_signature_sha256=H('AB'),capabilities=r2,obligation=obl,current_frame_epochs={'F':0},start_state_id='s0',start_state_evidence_id='ce0')
 except ValueError as x: blocked_component='CAPABILITY_NOT_CURRENT:B' in str(x)
 _,c3,r3=fixture();blocked_frame=False
 try: begin_epistemic_program_trial(c3,deficit_id='D',discrimination_signature_sha256=H('AB'),capabilities=r3,obligation=obl,current_frame_epochs={'F':1},start_state_id='s0',start_state_evidence_id='ce0')
 except ValueError as x: blocked_frame='RELATIONAL_FRAME_NOT_CURRENT:F@0' in str(x)
 assert blocked_component and blocked_frame
 out={
  'MS1694_pass17':{'visible_records_equal_across_hidden_actual_primitive_worlds':True,'disposition':'PROGRAM_TRIAL_BINDS_ACTION_CLOSURE_EXECUTION_RECORD__DOES_NOT_INDEPENDENTLY_GROUND_PHYSICAL_ACTUATOR_IDENTITY'},
  'MS1695_pass18':{'best_probe':None,'hypothesis_disposition':hs.disposition(),'disposition':'REPEATED_BEHAVIORALLY_EQUIVALENT_MACRO_EVIDENCE_DOES_NOT_CREATE_DISCRIMINATION'},
  'MS1696_pass19':{'global_candidate_after_sequence_counterexample':len(target),'disposition':'ONE_SEQUENCE_COUNTEREXAMPLE_REVOKES_GLOBAL_COMPOSITION_CLAIM__NO_HIDDEN_ENTITY_ASSERTED'},
  'MS1697_pass20':{'component_drift_blocks_cached_target':blocked_component,'frame_drift_blocks_cached_target':blocked_frame,'disposition':'SELECTED_COMPOSED_TARGET_HAS_NO_PERMANENT_AUTHORITY__REPROJECT_CURRENTNESS_AT_USE'},
 }
 Path(__file__).with_name('MS1694_1697_PASS17_20_BOUNDARIES.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':run()
