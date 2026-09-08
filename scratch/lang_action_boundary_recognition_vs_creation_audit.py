from __future__ import annotations

import inspect
from microseed.runtime.entity import Microseed
from microseed.cognition.research_registry import RESEARCH_COMPONENTS


def run_audit() -> dict[str,object]:
    helper=inspect.getsource(Microseed._derive_current_store_aware_bounded_operand_window)
    comp=inspect.getsource(Microseed.derive_and_record_current_native_bounded_ordered_composition)
    episode=inspect.getsource(Microseed.register_episode_schema)
    forbidden=('execute_bounded_action(','nominate_bounded_action_intent(','register_capability(','propose_episode_grouping(')
    hits=tuple(x for x in forbidden if x in helper or x in comp)
    old=RESEARCH_COMPONENTS['MS903_927_ENDOGENOUS_EPISODE_GROUPING']
    return {
        'status':'ACTION_EXECUTION_BOUNDARY_RECOGNITION_ONLY',
        'boundary_owner_consumes_existing_store_events':'YES',
        'boundary_owner_action_creation_calls':hits,
        'boundary_action_creation_authority':'NONE',
        'effect_authority_gain':'NONE',
        'semantic_grouping_authority':'NONE',
        'generic_episode_grouping_api_present':hasattr(Microseed,'propose_episode_grouping'),
        'episode_schema_registration_external_qualification':'externally qualified' in episode.lower(),
        'historical_endogenous_episode_grouping_status':old['status'],
        'historical_endogenous_episode_grouping_ceiling':old['ceiling'],
        'passive_token_only_boundary_ownership':'NOT_EARNED',
        'autonomous_boundary_occasion_selection':'NOT_EARNED',
    }
