from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed
from tests.embodiment import test_ms1327_integration as t

SCARS=[
 ('current_disagreement_probe_selection',t.test_current_disagreement_probe_is_selected_without_truth_or_switch_authority),
 ('zero_disagreement_abstains',t.test_zero_disagreement_pool_does_not_advertise_probe_access),
 ('unavailable_discriminator_is_action_limited',t.test_discriminating_but_stale_probe_access_is_action_limited),
 ('switched_law_narrows_alternative',t.test_repeated_probe_evidence_narrows_to_alternative_predictive_candidate_only),
 ('high_nuisance_narrows_historical',t.test_high_nuisance_batch_can_support_historical_predictive_law_without_noise_identity),
 ('hidden_mixture_stays_unresolved',t.test_hidden_mixture_remains_unresolved_within_finite_probe_bounds),
 ('unpredicted_outcome_challenges_model_space',t.test_unpredicted_probe_outcomes_are_model_space_challenge_not_new_cause),
 ('capability_drift_blocks_consumption',t.test_probe_capability_drift_after_plan_blocks_evidence_consumption),
 ('frame_drift_blocks_consumption',t.test_frame_drift_after_plan_blocks_evidence_consumption),
 ('evidence_content_binding_and_dedup',t.test_probe_evidence_is_content_bound_and_cannot_be_replayed_twice),
 ('restart_history_no_access_gain',t.test_plan_and_witness_replay_as_history_without_restoring_probe_access),
 ('finite_gates_are_content_bound',t.test_finite_evidence_gates_are_part_of_plan_and_cannot_be_changed_at_consumption),
]

def main():
 checks={}
 for name,fn in SCARS:
  try: fn();checks[name]=True
  except Exception as e: checks[name]=False;checks[name+'_error']=repr(e)
 root=Path(tempfile.mkdtemp(prefix='ms1327-status-'));m=Microseed(root);s=m.status()
 checks['historical_floor_ms1327_preserved']=s['research_terminal_ms']>=1327 and s['integration_evidence_through_ms']>=1327 and s['next_ms']>=1328
 checks['no_semantic_cause_classifier']=not hasattr(m,'classify_drift_cause')
 checks['no_intervention_synthesis']=not hasattr(m,'synthesize_intervention')
 checks['no_auto_model_switch']=not hasattr(m,'auto_switch_projection')
 out={'schema':'microseed.maindev-replay.ms1303-1327.v1','checks':checks,'passed':sum(v is True for v in checks.values()),'failed':sum(v is False for v in checks.values())}
 Path('MS1303_1327_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['failed']==0 else 1
if __name__=='__main__': raise SystemExit(main())
