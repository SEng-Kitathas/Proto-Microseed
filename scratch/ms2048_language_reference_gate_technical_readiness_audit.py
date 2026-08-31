from __future__ import annotations
import json, tempfile
from pathlib import Path
from microseed import Microseed
from microseed.cognition.research_registry import RESEARCH_COMPONENTS
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import run_ms2046
from scratch.ms2044_operational_body_counterparty_boundary import run_ms2044
from scratch.ms2043_four_referent_partial_observability_scale import run_ms2043


def run_ms2048(v1_whole_suite_closed: bool = False) -> dict[str, object]:
    ref=run_ms2046(); body=run_ms2044(); many=run_ms2043()
    assert ref['status']=='GROUNDED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE_EARNED'
    assert body['status']=='OPERATIONAL_BODY_COUNTERPARTY_BOUNDARY_EARNED'
    assert many['status']=='FOUR_REFERENT_PARTIAL_OBSERVABILITY_SCALE_EARNED'
    historical={k:v for k,v in RESEARCH_COMPONENTS.items() if 'LANGUAGE' in k or 'PREDICATE' in k or 'EVENT_FRAME' in k}
    assert historical and all(v.get('status')=='RESEARCH_ONLY' for v in historical.values())
    with tempfile.TemporaryDirectory(prefix='ms2048-') as td:
        ms=Microseed(Path(td))
        try:
            status=ms.status(); assert status['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
            forbidden=[x for x in ('language_manager','signal_meaning_registry','semantic_reference_registry','token_meaning_registry') if hasattr(ms,x)]
            assert forbidden==[]
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    return {
        'status':'TECHNICALLY_READY_FOR_OPERATOR_LANGUAGE_GATE_REVIEW' if v1_whole_suite_closed else 'PENDING_V1_WHOLE_SUITE',
        'language_facing_evidence':'GREEN',
        'grounded_reference_candidate':ref['status'],
        'many_referent':many['status'],
        'body_counterparty':body['status'],
        'runtime_language_status':status['language'],
        'historical_language_components':historical,
        'historical_language_authority':'DONOR_ONLY_RESEARCH_ONLY',
        'forbidden_language_manager_attrs_present':forbidden,
        'semantic_reference_authority':'NONE',
        'language_authority':'NONE',
        'v1_whole_suite_closed':v1_whole_suite_closed,
        'gate_authority':'OPERATOR_ONLY',
        'law':'GROUNDING_CANDIDATE != LANGUAGE_GATE_ADMISSION',
    }

if __name__=='__main__': print(json.dumps(run_ms2048(False),indent=2,sort_keys=True,default=str))
