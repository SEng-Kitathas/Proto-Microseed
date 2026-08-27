from __future__ import annotations
import json
from pathlib import Path
from tests.embodiment.test_ms1620_evidence_premise_currentness import established


def one(case: str):
    td,m,c,rid=established()
    try:
        before=m.action_outcome_predictive_relation_status(rid)
        if case=='TEMPORARY_LIVE_ACCESS_LOSS':
            changed=sorted(m.invalidate_capability('OBS',reason='TEMPORARY_LIVE_ACCESS_LOSS'))
        elif case=='PROSPECTIVE_MAPPING_EPOCH_CHANGE':
            changed=sorted(m.capabilities.change_dependency('OBS',reason='PROSPECTIVE_MAPPING_EPOCH_CHANGE'))
        elif case=='RETROSPECTIVE_ADMISSION_FALSIFICATION':
            changed=sorted(m.invalidate_capability('BASIS',reason='RETROSPECTIVE_HISTORICAL_ADMISSION_FALSE'))
        else:
            raise ValueError(case)
        after=m.action_outcome_predictive_relation_status(rid)
        return {'before':before,'changed':changed,'after':after}
    finally:
        td.cleanup()


def main():
    cases={k:one(k) for k in (
        'TEMPORARY_LIVE_ACCESS_LOSS',
        'PROSPECTIVE_MAPPING_EPOCH_CHANGE',
        'RETROSPECTIVE_ADMISSION_FALSIFICATION',
    )}
    afters={k:v['after']['status'] for k,v in cases.items()}
    out={
        'pass':'MS1628_PASS01',
        'discriminator':'same historical learned relation under three different post-acquisition events',
        'cases':cases,
        'observed_statuses':afters,
        'result':'CURRENT_MONOLITHIC_OBSERVATION_USE_BASIS_COLLAPSES_THREE_HISTORICALLY_DISTINCT_EVENTS' if len(set(afters.values()))==1 else 'EXISTING_PATH_ALREADY_SEPARATES_CASES',
        'scar':'LIVE_ACCESS_LOSS != PROSPECTIVE_MAPPING_CHANGE != RETROSPECTIVE_HISTORICAL_ADMISSION_FALSIFICATION',
        'next':'QUARRY_EXISTING_HISTORY_CURRENTNESS_PATTERNS_AND_SPLIT_LIVE_USE_FROM_HISTORICAL_ADMISSION_BEFORE_NEW_TYPE',
        'authority':'RESEARCH_ONLY',
    }
    p=Path('research/MS1628_PASS01_HISTORICAL_ADMISSION_THREE_WAY.json')
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
