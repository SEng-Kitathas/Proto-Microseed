from __future__ import annotations
import json
from pathlib import Path
from test_ms1477_integration import make_ms, setup, candidate, qualify


def main():
    td,ms=make_ms(); checks={}
    try:
        setup(ms); c=candidate(ms); bid=qualify(ms,c)
        checks['existing_v24_projection_is_selector_substrate']=c.projection_id=='P' and 'P' in ms.epistemic_projections.records and not hasattr(ms,'predictive_state_registry')
        checks['routing_candidate_is_proposal_only']=c.authority=='MODEL_OUTPUT_ONLY' and c.qualification_authority=='NONE' and c.semantic_regime_authority=='NONE'
        checks['selector_qualification_is_external_and_disjoint']=bool(ms.action_outcome_learning.projection_conditioned_bindings[bid].qualification_evidence_ids) and not (set(c.source_evidence_ids) & set(ms.action_outcome_learning.projection_conditioned_bindings[bid].qualification_evidence_ids))
        old_before=ms.action_outcome_predictive_relation_status('R-OLD')['status']
        k0=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='k0',action_id='A',task_id='TASK',channel_id='CH',horizon=2)
        k1=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='k1',action_id='A',task_id='TASK',channel_id='CH',horizon=2)
        checks['recurrent_contexts_can_coexist_without_global_switch']=k0['relation_id']=='R-OLD' and k1['relation_id']=='R-NEW' and k0['status']==k1['status']=='CURRENT_PARTITION_SCOPED_RELATION'
        checks['globally_stale_relation_can_be_narrowly_requalified']=old_before=='STALE_PREDICTIVE_RELATION' and k0['global_relation_status']=='STALE_PREDICTIVE_RELATION'
        checks['scoped_requalification_does_not_reactivate_global_relation']=ms.action_outcome_predictive_relation_status('R-OLD')['status']=='STALE_PREDICTIVE_RELATION'
        unknown=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='UNSEEN',action_id='A',task_id='TASK',channel_id='CH',horizon=2)
        checks['unqualified_selector_bucket_defers']=unknown['status']=='DEFER_UNKNOWN' and unknown['reason']=='PROJECTION_BUCKET_NOT_QUALIFIED'
        mismatch=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='k0',action_id='A',task_id='OTHER',channel_id='CH',horizon=2)
        checks['task_channel_horizon_scope_is_load_bearing']=mismatch['status']=='DEFER_UNKNOWN'
        ms.change_epistemic_projection('P',new_signature_sha256='d'*64,reason='SCAR-SELECTOR-BOUNDARY-CHANGED')
        checks['projection_change_stales_routing_without_erasing_history']=ms.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING' and bid in ms.action_outcome_learning.projection_conditioned_bindings
        checks['merge_split_statehood_not_promoted_to_semantic_regime']=not hasattr(ms,'discover_semantic_regime') and not hasattr(ms,'auto_split_predictive_state')
        checks['prediction_error_does_not_gain_model_switch_authority']=not hasattr(ms,'auto_switch_action_outcome_relation')
        checks['routing_has_no_truth_execution_or_self_qualification_authority']=all(getattr(ms.action_outcome_learning.projection_conditioned_bindings[bid],x)=='NONE' for x in ('truth_authority','execution_authority','self_qualification_authority'))
        out={'all_pass':all(checks.values()),'checks':checks}
        Path(__file__).resolve().parents[2].joinpath('MS1453_1477_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
        print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
    finally: td.cleanup()

if __name__=='__main__': raise SystemExit(main())
