from pathlib import Path
import tempfile,json
from microseed import Microseed,CapabilityContract,Authority,QualificationState,EpistemicStatus
from microseed.cognition.hypothesis import Hypothesis


def run():
    with tempfile.TemporaryDirectory(prefix='ms1128-1152-replay-') as td:
        m=Microseed(Path(td))
        h0=Hypothesis('h0',lambda x:0 if x in ('a','b') else 0)
        h1=Hypothesis('h1',lambda x:0 if x in ('a','b') else (1 if x=='d' else 0))
        no_probe=m.active_discrimination([h0,h1],['a','b'],[])['next_probe']
        yes_probe=m.active_discrimination([h0,h1],['a','b','d'],[])['next_probe']
        m.append_evidence('u',{'status':'UNKNOWN_NOW'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='REPLAY')
        m.record_action_limited_unknown(deficit_id='D',question_key='Q',hypothesis_digest_sha256='a'*64,unknown_evidence_id='u',missing_discriminator_signature_sha256='b'*64)
        p=CapabilityContract('probe','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1128-1152',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1)
        m.register_capability(p); before=m.bind_probe_capability('D','probe')
        m.append_evidence('pe',{'actual_probe':1},EpistemicStatus.PRESSURE_SUPPORTED,source='REPLAY')
        revisit=m.record_epistemic_probe_evidence('D','pe')
        m.change_capability_dependency('probe',reason='REPLAY_DRIFT')
        reopened=m.epistemic_deficit_status('D')
        s=m.status()
        checks={
            'zero_disagreement_not_probe':no_probe is None,
            'real_disagreement_probe_selected':yes_probe=='d',
            'action_limited_unknown_persisted':before['state']=='PROBE_AVAILABLE',
            'probe_availability_not_resolution':revisit['state']=='REVISIT_REQUIRED',
            'probe_drift_reopens_action_limited':reopened['state']=='ACTION_LIMITED',
            'truth_authority_none':reopened['truth_authority']=='NONE',
            'prelingual_hard_stop':s['next_ms']>=1203 and s.get(f"ms{s['next_ms']}_started") is False and s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE',
        }
        return {'schema':'microseed.ms1128-1152.maindev-replay.v1.4','checks':checks,'all_pass':all(checks.values()),'status':s}

if __name__=='__main__':
    x=run();print(json.dumps(x,indent=2,sort_keys=True));raise SystemExit(0 if x['all_pass'] else 1)
