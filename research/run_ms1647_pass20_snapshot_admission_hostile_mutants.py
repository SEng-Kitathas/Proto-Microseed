from __future__ import annotations
import json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENTITY=ROOT/'microseed/runtime/entity.py'; LEARN=ROOT/'microseed/development/action_learning.py'
TEST='tests/embodiment/test_ms1643_historical_admission_ingress.py'
mutants=[
 ('ALLOW_UNBOUND_HISTORICAL_BASIS',ENTITY,
  'if not admission_snapshot:\n                return {"status":"OUTCOME_REJECTED","reason":"HISTORICAL_ADMISSION_PREMISE_SIGNATURES_REQUIRED"}',
  'if False and not admission_snapshot:\n                return {"status":"OUTCOME_REJECTED","reason":"HISTORICAL_ADMISSION_PREMISE_SIGNATURES_REQUIRED"}',
  'test_split_historical_basis_requires_snapshot_bound_acquisition_premise'),
 ('BYPASS_ACQUISITION_SNAPSHOT_MATCH',ENTITY,
  'if premise_contract is None or premise_contract.computed_signature_sha256()!=sig:',
  'if premise_contract is None:',
  'test_old_historical_basis_cannot_admit_new_evidence_after_mapping_content_change'),
 ('DROP_INGRESS_HISTORICAL_SIGNATURE',ENTITY,
  'premise_signatures=((admission_basis_capability_id,admission_contract.computed_signature_sha256()),)',
  'premise_signatures=()',
  'test_split_ingress_persists_historical_basis_epoch_and_content_signature'),
 ('IGNORE_RELATION_PREMISE_SIGNATURE_CURRENTNESS',ENTITY,
  'for cid,sig in r.evidence_premise_signatures:\n            c=self.capabilities.contracts.get(cid)\n            if c is None or c.computed_signature_sha256()!=sig: return False',
  'for cid,sig in ():\n            c=self.capabilities.contracts.get(cid)\n            if c is None or c.computed_signature_sha256()!=sig: return False',
  'test_same_id_epoch_but_changed_basis_content_stales_relation'),
 ('DROP_CANDIDATE_PREMISE_SIGNATURE',LEARN,
  'topology_epochs=key[6], coordination_epochs=key[7], evidence_premise_epochs=key[8], evidence_premise_signatures=key[9],',
  'topology_epochs=key[6], coordination_epochs=key[7], evidence_premise_epochs=key[8], evidence_premise_signatures=(),',
  'test_historical_signature_reaches_candidate_and_qualified_relation'),
 ('IGNORE_HOLDOUT_PREMISE_SIGNATURE',LEARN,
  'and tuple((str(a), str(b)) for a, b in p.get("evidence_premise_signatures", ())) == candidate.evidence_premise_signatures',
  'and True',
  'test_holdout_without_matching_historical_signature_does_not_qualify_candidate'),
]
results=[]
for name,path,old,new,test in mutants:
    original=path.read_text()
    if old not in original:
        results.append({'mutant':name,'rejected':False,'reason':'MUTATION_PATTERN_NOT_FOUND'});continue
    try:
        path.write_text(original.replace(old,new,1))
        cp=subprocess.run(['python','-m','pytest','-q',f'{TEST}::{test}'],cwd=ROOT,env={**os.environ,'PYTHONPATH':'.'},capture_output=True,text=True,timeout=35)
        results.append({'mutant':name,'target_test':test,'rejected':cp.returncode!=0,'returncode':cp.returncode,'tail':'\n'.join((cp.stdout+cp.stderr).splitlines()[-8:])})
    finally: path.write_text(original)
out={'pass':'MS1647_PASS20','mutants':results,'rejected':sum(bool(x.get('rejected')) for x in results),'total':len(results),'result':'ALL_HOSTILE_MUTANTS_REJECTED' if results and all(x.get('rejected') for x in results) else 'HOSTILE_GAP',
     'known_deliberate_boundary':'A correctly snapshot-bound and currently qualified admission basis can still be physically false/incomplete; signature binding proves applicability/identity, not truth or completeness.',
     'pal169_scar':'AUTHORIZED_OR_INDEPENDENT_OR_CONTENT_BOUND_ADMISSION != EXHAUSTIVE_COMPLETENESS',
     'authority':'RESEARCH_ONLY','next':'REGRESSION_AND_BREADTH_RECONCILIATION__DO_NOT_PROMOTE_UNLESS_HISTORICAL_VS_LIVE_SEMANTICS_REMAIN_CLEAN'}
(ROOT/'research/MS1647_PASS20_SNAPSHOT_ADMISSION_HOSTILE_MUTANTS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if not (results and all(x.get('rejected') for x in results)): raise SystemExit(1)
