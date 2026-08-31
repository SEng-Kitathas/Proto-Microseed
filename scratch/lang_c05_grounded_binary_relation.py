from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from microseed import Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _build,_cap,_observe,_calibrate,derive_binding_candidate,_use_episode
from scratch.lang_c01_operational_reference_relation import admit_operational_reference_relation,resolve_current_operational_referent
from scratch.lang_c02_multi_token_restart_revalidation import add_sig_y,episodes

NONE={"semantic_reference_authority":"NONE","predicate_authority":"NONE","truth_authority":"NONE","execution_authority":"NONE","semantic_identity_authority":"NONE"}

def add_relation_signal(ms,world):
    def rel(**_):
        world.latent[0]+=1; world.latent[1]+=1
        return {"opaque_action_receipt":"SIG-R"}
    ms.register_capability(_cap("SIG-R",Authority.EFFECT,rel),coordination_dependencies=(("COORD-X",0),))
    # readable relation-shaped token intentionally ungrounded
    ms.register_capability(_cap("between",Authority.EFFECT,lambda **_: {"opaque_action_receipt":"between"}),coordination_dependencies=(("COORD-X",0),))

def build_refs(root:Path):
    ms,world=_build(root); add_sig_y(ms,world); add_relation_signal(ms,world)
    tx=episodes(ms,world,"SIG-X","A",0,10); hx=episodes(ms,world,"SIG-X","B",100,6)
    ty=episodes(ms,world,"SIG-Y","A",200,10); hy=episodes(ms,world,"SIG-Y","B",300,6)
    rx=admit_operational_reference_relation(ms,derive_binding_candidate(ms,tx,hx,"SIG-X"))
    ry=admit_operational_reference_relation(ms,derive_binding_candidate(ms,ty,hy,"SIG-Y"))
    assert rx["status"]==ry["status"]=="CURRENT_OPERATIONAL_REFERENCE_RELATION_RESEARCH_ONLY"
    return ms,world,rx,ry

def relation_episode(ms,world,signal_id:str,layout:str,index:int)->dict[str,object]:
    world.configure_layout(layout); world.configure_alias(False)
    cal=_calibrate(ms,world)
    if cal["status"]!="REFERENT_PARTITION_NOMINATED": return {"status":"DEFER_UNKNOWN","reason":"CURRENT_REFERENT_PARTITION_REQUIRED"}
    world.reset_state(); before=_observe(ms); receipt=ms.capabilities.invoke(signal_id, __import__('scratch.ms2046_grounded_operational_token_referent_binding_quarry',fromlist=['ACT']).ACT); after=_observe(ms)
    changed={i for i,(a,b) in enumerate(zip(before,after)) if a!=b}
    touched=[]
    for row in cal["rows"]:
        g=set(row["group"])
        if g and g.issubset(changed): touched.append(str(row["signature_sha256"]))
    if len(touched)!=2:
        return {"status":"DEFER_UNKNOWN","reason":"EXACT_TWO_CURRENT_OPERATIONAL_REFERENTS_MUST_BE_TOUCHED","touched":touched}
    cap=ms.capabilities.contracts[signal_id]
    return {"status":"CURRENT_GROUNDED_BINARY_RELATION_USE_EPISODE","episode_index":index,"relation_signal_id":signal_id,
      "relation_signal_epoch":ms.capabilities.epochs[signal_id],"relation_signal_signature":cap.computed_signature_sha256(),
      "referent_signature_set":sorted(touched),"receipt":receipt["value"]}

def derive_relation_candidate(ms,episodes:list[dict[str,object]],rx,ry,signal_id="SIG-R"):
    if len(episodes)<8:return {**NONE,"status":"DEFER_UNKNOWN","reason":"SUFFICIENT_RELATION_USE_HISTORY_REQUIRED"}
    if any(e.get("status")!="CURRENT_GROUNDED_BINARY_RELATION_USE_EPISODE" for e in episodes):return {**NONE,"status":"DEFER_UNKNOWN","reason":"EVERY_RELATION_EPISODE_MUST_GROUND_EXACTLY"}
    x=resolve_current_operational_referent(ms,rx,"SIG-X"); y=resolve_current_operational_referent(ms,ry,"SIG-Y")
    if x["status"]!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY" or y["status"]!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY":return {**NONE,"status":"DEFER_UNKNOWN","reason":"TWO_CURRENT_B1_REFERENTS_REQUIRED"}
    target=sorted([x["operational_referent_signature_sha256"],y["operational_referent_signature_sha256"]])
    sets={tuple(e["referent_signature_set"]) for e in episodes}
    if sets!={tuple(target)}:return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_EPISODES_DISAGREE_ON_REFERENT_PAIR"}
    if not ms.capabilities.is_current(signal_id):return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_SIGNAL_NOT_CURRENT"}
    cap=ms.capabilities.contracts[signal_id]
    first=episodes[0]
    if first["relation_signal_epoch"]!=ms.capabilities.epochs[signal_id] or first["relation_signal_signature"]!=cap.computed_signature_sha256():return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_SIGNAL_DESCRIPTOR_DRIFT"}
    return {**NONE,"status":"GROUNDED_OPERATIONAL_BINARY_RELATION_CANDIDATE_RESEARCH_ONLY","relation_token_capability_id":signal_id,
      "component_operational_referent_signatures":target,"relation_form":"SYMMETRIC_BINARY_COEFFECT","authority_gain":"NONE"}

def compose_relational_frame(ms,relation_candidate,rx,ry):
    if relation_candidate.get("status")!="GROUNDED_OPERATIONAL_BINARY_RELATION_CANDIDATE_RESEARCH_ONLY":return {**NONE,"status":"DEFER_UNKNOWN","reason":"GROUNDED_BINARY_RELATION_CANDIDATE_REQUIRED"}
    x=resolve_current_operational_referent(ms,rx,"SIG-X"); y=resolve_current_operational_referent(ms,ry,"SIG-Y")
    if x.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY" or y.get("status")!="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY":return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_B1_COMPONENTS_REQUIRED"}
    if sorted([x["operational_referent_signature_sha256"],y["operational_referent_signature_sha256"]])!=relation_candidate["component_operational_referent_signatures"]:return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_COMPONENT_BINDING_MISMATCH"}
    return {**NONE,"status":"B2_GROUNDED_BINARY_RELATIONAL_REFERENCE_FRAME_RESEARCH_ONLY","relation_token_capability_id":relation_candidate["relation_token_capability_id"],
      "arguments":[x["operational_referent_signature_sha256"],y["operational_referent_signature_sha256"]],"relation_form":relation_candidate["relation_form"],"authority_gain":"NONE"}

def run_campaign():
    with tempfile.TemporaryDirectory(prefix='lang-c05-') as td:
        ms,world,rx,ry=build_refs(Path(td))
        try:
            eps=[relation_episode(ms,world,"SIG-R","A" if i<6 else "B",i) for i in range(12)]
            cand=derive_relation_candidate(ms,eps,rx,ry); assert cand["status"]=="GROUNDED_OPERATIONAL_BINARY_RELATION_CANDIDATE_RESEARCH_ONLY",cand
            frame=compose_relational_frame(ms,cand,rx,ry); assert frame["status"]=="B2_GROUNDED_BINARY_RELATIONAL_REFERENCE_FRAME_RESEARCH_ONLY",frame
            readable=derive_relation_candidate(ms,[],rx,ry,signal_id="between"); assert readable["status"]=="DEFER_UNKNOWN"
            ms.invalidate_capability("SIG-R",reason="LANG_C05_RELATION_DRIFT")
            stale=derive_relation_candidate(ms,eps,rx,ry); assert stale["status"]=="DEFER_UNKNOWN"
        finally:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
    assert frame["semantic_reference_authority"]==frame["predicate_authority"]==frame["truth_authority"]==frame["execution_authority"]=="NONE"
    return {"status":"PASS","candidate":cand,"frame":frame,"readable_ungrounded":readable,"stale_relation":stale,
      "earned":"REPEATED_CURRENT_RELATION_SIGNAL_USE_CAN_GROUND_A_BINARY_OPERATIONAL_RELATION_OVER_TWO_CURRENT_B1_REFERENTS_AND_FORM_A_B2_RELATIONAL_REFERENCE_FRAME_WITHOUT_PREDICATE_OR_TRUTH_AUTHORITY",
      "nonclaim":"SYMMETRIC_COEFFECT_RELATION_IS_NOT_YET_A_SEMANTIC_PREDICATE_OR_DIRECTIONAL_RELATION",
      "next":"PRESS_DIRECTIONAL_RELATION_AND_PREDICATE_PARAMETERIZATION_WITHOUT_SUPPLIED_VOCABULARY"}
if __name__=='__main__':print(json.dumps(run_campaign(),indent=2,sort_keys=True))
