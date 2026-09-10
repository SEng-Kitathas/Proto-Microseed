import json
from pathlib import Path

from microseed import Authority, EpistemicStatus, Observation
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_obs,_close


def test_baseline_caller_delimiter_violation_is_preserved_in_campaign_record_but_current_runtime_denies_it():
    record=json.loads(Path('campaigns/MS_SUBSTRATE_INDEXING_2026-09-10/passes/P01_BASELINE_REPRODUCTION.json').read_text(encoding='utf-8'))
    assert record['status']=='PASS_VIOLATIONS_REPRODUCED'
    assert 'arbitrary caller-origin represented non-token evidence resets window' in record['evidence']['caller_nontoken_evidence_delimiter']

    td,m,world,seeded=_setup('SUBSTRATE-DELIMITER-REPAIRED')
    try:
        reset=m.observe_opaque_control_state(
            Observation('CAP-SUBSTRATE-DELIMITER-BASE','EXTERNAL','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-SUBSTRATE-DELIMITER-BASE',
        )
        assert reset['status']=='CURRENT_OPAQUE_CONTROL_STATE',reset
        _obs(m,('R4','T9'),400000,'SUBSTRATE-DELIMITER-PRE')
        m.append_evidence(
            'E-SUBSTRATE-ARBITRARY-CALLER-NONTOKEN',
            {'kind':'ARBITRARY_CALLER_REPRESENTED_EVIDENCE','note':'no endogenous grouping authority'},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source='ARBITRARY_CALLER',
        )
        _obs(m,('W3','K7'),400100,'SUBSTRATE-DELIMITER-POST')
        out=m._derive_current_store_aware_bounded_operand_window(max_events=65536,min_arity=2,max_arity=4)
        assert out['status']=='CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW',out
        assert out['derived_arity']==4,out
        assert tuple((r[1].get('payload') or {}).get('opaque_token') for r in out['selected'])==('R4','T9','W3','K7')
        assert out['last_boundary']['kind']=='OPAQUE_CONTROL_STATE_OBSERVED'
        assert out['last_boundary']['evidence_id']=='E-SUBSTRATE-DELIMITER-BASE'
        assert out['caller_evidence_grouping_authority']=='NONE'
        assert out['boundary_law']=='CALLER_EVIDENCE_INGRESS_HAS_NO_GROUPING_AUTHORITY'
    finally:
        _close(m);td.cleanup()
