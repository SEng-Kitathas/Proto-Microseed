from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scratch.lang_c02_multi_token_restart_revalidation import build_two_relations
from scratch.lang_c01_operational_reference_relation import resolve_current_operational_referent

NONE={"semantic_reference_authority":"NONE","truth_authority":"NONE","execution_authority":"NONE","predicate_authority":"NONE","semantic_identity_authority":"NONE"}

def compose_ordered(ms,components:list[tuple[str,dict[str,object]]])->dict[str,object]:
    if len(components)<2:return {**NONE,"status":"DEFER_UNKNOWN","reason":"AT_LEAST_TWO_INDEPENDENT_B1_COMPONENTS_REQUIRED"}
    relation_ids=[str(rel.get("relation",{}).get("binding_id","")) for _,rel in components]
    if len(set(relation_ids))!=len(relation_ids):return {**NONE,"status":"DEFER_UNKNOWN","reason":"INDEPENDENT_COMPONENT_RELATIONS_REQUIRED"}
    resolved=[]
    for token,rel in components:
        x=resolve_current_operational_referent(ms,rel,token)
        if x.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY":
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"EVERY_B1_COMPONENT_MUST_BE_CURRENT","failed_token":token,"component":x}
        resolved.append({"token_capability_id":token,"operational_referent_signature_sha256":x["operational_referent_signature_sha256"]})
    return {**NONE,"status":"B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RESEARCH_ONLY","composition_operator":"ORDERED_TUPLE",
            "components":resolved,"authority_gain":"NONE"}

def run_campaign():
    with tempfile.TemporaryDirectory(prefix='lang-c03-') as td:
        ms,world,rx,ry=build_two_relations(Path(td))
        try:
            xy=compose_ordered(ms,[("SIG-X",rx),("SIG-Y",ry)]); yx=compose_ordered(ms,[("SIG-Y",ry),("SIG-X",rx)])
            assert xy["status"]==yx["status"]=="B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RESEARCH_ONLY"
            assert [c["operational_referent_signature_sha256"] for c in xy["components"]]==list(reversed([c["operational_referent_signature_sha256"] for c in yx["components"]]))
            dup=compose_ordered(ms,[("SIG-X",rx),("SIG-X",rx)]); assert dup["status"]=="DEFER_UNKNOWN"
            ms.invalidate_capability("SIG-Y",reason="LANG_C03_COMPONENT_DRIFT")
            stale=compose_ordered(ms,[("SIG-X",rx),("SIG-Y",ry)]); assert stale["status"]=="DEFER_UNKNOWN"
        finally:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
    assert xy["semantic_reference_authority"]==xy["truth_authority"]==xy["execution_authority"]==xy["predicate_authority"]=="NONE"
    return {"status":"PASS","xy":xy,"yx":yx,"duplicate":dup,"stale_component":stale,
      "earned":"TWO_INDEPENDENT_CURRENT_B1_RELATIONS_CAN_COMPOSE_INTO_AN_ORDER_SENSITIVE_B2_OPERATIONAL_REFERENCE_STRUCTURE_WITHOUT_SEMANTIC_OR_PREDICATE_AUTHORITY",
      "nonclaim":"ORDERED_REFERENCE_COMPOSITION_IS_NOT_YET_A_GROUNDED_RELATION_OR_PREDICATE",
      "next":"LANG_C04_GROUNDED_RELATION_PREDICATE_QUARRY"}
if __name__=='__main__':print(json.dumps(run_campaign(),indent=2,sort_keys=True))
