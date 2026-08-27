from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from microseed import (
    Microseed, CapabilityContract, OperationalFrameContract, EpistemicCurrentnessAnchor,
    Authority, QualificationState, EpistemicStatus,
)


def main():
    with tempfile.TemporaryDirectory(prefix='ms1153-1177-replay-') as td:
        root=Path(td); m=Microseed(root)
        f=OperationalFrameContract(
            frame_id='F',purpose='opaque-question-premise',signature_sha256='f'*64,
            authority=Authority.DERIVED_READ_ONLY,lineage=('MS1153-1177',),currentness='CURRENT',
            qualification=QualificationState.SHADOW_QUALIFIED,
        )
        m.register_operational_frame(f)
        u=m.append_evidence('U',{'ambiguous':True},EpistemicStatus.UNKNOWN_INCOMPLETE,source='REPLAY')
        m.record_action_limited_unknown(
            deficit_id='D',question_key='opaque-Q',hypothesis_digest_sha256='a'*64,
            unknown_evidence_id=u.evidence_id,missing_discriminator_signature_sha256='b'*64,
            premise_anchors=(EpistemicCurrentnessAnchor('FRAME','F',0),),
        )
        initial=m.epistemic_deficit_status('D')
        probe=CapabilityContract(
            'P','opaque-probe',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1128-1152',),'CURRENT',{},
            qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1,
        )
        m.register_capability(probe); m.bind_probe_capability('D','P')
        m.change_capability_dependency('P',reason='REPLAY_PROBE_ACCESS_LOSS')
        reopened=m.epistemic_deficit_status('D')
        m.change_operational_frame('F',reason='REPLAY_PREMISE_DRIFT')
        stale=m.epistemic_deficit_status('D')
        del m
        m2=Microseed(root); replayed=m2.epistemic_deficit_status('D'); s=m2.status()
        checks={
            'initial_action_limited':initial['state']=='ACTION_LIMITED',
            'probe_loss_reopens_action_limited':reopened['state']=='ACTION_LIMITED',
            'premise_drift_stales_old_deficit':stale['state']=='STALE',
            'historical_unknown_preserved':stale['unknown_evidence_id']=='U',
            'stale_not_pressure_eligible':'D' not in m2.epistemic_development_pressure_ids(),
            'restart_preserves_stale_without_reactivation':replayed['state']=='STALE',
            'no_resolution_state':'RESOLVED' not in stale['state'],
            'no_truth_authority':stale['truth_authority']=='NONE' and stale['semantic_question_authority']=='NONE',
            'prelingual_hard_stop':s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE' and s['next_ms']>=1203 and s.get(f"ms{s['next_ms']}_started") is False,
            'selected_frontier':s['research_terminal_ms']>=1252 and s['frontier'].startswith('ATTN-MS'),
        }
        out={
            'schema':'microseed.ms1153-1177.maindev-replay.v1',
            'checks':checks,'all_pass':all(checks.values()),
            'initial':initial,'after_probe_loss':reopened,'after_premise_drift':stale,
            'after_restart':replayed,'status':s,
        }
        print(json.dumps(out,indent=2,sort_keys=True))
        return 0 if out['all_pass'] else 1

if __name__=='__main__': raise SystemExit(main())
