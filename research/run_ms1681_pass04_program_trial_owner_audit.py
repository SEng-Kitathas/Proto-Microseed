from __future__ import annotations
import json
from pathlib import Path
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord, ActionOutcomeRecord
from microseed.development.discovery import OperationalTrace
from microseed.development.epistemic import EpistemicDeficitRecord
from microseed.development.rehearsal import CounterfactualRehearsalProposal

def fields(cls): return sorted(cls.__dataclass_fields__)
rows={
 'CounterfactualRehearsalProposal':fields(CounterfactualRehearsalProposal),
 'BoundedActionIntent':fields(BoundedActionIntent),
 'ActionExecutionRecord':fields(ActionExecutionRecord),
 'ActionOutcomeRecord':fields(ActionOutcomeRecord),
 'OperationalTrace':fields(OperationalTrace),
 'EpistemicDeficitRecord':fields(EpistemicDeficitRecord),
}
reasons={
 'CounterfactualRehearsalProposal':'pre-action model-output proposal; does not bind actual multi-tick execution/outcome records or discrimination need',
 'OperationalTrace':'post-hoc supplied trace boundary/effect coordinates; does not bind actual ActionExecutionRecord/ActionOutcomeRecord ancestry or selected discriminator',
 'EpistemicDeficitRecord':'bounded UNKNOWN lifecycle but current probe binding is one capability_id/epoch, not an ordered physical program',
 'ActionClosureRecords':'step-local intent/execution/outcome provenance only; no cross-step epistemic trial identity',
}
for name,fs in rows.items():
    assert 'macro_trial_id' not in fs and 'program_trial_id' not in fs
out={'milestone':'MS1681','pass':4,'record_fields':rows,'reasons':reasons,
'disposition':'IRREDUCIBLE_REPRESENTATIONAL_GAP__NO_EXISTING_OWNER_BINDS_SELECTED_COMPOSED_DISCRIMINATOR_TO_ACTUAL_MULTI_TICK_STEP_RECORDS',
'earned_candidate':'TINY_PROPOSAL_ONLY_EPISTEMIC_PROGRAM_TRIAL_CARRIER__NO_EXECUTION_OR_TRUTH_AUTHORITY'}
Path(__file__).with_name('MS1681_PASS04_PROGRAM_TRIAL_OWNER_AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True))
print(json.dumps(out,indent=2,sort_keys=True))
