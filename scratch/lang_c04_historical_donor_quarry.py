from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from microseed.cognition.predicates import change,rise,ASSISTANCE_DENOMINATOR
from microseed.cognition.event_frames import infer_event_frame,effect_stationarity_boundaries
from microseed.cognition.operator_language import base_closure,compose,op_apply,ResearchOperator

def run_campaign():
    # Donor 1: extensional composition/fixpoint algorithm, not supplied state identities/operator semantics.
    K=3; inc=tuple(op_apply("INC",s,K) for s in range(K)); dec=tuple(op_apply("DEC",s,K) for s in range(K)); ident=tuple(range(K))
    closure=base_closure(K); assert compose(inc,dec)==ident and ident in closure
    donor=ResearchOperator("DONOR",1); assert donor.status=="RESEARCH_ONLY" and "STATE_IDENTITY_SUPPLIED" in donor.assistance_ancestry
    # Donor 2: ambiguity discipline from event-frame induction.
    amb=infer_event_frame(["a","a","b","b"],rival_segmentations=[[0,2],[0,1,2]])
    assert amb.status=="UNKNOWN_INCOMPLETE"
    simple=infer_event_frame(["a","a","b","b"]); assert simple.status=="NOMINATED_OPERATIONAL_FRAME"
    # Donor 3: predicates carry explicit supplied assistance and frame scope.
    c=change([0,0,1,1]); r=rise([0,0,1,1]); assert c.qualification==r.qualification=="RESEARCH_ONLY"
    assert "UPDATE_BOUNDARIES_SUPPLIED" in ASSISTANCE_DENOMINATOR and "QUALIFICATION_EVALUATOR_SUPPLIED" in ASSISTANCE_DENOMINATOR
    return {"status":"PASS",
      "admissible_parts":[
        "EXTENSIONAL_COMPOSITION_AS_PURE_ALGORITHMIC_INVARIANT",
        "FIXPOINT_CLOSURE_AS_PURE_SEARCH_MECHANIC",
        "MULTIPLE_LAWFUL_SEGMENTATIONS_REQUIRE_UNKNOWN"
      ],
      "quarantined_assumptions":[
        "SUPPLIED_STATE_IDENTITY","SUPPLIED_TRANSITION_BOUNDARIES","SUPPLIED_GENERIC_BRANCH_METALANGUAGE",
        "SUPPLIED_OPERATOR_NAMES_AND_VOCABULARY","SUPPLIED_PREDICATE_FRAME","SUPPLIED_QUALIFICATION_EVALUATOR"
      ],
      "event_frame_ambiguous":amb.status,"predicate_assistance":list(ASSISTANCE_DENOMINATOR),
      "earned":"C2_PARTS_QUARRY_CAN_TRANSFER_ALGORITHMIC_INVARIANTS_AND_ABSTENTION_DISCIPLINE_WITHOUT_TRANSFERRING_OLD_SEMANTIC_OR_ASSISTANCE_AUTHORITY",
      "next":"GROUND_RELATIONAL_STRUCTURE_FROM_CURRENT_B1_REFERENTS_BEFORE_REUSING_PREDICATE_OR_EVENT_FRAME_CODE"}
if __name__=='__main__':print(json.dumps(run_campaign(),indent=2,sort_keys=True))
