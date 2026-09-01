
from __future__ import annotations

import inspect
import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, Microseed, QualificationState
from microseed.runtime.composer import compose_capabilities
from tests.embodiment.test_frontier_i_growth_reusable_whole_reachability import _learn_and_admit_ab_whole,_close


def _q(cid:str, *, deps=(), resources=None):
    return CapabilityContract(
        cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,
        ('I-HARDENING-MEASUREMENT',),'CURRENT',dict(resources or {}),
        dependencies=tuple(deps),qualification=QualificationState.SHADOW_QUALIFIED,
    )


def test_runtime_composer_has_no_owned_plan_length_budget_or_execution_cost_semantics():
    sig=inspect.signature(compose_capabilities)
    assert tuple(sig.parameters)==('contracts','goals')
    assert 'budget' not in sig.parameters and 'max_nodes' not in sig.parameters and 'cost' not in sig.parameters
    td=tempfile.TemporaryDirectory(prefix='hardening-i-measure-');ms=Microseed(Path(td.name))
    try:
        whole,_=_learn_and_admit_ab_whole(ms)
        ms.register_capability(_q('CHEAP',resources={'declared_cost':0}))
        ms.register_capability(_q('EXPENSIVE',resources={'declared_cost':10**9}))
        # Composer reports dependency availability only; arbitrary resource metadata
        # does not alter composition status or grant a budget interpretation.
        assert ms.compose(['CHEAP']).status=='COMPOSED_EPHEMERAL'
        assert ms.compose(['EXPENSIVE']).status=='COMPOSED_EPHEMERAL'
        assert ms.compose([whole]).status=='COMPOSED_EPHEMERAL'
    finally:_close(ms,td)


def test_admitted_learned_whole_is_dependency_reuse_not_one_step_executable_behavior():
    td=tempfile.TemporaryDirectory(prefix='hardening-i-whole-');ms=Microseed(Path(td.name))
    try:
        whole,cand=_learn_and_admit_ab_whole(ms)
        contract=ms.capabilities.contracts[whole]
        assert contract.dependencies==('A','B')
        assert contract.authority==Authority.DERIVED_READ_ONLY
        assert contract.handler is None
        assert contract.resources.get('support',0)>0
        assert 'discovery_score' in contract.resources
        # Reification has earned a qualified/current dependency-bearing capability
        # description. It has not earned an EFFECT handler or an operational claim
        # that A->B now occurs as one physical/temporal action.
        out=ms.compose([whole])
        assert out.plan==('A','B',whole)
        assert out.authority==Authority.DERIVED_READ_ONLY
    finally:_close(ms,td)


def test_external_plan_node_budget_changes_research_classification_without_changing_any_microseed_state_or_reachability():
    td=tempfile.TemporaryDirectory(prefix='hardening-i-external-budget-');ms=Microseed(Path(td.name))
    try:
        whole,_=_learn_and_admit_ab_whole(ms)
        ms.register_capability(_q('TARGET-WHOLE',deps=(whole,'C')))
        before=(len(ms.store.events()),len(ms.action_closure.intents),len(ms.action_closure.executions))
        out=ms.compose(['TARGET-WHOLE'])
        assert out.status=='COMPOSED_EPHEMERAL'
        # Two evaluator-chosen thresholds classify the exact same substrate result
        # differently. That proves this 'budget' is not yet an organism-owned law.
        assert (len(out.plan)<=4) is False
        assert (len(out.plan)<=5) is True
        after=(len(ms.store.events()),len(ms.action_closure.intents),len(ms.action_closure.executions))
        assert before==after
        assert out.plan==('A','B',whole,'C','TARGET-WHOLE')
    finally:_close(ms,td)


def test_dependency_stripping_remains_invalid_even_after_measurement_gap_is_demoted():
    td=tempfile.TemporaryDirectory(prefix='hardening-i-lineage-');ms=Microseed(Path(td.name))
    try:
        whole,_=_learn_and_admit_ab_whole(ms)
        ms.register_capability(_q('FAKE-ATOMIC-AB'))
        ms.register_capability(_q('TARGET-HONEST',deps=(whole,'C')))
        ms.register_capability(_q('TARGET-FAKE',deps=('FAKE-ATOMIC-AB','C')))
        stale=ms.change_capability_dependency('A',reason='HARDENING-I-A-DRIFT')
        assert whole in stale and 'TARGET-HONEST' in stale
        assert ms.compose(['TARGET-HONEST']).status=='NO_PATH'
        assert ms.compose(['TARGET-FAKE']).status=='COMPOSED_EPHEMERAL'
        # Thus we retain the anti-laundering result while refusing to infer that a
        # new atomic mechanism is currently necessary.
    finally:_close(ms,td)
