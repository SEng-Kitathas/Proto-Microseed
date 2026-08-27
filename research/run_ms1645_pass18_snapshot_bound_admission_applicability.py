from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,QualificationState
from research.run_ms1578_pass01_actual_stream_misbinding import seeded


def snapshot(contract: CapabilityContract):
    return ((contract.capability_id, contract.computed_signature_sha256()),)


def applicable(m, hist_id: str) -> tuple[bool,str]:
    hist=m.capabilities.contracts[hist_id]
    raw=hist.boundary.get('admission_premise_signatures',())
    try: pairs=tuple((str(a),str(b).lower()) for a,b in raw)
    except Exception: return False,'MALFORMED_ADMISSION_PREMISE_SIGNATURES'
    if not pairs: return False,'ADMISSION_PREMISE_SIGNATURES_REQUIRED'
    for cid,sig in pairs:
        c=m.capabilities.contracts.get(cid)
        if c is None or c.computed_signature_sha256()!=sig:
            return False,'ADMISSION_PREMISE_SIGNATURE_MISMATCH'
    return True,'APPLICABLE_TO_CURRENT_ACQUISITION_PREMISES'


def main():
    with tempfile.TemporaryDirectory(prefix='ms1645-') as td:
        m,_=seeded(Path(td))
        obs=CapabilityContract('OBS','observation mapping',{'mapping':'V1'}, {},(),(),Authority.OBSERVATION_ONLY,('MS1645',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED)
        m.register_capability(obs)
        hist=CapabilityContract('HIST-ADMIT','historical admission basis',{'admission_premise_signatures':[list(x) for x in snapshot(obs)]}, {},('HISTORICAL_ONLY','NO_TRUTH_AUTHORITY'),(),Authority.DERIVED_READ_ONLY,('MS1645',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED)
        m.register_capability(hist)
        original=applicable(m,'HIST-ADMIT')
        # Temporary runtime epoch motion with identical immutable mapping content.
        m.change_capability_dependency('OBS',reason='TEMP_ACCESS_OR_REQUALIFICATION_EPOCH')
        o=m.capabilities.contracts['OBS'];o.qualification=QualificationState.SHADOW_QUALIFIED;o.currentness='CURRENT'
        same_content_new_epoch=applicable(m,'HIST-ADMIT')
        # Prospective mapping-content change must invalidate applicability for NEW acquisition.
        m.change_capability_dependency('OBS',reason='PROSPECTIVE_MAPPING_CHANGE')
        o=m.capabilities.contracts['OBS'];o.boundary={'mapping':'V2'};o.qualification=QualificationState.SHADOW_QUALIFIED;o.currentness='CURRENT'
        changed_mapping=applicable(m,'HIST-ADMIT')
        out={
            'pass':'MS1645_PASS18',
            'original':{'applicable':original[0],'reason':original[1]},
            'same_content_new_runtime_epoch':{'applicable':same_content_new_epoch[0],'reason':same_content_new_epoch[1]},
            'changed_mapping_content':{'applicable':changed_mapping[0],'reason':changed_mapping[1]},
            'result':'SNAPSHOT_BOUND_ADMISSION_APPLICABILITY_SEPARATES_RUNTIME_EPOCH_MOTION_FROM_MAPPING_CONTENT_CHANGE' if original[0] and same_content_new_epoch[0] and not changed_mapping[0] else 'FAILED',
            'scar':'HISTORICAL_ADMISSION_BASIS_VALIDITY != APPLICABILITY_TO_ARBITRARY_FUTURE_ACQUISITION_PREMISES',
            'nonclaim':'matching immutable premise signatures establishes basis applicability only; it does not prove the mapping or admission basis is physically correct or complete',
            'pal169_pressure':'AUTHORIZED_OR_CONTENT_BOUND_ADMISSION != EXHAUSTIVE_TRUTH',
            'next':'WIRE_THIS_AS_A_MANDATORY_CHECK_ON_SPLIT_HISTORICAL_ADMISSION_INGRESS_AND_HOSTILE_IT',
            'authority':'RESEARCH_ONLY',
        }
        p=Path('research/MS1645_PASS18_SNAPSHOT_BOUND_ADMISSION_APPLICABILITY.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
        assert out['result'].startswith('SNAPSHOT_BOUND')
if __name__=='__main__': main()
