from __future__ import annotations
import hashlib,json,random
from pathlib import Path
from microseed import Authority,CapabilityContract,OpaqueTransitionSample,QualificationState,QueryObligation,discover_opaque_action_composition_candidates
from microseed.cognition.hypothesis import Hypothesis,HypothesisSet
from microseed.development.action_closure import BoundedActionIntent,ActionExecutionRecord,ActionOutcomeRecord
from microseed.development.epistemic_program import begin_epistemic_program_trial,advance_epistemic_program_trial
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.commitment import RelationalCommitment,TernaryCommitment

def H(x):return hashlib.sha256(str(x).encode()).hexdigest()
def cap(cid):return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1699',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:None,operational_scope_id='S')
def run_world(seed):
 rng=random.Random(seed); toks=[f't{seed}-{i}-{rng.randrange(1_000_000)}' for i in range(8)];s0,s1,m0,m1,e0,e1,A,B=toks;C=f'c-{seed}-{rng.randrange(1_000_000)}';F=f'f-{seed}'
 def row(i,s,a,e,o):return OpaqueTransitionSample(i,o,s,a,e,F,0)
 rows=[row('a0',s0,A,m0,'oa0'),row('b0',m0,B,e0,'ob0'),row('c0',s0,C,e0,'oc0'),row('a1',s1,A,m1,'oa1'),row('b1',m1,B,e1,'ob1'),row('c1',s1,C,e1,'oc1')]
 cand=[x for x in discover_opaque_action_composition_candidates(rows,min_positive_support=2) if (x.direct_action_token,x.first_action_token,x.second_action_token)==(C,A,B)][0]
 r=CapabilityRegistry();r.register(cap(A));r.register(cap(B));obl=QueryObligation('Q','p',required_authority=Authority.EFFECT,operational_scope_id='S')
 trial=begin_epistemic_program_trial(cand,deficit_id='D',discrimination_signature_sha256=H(seed),capabilities=r,obligation=obl,current_frame_epochs={F:0},start_state_id=s0,start_state_evidence_id='ce0')
 def rec(cid,idx,start,evid,nexts):
  cm=RelationalCommitment(f'cm{idx}',f't{idx}',TernaryCommitment.YES); intent=BoundedActionIntent(f'i{idx}',f'p{idx}',f'd{idx}',cm,cid,0,start,evid,nexts,0.0,('V',0),'Q','S');ex=ActionExecutionRecord(f'x{idx}',f'i{idx}',cid,0,start,'h');pc=RelationalCommitment(f'pc{idx}',f'pt{idx}',TernaryCommitment.YES);out=ActionOutcomeRecord(f'o{idx}',f'x{idx}',f'ev{idx}',nexts,float(idx),'V',pc,actual_value_effect=0.0);return intent,ex,out
 i0,x0,o0=rec(A,0,s0,'ce0',m0);t1=advance_epistemic_program_trial(trial,intent=i0,execution=x0,outcome=o0,capabilities=r,current_frame_epochs={F:0})
 i1,x1,o1=rec(B,1,m0,'ev0',e0);t2=advance_epistemic_program_trial(t1,intent=i1,execution=x1,outcome=o1,capabilities=r,current_frame_epochs={F:0})
 clean=t2.status=='COMPLETE'
 # Wrong continuity.
 bad_i,bad_x,bad_o=rec(A,0,s0,'WRONG',m0);bad=advance_epistemic_program_trial(trial,intent=bad_i,execution=bad_x,outcome=bad_o,capabilities=r,current_frame_epochs={F:0}).status=='INVALID'
 # Frame drift after one step.
 fi=advance_epistemic_program_trial(t1,intent=i1,execution=x1,outcome=o1,capabilities=r,current_frame_epochs={F:1}).status=='INVALID'
 # Component invalidation before begin blocks old target.
 r2=CapabilityRegistry();r2.register(cap(A));r2.register(cap(B));r2.invalidate(B);stale=False
 try:begin_epistemic_program_trial(cand,deficit_id='D',discrimination_signature_sha256=H(seed),capabilities=r2,obligation=obl,current_frame_epochs={F:0},start_state_id=s0,start_state_evidence_id='ce0')
 except ValueError:stale=True
 hs=HypothesisSet([Hypothesis('h1',lambda x:'same'),Hypothesis('h2',lambda x:'same')]);nondisc=hs.best_probe([(A,B)]) is None and hs.disposition()=='UNRESOLVED'
 return clean,bad,fi,stale,nondisc

rows=[run_world(170000+i) for i in range(64)]
counts=[sum(x[i] for x in rows) for i in range(5)]
assert counts==[64]*5,counts
out={'milestone':'MS1699','pass':22,'worlds':64,'families':{'gauge_renamed_clean_program_complete':counts[0],'wrong_control_state_rejected':counts[1],'frame_drift_rejected':counts[2],'stale_component_blocks_begin':counts[3],'behaviorally_equivalent_macro_remains_unresolved':counts[4]},'disposition':'5_FAMILY_X_64_BREADTH_PASS'}
Path(__file__).with_name('MS1699_PASS22_PROGRAM_BREADTH.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
