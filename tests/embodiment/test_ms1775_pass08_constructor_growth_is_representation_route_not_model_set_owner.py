import inspect

from microseed.development.constructor_growth import ConstructorGrowthConfig, ConstructorProjectionSample
from microseed.runtime.entity import Microseed


def test_constructor_growth_can_search_conflict_directed_observed_history_representation_but_still_requires_supplied_samples_and_does_not_own_transition_model_sets():
    cfg=ConstructorGrowthConfig()
    ancestry=set(cfg.assistance_ancestry())
    assert 'SUPPLIED_RAW_OBSERVATION_BOUNDARIES' in ancestry
    assert 'SUPPLIED_OPAQUE_ACTION_TOKENS' in ancestry
    assert 'SUPPLIED_OPAQUE_EFFECT_TOKENS' in ancestry
    assert any(x.startswith('SUPPLIED_HISTORY_WINDOW_MAX_LAG_') for x in ancestry)

    sig=inspect.signature(Microseed.discover_epistemic_constructor_candidates)
    for required in ('training_samples','pressure_samples','validation_samples'):
        assert required in sig.parameters and sig.parameters[required].default is inspect._empty

    sample=ConstructorProjectionSample('S',(('visible-now',),('visible-prev',)),'A','out','SCOPE','F',0,'EP',0)
    p=sample.serializable()
    assert 'raw_history' in p and 'action_token' in p and 'effect_token' in p
    for forbidden in ('relation_sets','transition_model_id','hypothesis_id','truth_authority'):
        assert forbidden not in p
