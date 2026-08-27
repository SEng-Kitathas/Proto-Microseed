from pathlib import Path
import hashlib, json, random, tempfile
from microseed import *

def H(x):return hashlib.sha256(x.encode()).hexdigest()
def rows(prefix,n=1800,causal=(2,11,19),noise=.02,seed=1,structured=None,invert=False):
 r=random.Random(seed);out=[]
 for i in range(n):
  raw=tuple(str(r.randrange(2)) for _ in range(24));a=r.randrange(2);y=a
  for j in causal:y^=int(raw[j])
  if structured is not None and raw[structured]=='1':y^=1
  elif r.random()<noise:y^=1
  if invert:y^=1
  out.append(ConstructorProjectionSample(f'{prefix}-{i}',(raw,),f'a{a}',f'e{y}',None,'F',0))
 return out
def cfg(**kw):
 b=dict(max_support_ceiling=4,max_lag_ceiling=0,top_supports_per_order=16,min_train_support=100,min_validation_accuracy=.90,min_lift_over_action_baseline=.30,min_scope_accuracy=.90,max_conflict_edges=5000,combination_budget=20000,max_candidates=8);b.update(kw);return RobustConstructorGrowthConfig(**b)
def discover(m,xs,**kw):
 n=len(xs);return m.discover_robust_epistemic_constructor_candidates(xs[:n//2],xs[n//2:3*n//4],xs[3*n//4:],cfg(**kw))
def q(m,cid,eid):
 ev=m.append_evidence(eid,{'heldout':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_MS1302_REPLAY')
 return ExternalRobustConstructorQualifier(m.evidence,qualifier_id='HSP-MS1302-REPLAY').qualify(m.robust_epistemic_constructor_candidates[cid],qualification_evidence=(ev,))
def main():
 checks={}
 with tempfile.TemporaryDirectory(prefix='ms1302-replay-') as td:
  root=Path(td);m=Microseed(root);m.register_operational_frame(OperationalFrameContract('F','opaque',H('f'),Authority.DERIVED_READ_ONLY,('MS1302',),'CURRENT',QualificationState.SHADOW_QUALIFIED,('EXT',),('NO_SEMANTIC_FEATURE_AUTHORITY',)))
  A=rows('A',2600,seed=1);fa=discover(m,A);ca=fa[0]['candidate_id'];m.admit_robust_epistemic_constructor_candidate(q(m,ca,'QA'),projection_id='P')
  B=rows('B',1500,causal=(2,11,20),seed=2);dw=m.assess_epistemic_projection_predictive_currentness('P',B,ProjectionPredictiveCurrentnessConfig(256,.82,2));checks['predictive_drift_stales_without_cause_identity']=dw['status']=='DRIFT_WITNESS' and dw['drift_cause_authority']=='NONE'
  fb=discover(m,B);cb=fb[0]['candidate_id'];sw=m.assess_epistemic_projection_drift_structure('P',q(m,cb,'QB'),B,ProjectionDriftStructureConfig(.90,.20));checks['qualified_distinct_structure_can_be_supported']=sw['status']=='ALTERNATIVE_STRUCTURE_SUPPORTED' and sw['drift_cause_authority']=='NONE'
  checks['alternative_structure_has_no_admission_authority']=sw['admission_authority']=='NONE'
  AR=rows('AR',1800,seed=3);rw=m.assess_epistemic_projection_recurrence('P',AR);checks['historical_predictive_law_can_recur']=rw['status']=='RECURRENCE_EVIDENCE'
  checks['recurrence_has_no_regime_or_reactivation_authority']=rw['regime_identity_authority']=='NONE' and rw['reactivation_authority']=='NONE'
  wit=m.epistemic_projection_recurrence_witnesses[rw['witness_sha256']];ev=m.append_evidence('QR',{'fresh':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_MS1302_REPLAY');t=ExternalProjectionRecurrenceQualifier(m.evidence,qualifier_id='HSP-MS1302-RECURRENCE').qualify(wit,qualification_evidence=(ev,));old_epoch=m.epistemic_projections.records['P'].epoch;rr=m.reactivate_epistemic_projection_from_recurrence(t);checks['external_requalification_creates_new_current_epoch']=rr.current and rr.epoch==old_epoch+1
  checks['reactivation_preserves_no_regime_identity_ancestry']='NO_RECURRING_REGIME_IDENTITY_AUTHORITY' in rr.assistance_ancestry
  del m;m2=Microseed(root);checks['recurrence_and_reactivation_survive_restart']=m2.epistemic_projections.records['P'].current and rw['witness_sha256'] in m2.epistemic_projection_recurrence_witnesses
  checks['no_regime_classifier_or_noise_model']=not hasattr(m2,'discover_regime_identity') and not hasattr(m2,'infer_noise_model') and not hasattr(m2,'classify_drift_cause')
 with tempfile.TemporaryDirectory(prefix='ms1302-noise-') as td:
  m=Microseed(Path(td));m.register_operational_frame(OperationalFrameContract('F','opaque',H('f'),Authority.DERIVED_READ_ONLY,('MS1302',),'CURRENT',QualificationState.SHADOW_QUALIFIED,('EXT',),('NO_SEMANTIC_FEATURE_AUTHORITY',)))
  A=rows('A',2600,seed=4);ca=discover(m,A)[0]['candidate_id'];m.admit_robust_epistemic_constructor_candidate(q(m,ca,'QA2'),projection_id='P');N=rows('N',1600,noise=.24,seed=5);m.assess_epistemic_projection_predictive_currentness('P',N,ProjectionPredictiveCurrentnessConfig(256,.82,2));fn=discover(m,N,min_validation_accuracy=.70,min_lift_over_action_baseline=.15,min_scope_accuracy=.70);cn=fn[0]['candidate_id'];nw=m.assess_epistemic_projection_drift_structure('P',q(m,cn,'QN'),N,ProjectionDriftStructureConfig(.70,.15));checks['no_distinct_structure_does_not_identify_noise']=nw['status']=='NO_ALTERNATIVE_STRUCTURE_WITHIN_BOUNDS' and nw['noise_semantics_authority']=='NONE'
  nr=m.assess_epistemic_projection_recurrence('P',N);checks['high_noise_not_false_recurrence']=nr['status']=='NO_RECURRENCE_WITHIN_BOUNDS'
 with tempfile.TemporaryDirectory(prefix='ms1302-alias-') as td:
  m=Microseed(Path(td));m.register_operational_frame(OperationalFrameContract('F','opaque',H('f'),Authority.DERIVED_READ_ONLY,('MS1302',),'CURRENT',QualificationState.SHADOW_QUALIFIED,('EXT',),('NO_SEMANTIC_FEATURE_AUTHORITY',)))
  A=rows('A',2600,seed=6);ca=discover(m,A)[0]['candidate_id'];m.admit_robust_epistemic_constructor_candidate(q(m,ca,'QA3'),projection_id='P');B=rows('B',1400,causal=(2,11,20),seed=7);m.assess_epistemic_projection_predictive_currentness('P',B,ProjectionPredictiveCurrentnessConfig(256,.82,2));alias=rows('INV',1600,seed=8,invert=True);ar=m.assess_epistemic_projection_recurrence('P',alias);checks['same_support_wrong_mapping_not_recurrence']=ar['status']=='NO_RECURRENCE_WITHIN_BOUNDS'
  m.change_operational_frame('F',reason='DRIFT');
  try:m.assess_epistemic_projection_recurrence('P',rows('AR',900,seed=9));checks['frame_drift_blocks_recurrence']=False
  except ValueError:checks['frame_drift_blocks_recurrence']=True
 s=Microseed(tempfile.mkdtemp(prefix='ms1302-status-')).status();checks['ms1302_is_preserved_as_ancestral_floor']=s['research_terminal_ms']>=1302 and s['integration_evidence_through_ms']>=1302 and s['next_ms']>=1303
 checks['active_cause_discriminator_was_not_promoted_to_semantic_classifier']=not hasattr(m,'classify_drift_cause')
 checks['language_and_identity_not_promoted']=s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE' and 'NUMERICAL_SELFHOOD_NOT_QUALIFIED' in s['persistent_identity']
 out={'schema':'microseed.ms1278-1302.integration-scar-replay.v1','checks':checks,'passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values())};print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
