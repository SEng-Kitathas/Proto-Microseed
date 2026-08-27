from __future__ import annotations
import json,subprocess,sys,tempfile
from pathlib import Path
from microseed import Authority,QualificationState
from research.run_ms1578_pass01_actual_stream_misbinding import seeded,prepare
from tests.embodiment.test_ms1643_historical_admission_ingress import install,call


def main():
    with tempfile.TemporaryDirectory(prefix='ms1646-') as td:
        m,_=seeded(Path(td));install(m)
        e0,_=prepare(m,'OLD');old=call(m,e0,'OLD');assert old['status']=='ACTION_OUTCOME_OBSERVED'
        # Prospective mapping-content change while leaving old HIST basis untouched.
        m.change_capability_dependency('OBS',reason='NEW_OBSERVATION_MAPPING')
        obs=m.capabilities.contracts['OBS'];obs.purpose='NEW OBSERVATION MAPPING';obs.boundary={'mapping':'V2'};obs.qualification=QualificationState.SHADOW_QUALIFIED;obs.currentness='CURRENT'
        m.change_capability_dependency('LIVE-BASIS',reason='NEW_OBSERVATION_MAPPING')
        live=m.capabilities.contracts['LIVE-BASIS'];live.qualification=QualificationState.SHADOW_QUALIFIED;live.currentness='CURRENT'
        e1,_=prepare(m,'NEW');blocked=call(m,e1,'NEW')
        # Exact same mapping-content epoch motion remains applicable.
        m2,_=seeded(Path(td)/'same');install(m2)
        m2.change_capability_dependency('OBS',reason='TEMP_RUNTIME_EPOCH')
        o=m2.capabilities.contracts['OBS'];o.qualification=QualificationState.SHADOW_QUALIFIED;o.currentness='CURRENT'
        m2.change_capability_dependency('LIVE-BASIS',reason='TEMP_RUNTIME_EPOCH')
        lb=m2.capabilities.contracts['LIVE-BASIS'];lb.qualification=QualificationState.SHADOW_QUALIFIED;lb.currentness='CURRENT'
        e2,_=prepare(m2,'SAME');same=call(m2,e2,'SAME')
        out={
          'pass':'MS1646_PASS19','old_acquisition':old['status'],'prospective_mapping_change_with_old_basis':blocked,
          'same_mapping_content_new_runtime_epoch':same['status'],
          'result':'OLD_ADMISSION_BASIS_REUSE_BLOCKED_WITHOUT_OVERINVALIDATING_SAME_CONTENT_RUNTIME_EPOCH' if blocked.get('reason')=='HISTORICAL_ADMISSION_BASIS_NOT_APPLICABLE_TO_CURRENT_PREMISES' and same['status']=='ACTION_OUTCOME_OBSERVED' else 'FAILED',
          'survivor':'SNAPSHOT_BOUND_HISTORICAL_ADMISSION_APPLICABILITY_CHECK_ON_EXISTING_INGRESS',
          'nonclaim':'snapshot/signature applicability does not establish physical correctness, causal completeness, or noncircular qualification of the basis',
          'next':'HOSTILE_MUTATE_SIGNATURE_BINDING_AND_PRESERVE_FALSELY_QUALIFIED_BUT_CORRECTLY_BOUND_BASIS_AS_EXPLICIT_FAILURE_BOUNDARY',
          'authority':'RESEARCH_ONLY'}
        Path('research/MS1646_PASS19_SNAPSHOT_BOUND_INGRESS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True));assert out['result'].startswith('OLD_ADMISSION')
if __name__=='__main__':main()
