from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.cognition.referents import OperationalReferentSignature
from microseed.development.action_closure import OpaqueControlStateWitness
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier,QualifiedActionOutcomePredictiveRelation
from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import CounterfactualRehearsalConfig
from microseed.runtime.types import (
    Authority,CapabilityContract,EpisodeSchemaContract,EpistemicStatus,FeasibilityState,
    OperationalFrameContract,QualificationState,QueryObligation,ValueVariableContract,
)
from scratch.ms2003_operational_referent_class_set_routing import ACTIONS,CONTEXT_A,CONTEXT_B,ALIASED,UNKNOWN_CONTEXT

CONTROL_ACTIONS=("X","Y")


def _close(ms:Microseed)->None:
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()


def _sig(row:dict[str,object])->OperationalReferentSignature:
    return OperationalReferentSignature(
        "OPERATIONAL_REFERENT_SIGNATURE_DERIVED",str(row["signature_sha256"]),
        tuple((str(a),tuple(bool(x) for x in bits)) for a,bits in row["action_response_rows"]), # type: ignore[index]
        "AFFORDANCE_RELATIVE_BOUNDARY_RESPONSE_ONLY",
    )


def _persist(ms:Microseed,tag:str,samples)->dict[str,object]:
    d=ms.derive_operational_referent_signatures_from_raw_trace(samples,ACTIONS)
    assert d["status"]=="OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE",d
    for i,row in enumerate(d["signature_classes"]):
        ms.record_operational_referent_signature(f"MS2003-INTENT-{tag}-{i}",_sig(row))
    c=ms.derive_current_operational_referent_class_set_context(samples,ACTIONS,max_records=128)
    assert c["status"]=="CURRENT_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SET_CONTEXT",c
    return c


def _relation(ms:Microseed,rid:str,action:str,next_state:str,effect:float,tag:str)->QualifiedActionOutcomePredictiveRelation:
    r=QualifiedActionOutcomePredictiveRelation(
        relation_id=rid,candidate_id=f"C-{rid}",candidate_sha256=(tag.lower()[0])*64,
        start_state_id="S0",capability_id=action,next_state_id=next_state,value_effect=effect,
        support=24,consistency=1.0,source_evidence_ids=(f"SRC-{rid}",),qualification_evidence_ids=(f"QUAL-{rid}",),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=ms.capabilities.epochs[action],
        frame_epochs=(("F",ms.frames.epochs["F"]),),episode_schema_epochs=(("E",ms.episodes.epochs["E"]),),
        value_epoch=("V",ms.values.epochs["V"]),
    )
    ms.action_outcome_learning.add_relation(r);return r


def _holdout(ms:Microseed,projection,task,bucket,action,relation,tag):
    refs=[]
    for i in range(12):
        refs.append(ms.append_evidence(f"MS2003-INTENT-HOLD-{tag}-{i}",{
            "kind":"PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT",
            "projection_id":projection.projection_id,"projection_epoch":projection.epoch,
            "projection_signature_sha256":projection.signature_sha256,"task_id":task,"horizon":1,
            "action_id":action,"channel_id":"opaque-control","projection_bucket_id":bucket,
            "actual_next_state_id":relation.next_state_id,"actual_value_effect":relation.value_effect,
        },EpistemicStatus.PRESSURE_SUPPORTED,source="MS2003-HSP-INDEPENDENT-HOLDOUT"))
    return tuple(refs)


def run_ms2003_action_intent()->dict[str,object]:
    td=tempfile.TemporaryDirectory(prefix="ms2003-action-intent-");ms=Microseed(Path(td.name))
    try:
        ms.register_operational_frame(OperationalFrameContract(
            "F","opaque frame","e"*64,Authority.REFERENCE_ONLY,("MS2003",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED))
        ms.register_value_variable(ValueVariableContract(
            "V","opaque regulatory coordinate",.9,1.1,"c"*64,Authority.REFERENCE_ONLY,("MS2003",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED))
        ms.register_episode_schema(EpisodeSchemaContract(
            "E","opaque one-step grouping","f"*64,Authority.REFERENCE_ONLY,("MS2003",),"CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(("F",0),),value_epochs=(("V",0),)))
        for action in CONTROL_ACTIONS:
            ms.register_capability(CapabilityContract(
                action,"opaque effect",{}, {},(),(),Authority.EFFECT,("MS2003",),"CURRENT",{},
                qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda:None))
        ms.observe_value_state("V",0.0)
        state_ref=ms.append_evidence("MS2003-CONTROL-S0",{"kind":"OPAQUE_CONTROL_STATE_FIXTURE","state":"S0"},EpistemicStatus.PRESSURE_SUPPORTED,source="MS2003-EXTERNAL-OBSERVATION")
        ms.action_closure.set_state(OpaqueControlStateWitness("S0",state_ref.evidence_id))

        # Context A says X is regulatory-improving; context B says Y is. These are
        # pre-existing independently qualified relation fixtures, not learned here.
        rels={
            "AX":_relation(ms,"REL-AX","X","SA-X",+1.0,"a"),
            "AY":_relation(ms,"REL-AY","Y","SA-Y",-1.0,"b"),
            "BX":_relation(ms,"REL-BX","X","SB-X",-1.0,"c"),
            "BY":_relation(ms,"REL-BY","Y","SB-Y",+1.0,"d"),
        }
        for r in rels.values():
            for eid in r.source_evidence_ids+r.qualification_evidence_ids:
                if ms.evidence.get(eid) is None:
                    ms.append_evidence(eid,{"kind":"PREEXISTING_QUALIFIED_RELATION_ANCESTRY","relation_id":r.relation_id},EpistemicStatus.PRESSURE_SUPPORTED,source="MS2003-PREQUALIFIED-FIXTURE")

        ca=_persist(ms,"A",CONTEXT_A);cb=_persist(ms,"B",CONTEXT_B)
        coordinate=ms.register_epistemic_projection(
            "MS2003-CLASS-SET-POLICY",ms.operational_referent_class_set_projection_signature_sha256(),
            assistance_ancestry=("SUPPLIED_OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_COORDINATE","NO_SEMANTIC_REFERENT_AUTHORITY"))
        task="MS2003-CLASS-SET-POLICY"
        prop=ms.append_evidence("MS2003-POLICY-ROUTE-PROP",{
            "kind":"ROUTING_PROPOSAL","basis":"OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_CONTEXT",
            "identity_authority":"NONE","semantic_reference_authority":"NONE","preferred_action_authority":"NONE",
        },EpistemicStatus.PRESSURE_SUPPORTED,source="MICROSEED-PROPOSAL")
        route=ms.nominate_projection_conditioned_relation_routing(
            projection_id=coordinate.projection_id,task_id=task,action_ids=CONTROL_ACTIONS,channel_ids=("opaque-control",),horizon=1,
            default_action_relations=(("X",rels["AX"].relation_id),("Y",rels["AY"].relation_id)),
            bucket_action_overrides=((str(cb["projection_bucket_id"]),"X",rels["BX"].relation_id),(str(cb["projection_bucket_id"]),"Y",rels["BY"].relation_id)),
            source_evidence_ids=(prop.evidence_id,))
        refs=()
        for bucket,prefix in ((str(ca["projection_bucket_id"]),"A"),(str(cb["projection_bucket_id"]),"B")):
            for action in CONTROL_ACTIONS:
                rel=rels[prefix+action]
                refs += _holdout(ms,coordinate,task,bucket,action,rel,prefix+action)
        ticket=ExternalProjectionConditionedRelationQualifier(ms.evidence,qualifier_id="EXTERNAL-MS2003-CLASS-SET-POLICY").qualify(
            route,qualification_evidence=refs,relations=ms.action_outcome_learning.relations,min_support=24,min_accuracy=.95)
        admitted=ms.qualify_projection_conditioned_relation_routing(ticket)
        assert admitted["status"]=="CURRENT_PROJECTION_CONDITIONED_ROUTING",admitted
        binding=admitted["binding"]["binding_id"]
        opts=tuple(RecruitmentOption(a,FeasibilityState.FEASIBLE) for a in CONTROL_ACTIONS)
        cfg=CounterfactualRehearsalConfig(max_horizon=1,max_nodes=16)

        pa=ms.nominate_current_operational_referent_class_set_conditioned_rehearsal(
            (),opts,CONTEXT_A,ACTIONS,start_state_id="S0",value_id="V",projection_routing_id=binding,
            routing_task_id=task,routing_channel_id="opaque-control",max_records=128,config=cfg)
        pb=ms.nominate_current_operational_referent_class_set_conditioned_rehearsal(
            (),opts,CONTEXT_B,ACTIONS,start_state_id="S0",value_id="V",projection_routing_id=binding,
            routing_task_id=task,routing_channel_id="opaque-control",max_records=128,config=cfg)
        assert pa is not None and pb is not None,(pa,pb)
        assert pa.sequence==("X",) and pb.sequence==("Y",),(pa.serializable(),pb.serializable())
        obligation=QueryObligation("MS2003-ACT","opaque bounded action",required_authority=Authority.EFFECT)
        ia=ms.nominate_bounded_action_intent(pa.proposal_id,obligation)
        ib=ms.nominate_bounded_action_intent(pb.proposal_id,obligation)
        assert ia["status"]==ib["status"]=="ACTION_INTENT_NOMINATED",(ia,ib)
        assert ia["intent"]["capability_id"]=="X" and ib["intent"]["capability_id"]=="Y"
        assert ia["execution_authority"]==ib["execution_authority"]=="NONE"

        # Unknown/aliased class pressure cannot produce a rehearsal or intent.
        pu=ms.nominate_current_operational_referent_class_set_conditioned_rehearsal(
            (),opts,UNKNOWN_CONTEXT,ACTIONS,start_state_id="S0",value_id="V",projection_routing_id=binding,
            routing_task_id=task,routing_channel_id="opaque-control",max_records=128,config=cfg)
        palias=ms.nominate_current_operational_referent_class_set_conditioned_rehearsal(
            (),opts,ALIASED,ACTIONS,start_state_id="S0",value_id="V",projection_routing_id=binding,
            routing_task_id=task,routing_channel_id="opaque-control",max_records=128,config=cfg)
        assert pu is None and palias is None

        return {
            "status":"PASS","context_a_bucket":ca["projection_bucket_id"],"context_b_bucket":cb["projection_bucket_id"],
            "context_a_rehearsal":list(pa.sequence),"context_b_rehearsal":list(pb.sequence),
            "context_a_intent":ia["intent"]["capability_id"],"context_b_intent":ib["intent"]["capability_id"],
            "supplied_rehearsal_rows":0,"caller_supplied_projection_bucket":"NO","caller_supplied_referent_class":"NO",
            "caller_supplied_preferred_action":"NO","unknown_context_rehearsal":"NONE","aliased_context_rehearsal":"NONE",
            "identity_authority":"NONE","semantic_reference_authority":"NONE","truth_authority":"NONE","execution_authority":"NONE",
            "new_policy_manager_required":"NO","new_referent_manager_required":"NO",
            "remaining_assistance":"SUPPLIED_OPAQUE_CLASS_SET_COORDINATE_PLUS_EXTERNAL_RELATION_AND_ROUTING_QUALIFICATION",
            "earned":"OWNED_RAW_OPERATIONAL_REFERENT_CLASS_SET_CONTEXT_CAN_CHANGE_ZERO_ROW_REHEARSAL_AND_BOUNDED_ACTION_INTENT_THROUGH_EXISTING_QUALIFIED_ROUTING_WITHOUT_CALLER_BUCKET_CLASS_PREFERRED_ACTION_OR_NEW_REFERENT_POLICY_MANAGER",
        }
    finally:_close(ms);td.cleanup()


def main()->None:print(json.dumps(run_ms2003_action_intent(),indent=2,sort_keys=True))
if __name__=="__main__":main()
