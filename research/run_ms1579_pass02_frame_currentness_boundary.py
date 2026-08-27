from __future__ import annotations
import json, tempfile
from pathlib import Path
from microseed import Authority, Observation
from research.run_ms1578_pass01_actual_stream_misbinding import seeded, prepare

FALSE_POST={"ENERGY":4.60,"THERMAL":8.30,"INTEGRITY":5.10}

def main():
    with tempfile.TemporaryDirectory(prefix='ms1579-p2-') as td:
        ms,_=seeded(Path(td))
        exid,_=prepare(ms,'FRAME')
        epoch=ms.frames.change('F',reason='HOSTILE_FRAME_RELATION_CHANGED')
        r=ms.record_bounded_action_outcome(
            exid,
            Observation('OUT-FRAME','MISBOUND',f'action-execution:{exid}',{"next_state_id":"FALSE-NEXT","observed_values":FALSE_POST},authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-OUT-FRAME',
        )
        learned=ms._action_outcome_experiences()
        out={
          'pass':'MS1579_PASS02',
          'frame_epoch_after_change':epoch,
          'outcome_status':r.get('status'),
          'outcome_learning_ancestry':{x['value_id']:x['learning_ancestry_status'] for x in r.get('outcome',{}).get('value_outcomes',[])},
          'scalar_learning_rows_after_stale_frame':len(learned),
          'durable_outcome_count':len(ms.action_closure.outcomes),
          'ledger_source':ms.evidence.get('E-OUT-FRAME')['source'],
          'result':'FRAME_CURRENTNESS_CAN_WITHHOLD_DOWNSTREAM_LEARNING_ANCESTRY_BUT_DOES_NOT_AUTHENTICATE_OR_REJECT_OUTCOME_STREAM',
          'authority':'RESEARCH_ONLY',
        }
        Path('research/MS1579_PASS02_FRAME_CURRENTNESS_BOUNDARY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
        print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
