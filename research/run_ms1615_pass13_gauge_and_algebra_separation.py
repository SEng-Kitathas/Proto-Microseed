from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed

def main():
  with tempfile.TemporaryDirectory(prefix='ms1615-') as td:
    m=Microseed(Path(td))
    a=m.infer_event_frame(['e0','e0','e1','e1'])
    b=m.infer_event_frame(['renamed0','renamed0','renamed1','renamed1'])
    ambiguous=m.infer_event_frame(['opaqueA','opaqueA','opaqueB','opaqueB'],rival_segmentations=[[0,2],[0,1,2]])
  out={'pass':'MS1615_PASS13','gauge_A':a.__dict__,'gauge_B':b.__dict__,'ambiguous_frame':ambiguous.__dict__,
       'gauge_boundary_equivalent':a.boundaries==b.boundaries,
       'result':'EVENT_BOUNDARY_STRUCTURE_CAN_BE_GAUGE_EQUIVALENT_WHILE_AMBIGUOUS_FRAME_REMAINS_UNKNOWN__ACTUAL_STREAM_BINDING_DOES_NOT_SOLVE_ALGEBRA_CONSTRUCTION','authority':'RESEARCH_ONLY'}
  Path('research/MS1615_PASS13_GAUGE_AND_ALGEBRA_SEPARATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
