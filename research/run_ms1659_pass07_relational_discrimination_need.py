from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions,direct_lookup
from microseed.cognition.hypothesis import Hypothesis,HypothesisSet
OUT=Path(__file__).with_name('MS1659_PASS07_RELATIONAL_DISCRIMINATION_NEED.json')

def fixture():
 # Two candidate relational explanations for C agree on S0,S1 but differ on S2,S3.
 rows=[];states=['S0','S1','S2','S3'];
 def add(s,a,e):rows.append(Transition(digest((s,a,e)),digest(('o',s,a,e)),s,a,e))
 # A,A => C truth globally: A = +1.
 for i,s in enumerate(states):add(s,'A',states[(i+1)%4])
 # D then E matches C on S0/S1, diverges S2/S3.
 mids=['M0','M1','M2','M3']
 for i,s in enumerate(states):add(s,'D',mids[i])
 outs=['S2','S3','S1','S0']
 for i,m in enumerate(mids):add(m,'E',outs[i])
 # direct C only S0/S1 to establish ambiguity
 add('S0','C','S2');add('S1','C','S3')
 return rows

def main():
 rows=fixture(); rels=construct_global_compositions(rows,2)
 target=[r for r in rels if r.direct_action=='C' and (r.first_action,r.second_action) in {('A','A'),('D','E')}]
 by=direct_lookup(rows)
 def pred_for(r,s):
  m=by.get((s,r.first_action));return None if m is None else by.get((m,r.second_action))
 hypotheses=[Hypothesis(r.relation_id,lambda probe,r=r: pred_for(r,probe)) for r in target]
 hs=HypothesisSet(hypotheses)
 full=['S0','S1','S2','S3']; available_nondisc=['S0','S1']; available_with_disc=['S0','S1','S2']
 no_probe=hs.best_probe(available_nondisc)
 disc_probe=hs.best_probe(available_with_disc)
 predictions={s:[pred_for(r,s) for r in target] for s in full}
 out={'milestone':'MS1659','pass':7,'candidate_relations':[r.__dict__ for r in target],'predictions':predictions,'no_discriminator_repertoire':available_nondisc,'with_discriminator_repertoire':available_with_disc,'selected_without_discriminator':no_probe,'selected_with_discriminator':disc_probe,
 'checks':{'two_competing_relations_present':len(target)==2,'same_repertoire_has_no_discriminating_probe':no_probe is None,'expanded_existing_repertoire_selects_discriminator':disc_probe=='S2'},
 'disposition':'EXISTING_ACTIVE_DISCRIMINATION_CONSUMES_RELATIONAL_ALTERNATIVES__AFFORDANCE_GAP_EXPLICIT'}
 out['pass_all']=all(out['checks'].values());OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
