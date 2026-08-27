from __future__ import annotations
import hashlib,json,random,tempfile
from pathlib import Path
from microseed import Microseed,Authority,EpistemicStatus,QualificationState,OperationalFrameContract,ProjectionSample,ProjectionDiscoveryConfig,ExternalProjectionQualifier

def H(x):return hashlib.sha256(x.encode()).hexdigest()
def rows(n=2400,seed=1227):
 r=random.Random(seed);o=[]
 for i in range(n):
  raw=[str(r.randint(0,1)) for _ in range(7)];a='a0' if r.random()<.5 else 'a1';p=int(raw[1])^int(raw[4]);y=p^(a=='a1')
  if r.random()<.02:y^=1
  o.append(ProjectionSample(f's{i}',tuple(raw),a,f'e{int(y)}',f'r{i%3}','F',0))
 return o
def main():
 with tempfile.TemporaryDirectory(prefix='ms1203-1227-replay-') as td:
  root=Path(td);m=Microseed(root)
  m.register_operational_frame(OperationalFrameContract(frame_id='F',purpose='opaque',signature_sha256=H('F0'),authority=Authority.DERIVED_READ_ONLY,lineage=('MS1203-1227',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNAL_FRAME_QUALIFICATION',),invariants=('NO_SEMANTIC_FEATURE_AUTHORITY',)))
  rr=rows();found=m.discover_epistemic_projection_candidates(rr[:1600],rr[1600:],ProjectionDiscoveryConfig(max_subset=2,min_train_support=20,min_key_action_support=3,min_validation_accuracy=.82,min_lift_over_action_baseline=.18,min_scope_accuracy=.74))
  c=m.epistemic_projection_candidates[found[0]['candidate_id']]
  q=m.append_evidence('Q',{'independent_holdout':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL')
  ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1227').qualify(c,qualification_evidence=(q,))
  rec=m.admit_epistemic_projection_candidate(ticket,projection_id='P')
  sig=c.digest();cid=c.candidate_id;status=m.status();del m
  m2=Microseed(root);c2=m2.epistemic_projection_candidates[cid];r2=m2.epistemic_projections.records['P']
  checks={
   'true_pair_recovered':c.input_positions==(1,4) and c.validation_accuracy>.93,
   'predictive_partition_nontrivial':c.bucket_count==2 and c.raw_key_count==4,
   'proposal_has_no_authority':c.proposal_authority=='NONE' and c.qualification_authority=='NONE' and c.truth_authority=='NONE',
   'assistance_ancestry_visible':'FIXED_SUBSET_GRAMMAR_MAX_2' in c.assistance_ancestry and 'SUPPLIED_RAW_OBSERVATION_BOUNDARIES' in c.assistance_ancestry,
   'no_semantic_xor_operator':not any('XOR' in x for x in c.assistance_ancestry),
   'external_qualification_preserved':rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED' and rec.proposal_candidate_sha256==sig and rec.qualification_evidence_ids==('Q',),
   'replay_no_qualification_gain':c2.digest()==sig and c2.qualification_authority=='NONE',
   'admitted_projection_replays':r2.proposal_candidate_sha256==sig and r2.discovery_authority=='NONE',
   'self_qualification_absent':not hasattr(m2,'qualify_epistemic_projection_candidate'),
   'general_projection_discovery_absent':not hasattr(m2,'discover_general_epistemic_projection'),
   'prelingual':status['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE',
   'hard_stop':status['research_terminal_ms']>=1227 and status['integration_evidence_through_ms']>=1227 and status['next_ms']>=1228 and status.get(f"ms{status['next_ms']}_started") is False,
   'frontier_current':status['research_terminal_ms']>=1252 and status['frontier'].startswith('ATTN-MS'),
   'numerical_selfhood_unqualified':status['identity_claim']=='NOT_QUALIFIED',
  }
  out={'schema':'microseed.ms1203-1227.maindev-replay.v1','checks':checks,'passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values())}
  print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
