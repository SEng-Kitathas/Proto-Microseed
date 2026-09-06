from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _calibrate,_observe,ACT
from scratch.lang_c01_operational_reference_relation import resolve_current_operational_referent
from scratch.lang_c02_multi_token_restart_revalidation import build_two_relations
from scratch.lang_c03_b2_ordered_reference_composition import compose_ordered

NONE={"semantic_reference_authority":"NONE","predicate_authority":"NONE","truth_authority":"NONE","execution_authority":"NONE","language_authority":"NONE","semantic_identity_authority":"NONE"}


def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def apply_external_asymmetric_event(world,mode:str)->None:
    """Environment-side causal event. It is not registered as a Microseed action/capability."""
    if mode=="PQ": world.latent[0]-=1; world.latent[1]+=1
    elif mode=="QP": world.latent[1]-=1; world.latent[0]+=1
    else: raise ValueError(mode)


def _local_effect_basis(ms,world,cal):
    out={}
    for row in cal["rows"]:
        local=[]
        for action,responses in row["action_response_rows"]:
            if action in {"FX-P","FX-Q"} and responses and all(bool(x) for x in responses): local.append(action)
        if len(local)!=1:
            return {"status":"DEFER_UNKNOWN","reason":"EXACT_ONE_LOCAL_GROUNDED_EFFECT_BASIS_REQUIRED","row":row}
        world.reset_state(); before=_observe(ms); ms.capabilities.invoke(local[0],ACT); after=_observe(ms)
        group=tuple(row["group"]); delta=tuple(after[i]-before[i] for i in group)
        if not delta or any(d==0 for d in delta):
            return {"status":"DEFER_UNKNOWN","reason":"LOCAL_EFFECT_BASIS_MUST_MOVE_EVERY_REFERENT_CHANNEL"}
        out[str(row["signature_sha256"])]=delta
    return {"status":"CURRENT_AFFORDANCE_RELATIVE_EFFECT_BASES_DERIVED","bases":out}


def external_direction_episode(ms,world,layout:str,index:int,mode:str)->dict[str,object]:
    world.configure_layout(layout); world.configure_alias(False)
    cal=_calibrate(ms,world)
    if cal["status"]!="REFERENT_PARTITION_NOMINATED" or len(cal["rows"])!=2:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_TWO_CURRENT_OPERATIONAL_REFERENTS_REQUIRED"}
    basis=_local_effect_basis(ms,world,cal)
    if basis.get("status")!="CURRENT_AFFORDANCE_RELATIVE_EFFECT_BASES_DERIVED":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_LOCAL_EFFECT_BASES_REQUIRED","basis":basis}
    world.reset_state(); before=_observe(ms)
    apply_external_asymmetric_event(world,mode)
    after=_observe(ms)
    by_effect={}; diagnostic=[]
    for row in cal["rows"]:
        group=tuple(row["group"]); sig=str(row["signature_sha256"])
        event_delta=tuple(after[i]-before[i] for i in group); local_basis=tuple(basis["bases"][sig])
        score=sum(a*b for a,b in zip(event_delta,local_basis))
        if score<0: cls="OPPOSED_TO_LOCAL_GROUNDED_EFFECT"
        elif score>0: cls="ALIGNED_WITH_LOCAL_GROUNDED_EFFECT"
        else: return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXTERNAL_EVENT_ORIENTATION_UNRESOLVED_RELATIVE_TO_LOCAL_EFFECT","group":group}
        if cls in by_effect:return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXTERNAL_EVENT_ORIENTATION_CLASS_NOT_UNIQUE"}
        by_effect[cls]=sig
        diagnostic.append({"operational_referent_signature_sha256":sig,"affordance_relative_effect_class":cls,"event_delta":event_delta,"local_effect_basis":local_basis,"alignment_score":score})
    required={"OPPOSED_TO_LOCAL_GROUNDED_EFFECT","ALIGNED_WITH_LOCAL_GROUNDED_EFFECT"}
    if set(by_effect)!=required:return {**NONE,"status":"DEFER_UNKNOWN","reason":"ONE_OPPOSED_AND_ONE_ALIGNED_CURRENT_REFERENT_EFFECT_REQUIRED"}
    payload={"episode_index":index,"before_raw":list(before),"after_raw":list(after),
      "ordered_operational_referent_signatures":[by_effect["OPPOSED_TO_LOCAL_GROUNDED_EFFECT"],by_effect["ALIGNED_WITH_LOCAL_GROUNDED_EFFECT"]],
      "order_basis":"OPPOSED_TO_LOCAL_GROUNDED_EFFECT_THEN_ALIGNED_WITH_LOCAL_GROUNDED_EFFECT","diagnostic":diagnostic}
    return {**NONE,"status":"CURRENT_GROUNDED_EXTERNAL_DIRECTIONAL_EVENT_EPISODE","payload":payload,"episode_sha256":_sha(payload)}

def derive_directional_relation_candidate(ms,train,holdouts,rx,ry):
    if len(train)<8:return {**NONE,"status":"DEFER_UNKNOWN","reason":"SUFFICIENT_DIRECTIONAL_EVENT_HISTORY_REQUIRED"}
    if len(holdouts)<4:return {**NONE,"status":"DEFER_UNKNOWN","reason":"INDEPENDENT_DIRECTIONAL_HOLDOUT_REQUIRED"}
    rows=tuple(train)+tuple(holdouts)
    if any(e.get("status")!="CURRENT_GROUNDED_EXTERNAL_DIRECTIONAL_EVENT_EPISODE" for e in rows):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EVERY_DIRECTIONAL_EVENT_EPISODE_MUST_GROUND_EXACTLY"}
    x=resolve_current_operational_referent(ms,rx,"SIG-X"); y=resolve_current_operational_referent(ms,ry,"SIG-Y")
    if x.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY" or y.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"TWO_CURRENT_B1_REFERENTS_REQUIRED"}
    current={x["operational_referent_signature_sha256"],y["operational_referent_signature_sha256"]}
    train_orders={tuple(e["payload"]["ordered_operational_referent_signatures"]) for e in train}
    hold_orders={tuple(e["payload"]["ordered_operational_referent_signatures"]) for e in holdouts}
    if len(train_orders)!=1:return {**NONE,"status":"DEFER_UNKNOWN","reason":"TRAINING_DIRECTION_NOT_UNIQUE"}
    order=next(iter(train_orders))
    if hold_orders!={order}:return {**NONE,"status":"DEFER_UNKNOWN","reason":"HOLDOUT_DIRECTION_DISAGREES"}
    if len(order)!=2 or set(order)!=current:return {**NONE,"status":"DEFER_UNKNOWN","reason":"DIRECTIONAL_RELATION_COMPONENT_BINDING_MISMATCH"}
    evidence={"ordered_operational_referent_signatures":list(order),"training_episode_sha256":[e["episode_sha256"] for e in train],"holdout_episode_sha256":[e["episode_sha256"] for e in holdouts]}
    return {**NONE,"status":"GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY",
      "derived_relation_id":"OP-DIR-REL-"+_sha(evidence)[:24],"ordered_operational_referent_signatures":list(order),
      "order_basis":"OPPOSED_TO_LOCAL_GROUNDED_EFFECT_THEN_ALIGNED_WITH_LOCAL_GROUNDED_EFFECT","relation_form":"AFFORDANCE_RELATIVE_ORDERED_EXTERNAL_COEFFECT",
      "source_episode_sha256":evidence["training_episode_sha256"]+evidence["holdout_episode_sha256"],"authority_gain":"NONE"}


def compose_directional_frame(ms,candidate,components):
    if candidate.get("status")!="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"GROUNDED_DIRECTIONAL_RELATION_CANDIDATE_REQUIRED"}
    ordered=compose_ordered(ms,components)
    if ordered.get("status")!="B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_ORDERED_B1_COMPOSITION_REQUIRED","component":ordered}
    actual=[c["operational_referent_signature_sha256"] for c in ordered["components"]]
    if actual!=candidate["ordered_operational_referent_signatures"]:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"ARGUMENT_ORDER_NOT_GROUNDED_BY_EXTERNAL_RELATION_EVIDENCE","observed_relation_order":candidate["ordered_operational_referent_signatures"],"requested_order":actual}
    return {**NONE,"status":"B2_GROUNDED_DIRECTIONAL_RELATIONAL_REFERENCE_FRAME_RESEARCH_ONLY","derived_relation_id":candidate["derived_relation_id"],
      "arguments":actual,"relation_form":candidate["relation_form"],"order_basis":candidate["order_basis"],"authority_gain":"NONE"}


def _components_in_candidate_order(ms,candidate,rx,ry):
    x=resolve_current_operational_referent(ms,rx,"SIG-X"); y=resolve_current_operational_referent(ms,ry,"SIG-Y")
    lookup={x["operational_referent_signature_sha256"]:("SIG-X",rx),y["operational_referent_signature_sha256"]:("SIG-Y",ry)}
    return [lookup[s] for s in candidate["ordered_operational_referent_signatures"]]


def revalidate_directional_relation(ms,world,candidate,rx,ry,mode:str,start:int=800):
    fresh=tuple(external_direction_episode(ms,world,"A" if i%2==0 else "B",start+i,mode) for i in range(6))
    if any(e.get("status")!="CURRENT_GROUNDED_EXTERNAL_DIRECTIONAL_EVENT_EPISODE" for e in fresh):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"FRESH_DIRECTIONAL_EVIDENCE_REQUIRED"}
    orders={tuple(e["payload"]["ordered_operational_referent_signatures"]) for e in fresh}
    expected=tuple(candidate.get("ordered_operational_referent_signatures",()))
    if orders!={expected}:return {**NONE,"status":"DEFER_UNKNOWN","reason":"POST_BINDING_EMPIRICAL_DIRECTION_DRIFT","fresh_orders":[list(x) for x in sorted(orders)]}
    # Re-resolve components so stale B1 bindings cannot be hidden by matching raw event order.
    x=resolve_current_operational_referent(ms,rx,"SIG-X"); y=resolve_current_operational_referent(ms,ry,"SIG-Y")
    if x.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY" or y.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_B1_COMPONENTS_REQUIRED"}
    return {**NONE,"status":"CURRENT_DIRECTIONAL_RELATION_REVALIDATED_RESEARCH_ONLY","fresh_episode_sha256":[e["episode_sha256"] for e in fresh],"authority_gain":"NONE"}


def run_campaign():
    with tempfile.TemporaryDirectory(prefix='lang-c06-') as td:
        ms,world,rx,ry=build_two_relations(Path(td))
        try:
            action_ids_before=set(ms.capabilities.contracts)
            train=tuple(external_direction_episode(ms,world,"A" if i<5 else "B",i,"PQ") for i in range(10))
            hold=tuple(external_direction_episode(ms,world,"A" if i<3 else "B",100+i,"PQ") for i in range(6))
            cand=derive_directional_relation_candidate(ms,train,hold,rx,ry)
            assert cand["status"]=="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY",cand
            components=_components_in_candidate_order(ms,cand,rx,ry)
            frame=compose_directional_frame(ms,cand,components)
            assert frame["status"]=="B2_GROUNDED_DIRECTIONAL_RELATIONAL_REFERENCE_FRAME_RESEARCH_ONLY",frame
            reversed_frame=compose_directional_frame(ms,cand,list(reversed(components)))
            assert reversed_frame["status"]=="DEFER_UNKNOWN" and reversed_frame["reason"]=="ARGUMENT_ORDER_NOT_GROUNDED_BY_EXTERNAL_RELATION_EVIDENCE"

            reverse_hold=tuple(external_direction_episode(ms,world,"A" if i<3 else "B",200+i,"QP") for i in range(6))
            convention_reversal=derive_directional_relation_candidate(ms,train,reverse_hold,rx,ry)
            assert convention_reversal["status"]=="DEFER_UNKNOWN" and convention_reversal["reason"]=="HOLDOUT_DIRECTION_DISAGREES"

            fresh_same=revalidate_directional_relation(ms,world,cand,rx,ry,"PQ",300)
            assert fresh_same["status"]=="CURRENT_DIRECTIONAL_RELATION_REVALIDATED_RESEARCH_ONLY"
            fresh_reversed=revalidate_directional_relation(ms,world,cand,rx,ry,"QP",400)
            assert fresh_reversed["status"]=="DEFER_UNKNOWN" and fresh_reversed["reason"]=="POST_BINDING_EMPIRICAL_DIRECTION_DRIFT"

            # Full sensor-polarity inversion changes raw signs but not the affordance-relative order.
            original_observe=world.observe
            world.observe=lambda: tuple(-x for x in original_observe())
            try:
                inv_train=tuple(external_direction_episode(ms,world,"A" if i<5 else "B",500+i,"PQ") for i in range(10))
                inv_hold=tuple(external_direction_episode(ms,world,"A" if i<3 else "B",600+i,"PQ") for i in range(6))
                sensor_inverted=derive_directional_relation_candidate(ms,inv_train,inv_hold,rx,ry)
            finally:
                world.observe=original_observe
            assert sensor_inverted["status"]=="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY",sensor_inverted
            assert sensor_inverted["ordered_operational_referent_signatures"]==cand["ordered_operational_referent_signatures"]

            action_ids_after=set(ms.capabilities.contracts)
            assert action_ids_after==action_ids_before, (action_ids_before,action_ids_after)
            assert "derived_relation_id" in cand and all("capability" not in k.lower() for k in cand)
            assert "relation_signal_id" not in cand and "predicate" not in cand["relation_form"].lower()
            assert not hasattr(ms,"predicate_registry") and not hasattr(ms,"language_module") and not hasattr(ms,"faculty_registry")
            persisted_candidate=json.dumps(cand,sort_keys=True)
        finally: ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()

        # Restart does not make the relation current by memory alone. Rebuild current B1 owners, then require fresh external evidence.
        ms2,world2,rx2,ry2=build_two_relations(Path(td))
        try:
            restored=json.loads(persisted_candidate)
            restart_action_ids_before=set(ms2.capabilities.contracts)
            restart_same=revalidate_directional_relation(ms2,world2,restored,rx2,ry2,"PQ",700)
            restart_reversed=revalidate_directional_relation(ms2,world2,restored,rx2,ry2,"QP",800)
            assert restart_same["status"]=="CURRENT_DIRECTIONAL_RELATION_REVALIDATED_RESEARCH_ONLY"
            assert restart_reversed["status"]=="DEFER_UNKNOWN" and restart_reversed["reason"]=="POST_BINDING_EMPIRICAL_DIRECTION_DRIFT"
            restart_action_ids_after=set(ms2.capabilities.contracts)
            assert restart_action_ids_after==restart_action_ids_before
        finally: ms2.biography.close();ms2.evidence.conn.close();ms2.store.conn.close()
    return {"status":"PASS","candidate":cand,"frame":frame,"reversed_argument_order":reversed_frame,
      "convention_reversal":convention_reversal,"fresh_same":fresh_same,"fresh_reversed":fresh_reversed,"sensor_polarity_inverted":sensor_inverted,
      "restart_same":restart_same,"restart_reversed":restart_reversed,
      "new_microseed_action_contracts_registered":sorted(action_ids_after-action_ids_before),
      "restart_new_microseed_action_contracts_registered":sorted(restart_action_ids_after-restart_action_ids_before),
      "earned":"REPEATED_CURRENT_ASYMMETRIC_EXTERNAL_OUTCOMES_OVER_TWO_CURRENT_B1_REFERENTS_CAN_SUPPORT_AN_ORDERED_OPERATIONAL_RELATION_AND_ORDER_CHECKED_RELATIONAL_FRAME_WITHOUT_REGISTERING_A_NEW_RELATION_ACTION_CAPABILITY_SUPPLYING_SEMANTIC_ROLES_OR_INSTALLING_A_GENERIC_CAPABILITY_FACULTY",
      "technical_name":"AFFORDANCE_RELATIVE_GROUNDED_ORDER_RELATION_FROM_EXTERNAL_OUTCOME_EVIDENCE",
      "nonclaim":"THE_DERIVED_ORDER_IS_NOT_A_SEMANTIC_PREDICATE_PROPOSITION_TRUTH_BEARER_LANGUAGE_FACULTY_OR_EXECUTION_CAPABILITY",
      "next":"PRESS_RELATION_HANDLE_TO_OPAQUE_OBSERVED_TOKEN_BINDING_WITHOUT_EXECUTABLE_RELATION_ACTION_PREDICATE_OR_CAPABILITY_PRIMITIVES_BEFORE_ANY_PROPOSITIONAL_COMPOSITION"}

if __name__=='__main__':print(json.dumps(run_campaign(),indent=2,sort_keys=True))
