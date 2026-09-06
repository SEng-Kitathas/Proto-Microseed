from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from microseed import Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _cap,_calibrate,_observe,ACT
from scratch.lang_c01_operational_reference_relation import resolve_current_operational_referent
from scratch.lang_c03_b2_ordered_reference_composition import compose_ordered
from scratch.lang_c05_grounded_binary_relation import build_refs

NONE={"semantic_reference_authority":"NONE","predicate_authority":"NONE","truth_authority":"NONE","execution_authority":"NONE","language_authority":"NONE","semantic_identity_authority":"NONE"}


def _configure_direction(world,mode:str)->None:
    if mode not in {"PQ","QP"}: raise ValueError(mode)
    world._c06_direction_mode=mode


def add_directional_relation_signals(ms,world):
    _configure_direction(world,"PQ")
    def act_direction(**_):
        mode=getattr(world,"_c06_direction_mode","PQ")
        if mode=="PQ":
            world.latent[0]-=1; world.latent[1]+=1
        elif mode=="QP":
            world.latent[1]-=1; world.latent[0]+=1
        else: raise ValueError(mode)
        return {"opaque_action_receipt":"C06-DIRECTION-EFFECT"}
    # Both surfaces share the same physical law. Human readability has no authority.
    for sid in ("SIG-D","gives"):
        ms.register_capability(_cap(sid,Authority.EFFECT,act_direction),coordination_dependencies=(("COORD-X",0),))


def direction_episode(ms,world,signal_id:str,layout:str,index:int,mode:str="PQ")->dict[str,object]:
    world.configure_layout(layout); world.configure_alias(False); _configure_direction(world,mode)
    cal=_calibrate(ms,world)
    if cal["status"]!="REFERENT_PARTITION_NOMINATED" or len(cal["rows"])!=2:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_TWO_CURRENT_OPERATIONAL_REFERENTS_REQUIRED"}
    world.reset_state(); before=_observe(ms)
    receipt=ms.capabilities.invoke(signal_id,ACT)
    after=_observe(ms)
    by_effect={}
    diagnostic=[]
    for row in cal["rows"]:
        group=tuple(row["group"]); deltas=tuple(after[i]-before[i] for i in group)
        if deltas and all(d<0 for d in deltas): effect_class="NEGATIVE_RAW_CHANGE"
        elif deltas and all(d>0 for d in deltas): effect_class="POSITIVE_RAW_CHANGE"
        else:
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_EFFECT_NOT_SIGN_COHERENT_ON_CURRENT_REFERENT","group":group,"deltas":deltas}
        if effect_class in by_effect:
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_EFFECT_CLASS_NOT_UNIQUE"}
        by_effect[effect_class]=str(row["signature_sha256"])
        diagnostic.append({"operational_referent_signature_sha256":str(row["signature_sha256"]),"raw_effect_class":effect_class,"channel_deltas":deltas})
    if set(by_effect)!={"NEGATIVE_RAW_CHANGE","POSITIVE_RAW_CHANGE"}:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"ONE_NEGATIVE_AND_ONE_POSITIVE_CURRENT_REFERENT_EFFECT_REQUIRED"}
    cap=ms.capabilities.contracts[signal_id]
    return {**NONE,"status":"CURRENT_GROUNDED_DIRECTIONAL_RELATION_USE_EPISODE","episode_index":index,
      "relation_signal_id":signal_id,"relation_signal_epoch":ms.capabilities.epochs[signal_id],
      "relation_signal_signature":cap.computed_signature_sha256(),
      "ordered_operational_referent_signatures":[by_effect["NEGATIVE_RAW_CHANGE"],by_effect["POSITIVE_RAW_CHANGE"]],
      "order_basis":"NEGATIVE_RAW_CHANGE_THEN_POSITIVE_RAW_CHANGE","diagnostic":diagnostic,"receipt":receipt["value"]}


def derive_directional_relation_candidate(ms,episodes,rx,ry,signal_id="SIG-D"):
    if len(episodes)<8:return {**NONE,"status":"DEFER_UNKNOWN","reason":"SUFFICIENT_DIRECTIONAL_RELATION_USE_HISTORY_REQUIRED"}
    if any(e.get("status")!="CURRENT_GROUNDED_DIRECTIONAL_RELATION_USE_EPISODE" for e in episodes):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EVERY_DIRECTIONAL_RELATION_EPISODE_MUST_GROUND_EXACTLY"}
    x=resolve_current_operational_referent(ms,rx,"SIG-X"); y=resolve_current_operational_referent(ms,ry,"SIG-Y")
    if x.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY" or y.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"TWO_CURRENT_B1_REFERENTS_REQUIRED"}
    current={x["operational_referent_signature_sha256"],y["operational_referent_signature_sha256"]}
    orders={tuple(e["ordered_operational_referent_signatures"]) for e in episodes}
    if len(orders)!=1:return {**NONE,"status":"DEFER_UNKNOWN","reason":"DIRECTIONAL_RELATION_EPISODES_DISAGREE_ON_ORDER"}
    order=next(iter(orders))
    if len(order)!=2 or set(order)!=current:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"DIRECTIONAL_RELATION_COMPONENT_BINDING_MISMATCH"}
    if not ms.capabilities.is_current(signal_id):return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_SIGNAL_NOT_CURRENT"}
    cap=ms.capabilities.contracts[signal_id]; first=episodes[0]
    if first["relation_signal_id"]!=signal_id or first["relation_signal_epoch"]!=ms.capabilities.epochs[signal_id] or first["relation_signal_signature"]!=cap.computed_signature_sha256():
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_SIGNAL_DESCRIPTOR_DRIFT"}
    return {**NONE,"status":"GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY",
      "relation_signal_id":signal_id,"relation_signal_epoch":ms.capabilities.epochs[signal_id],
      "relation_signal_signature":cap.computed_signature_sha256(),"ordered_operational_referent_signatures":list(order),
      "order_basis":"NEGATIVE_RAW_CHANGE_THEN_POSITIVE_RAW_CHANGE","relation_form":"SIGNED_ORDERED_COEFFECT",
      "authority_gain":"NONE"}


def compose_directional_frame(ms,candidate,components):
    if candidate.get("status")!="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"GROUNDED_DIRECTIONAL_RELATION_CANDIDATE_REQUIRED"}
    ordered=compose_ordered(ms,components)
    if ordered.get("status")!="B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_ORDERED_B1_COMPOSITION_REQUIRED","component":ordered}
    actual=[c["operational_referent_signature_sha256"] for c in ordered["components"]]
    if actual!=candidate["ordered_operational_referent_signatures"]:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"ARGUMENT_ORDER_NOT_GROUNDED_BY_RELATION_USE","observed_relation_order":candidate["ordered_operational_referent_signatures"],"requested_order":actual}
    sid=candidate["relation_signal_id"]
    if not ms.capabilities.is_current(sid):return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_SIGNAL_NOT_CURRENT"}
    cap=ms.capabilities.contracts[sid]
    if candidate["relation_signal_epoch"]!=ms.capabilities.epochs[sid] or candidate["relation_signal_signature"]!=cap.computed_signature_sha256():
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_SIGNAL_DESCRIPTOR_DRIFT"}
    return {**NONE,"status":"B2_GROUNDED_DIRECTIONAL_RELATIONAL_REFERENCE_FRAME_RESEARCH_ONLY","relation_signal_id":sid,
      "arguments":actual,"relation_form":"SIGNED_ORDERED_COEFFECT","order_basis":candidate["order_basis"],"authority_gain":"NONE"}


def _components_in_candidate_order(ms,candidate,rx,ry):
    x=resolve_current_operational_referent(ms,rx,"SIG-X"); y=resolve_current_operational_referent(ms,ry,"SIG-Y")
    lookup={x["operational_referent_signature_sha256"]:("SIG-X",rx),y["operational_referent_signature_sha256"]:("SIG-Y",ry)}
    return [lookup[s] for s in candidate["ordered_operational_referent_signatures"]]


def run_campaign():
    with tempfile.TemporaryDirectory(prefix='lang-c06-') as td:
        ms,world,rx,ry=build_refs(Path(td)); add_directional_relation_signals(ms,world)
        try:
            eps=[direction_episode(ms,world,"SIG-D","A" if i<6 else "B",i,"PQ") for i in range(12)]
            cand=derive_directional_relation_candidate(ms,eps,rx,ry,"SIG-D")
            assert cand["status"]=="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY",cand
            components=_components_in_candidate_order(ms,cand,rx,ry)
            frame=compose_directional_frame(ms,cand,components)
            assert frame["status"]=="B2_GROUNDED_DIRECTIONAL_RELATIONAL_REFERENCE_FRAME_RESEARCH_ONLY",frame
            reversed_frame=compose_directional_frame(ms,cand,list(reversed(components)))
            assert reversed_frame["status"]=="DEFER_UNKNOWN" and reversed_frame["reason"]=="ARGUMENT_ORDER_NOT_GROUNDED_BY_RELATION_USE"

            # Readable surface has no privilege; with the same actual history it grounds the same operational order, still without semantics.
            readable_eps=[direction_episode(ms,world,"gives","A" if i<6 else "B",100+i,"PQ") for i in range(12)]
            readable=derive_directional_relation_candidate(ms,readable_eps,rx,ry,"gives")
            assert readable["status"]=="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY"
            assert readable["ordered_operational_referent_signatures"]==cand["ordered_operational_referent_signatures"]
            assert readable["semantic_reference_authority"]==readable["predicate_authority"]==readable["language_authority"]=="NONE"

            # A convention reversal in fresh held-out reality prevents one stable directional binding.
            reversal=[direction_episode(ms,world,"SIG-D","A",200+i,"PQ") for i in range(6)] + [direction_episode(ms,world,"SIG-D","B",300+i,"QP") for i in range(6)]
            reversed_candidate=derive_directional_relation_candidate(ms,reversal,rx,ry,"SIG-D")
            assert reversed_candidate["status"]=="DEFER_UNKNOWN" and reversed_candidate["reason"]=="DIRECTIONAL_RELATION_EPISODES_DISAGREE_ON_ORDER"

            ms.invalidate_capability("SIG-D",reason="LANG_C06_RELATION_SIGNAL_DRIFT")
            stale=compose_directional_frame(ms,cand,components)
            assert stale["status"]=="DEFER_UNKNOWN" and stale["reason"]=="RELATION_SIGNAL_NOT_CURRENT"

            assert not hasattr(ms,"predicate_registry")
            assert not hasattr(ms,"language_module")
            assert not hasattr(ms,"faculty_registry")
        finally: ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
    return {"status":"PASS","candidate":cand,"frame":frame,"reversed_argument_order":reversed_frame,
      "readable_surface_same_grounding":readable,"convention_reversal":reversed_candidate,"stale_relation":stale,
      "earned":"REPEATED_CURRENT_ASYMMETRIC_GROUNDED_RELATION_USE_CAN_SUPPORT_AN_ORDERED_OPERATIONAL_RELATION_OVER_TWO_CURRENT_B1_REFERENTS_WITHOUT_SUPPLIED_SEMANTIC_ROLES_PREDICATE_MEANING_OR_A_GENERIC_CAPABILITY_FACULTY",
      "technical_name":"GROUNDED_SIGNED_ORDER_RELATION",
      "nonclaim":"SIGNED_ORDERED_COEFFECT_IS_NOT_YET_A_SEMANTIC_PREDICATE_PROPOSITION_TRUTH_BEARER_OR_LANGUAGE_CAPABILITY",
      "next":"PRESS_REPRESENTATION_INVARIANCE_AND_FRESH_POST_BINDING_EMPIRICAL_CURRENTNESS_BEFORE_ANY_PROPOSITIONAL_COMPOSITION"}

if __name__=='__main__':print(json.dumps(run_campaign(),indent=2,sort_keys=True))
