from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed
from tests.embodiment import test_ms1352_integration as t
SCARS=[
 ('bounded_rehearsal_beats_myopic',t.test_bounded_rehearsal_beats_myopic_without_authority_gain),
 ('refusal_unknown_preserved',t.test_refusal_and_unknown_are_not_overridden_by_rehearsal),
 ('ambiguous_transition_abstains',t.test_ambiguous_transition_is_not_forced_into_a_prediction),
 ('value_currentness_required',t.test_value_currentness_is_required_for_rehearsal),
 ('frame_episode_topology_coordination_currentness',t.test_frame_episode_topology_and_coordination_currentness_filter_stale_evidence),
 ('capability_epoch_drift_filters_evidence',t.test_capability_epoch_drift_filters_old_transition_evidence),
 ('proposal_currentness_rechecks_ancestry',t.test_proposal_currentness_rechecks_all_bound_ancestry),
 ('restart_no_execute_or_qualify_api',t.test_restart_preserves_history_but_does_not_create_execute_or_qualify_api),
 ('forged_authority_rejected',t.test_registry_rejects_forged_authority),
 ('budget_exhaustion_abstains',t.test_budget_exhaustion_abstains_instead_of_returning_partial_plan),
 ('general_planner_unqualified',t.test_status_keeps_general_planner_unqualified),
 ('qualified_whole_enlarges_second_order_closure',t.test_external_qualification_of_rehearsed_whole_enlarges_second_order_capability_closure),
]
def main():
 checks={}
 for name,fn in SCARS:
  try: fn(); checks[name]=True
  except Exception as e: checks[name]=False; checks[name+'_error']=repr(e)
 m=Microseed(Path(tempfile.mkdtemp(prefix='ms1352-status-'))); s=m.status()
 checks['historical_floor_ms1352_current']=s['research_terminal_ms']>=1352 and s['integration_evidence_through_ms']>=1352 and s['next_ms']>=1353
 hist=json.loads(Path('CURRENT_STATE_MS1352.json').read_text())
 checks['ternary_interrupt_historical_ceiling_preserved']=hist['next_state']['selected_frontier']=='ATTN-MS1352-TERNARY-RELATIONAL-COMMITMENT-NULL-BINDING__ARCHITECTURAL-COMPRESSION-OARR' and 'ternary+NULL architecture is selected for OARR but not yet integrated' in hist['critical_limitations']
 out={'schema':'microseed.maindev-replay.ms1328-1352.v1','checks':checks,'passed':sum(v is True for v in checks.values()),'failed':sum(v is False for v in checks.values())}
 Path('MS1328_1352_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out['failed']==0 else 1
if __name__=='__main__': raise SystemExit(main())
