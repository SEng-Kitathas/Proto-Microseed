from __future__ import annotations
import json
import pytest
from microseed import OperationalTrace, ExternalCapabilityQualifier, EpistemicStatus, QualificationState
from test_ms1502_integration import seeded, seed_discovery_traces, discovered

def run():
 checks={}
 # 1 unknown topology cannot enter trace ancestry
 td,ms=seeded()
 try:
  try: ms.record_operational_trace(OperationalTrace('h1',('A',),((1.0,),),topology_ids=('NOPE',))); ok=False
  except ValueError as e: ok='unknown/stale recruitment topology:NOPE' in str(e)
  checks['unknown_topology_rejected']=ok
 finally: td.cleanup()
 # 2 stale topology cannot enter trace ancestry
 td,ms=seeded()
 try:
  ms.change_recruitment_topology('T',reason='HOSTILE')
  try: ms.record_operational_trace(OperationalTrace('h2',('A',),((1.0,),),topology_ids=('T',))); ok=False
  except ValueError as e: ok='unknown/stale recruitment topology:T' in str(e)
  checks['stale_topology_rejected']=ok
 finally: td.cleanup()
 # 3 unknown counterparty
 td,ms=seeded()
 try:
  try: ms.record_operational_trace(OperationalTrace('h3',('A',),((1.0,),),counterparty_ids=('NOPE',))); ok=False
  except ValueError as e: ok='unknown/stale operational counterparty:NOPE' in str(e)
  checks['unknown_counterparty_rejected']=ok
 finally: td.cleanup()
 # 4 stale counterparty
 td,ms=seeded()
 try:
  ms.change_operational_counterparty('CPA',reason='HOSTILE')
  try: ms.record_operational_trace(OperationalTrace('h4',('A',),((1.0,),),counterparty_ids=('CPA',))); ok=False
  except ValueError as e: ok='unknown/stale operational counterparty:CPA' in str(e)
  checks['stale_counterparty_rejected']=ok
 finally: td.cleanup()
 # 5 unknown coordination
 td,ms=seeded()
 try:
  try: ms.record_operational_trace(OperationalTrace('h5',('A',),((1.0,),),coordination_ids=('NOPE',))); ok=False
  except ValueError as e: ok='unknown/stale operational coordination:NOPE' in str(e)
  checks['unknown_coordination_rejected']=ok
 finally: td.cleanup()
 # 6 stale coordination
 td,ms=seeded()
 try:
  ms.change_operational_coordination('R',reason='HOSTILE')
  try: ms.record_operational_trace(OperationalTrace('h6',('A',),((1.0,),),coordination_ids=('R',))); ok=False
  except ValueError as e: ok='unknown/stale operational coordination:R' in str(e)
  checks['stale_coordination_rejected']=ok
 finally: td.cleanup()
 # 7 coordination ancestry must pull participant counterparties
 td,ms=seeded()
 try:
  t=ms.record_operational_trace(OperationalTrace('h7',('A','B'),((1.0,),(2.0,)),coordination_ids=('R',)))
  checks['coordination_inherits_counterparty_ancestry']=t.counterparty_epochs==(('CPA',0),('CPB',0))
 finally: td.cleanup()
 # 8 candidate keeps all epoch families proposal-only
 td,ms=seeded()
 try:
  seed_discovery_traces(ms); c=discovered(ms); s=c.operational_signature
  checks['candidate_preserves_existing_epoch_families_without_authority_gain']=(s['topology_epochs']==[['T',0]] and s['counterparty_epochs']==[['CPA',0],['CPB',0]] and s['coordination_epochs']==[['R',0]] and c.proposed_contract.qualification==QualificationState.CANDIDATE)
 finally: td.cleanup()
 # 9 post-ticket topology drift blocks existing admission route
 td,ms=seeded()
 try:
  seed_discovery_traces(ms); c=discovered(ms); q=ms.append_evidence('H9',{'heldout':1},EpistemicStatus.PROVED,source='HSP_EXTERNAL'); t=ExternalCapabilityQualifier(ms.evidence).qualify(c,qualification_evidence=(q,)); ms.change_recruitment_topology('T',reason='HOSTILE')
  try: ms.admit_capability_candidate(t); ok=False
  except ValueError as e: ok='CANDIDATE_TOPOLOGY_EPOCH_DRIFT:T' in str(e)
  checks['post_ticket_topology_drift_blocks_admission']=ok
 finally: td.cleanup()
 # 10 post-ticket counterparty drift blocks via existing currentness chain
 td,ms=seeded()
 try:
  seed_discovery_traces(ms); c=discovered(ms); q=ms.append_evidence('H10',{'heldout':1},EpistemicStatus.PROVED,source='HSP_EXTERNAL'); t=ExternalCapabilityQualifier(ms.evidence).qualify(c,qualification_evidence=(q,)); ms.change_operational_counterparty('CPA',reason='HOSTILE')
  try: ms.admit_capability_candidate(t); ok=False
  except ValueError as e: ok=('CANDIDATE_COUNTERPARTY_EPOCH_DRIFT:CPA' in str(e) or 'CANDIDATE_COORDINATION_EPOCH_DRIFT:R' in str(e))
  checks['post_ticket_counterparty_drift_blocks_admission']=ok
 finally: td.cleanup()
 # 11 admitted composite selectively stales without staling child capabilities
 td,ms=seeded()
 try:
  seed_discovery_traces(ms); c=discovered(ms); q=ms.append_evidence('H11',{'heldout':1},EpistemicStatus.PROVED,source='HSP_EXTERNAL'); t=ExternalCapabilityQualifier(ms.evidence).qualify(c,qualification_evidence=(q,)); a=ms.admit_capability_candidate(t); stale=ms.change_operational_coordination('R',reason='HOSTILE')
  checks['bound_drift_selectively_stales_composite']=a.capability_id in stale and ms.capabilities.contracts[a.capability_id].qualification==QualificationState.STALE and ms.capabilities.contracts['A'].qualification in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED} and ms.capabilities.contracts['B'].qualification in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED}
 finally: td.cleanup()
 # 12 no parallel planner/registry/qualification authority
 td,ms=seeded()
 try:
  checks['no_parallel_composition_architecture']=all(not hasattr(ms,n) for n in ('multi_child_planner','multi_child_registry','semantic_child_registry','auto_qualify_composition','infer_transaction_semantics'))
 finally: td.cleanup()
 return checks

if __name__=='__main__':
 c=run(); out={'passed':sum(c.values()),'total':len(c),'all_pass':all(c.values()),'checks':c}; print(json.dumps(out,indent=2,sort_keys=True)); raise SystemExit(0 if out['all_pass'] else 1)
