import inspect

from microseed.cognition.hypothesis import Hypothesis, HypothesisSet
from microseed.runtime.entity import Microseed


def test_active_discrimination_maintains_and_probes_supplied_hypotheses_but_does_not_generate_or_ground_them():
    hs = HypothesisSet((Hypothesis('H0', lambda x: 0), Hypothesis('H1', lambda x: int(x) % 2)))
    hs.observe(0, 0)
    assert {h.hypothesis_id for h in hs.live} == {'H0','H1'}
    assert hs.best_probe((1,2,3)) in {1,3}

    sig = inspect.signature(Microseed.active_discrimination)
    assert 'hypotheses' in sig.parameters and sig.parameters['hypotheses'].default is inspect._empty
    # The hypotheses themselves are caller-owned executable predictors; there is
    # no evidence/currentness/qualification/model-authority ancestry on the type.
    h = hs.live[0]
    assert set(h.__dataclass_fields__) == {'hypothesis_id','predict','complexity'}
