from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import (
    ShadowEnvironmentAdapter, AdapterConfig, ForkedWorldQualificationSource,
)
from scratch.ms1949_shadow_substrate_adapter import ChargeWorld
from scratch.ms1952_cross_world_compatibility_hostile import DriftedChargeWorld
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _new(world, *, source=None, instance='MS1954'):
    td=tempfile.TemporaryDirectory(prefix=f'ms1954-{instance.lower()}-')
    ms=Microseed(Path(td.name))
    adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id=instance),qualification_source=source)
    adapter.attach(ms)
    return td,ms,adapter


def run_separation():
    # Missing source fails before physical training.
    td,ms,adapter=_new(ChargeWorld(),source=None,instance='NO-SOURCE')
    try:
        try:
            adapter.train_actual_history(ms,'CHARGE')
            raise AssertionError('missing qualification source unexpectedly accepted')
        except ValueError as exc:
            assert str(exc)=='EXTERNAL_QUALIFICATION_SOURCE_REQUIRED'
        assert len(ms.action_closure.outcomes)==0
        missing={'reason':'EXTERNAL_QUALIFICATION_SOURCE_REQUIRED','outcome_count':0}
    finally:
        _close(ms);td.cleanup()

    # Compatibility-mismatched qualification source also fails before intervention.
    live=ChargeWorld(); mismatched=ForkedWorldQualificationSource(DriftedChargeWorld(),provider_id='QUAL-MISMATCH')
    td,ms,adapter=_new(live,source=mismatched,instance='MISMATCH')
    try:
        try:
            adapter.train_actual_history(ms,'CHARGE')
            raise AssertionError('mismatched qualification source unexpectedly accepted')
        except ValueError as exc:
            assert str(exc)=='QUALIFICATION_SOURCE_ENVIRONMENT_COMPATIBILITY_MISMATCH'
        assert len(ms.action_closure.outcomes)==0
        mismatch={'reason':'QUALIFICATION_SOURCE_ENVIRONMENT_COMPATIBILITY_MISMATCH','outcome_count':0}
    finally:
        _close(ms);td.cleanup()

    # Matched but structurally separate source supplies qualification evidence.
    live=ChargeWorld(); source_world=ChargeWorld(); source=ForkedWorldQualificationSource(source_world,provider_id='QUAL-MATCHED')
    assert source is not live and source.prototype is not live
    td,ms,adapter=_new(live,source=source,instance='MATCHED')
    try:
        relation_id,_=adapter.train_actual_history(ms,'CHARGE')
        relation=ms.action_outcome_learning.relations[relation_id]
        sources=[]; provider_ids=[]
        for eid in relation.qualification_evidence_ids:
            row=ms.evidence.get(eid) or {}; sources.append(row.get('source')); provider_ids.append((row.get('payload') or {}).get('qualification_provider_id'))
        assert set(sources)=={'EXTERNAL-QUALIFICATION:QUAL-MATCHED'}
        assert set(provider_ids)=={'QUAL-MATCHED'}
        assert len(relation.qualification_evidence_ids)==16
        matched={
            'relation_id':relation_id,
            'qualification_evidence_count':16,
            'qualification_evidence_sources':sorted(set(sources)),
            'provider_ids':sorted(set(provider_ids)),
            'runtime_world_object_is_qualification_world_object':live is source.prototype,
        }
    finally:
        _close(ms);td.cleanup()

    return {
        'status':'PASS',
        'missing_source':missing,
        'mismatched_source':mismatch,
        'matched_separate_source':matched,
        'earned':'RUNTIME_ENVIRONMENT_AND_QUALIFICATION_SOURCE_ARE_SEPARATE_SUBSTRATE_ROLES_WITH_COMPATIBILITY_BOUNDARY',
        'evidence_independence_authority':'NONE',
        'boundary':'SEPARATE_QUALIFICATION_ROLE != EVIDENCE_INDEPENDENCE_PROVED',
    }


def main(): print(json.dumps(run_separation(),indent=2,sort_keys=True))
if __name__=='__main__': main()
