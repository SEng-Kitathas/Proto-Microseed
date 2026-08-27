from __future__ import annotations
import json, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ENTITY=ROOT/'microseed/runtime/entity.py'
LEARN=ROOT/'microseed/development/action_learning.py'
TEST='tests/embodiment/test_ms1620_evidence_premise_currentness.py'

mutants=[
 ('DROP_INGRESS_PREMISE',ENTITY,
  'evidence_premise_epochs=((basis_capability_id, self.capabilities.epochs[basis_capability_id]),),',
  'evidence_premise_epochs=(),',
  'test_basis_epoch_reaches_candidate_and_relation'),
 ('BYPASS_RELATION_PREMISE_CURRENTNESS',ENTITY,
  'for cid,ep in r.evidence_premise_epochs:\n            c=self.capabilities.contracts.get(cid)',
  'for cid,ep in ():\n            c=self.capabilities.contracts.get(cid)',
  'test_basis_challenge_stales_downstream_relation'),
 ('DROP_CANDIDATE_PREMISE',LEARN,
  'topology_epochs=key[6], coordination_epochs=key[7], evidence_premise_epochs=key[8],',
  'topology_epochs=key[6], coordination_epochs=key[7], evidence_premise_epochs=(),',
  'test_basis_epoch_reaches_candidate_and_relation'),
 ('IGNORE_HOLDOUT_PREMISE',LEARN,
  'and tuple((str(a), int(b)) for a, b in p.get("evidence_premise_epochs", ())) == candidate.evidence_premise_epochs',
  'and True',
  'test_holdout_without_matching_evidence_premise_does_not_qualify_assured_candidate'),
 ('DROP_RELATION_PREMISE_COPY',ENTITY,
  'coordination_epochs=c.coordination_epochs,evidence_premise_epochs=c.evidence_premise_epochs,',
  'coordination_epochs=c.coordination_epochs,evidence_premise_epochs=(),',
  'test_basis_epoch_reaches_candidate_and_relation'),
 ('ALLOW_REHEARSAL_ANCESTRY_DROP',LEARN,
  'if len(self.frame_epochs) != 1 or len(self.episode_schema_epochs) != 1 or self.evidence_premise_epochs:',
  'if len(self.frame_epochs) != 1 or len(self.episode_schema_epochs) != 1:',
  'test_rehearsal_conversion_refuses_to_drop_evidence_premise_ancestry'),
]
results=[]
for name,path,old,new,testname in mutants:
    src=path.read_text()
    if old not in src:
        results.append({'mutant':name,'status':'MUTATION_PATTERN_NOT_FOUND'})
        continue
    try:
        path.write_text(src.replace(old,new,1))
        cp=subprocess.run(['python','-m','pytest','-q',f'{TEST}::{testname}'],cwd=ROOT,env={**__import__('os').environ,'PYTHONPATH':'.'},capture_output=True,text=True,timeout=40)
        rejected=cp.returncode!=0
        results.append({'mutant':name,'rejected':rejected,'returncode':cp.returncode,'stdout_tail':cp.stdout[-500:],'stderr_tail':cp.stderr[-300:]})
    finally:
        path.write_text(src)
out={'pass':'MS1621_PASS19','mutants':results,'rejected':sum(bool(x.get('rejected')) for x in results),'total':len(results),'result':'HOSTILE_MUTANTS_REJECTED' if all(x.get('rejected') for x in results) else 'HOSTILE_GAP','authority':'RESEARCH_ONLY'}
(ROOT/'research/MS1621_PASS19_EVIDENCE_PREMISE_HOSTILE_MUTANTS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
