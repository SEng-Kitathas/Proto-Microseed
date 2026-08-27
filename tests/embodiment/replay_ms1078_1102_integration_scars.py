from __future__ import annotations
import json,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from microseed import Microseed,Authority,QualificationState,CapabilityContract,OperationalCounterpartyContract,OperationalCoordinationContract,CapabilityCandidate,ExternalCapabilityQualifier,EpistemicStatus

def cp(cid='P'):
 c=OperationalCounterpartyContract(counterparty_id=cid,purpose='opaque',signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1053-1077',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('HSP_EXTERNAL_COUNTERPARTY_QUALIFICATION',));c.signature_sha256=c.computed_signature_sha256();return c

def rel(rid,cid='P'):
 c=OperationalCoordinationContract(coordination_id=rid,purpose='opaque-mutual-contingency',participant_counterparty_epochs=((cid,0),),signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1078-1102',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('HSP_EXTERNAL_COORDINATION_QUALIFICATION',));c.signature_sha256=c.computed_signature_sha256();return c

def cap(cid):
 return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1078-1102',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1)

def main():
 with tempfile.TemporaryDirectory(prefix='ms1078-1102-replay-') as td:
  ms=Microseed(Path(td));ms.register_operational_counterparty(cp());ms.register_operational_coordination(rel('RA'));ms.register_operational_coordination(rel('RB'))
  ms.register_capability(cap('JA'),coordination_dependencies=(('RA',0),));ms.register_capability(cap('JB'),coordination_dependencies=(('RB',0),))
  preA=ms.compose(['JA']).status;preB=ms.compose(['JB']).status
  stale=ms.change_operational_coordination('RA',reason='REPLAY_COORDINATION_DRIFT')
  postA=ms.compose(['JA']).status;postB=ms.compose(['JB']).status
  # pending candidate relation epoch recheck
  ms2=Microseed(Path(td)/'pending');ms2.register_operational_counterparty(cp());ms2.register_operational_coordination(rel('R0'))
  pe=ms2.append_evidence('PE',{'proposal':1},EpistemicStatus.PRESSURE_SUPPORTED);qe=ms2.append_evidence('QE',{'heldout':1},EpistemicStatus.PROVED)
  c=CapabilityContract('PJ','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1078-1102',),'CANDIDATE',{},qualification=QualificationState.CANDIDATE)
  cand=CapabilityCandidate('PJ',c,(pe,),operational_signature={'coordination_epochs':[['R0',0]]});ms2.nominate_capability_candidate(cand);ticket=ExternalCapabilityQualifier(ms2.evidence).qualify(cand,qualification_evidence=(qe,));ms2.change_operational_coordination('R0',reason='POST_TICKET')
  rejected=False
  try:ms2.admit_capability_candidate(ticket)
  except ValueError as e:rejected='CANDIDATE_COORDINATION_EPOCH_DRIFT' in str(e)
  s=ms.status();checks={
   'both_relations_current_before_drift':preA=='COMPOSED_EPHEMERAL' and preB=='COMPOSED_EPHEMERAL',
   'relation_specific_drift_stales_only_bound_capability':'JA' in stale and postA=='NO_PATH' and postB=='COMPOSED_EPHEMERAL',
   'broad_counterparty_remains_current':ms.counterparties.is_current('P',0),
   'pending_candidate_rechecks_coordination_epoch':rejected,
   'coordination_has_no_semantic_commitment_authority':s['coordination_semantic_commitment_authority']=='NONE' and s['coordination_intention_authority']=='NONE' and s['coordination_promise_authority']=='NONE',
   'coordination_discovery_not_promoted':not hasattr(ms,'discover_operational_coordination'),
   'prelingual_hard_stop':s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE' and s['next_ms']>=1203 and s.get(f"ms{s['next_ms']}_started") is False,
   'selected_frontier':s['research_terminal_ms']>=1252 and s['frontier'].startswith('ATTN-MS'),
  }
  out={'schema':'microseed.ms1078-1102.maindev-replay.v1.2','checks':checks,'all_pass':all(checks.values()),'status':s,'stale':sorted(stale)}
  print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
