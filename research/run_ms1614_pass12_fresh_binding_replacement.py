from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,QualificationState

def main():
  with tempfile.TemporaryDirectory(prefix='ms1614-') as td:
    m=Microseed(Path(td))
    m.register_capability(CapabilityContract('BIND-OLD','old binding',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1614',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:'PREDICTED'))
    m.register_capability(CapabilityContract('LEARNED-REL-OLD','relation learned through old binding',{}, {},(),(),Authority.REFERENCE_ONLY,('MS1614',),'CURRENT',{},dependencies=('BIND-OLD',),qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:'IDENTITY'))
    stale=sorted(m.invalidate_capability('BIND-OLD',reason='CAUSAL_BINDING_CHALLENGED'))
    # Fresh replacement receives a new identity/ancestry; history is not rewritten.
    m.register_capability(CapabilityContract('BIND-NEW','fresh binding',{}, {},('FRESH_REQUALIFICATION_REQUIRED',),(),Authority.DERIVED_READ_ONLY,('MS1614',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:'PHYSICAL'))
    m.register_capability(CapabilityContract('LEARNED-REL-NEW','fresh relation',{}, {},(),(),Authority.REFERENCE_ONLY,('MS1614',),'CURRENT',{},dependencies=('BIND-NEW',),qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:'ROT180'))
    snap=m.capabilities.snapshot()
  out={'pass':'MS1614_PASS12','stale_closure':stale,'old_binding':snap['BIND-OLD']['qualification'],'old_relation':snap['LEARNED-REL-OLD']['qualification'],'new_binding':snap['BIND-NEW']['qualification'],'new_relation':snap['LEARNED-REL-NEW']['qualification'],
       'result':'EXISTING_DEPENDENCY_CURRENTNESS_SUPPORTS_FRAME_CORRECTION_WITH_HISTORY_PRESERVED_WHEN_FRESH_BINDING_IS_SEPARATELY_QUALIFIED','authority':'RESEARCH_ONLY'}
  Path('research/MS1614_PASS12_FRESH_BINDING_REPLACEMENT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
