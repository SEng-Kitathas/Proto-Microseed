from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions,predict_via_composition
OUT=Path(__file__).with_name('MS1667_PASS15_PARTIAL_AFFORDANCE_MISSING_PATH.json')
def main():
 states=['S0','S1','S2','S3'];rows=[]
 def add(s,a,e):rows.append(Transition(digest((s,a,e)),digest(('o',s,a,e)),s,a,e))
 # Establish C=A then B on S0,S1; A/B path at S2 is incomplete (B unavailable after A).
 add('S0','A','M0');add('M0','B','S2');add('S0','C','S2');add('S1','A','M1');add('M1','B','S3');add('S1','C','S3');add('S2','A','M2')
 rels=construct_global_compositions(rows,2);p,status,expr=predict_via_composition('S2','C',rels,rows)
 checks={'relation_can_be_nominated_from_observed_paths':any(r.direct_action=='C' and r.first_action=='A' and r.second_action=='B' for r in rels),'missing_component_path_returns_unknown':p is None and status=='UNKNOWN_NO_RELATION'}
 out={'milestone':'MS1667','pass':15,'prediction':p,'status':status,'expressions':expr,'checks':checks,'pass_all':all(checks.values()),'scar':'RELATIONAL_KNOWLEDGE_NE_AVAILABLE_COMPONENT_AFFORDANCE'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
