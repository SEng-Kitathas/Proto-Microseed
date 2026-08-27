from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority, CapabilityContract, Microseed, QualificationState, QueryObligation

def main():
  with tempfile.TemporaryDirectory(prefix='ms1581-p4-') as td:
    m=Microseed(Path(td)); emitted={"next_state_id":"S1","observed_values":{"V":999.0}}
    c=CapabilityContract('OBS-OUTCOME','opaque observation channel',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1581-P4',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(emitted),operational_scope_id='R2')
    m.register_capability(c)
    good=QueryObligation('OBS-Q','observe outcome',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id='R2')
    wrongq=QueryObligation('OTHER','observe outcome',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id='R2')
    wrongs=QueryObligation('OBS-Q','observe outcome',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id='OTHER')
    a=m.capabilities.invoke('OBS-OUTCOME',good)
    b=m.capabilities.invoke('OBS-OUTCOME',wrongq)
    c2=m.capabilities.invoke('OBS-OUTCOME',wrongs)
    m.invalidate_capability('OBS-OUTCOME',reason='CHANNEL_MAPPING_CHALLENGED')
    d=m.capabilities.invoke('OBS-OUTCOME',good)
    out={
      'pass':'MS1581_PASS04',
      'matching_query_scope':a,
      'wrong_query':b,
      'wrong_scope':c2,
      'after_invalidation':d,
      'handler_payload_is_still_taken_as_capability_result_without_mapping_truth_check':a.get('value')==emitted,
      'result':'EXISTING_CAPABILITY_CURRENTNESS_QUERY_SCOPE_CAN_OWN_OBSERVATION_CHANNEL_USE__BUT_NOT_MAPPING_TRUTH',
      'authority':'RESEARCH_ONLY'
    }
    Path('research/MS1581_PASS04_OBSERVATION_CAPABILITY_QUARRY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
