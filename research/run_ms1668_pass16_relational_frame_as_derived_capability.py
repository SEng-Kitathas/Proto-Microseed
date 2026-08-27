from __future__ import annotations
import json
from pathlib import Path
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.types import CapabilityContract,Authority,QualificationState,QueryObligation
OUT=Path(__file__).with_name('MS1668_PASS16_RELATIONAL_FRAME_AS_DERIVED_CAPABILITY.json')
def cap(cid,authority,deps=(),handler=None):
 return CapabilityContract(cid,f'opaque-{cid}',{'kind':'OPAQUE_ACTION_OR_RELATION','expression':cid},{'opaque':True},('NO_SEMANTIC_COORDINATE_AUTHORITY',),(),authority,('MS1668',),'CURRENT',{},deps,None,None,QualificationState.SHADOW_QUALIFIED,handler,(),None)
def main():
 r=CapabilityRegistry();
 for x in ('A','B','C'):r.register(cap(x,Authority.EFFECT,handler=lambda **_: {'effect':'opaque'}))
 r.register(cap('REL-C-EQ-A-THEN-B',Authority.DERIVED_READ_ONLY,('A','B','C'),handler=lambda **_: {'relation':'C≈A∘B'}))
 q=QueryObligation('Q','read-relation',Authority.DERIVED_READ_ONLY)
 before=r.invoke('REL-C-EQ-A-THEN-B',q);stale=r.change_dependency('A',reason='ACTION_MAPPING_CHANGED');after=r.invoke('REL-C-EQ-A-THEN-B',q)
 checks={'relation_invokes_only_read_only':before['status']=='CAPABILITY_RESULT' and before['authority']==Authority.DERIVED_READ_ONLY.value,'action_change_transitively_stales_relation':'REL-C-EQ-A-THEN-B' in stale,'stale_relation_refuses_use':after['status']=='UNKNOWN_INCOMPLETE','relation_never_has_effect_authority':r.contracts['REL-C-EQ-A-THEN-B'].authority==Authority.DERIVED_READ_ONLY}
 out={'milestone':'MS1668','pass':16,'checks':checks,'pass_all':all(checks.values()),'before':before,'after':after,'stale_set':sorted(stale),'disposition':'ORDINARY_CAPABILITY_CURRENTNESS_CAN_CARRY_RELATIONAL_FRAME'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
