from __future__ import annotations
import json,inspect
from pathlib import Path
from microseed.development.action_learning import ActionOutcomeExperience,ActionOutcomePredictiveCandidate,QualifiedActionOutcomePredictiveRelation
classes=(ActionOutcomeExperience,ActionOutcomePredictiveCandidate,QualifiedActionOutcomePredictiveRelation)
fields={c.__name__:list(c.__dataclass_fields__) for c in classes}
existing=set(fields['QualifiedActionOutcomePredictiveRelation'])
needed='evidence_admission_premise_epochs'
out={
 'pass':'MS1619_PASS17',
 'fields':fields,
 'existing_currentness_ancestry':['capability_epoch','frame_epochs','episode_schema_epochs','value_epoch','topology_epochs','coordination_epochs'],
 'missing_generic_carrier':needed not in existing,
 'result':'IRREDUCIBLE_WIRING_GAP__LEARNED_ACTION_OUTCOME_RELATIONS_CANNOT_CURRENTLY_CARRY_EVIDENCE_ADMISSION_VALIDITY_EPOCHS',
 'nonclaim':'This does not identify how an actual-event binding is grounded; it only localizes how a later binding correction could reach dependent learning.',
 'authority':'RESEARCH_ONLY'
}
Path('research/MS1619_PASS17_ACTION_LEARNING_SCHEMA_IRREDUCIBILITY_AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
