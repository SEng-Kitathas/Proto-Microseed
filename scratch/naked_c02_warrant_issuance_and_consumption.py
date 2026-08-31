from __future__ import annotations
from dataclasses import dataclass
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scratch.naked_c01_explicit_experimental_warrant_quarry import ActionDescriptor,derive_warrant,authorize

@dataclass
class WarrantLedger:
    consumed: set[str]
    def reserve_before_effect(self,warrant_id:str)->bool:
        if warrant_id in self.consumed: return False
        self.consumed.add(warrant_id)
        return True
    def snapshot(self)->str:
        return json.dumps(sorted(self.consumed))
    @classmethod
    def restore(cls,s:str): return cls(set(json.loads(s)))

def automatic_issue_for_every_unknown(actions:list[ActionDescriptor],state:str)->list[object]:
    return [derive_warrant(a,state) for a in actions if not a.consequence_modeled]

def issue_only_explicitly_nominated(action:ActionDescriptor,state:str, nominated_capability_id:str|None):
    # Candidate constitutional narrowing: the experimental constitution itself
    # must select one exact subject; unknownness alone is not a selector.
    if nominated_capability_id!=action.capability_id: return None
    return derive_warrant(action,state)

def execute_once_crash_safe(w,action,state,ledger:WarrantLedger,*,simulate_crash_after_reservation=False):
    pre=authorize(w,action,state,0)
    if pre["status"]!="AUTHORIZED_ONCE": return {"status":"ABSTAIN","pre":pre,"effect_calls":0}
    if not ledger.reserve_before_effect(w.warrant_id):
        return {"status":"ABSTAIN","reason":"WARRANT_ALREADY_CONSUMED","effect_calls":0}
    if simulate_crash_after_reservation:
        return {"status":"CRASH_AFTER_AUTHORITY_CONSUMPTION_BEFORE_EFFECT","effect_calls":0,"ledger":ledger.snapshot()}
    return {"status":"EFFECT_CALLED_ONCE","effect_calls":1,"ledger":ledger.snapshot()}

def run_campaign():
    actions=[ActionDescriptor(f"A{i}",0,f"sig{i}","S") for i in range(20)]
    broad=automatic_issue_for_every_unknown(actions,"state")
    # This hostile demonstrates that the C01 derivation, if applied mechanically
    # to every unknown action, becomes a generic first-sample policy.
    assert len([w for w in broad if w is not None])==20
    target=actions[7]
    w=issue_only_explicitly_nominated(target,"state",target.capability_id); assert w is not None
    assert all(issue_only_explicitly_nominated(a,"state",target.capability_id) is None for a in actions if a is not target)
    ledger=WarrantLedger(set())
    crash=execute_once_crash_safe(w,target,"state",ledger,simulate_crash_after_reservation=True)
    assert crash["status"]=="CRASH_AFTER_AUTHORITY_CONSUMPTION_BEFORE_EFFECT" and crash["effect_calls"]==0
    restored=WarrantLedger.restore(crash["ledger"])
    retry=execute_once_crash_safe(w,target,"state",restored)
    assert retry["status"]=="ABSTAIN" and retry["effect_calls"]==0
    # Normal path also cannot repeat.
    w2=issue_only_explicitly_nominated(actions[8],"state",actions[8].capability_id); assert w2
    l2=WarrantLedger(set()); first=execute_once_crash_safe(w2,actions[8],"state",l2); second=execute_once_crash_safe(w2,actions[8],"state",l2)
    assert first["effect_calls"]==1 and second["effect_calls"]==0
    return {"status":"PASS",
      "broad_auto_issue_count":len(broad),
      "broad_auto_issue_classification":"REJECT__UNKNOWNNESS_ALONE_BECOMES_GENERIC_FIRST_SAMPLE_POLICY",
      "explicit_nomination":"ONE_EXACT_SUBJECT_ONLY",
      "crash":crash,"retry":retry,"normal_first":first,"normal_second":second,
      "earned":"WARRANT_AUTHORITY_MUST_BE_CONSUMED_BEFORE_EFFECT_AND_UNKNOWNNESS_ALONE_CANNOT_SELECT_WARRANT_SUBJECT",
      "open_seam":"WHAT_CONSTITUTIONALLY_LAWFUL_NON_CIRCULAR_OWNER_NOMINATES_THE_ONE_EXACT_EXPERIMENT_SUBJECT",
      "next":"NAKED_C03_NOMINATION_AUTHORITY_QUARRY"}
if __name__=='__main__': print(json.dumps(run_campaign(),indent=2,sort_keys=True))
