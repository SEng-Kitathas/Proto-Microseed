from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from microseed import Microseed
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter,AdapterConfig
from scratch.ms1949_shadow_substrate_adapter import ChargeWorld
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

def main():
    td=tempfile.TemporaryDirectory(prefix='ms1954-pre-'); ms=Microseed(Path(td.name)); world=ChargeWorld(); adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id='PRE1954'))
    try:
        adapter.attach(ms); relation_id,_=adapter.train_actual_history(ms,'CHARGE')
        relation=ms.action_outcome_learning.relations[relation_id]
        sources=[]
        for eid in relation.qualification_evidence_ids:
            row=ms.evidence.get(eid) or {}; sources.append(row.get('source'))
        result={
            'status':'CONFLATED',
            'adapter_has_separate_qualification_source':hasattr(adapter,'qualification_source'),
            'qualification_evidence_sources':sorted(set(sources)),
            'qualification_evidence_count':len(sources),
            'world_provider_type':type(world).__name__,
            'boundary':'EXTERNAL_TO_MICROSEED != INDEPENDENT_QUALIFICATION_SOURCE',
            'evidence_independence_authority':'NONE',
        }
        print(json.dumps(result,indent=2,sort_keys=True))
    finally:
        _close(ms); td.cleanup()
if __name__=='__main__': main()
