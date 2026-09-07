from __future__ import annotations

import inspect
from pathlib import Path

import microseed.runtime.entity as entity
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from tests.embodiment.test_lang_active_acquisition_nomination_effect_boundary import _prepare,_execute,_close


def _token_rows(m):
    return tuple(
        row for row in m.evidence.list()
        if (row.get('payload') or {}).get('kind')=='OPAQUE_EXTERNAL_TOKEN_OBSERVATION'
    )


def run_campaign() -> dict[str,object]:
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        production=Path(inspect.getsourcefile(entity.Microseed)).read_text(encoding='utf-8')
        # Production owns chronology consumption but not token-event creation.
        production_token_kind_mentions=production.count('OPAQUE_EXTERNAL_TOKEN_OBSERVATION')
        production_token_writer_patterns=sum(
            production.count(pattern) for pattern in (
                '"kind":"OPAQUE_EXTERNAL_TOKEN_OBSERVATION"',
                '"kind": "OPAQUE_EXTERNAL_TOKEN_OBSERVATION"',
                "'kind':'OPAQUE_EXTERNAL_TOKEN_OBSERVATION'",
                "'kind': 'OPAQUE_EXTERNAL_TOKEN_OBSERVATION'",
            )
        )
        before=len(_token_rows(m))
        execution=_execute(m,selected,nominated)
        assert execution['status']=='ACTION_EXECUTED',execution
        after_effect=len(_token_rows(m))
        external=observe_opaque_token(m,'OPAQUE-ENV-COUPLING-AUDIT',9300,phase='ACTIVE-ACQ-ENV-COUPLING')
        assert external['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',external
        after_external=len(_token_rows(m))
        return {
            'status':'STOP_NOVEL_ASSOCIATION_ACQUISITION_AT_EXOGENOUS_TOKEN_PRESENTATION_BOUNDARY',
            'selected_probe_action_id':nominated['selected_probe_action_id'],
            'effect_execution_status':execution['status'],
            'token_observations_before_effect':before,
            'token_observations_after_effect':after_effect,
            'token_observations_after_external_ingress':after_external,
            'effect_created_token_observation':'YES' if after_effect>before else 'NO',
            'external_ingress_created_token_observation':'YES' if after_external>after_effect else 'NO',
            'production_token_kind_mentions':production_token_kind_mentions,
            'production_token_writer_patterns':production_token_writer_patterns,
            'token_presentation_owner':'EXOGENOUS_INGRESS',
            'novel_pair_active_acquisition_closure':'NOT_EARNED',
            'remaining_missing_mechanism':'LAWFUL_ENVIRONMENTAL_TOKEN_COUPLING_TO_ACQUISITION_EVENT',
            'effect_authority_from_token_need':'NONE',
        }
    finally:
        _close(m,td)
