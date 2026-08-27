from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority, Observation
from research.run_ms1578_pass01_actual_stream_misbinding import seeded,prepare

REPORTED={"ENERGY":4.6,"THERMAL":8.3,"INTEGRITY":5.1}

def run(root:Path, hidden_truth:dict[str,float]):
    m,calls=seeded(root)
    exid,_=prepare(m,'EQ')
    r=m.record_bounded_action_outcome(exid,Observation('OUT-EQ','INTERFACE',f'action-execution:{exid}',{"next_state_id":"R","observed_values":REPORTED},authority=Authority.OBSERVATION_ONLY,lineage=('LABELLED_ACTUAL',)),evidence_id='E-OUT-EQ')
    return {
      'organism_visible':{
        'status':r['status'],'outcome':r['outcome'],'evidence':m.evidence.get('E-OUT-EQ'),
        'learning_rows':[x.serializable() for x in m._action_outcome_experiences()],
        'calls':calls,
      },
      'evaluator_hidden_true_post':hidden_truth,
    }

def main():
  with tempfile.TemporaryDirectory(prefix='ms1583-p6-') as td:
    a=run(Path(td)/'a',{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34})
    b=run(Path(td)/'b',{"ENERGY":5.1,"THERMAL":6.2,"INTEGRITY":7.4})
    for row in (a['organism_visible']['evidence'], b['organism_visible']['evidence']): row.pop('created_ns',None)
    equal=a['organism_visible']==b['organism_visible']
    out={'pass':'MS1583_PASS06','organism_visible_records_equal':equal,'world_A_hidden_truth':a['evaluator_hidden_true_post'],'world_B_hidden_truth':b['evaluator_hidden_true_post'],'reported_interface_stream':REPORTED,'result':'SAME_STREAM_CANNOT_SELF_AUTHENTICATE_ACTUALNESS__HIDDEN_WORLDS_OBSERVATIONALLY_EQUIVALENT_AT_CURRENT_INTERFACE' if equal else 'UNEXPECTED_VISIBLE_DIFFERENCE','authority':'RESEARCH_ONLY'}
    Path('research/MS1583_PASS06_ACTUAL_STREAM_OBSERVATIONAL_EQUIVALENCE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
