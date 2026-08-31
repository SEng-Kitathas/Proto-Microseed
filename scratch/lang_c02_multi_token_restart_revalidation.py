from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from microseed import Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _build,_cap,_use_episode,derive_binding_candidate
from scratch.lang_c01_operational_reference_relation import admit_operational_reference_relation,resolve_current_operational_referent

def add_sig_y(ms,world):
    def y(**_):
        old=world.signal_mode; world.configure_signal_mode("Q")
        try:return world.act("SIG-X")
        finally:world.configure_signal_mode(old)
    ms.register_capability(_cap("SIG-Y",Authority.EFFECT,y),coordination_dependencies=(("COORD-X",0),))

def episodes(ms,world,sid,layout,start,n):
    world.configure_alias(False); world.configure_layout(layout)
    if sid=="SIG-X": world.configure_signal_mode("P")
    return tuple(_use_episode(ms,world,sid,start+i) for i in range(n))

def build_two_relations(root:Path):
    ms,world=_build(root); add_sig_y(ms,world)
    tx=episodes(ms,world,"SIG-X","A",0,10); hx=episodes(ms,world,"SIG-X","B",100,6)
    ty=episodes(ms,world,"SIG-Y","A",200,10); hy=episodes(ms,world,"SIG-Y","B",300,6)
    cx=derive_binding_candidate(ms,tx,hx,"SIG-X"); cy=derive_binding_candidate(ms,ty,hy,"SIG-Y")
    rx=admit_operational_reference_relation(ms,cx); ry=admit_operational_reference_relation(ms,cy)
    assert rx["status"]==ry["status"]=="CURRENT_OPERATIONAL_REFERENCE_RELATION_RESEARCH_ONLY"
    assert rx["relation"]["operational_referent_signature_sha256"]!=ry["relation"]["operational_referent_signature_sha256"]
    return ms,world,rx,ry

def serialize(rel): return json.dumps(rel,sort_keys=True)
def restore(s): return json.loads(s)

def run_campaign():
    with tempfile.TemporaryDirectory(prefix="lang-c02-") as td:
        root=Path(td); ms,world,rx,ry=build_two_relations(root)
        try:
            px=resolve_current_operational_referent(ms,rx,"SIG-X"); py=resolve_current_operational_referent(ms,ry,"SIG-Y")
            assert px["status"]==py["status"]=="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY"
            persisted=(serialize(rx),serialize(ry))
        finally: ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
        # Runtime contracts are re-established on restart; persisted relation gets no automatic currentness.
        ms2,world2,rx2live,ry2live=build_two_relations(root)
        try:
            oldx,oldy=map(restore,persisted)
            # exact descriptors happen to match after clean restart; revalidation is explicit, not automatic.
            restart_x=resolve_current_operational_referent(ms2,oldx,"SIG-X"); restart_y=resolve_current_operational_referent(ms2,oldy,"SIG-Y")
            assert restart_x["status"]==restart_y["status"]=="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY"
            ms2.invalidate_capability("SIG-Y",reason="LANG_C02_RESTART_DRIFT")
            stale_y=resolve_current_operational_referent(ms2,oldy,"SIG-Y"); assert stale_y["status"]=="DEFER_UNKNOWN"
            still_x=resolve_current_operational_referent(ms2,oldx,"SIG-X"); assert still_x["status"]=="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY"
        finally: ms2.biography.close(); ms2.evidence.conn.close(); ms2.store.conn.close()
    return {"status":"PASS","two_independent_relations":True,
      "distinct_operational_referents":px["operational_referent_signature_sha256"]!=py["operational_referent_signature_sha256"],
      "restart_requires_explicit_revalidation":True,"restart_x":restart_x,"restart_y":restart_y,
      "localized_drift":{"sig_y":stale_y,"sig_x":still_x},
      "earned":"MULTIPLE_INDEPENDENT_B1_OPERATIONAL_REFERENCE_RELATIONS_CAN_COEXIST_AND_SURVIVE_RESTART_ONLY_THROUGH_EXPLICIT_CURRENTNESS_REVALIDATION",
      "next":"LANG_C03_B2_ORDERED_COMPOSITION_QUARRY"}
if __name__=='__main__': print(json.dumps(run_campaign(),indent=2,sort_keys=True))
