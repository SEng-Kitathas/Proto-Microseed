
from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, Microseed, QualificationState
from tests.embodiment.test_frontier_i_growth_reusable_whole_reachability import _learn_and_admit_ab_whole, _close


def _q(cid: str, *, deps=()) -> CapabilityContract:
    return CapabilityContract(
        cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,
        ('I-GROWTH-ATOMIC-HOSTILE',),'CURRENT',{},dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def test_stripping_dependency_lineage_can_fake_atomic_budget_reachability_but_loses_currentness_causality():
    td=tempfile.TemporaryDirectory(prefix='frontier-i-growth-atomic-')
    ms=Microseed(Path(td.name))
    try:
        honest,_=_learn_and_admit_ab_whole(ms)
        # Honest target preserves learned whole -> primitive ancestry.
        ms.register_capability(_q('TARGET-HONEST',deps=(honest,'C')))
        honest_plan=ms.compose(['TARGET-HONEST'])
        assert honest_plan.status=='COMPOSED_EPHEMERAL'
        assert honest_plan.plan==('A','B',honest,'C','TARGET-HONEST')
        assert len(honest_plan.plan)==5

        # Cheap rival: declare an ancestry-free atom with the same informal role.
        # This fits the desired four-node budget but is not evidence-equivalent.
        ms.register_capability(_q('FAKE-ATOMIC-AB'))
        ms.register_capability(_q('TARGET-FAKE',deps=('FAKE-ATOMIC-AB','C')))
        fake_plan=ms.compose(['TARGET-FAKE'])
        assert fake_plan.status=='COMPOSED_EPHEMERAL'
        assert fake_plan.plan==('FAKE-ATOMIC-AB','C','TARGET-FAKE')
        assert len(fake_plan.plan)<=4

        # Primitive A drift correctly kills the honest learned whole and target.
        stale=ms.change_capability_dependency('A',reason='I-GROWTH-ATOMIC-HOSTILE-A-DRIFT')
        assert honest in stale and 'TARGET-HONEST' in stale
        assert ms.compose(['TARGET-HONEST']).status=='NO_PATH'

        # The fake atom stays current because its dependency/currentness lineage was
        # stripped to buy apparent atomicity. This is the exact laundering hazard.
        assert ms.capabilities.is_current('FAKE-ATOMIC-AB')
        assert ms.capabilities.is_current('TARGET-FAKE')
        assert ms.compose(['TARGET-FAKE']).status=='COMPOSED_EPHEMERAL'
    finally:
        _close(ms,td)


def test_dependency_preserving_wrapper_is_not_atomic_under_current_composer():
    td=tempfile.TemporaryDirectory(prefix='frontier-i-growth-wrapper-')
    ms=Microseed(Path(td.name))
    try:
        honest,_=_learn_and_admit_ab_whole(ms)
        # Any wrapper that honestly declares the learned whole as a dependency is
        # recursively expanded by the current composer; naming it a wrapper does not
        # turn it into one operational step.
        ms.register_capability(_q('HONEST-WRAPPER',deps=(honest,)))
        ms.register_capability(_q('TARGET-WRAPPED',deps=('HONEST-WRAPPER','C')))
        out=ms.compose(['TARGET-WRAPPED'])
        assert out.status=='COMPOSED_EPHEMERAL'
        assert out.plan==('A','B',honest,'HONEST-WRAPPER','C','TARGET-WRAPPED')
        assert len(out.plan)==6
        stale=ms.change_capability_dependency('A',reason='I-GROWTH-HONEST-WRAPPER-A-DRIFT')
        assert honest in stale and 'HONEST-WRAPPER' in stale and 'TARGET-WRAPPED' in stale
    finally:
        _close(ms,td)
