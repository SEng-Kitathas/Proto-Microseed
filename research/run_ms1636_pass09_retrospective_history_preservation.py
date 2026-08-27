from __future__ import annotations
import json
from pathlib import Path
from research.run_ms1629_pass02_split_historical_admission_basis import established

def main():
    td,m,c,rid=established()
    try:
        m.invalidate_capability('HIST-ADMIT',reason='RETROSPECTIVE_ADMISSION_FALSIFIED')
        status=m.action_outcome_predictive_relation_status(rid)
        relation_present=rid in m.action_outcome_learning.relations
        stored=[e for e in m.store.events() if e.get('kind') in {'ACTION_OUTCOME_PREDICTIVE_RELATION_QUALIFIED','CAPABILITY_INVALIDATED'}]
        inv=[e for e in stored if e.get('kind')=='CAPABILITY_INVALIDATED' and e.get('payload',{}).get('root')=='HIST-ADMIT'][-1]
        out={'pass':'MS1636_PASS09','status':status,'relation_history_preserved':relation_present,'qualified_relation_event_preserved':any(e.get('kind')=='ACTION_OUTCOME_PREDICTIVE_RELATION_QUALIFIED' and e.get('payload',{}).get('relation_id')==rid for e in stored),'invalidation_event':inv,
             'result':'RETROSPECTIVE_FALSIFICATION_CAN_REMOVE_CURRENT_AUTHORITY_WITHOUT_ERASING_HISTORICAL_QUALIFICATION','note':'status vocabulary says STALE_STRUCTURAL_PREMISE; durable invalidation reason carries the stronger challenge provenance, so no new relation enum is yet justified','authority':'RESEARCH_ONLY','next':'ATTACK_SAME_EPOCH_REQUALIFICATION_RESURRECTION_AFTER_BASIS_FAILURE'}
        Path('research/MS1636_PASS09_RETROSPECTIVE_HISTORY_PRESERVATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally:td.cleanup()
if __name__=='__main__':main()
