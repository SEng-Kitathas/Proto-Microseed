from __future__ import annotations
import json,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from microseed import Microseed,Authority,QualificationState,CapabilityContract,OperationalCounterpartyContract,CapabilityCandidate,ExternalCapabilityQualifier,EpistemicStatus

def cp(cid="P"):
 c=OperationalCounterpartyContract(counterparty_id=cid,purpose="opaque",signature_sha256="",authority=Authority.DERIVED_READ_ONLY,lineage=("MS1053-1077",),currentness="CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=("HSP_EXTERNAL_COUNTERPARTY_QUALIFICATION",));c.signature_sha256=c.computed_signature_sha256();return c
def main():
 with tempfile.TemporaryDirectory(prefix="ms1053-1077-replay-") as td:
  ms=Microseed(Path(td));ms.register_operational_counterparty(cp())
  a=CapabilityContract("J","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1053-1077",),"CURRENT",{},qualification=QualificationState.SHADOW_QUALIFIED)
  b=CapabilityContract("K","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1053-1077",),"CURRENT",{},dependencies=("J",),qualification=QualificationState.SHADOW_QUALIFIED)
  ms.register_capability(a,counterparty_dependencies=(("P",0),));ms.register_capability(b)
  pre=ms.compose(["K"]).status;stale=ms.change_operational_counterparty("P",reason="REPLAY_DRIFT");post=ms.compose(["K"]).status
  ms2=Microseed(Path(td)/"pending");ms2.register_operational_counterparty(cp())
  pe=ms2.append_evidence("PE",{"proposal":1},EpistemicStatus.PRESSURE_SUPPORTED);qe=ms2.append_evidence("QE",{"heldout":1},EpistemicStatus.PROVED)
  c=CapabilityContract("PJ","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1053-1077",),"CANDIDATE",{},qualification=QualificationState.CANDIDATE)
  cand=CapabilityCandidate("PJ",c,(pe,),operational_signature={"counterparty_epochs":[["P",0]]});ms2.nominate_capability_candidate(cand);ticket=ExternalCapabilityQualifier(ms2.evidence).qualify(cand,qualification_evidence=(qe,));ms2.change_operational_counterparty("P",reason="POST_TICKET")
  rejected=False
  try:ms2.admit_capability_candidate(ticket)
  except ValueError as e:rejected="CANDIDATE_COUNTERPARTY_EPOCH_DRIFT" in str(e)
  s=ms.status();checks={
   "distributed_capability_current_before_partner_drift":pre=="COMPOSED_EPHEMERAL",
   "partner_drift_stales_joint_and_transitive_dependent":{"J","K"}<=stale and post=="NO_PATH",
   "pending_candidate_rechecks_counterparty_epoch":rejected,
   "counterparty_has_no_identity_authority":s["counterparty_semantic_identity_authority"]=="NONE" and s["counterparty_numerical_identity_authority"]=="NONE",
   "agent_discovery_not_promoted":s["agent_discovery"].startswith("BOUNDED_RESEARCH"),
   "prelingual_hard_stop":s["language"]=="DEFERRED_PRELINGUAL_COGNITION_ACTIVE" and s["next_ms"]>=1203 and s.get(f"ms{s['next_ms']}_started") is False,
   "selected_frontier":s["research_terminal_ms"]>=1252 and s["frontier"].startswith("ATTN-MS"),
  }
  out={"schema":"microseed.ms1053-1077.maindev-replay.v1.1","checks":checks,"all_pass":all(checks.values()),"status":s,"stale":sorted(stale)}
  print(json.dumps(out,indent=2,sort_keys=True));return 0 if out["all_pass"] else 1
if __name__=="__main__":raise SystemExit(main())
