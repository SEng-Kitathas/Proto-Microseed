from __future__ import annotations
import json
from pathlib import Path
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.types import QueryObligation,Authority
OUT=Path(__file__).with_name('MS1658_PASS06_SYMBOLIC_RELATION_NOT_AFFORDANCE.json')
def main():
 reg=CapabilityRegistry(); obligation=QueryObligation('Q-ACT','PASS06_ACTUATION_CHECK',Authority.EFFECT,None,'SCOPE-A')
 invented='COMP-A-A-AS-C'
 res=reg.invoke(invented,obligation)
 checks={'invented_symbolic_action_has_no_path':res['status']=='NO_PATH','invented_symbolic_action_has_no_authority':res['authority']==Authority.NONE.value}
 out={'milestone':'MS1658','pass':6,'symbolic_action':invented,'invoke_result':res,'checks':checks,'pass_all':all(checks.values()),'scar':'RELATIONAL_ACTION_EXPRESSION_NE_EXECUTABLE_AFFORDANCE','disposition':'EXISTING_CAPABILITY_BOUNDARY_ALREADY_BLOCKS_SYMBOLIC_ACTUATOR_FABRICATION'}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
