from __future__ import annotations
import json, subprocess
from pathlib import Path
p=Path('microseed/runtime/entity.py'); original=p.read_text()
mutants=[
 ('DROP_BASIS_DEPENDENCY', 'if basis_contract is None or observation_capability_id not in basis_contract.dependencies:', 'if basis_contract is None:', 'test_basis_must_depend_on_selected_observation_channel'),
 ('ACCEPT_ANY_BASIS_AUTHORITY', 'or basis.get("authority") != Authority.DERIVED_READ_ONLY.value', 'or False', 'test_basis_capability_must_carry_derived_read_only_authority'),
 ('ACCEPT_ANY_OBSERVATION_AUTHORITY', 'or observed.get("authority") != Authority.OBSERVATION_ONLY.value', 'or False', 'test_observation_capability_must_carry_observation_only_authority'),
 ('DROP_OBSERVATION_LINEAGE', 'lineage=(\n                f"OBSERVATION_CAPABILITY:{observation_capability_id}@{self.capabilities.epochs[observation_capability_id]}",\n                f"OBSERVATION_USE_BASIS:{basis_capability_id}@{self.capabilities.epochs[basis_capability_id]}",\n            ),', 'lineage=(),', 'test_current_basis_and_channel_close_outcome_and_preserve_ancestry'),
 ('DROP_CURRENTNESS_BASIS_TAG', 'currentness_basis="QUALIFIED_OBSERVATION_CAPABILITY_AND_BOUNDED_USE_BASIS",', 'currentness_basis="UNDECLARED",', 'test_current_basis_and_channel_close_outcome_and_preserve_ancestry'),
 ('BYPASS_BASIS_CURRENTNESS', 'if (\n            basis.get("status") != "CAPABILITY_RESULT"', 'if False and (\n            basis.get("status") != "CAPABILITY_RESULT"', 'test_stale_channel_transitively_stales_basis_and_rejects_ingress'),
 ('BYPASS_OBSERVATION_CURRENTNESS', 'if (\n            observed.get("status") != "CAPABILITY_RESULT"', 'if False and (\n            observed.get("status") != "CAPABILITY_RESULT"', 'test_observation_channel_currentness_is_checked_even_if_basis_metadata_is_still_current'),
]
results=[]
try:
  for name,old,new,test in mutants:
    assert old in original,(name,'needle missing')
    p.write_text(original.replace(old,new,1))
    cp=subprocess.run(['pytest','-q',f'tests/embodiment/test_ms1598_observation_basis_ingress.py::{test}'],env={**__import__('os').environ,'PYTHONPATH':'.'},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=20)
    results.append({'mutant':name,'target_test':test,'rejected':cp.returncode!=0,'pytest_tail':'\n'.join(cp.stdout.splitlines()[-5:])})
finally:
  p.write_text(original)
out={'pass':'MS1599_PASS22','mutants':results,'rejected_count':sum(r['rejected'] for r in results),'total':len(results),'result':'ALL_HOSTILE_MUTANTS_REJECTED' if all(r['rejected'] for r in results) else 'HOSTILE_GAP_OPEN','known_unfixed_boundary':'FALSE_BUT_CURRENT_MAPPING_REMAINS_ACCEPTED_BY_DESIGN_OF_THIS_BRIDGE','authority':'RESEARCH_ONLY'}
Path('research/MS1599_PASS22_HOSTILE_MUTANTS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'pass':out['pass'],'rejected_count':out['rejected_count'],'total':out['total'],'result':out['result'],'known_unfixed_boundary':out['known_unfixed_boundary']},indent=2))
