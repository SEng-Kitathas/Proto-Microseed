from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.cognition.referents import OperationalReferentSignature
from microseed.development.action_learning import (
    ExternalProjectionConditionedRelationQualifier,
    QualifiedActionOutcomePredictiveRelation,
)
from microseed.runtime.types import Authority,CapabilityContract,EpistemicStatus,QualificationState,ValueVariableContract

ACTIONS=("P0","P1","P2","P3","P4")


def _samples(boundary_sets: tuple[tuple[int,...],...]) -> tuple[tuple[int,...],...]:
    n=max(max(x,default=0) for x in boundary_sets)+1
    vals=[0 for _ in boundary_sets]; rows=[tuple(vals)]
    for t in range(1,n):
        for i,b in enumerate(boundary_sets):
            if t in b: vals[i]=1-vals[i]
        rows.append(tuple(vals))
    # Ensure exactly len(ACTIONS)+1 samples while preserving all boundaries.
    while len(rows)<len(ACTIONS)+1: rows.append(tuple(vals))
    assert len(rows)==len(ACTIONS)+1,(len(rows),boundary_sets)
    return tuple(rows)

CONTEXT_A=_samples(((1,3),(1,3),(2,4),(2,4)))
CONTEXT_B=_samples(((1,4),(1,4),(2,5),(2,5)))
ALIASED=_samples(((1,2),(1,2),(1,2),(1,2)))
UNKNOWN_CONTEXT=_samples(((1,5),(1,5),(3,4),(3,4)))


def _close(ms:Microseed)->None:
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()


def _sig(row:dict[str,object])->OperationalReferentSignature:
    return OperationalReferentSignature(
        "OPERATIONAL_REFERENT_SIGNATURE_DERIVED",str(row["signature_sha256"]),
        tuple((str(a),tuple(bool(x) for x in bits)) for a,bits in row["action_response_rows"]), # type: ignore[index]
        "AFFORDANCE_RELATIVE_BOUNDARY_RESPONSE_ONLY",
    )


def _persist_context(ms:Microseed,tag:str,samples)->dict[str,object]:
    d=ms.derive_operational_referent_signatures_from_raw_trace(samples,ACTIONS)
    assert d["status"]=="OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE",d
    for i,row in enumerate(d["signature_classes"]):
        ms.record_operational_referent_signature(f"MS2003-{tag}-{i}",_sig(row))
    c=ms.derive_current_operational_referent_class_set_context(samples,ACTIONS,max_records=128)
    assert c["status"]=="CURRENT_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SET_CONTEXT",c
    return c


def _relation(ms:Microseed,rid:str,next_state:str,effect:float,tag:str)->QualifiedActionOutcomePredictiveRelation:
    r=QualifiedActionOutcomePredictiveRelation(
        relation_id=rid,candidate_id=f"C-{rid}",candidate_sha256=("a" if tag=="A" else "b")*64,
        start_state_id="S0",capability_id="ACT",next_state_id=next_state,value_effect=effect,
        support=24,consistency=1.0,source_evidence_ids=(f"SRC-{tag}",),qualification_evidence_ids=(f"QUAL-{tag}",),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=ms.capabilities.epochs["ACT"],
        frame_epochs=(),episode_schema_epochs=(),value_epoch=("V",ms.values.epochs["V"]),
    )
    ms.action_outcome_learning.add_relation(r)
    return r


def _holdouts(ms:Microseed,projection,task,bucket,relation,tag)->tuple:
    refs=[]
    for i in range(12):
        refs.append(ms.append_evidence(
            f"HOLD-{tag}-{i}",{
                "kind":"PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT",
                "projection_id":projection.projection_id,"projection_epoch":projection.epoch,
                "projection_signature_sha256":projection.signature_sha256,
                "task_id":task,"horizon":1,"action_id":"ACT","channel_id":"opaque-control",
                "projection_bucket_id":bucket,"actual_next_state_id":relation.next_state_id,
                "actual_value_effect":relation.value_effect,
            },EpistemicStatus.PRESSURE_SUPPORTED,source="MS2003-HSP-INDEPENDENT-HOLDOUT"
        ))
    return tuple(refs)


def _qualify_binding(ms:Microseed,projection,bucket_a,bucket_b,ra,rb,*,task="MS2003-REFSET"):
    prop=ms.append_evidence("MS2003-ROUTE-PROP-"+projection.projection_id,{
        "kind":"ROUTING_PROPOSAL","basis":"OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_CONTEXT",
        "identity_authority":"NONE","semantic_reference_authority":"NONE",
    },EpistemicStatus.PRESSURE_SUPPORTED,source="MICROSEED-PROPOSAL")
    route=ms.nominate_projection_conditioned_relation_routing(
        projection_id=projection.projection_id,task_id=task,action_ids=("ACT",),channel_ids=("opaque-control",),horizon=1,
        default_action_relations=(("ACT",ra.relation_id),),
        bucket_action_overrides=((bucket_b,"ACT",rb.relation_id),),source_evidence_ids=(prop.evidence_id,),
    )
    refs=_holdouts(ms,projection,task,bucket_a,ra,projection.projection_id+"-A")+_holdouts(ms,projection,task,bucket_b,rb,projection.projection_id+"-B")
    ticket=ExternalProjectionConditionedRelationQualifier(ms.evidence,qualifier_id="EXTERNAL-MS2003-REFSET-ROUTING").qualify(
        route,qualification_evidence=refs,relations=ms.action_outcome_learning.relations,min_support=12,min_accuracy=.95
    )
    admitted=ms.qualify_projection_conditioned_relation_routing(ticket)
    assert admitted["status"]=="CURRENT_PROJECTION_CONDITIONED_ROUTING",admitted
    return admitted["binding"]["binding_id"]


def run_ms2003_routing()->dict[str,object]:
    td=tempfile.TemporaryDirectory(prefix="ms2003-refset-routing-");ms=Microseed(Path(td.name))
    try:
        ms.register_value_variable(ValueVariableContract(
            "V","opaque regulatory coordinate",-1.0,1.0,"c"*64,Authority.REFERENCE_ONLY,("MS2003",),"CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
        ))
        ms.register_capability(CapabilityContract(
            "ACT","opaque effect",{}, {},(),(),Authority.EFFECT,("MS2003",),"CURRENT",{},
            qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda:None,
        ))
        # Evidence IDs make the fixture's relation ancestry explicit and disjoint from routing holdout.
        for eid in ("SRC-A","QUAL-A","SRC-B","QUAL-B"):
            ms.append_evidence(eid,{"kind":"PREEXISTING_RELATION_ANCESTRY","id":eid},EpistemicStatus.PRESSURE_SUPPORTED,source="MS2003-PREQUALIFIED-FIXTURE")
        ra=_relation(ms,"REL-A","S-A",-0.5,"A"); rb=_relation(ms,"REL-B","S-B",0.5,"B")
        ca=_persist_context(ms,"CTX-A",CONTEXT_A); cb=_persist_context(ms,"CTX-B",CONTEXT_B)
        assert ca["projection_bucket_id"]!=cb["projection_bucket_id"]
        coordinate=ms.register_epistemic_projection(
            "MS2003-OPERATIONAL-CLASS-SET",ms.operational_referent_class_set_projection_signature_sha256(),
            assistance_ancestry=("SUPPLIED_OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_COORDINATE","NO_SEMANTIC_REFERENT_AUTHORITY"),
        )
        binding=_qualify_binding(ms,coordinate,str(ca["projection_bucket_id"]),str(cb["projection_bucket_id"]),ra,rb)
        resolved_a=ms.resolve_current_operational_referent_class_set_conditioned_relation(
            binding,CONTEXT_A,ACTIONS,action_id="ACT",task_id="MS2003-REFSET",channel_id="opaque-control",horizon=1,max_records=128)
        resolved_b=ms.resolve_current_operational_referent_class_set_conditioned_relation(
            binding,CONTEXT_B,ACTIONS,action_id="ACT",task_id="MS2003-REFSET",channel_id="opaque-control",horizon=1,max_records=128)
        assert resolved_a["status"]==resolved_b["status"]=="CURRENT_PARTITION_SCOPED_RELATION",(resolved_a,resolved_b)
        assert resolved_a["relation_id"]=="REL-A" and resolved_b["relation_id"]=="REL-B"
        assert resolved_a["referent_witness_selection"]==resolved_b["referent_witness_selection"]=="NONE__CLASS_SET_ONLY"

        # A current raw context with no persisted class ancestry cannot enter routing.
        unknown=ms.resolve_current_operational_referent_class_set_conditioned_relation(
            binding,UNKNOWN_CONTEXT,ACTIONS,action_id="ACT",task_id="MS2003-REFSET",channel_id="opaque-control",horizon=1,max_records=128)
        assert unknown["status"]=="DEFER_UNKNOWN",unknown
        # Symmetry/alias remains unknown; no caller may force a partition.
        aliased=ms.resolve_current_operational_referent_class_set_conditioned_relation(
            binding,ALIASED,ACTIONS,action_id="ACT",task_id="MS2003-REFSET",channel_id="opaque-control",horizon=1,max_records=128)
        assert aliased["status"]=="DEFER_UNKNOWN" and aliased["reason"]=="BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS",aliased
        # Bounded evidence scan exhaustion is not false absence/currentness.
        budget=ms.resolve_current_operational_referent_class_set_conditioned_relation(
            binding,CONTEXT_A,ACTIONS,action_id="ACT",task_id="MS2003-REFSET",channel_id="opaque-control",horizon=1,max_records=0)
        assert budget["status"]=="DEFER_UNKNOWN",budget

        # An otherwise qualified binding using an arbitrary supplied projection cannot use this bridge.
        wrong=ms.register_epistemic_projection("MS2003-WRONG-COORDINATE","d"*64,assistance_ancestry=("ARBITRARY_SUPPLIED_COORDINATE",))
        wrong_binding=_qualify_binding(ms,wrong,str(ca["projection_bucket_id"]),str(cb["projection_bucket_id"]),ra,rb,task="MS2003-WRONG")
        mismatch=ms.resolve_current_operational_referent_class_set_conditioned_relation(
            wrong_binding,CONTEXT_A,ACTIONS,action_id="ACT",task_id="MS2003-WRONG",channel_id="opaque-control",horizon=1,max_records=128)
        assert mismatch["status"]=="DEFER_UNKNOWN" and mismatch["reason"]=="OPERATIONAL_REFERENT_CLASS_SET_COORDINATE_MISMATCH",mismatch

        return {
            "status":"PASS","context_a_bucket":ca["projection_bucket_id"],"context_b_bucket":cb["projection_bucket_id"],
            "context_a_relation":resolved_a["relation_id"],"context_b_relation":resolved_b["relation_id"],
            "unknown_context":unknown,"aliased":aliased,"budget_exhaustion":budget,"wrong_coordinate":mismatch,
            "caller_supplied_projection_bucket":"NO","caller_supplied_referent_class":"NO","referent_witness_selection":"NONE__CLASS_SET_ONLY",
            "identity_authority":"NONE","semantic_reference_authority":"NONE","truth_authority":"NONE","execution_authority":"NONE",
            "new_referent_manager_required":"NO","routing_owner":"EXISTING_EXTERNALLY_QUALIFIED_PROJECTION_CONDITIONED_RELATION_BINDING",
            "remaining_assistance":"SUPPLIED_AND_PROVENANCED_OPAQUE_CLASS_SET_COORDINATE_PLUS_EXTERNAL_ROUTING_QUALIFICATION",
            "earned":"OWNED_RAW_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SET_CONTEXT_CAN_SELECT_BETWEEN_EXISTING_QUALIFIED_PREDICTIVE_RELATIONS_WITHOUT_CALLER_BUCKET_CLASS_OBJECT_IDENTITY_OR_NEW_REFERENT_MANAGER",
        }
    finally:_close(ms);td.cleanup()


def main()->None:print(json.dumps(run_ms2003_routing(),indent=2,sort_keys=True))
if __name__=="__main__":main()
