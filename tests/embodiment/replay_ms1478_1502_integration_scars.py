from __future__ import annotations
import json
from pathlib import Path
from microseed import OperationalTrace, ExternalCapabilityQualifier, EpistemicStatus, QualificationState
from test_ms1502_integration import seeded, seed_discovery_traces, discovered

def main():
 td,ms=seeded(); checks={}
 try:
  seed_discovery_traces(ms); c=discovered(ms); s=c.operational_signature
  t=ms.record_operational_trace(OperationalTrace('scar-joint',('A','B'),((1.0,0.0),(0.0,2.0)),'scar',topology_ids=('T',),coordination_ids=('R',)))
  checks['trace_binds_existing_topology_epoch']=t.topology_epochs==(('T',0),)
  checks['trace_binds_existing_coordination_epoch']=t.coordination_epochs==(('R',0),)
  checks['coordination_ancestry_inherits_counterparties']=t.counterparty_epochs==(('CPA',0),('CPB',0))
  checks['discovery_preserves_topology_epoch']=s['topology_epochs']==[['T',0]]
  checks['discovery_preserves_counterparty_epochs']=s['counterparty_epochs']==[['CPA',0],['CPB',0]]
  checks['discovery_preserves_coordination_epoch']=s['coordination_epochs']==[['R',0]]
  checks['candidate_remains_proposal_only']=c.proposed_contract.qualification==QualificationState.CANDIDATE
  q=ms.append_evidence('SCAR-Q1502',{'heldout':'independent'},EpistemicStatus.PROVED,source='HSP_EXTERNAL'); ticket=ExternalCapabilityQualifier(ms.evidence,qualifier_id='HSP-SCAR-MS1502').qualify(c,qualification_evidence=(q,)); a=ms.admit_capability_candidate(ticket)
  checks['existing_external_qualification_and_admission_path_reused']=a.qualification in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED}
  stale=ms.change_operational_coordination('R',reason='SCAR-COORDINATION-DRIFT')
  checks['coordination_drift_stales_composite']=a.capability_id in stale and ms.capabilities.contracts[a.capability_id].qualification==QualificationState.STALE
  checks['coordination_drift_does_not_stale_children']=ms.capabilities.contracts['A'].qualification in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED} and ms.capabilities.contracts['B'].qualification in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED}
  checks['history_preserved_after_stale']=a.capability_id in ms.capabilities.contracts
  checks['no_multi_child_planner_or_self_qualification']=not hasattr(ms,'multi_child_planner') and not hasattr(ms,'auto_qualify_composition')
  out={'all_pass':all(checks.values()),'checks':checks}
  Path(__file__).resolve().parents[2].joinpath('MS1478_1502_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
  print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out['all_pass'] else 1
 finally: td.cleanup()
if __name__=='__main__': raise SystemExit(main())
