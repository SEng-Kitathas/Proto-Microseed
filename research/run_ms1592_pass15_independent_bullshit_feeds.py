from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,QualificationState,QueryObligation

def main():
  with tempfile.TemporaryDirectory(prefix='ms1592-p15-') as td:
    m=Microseed(Path(td))
    # Two functionally distinct interface feeds; evaluator knows both are derived from a predicted model, not the physical world.
    m.register_capability(CapabilityContract('OBS-A','feed A',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1592-P15',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda probe=None,**_:{'reading':10 if probe!='PERTURB_A' else 11}))
    m.register_capability(CapabilityContract('OBS-B','feed B',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1592-P15',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda probe=None,**_:{'reading':20 if probe!='PERTURB_B' else 21}))
    m.register_capability(CapabilityContract('PAIR-SEPARATE','separation',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1592-P15',),'CURRENT',{},dependencies=('OBS-A','OBS-B'),query_obligation_id='PAIR-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:'SEPARATE',operational_scope_id='SELECTIVE-PROBES'))
    pair=m.capabilities.invoke('PAIR-SEPARATE',QueryObligation('PAIR-Q','pair',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='SELECTIVE-PROBES'))
    a0=m.capabilities.invoke('OBS-A',QueryObligation('A','a'),probe='NONE'); a1=m.capabilities.invoke('OBS-A',QueryObligation('A','a'),probe='PERTURB_A')
    b0=m.capabilities.invoke('OBS-B',QueryObligation('B','b'),probe='NONE'); b1=m.capabilities.invoke('OBS-B',QueryObligation('B','b'),probe='PERTURB_B')
    out={'pass':'MS1592_PASS15','pair_relation_current':pair,'selective_behavior':{'A':[a0['value'],a1['value']],'B':[b0['value'],b1['value']]},'evaluator_hidden_origin':'BOTH_FEEDS_DERIVED_FROM_NONPHYSICAL_PREDICTION_PIPELINES','result':'FUNCTIONAL_CHANNEL_SEPARATION_PLUS_CURRENTNESS_DOES_NOT_ESTABLISH_ACTUAL_WORLD_BINDING','authority':'RESEARCH_ONLY'}
    Path('research/MS1592_PASS15_INDEPENDENT_BULLSHIT_FEEDS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
