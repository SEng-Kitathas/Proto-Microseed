
from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import (
    Authority, CapabilityContract, EpistemicStatus, ExternalCapabilityQualifier,
    Microseed, OperationalTrace, QualificationState,
)


def _q(cid: str, *, deps=()) -> CapabilityContract:
    return CapabilityContract(
        cid, 'opaque', {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ('I-GROWTH-FRONTIER',), 'CURRENT', {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def _close(ms: Microseed, td: tempfile.TemporaryDirectory) -> None:
    try:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    finally:
        td.cleanup()


def _learn_and_admit_ab_whole(ms: Microseed):
    ms.register_capability(_q('A')); ms.register_capability(_q('B')); ms.register_capability(_q('C'))
    # Singleton baselines plus recurrent A->B residual motif, preserving the known
    # supplied trace-boundary/effect-coordinate assistance ceiling of this owner.
    for i in range(6):
        ms.record_operational_trace(OperationalTrace(f'a-{i}', ('A',), ((1.0, 0.0),), 'r0'))
        ms.record_operational_trace(OperationalTrace(f'b-{i}', ('B',), ((0.0, 1.0),), 'r0'))
    for scope in ('r0', 'r1'):
        for i in range(10):
            ms.record_operational_trace(
                OperationalTrace(f'ab-{scope}-{i}', ('A','B'), ((1.0,0.0),(0.0,2.0)), scope)
            )
    proposals = ms.discover_capability_candidates()
    assert proposals
    cid = proposals[0]['candidate_id']
    cand = ms.capability_candidates[cid]
    assert cand.proposed_contract.dependencies == ('A','B')
    assert cand.proposed_contract.qualification == QualificationState.CANDIDATE
    assert ms.compose([cid]).status == 'NO_PATH'
    external = ms.append_evidence(
        'I-GROWTH-HOLDOUT', {'heldout_transfer': .99, 'shuffled_control': .01},
        EpistemicStatus.PRESSURE_SUPPORTED, source='HSP-I-GROWTH'
    )
    ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id='HSP-I-GROWTH').qualify(
        cand, qualification_evidence=(external,)
    )
    ms.admit_capability_candidate(ticket)
    return cid, cand


def _within_plan_budget(ms: Microseed, goal: str, budget: int):
    out = ms.compose([goal])
    return out.status == 'COMPOSED_EPHEMERAL' and len(out.plan) <= budget, out


def test_qualified_whole_is_reusable_but_not_atomic_or_plan_compressing_in_current_composer() -> None:
    td = tempfile.TemporaryDirectory(prefix='frontier-i-growth-')
    ms = Microseed(Path(td.name))
    try:
        whole, cand = _learn_and_admit_ab_whole(ms)
        direct = ms.compose(['A','B'])
        via_whole = ms.compose([whole])
        assert direct.status == via_whole.status == 'COMPOSED_EPHEMERAL'
        assert direct.plan == ('A','B')
        # Critical negative: the admitted whole expands through its prerequisites;
        # it is not treated as one atomic composition step.
        assert via_whole.plan == ('A','B',whole)
        assert len(via_whole.plan) > len(direct.plan)
        assert via_whole.authority == Authority.DERIVED_READ_ONLY
        assert 'SUPPLIED_TRACE_BOUNDARIES' in cand.assistance_ancestry
    finally:
        _close(ms, td)


def test_learned_whole_does_not_expand_fixed_plan_budget_reachability_against_primitive_oracle() -> None:
    td = tempfile.TemporaryDirectory(prefix='frontier-i-growth-')
    ms = Microseed(Path(td.name))
    try:
        whole, _ = _learn_and_admit_ab_whole(ms)
        # Oracle target exposes the primitive A,B,C dependency shape directly.
        ms.register_capability(_q('TARGET-PRIMITIVE', deps=('A','B','C')))
        # Whole-based target treats the learned AB unit as the first dependency.
        ms.register_capability(_q('TARGET-WHOLE', deps=(whole,'C')))

        primitive_ok, primitive = _within_plan_budget(ms, 'TARGET-PRIMITIVE', 4)
        whole_ok_4, whole_plan = _within_plan_budget(ms, 'TARGET-WHOLE', 4)
        whole_ok_5, whole_plan_hi = _within_plan_budget(ms, 'TARGET-WHOLE', 5)
        assert primitive_ok is True
        assert primitive.plan == ('A','B','C','TARGET-PRIMITIVE')
        assert whole_ok_4 is False
        assert whole_ok_5 is True
        assert whole_plan.plan == whole_plan_hi.plan == ('A','B',whole,'C','TARGET-WHOLE')
        # Therefore the current reusable-whole owner does not create the requested
        # fixed-budget reachability expansion; it adds a lineage-bearing node.
        assert len(whole_plan.plan) == len(primitive.plan) + 1
    finally:
        _close(ms, td)


def test_whole_dependency_is_real_and_stales_transitively_even_though_it_does_not_compress_reachability() -> None:
    td = tempfile.TemporaryDirectory(prefix='frontier-i-growth-')
    ms = Microseed(Path(td.name))
    try:
        whole, _ = _learn_and_admit_ab_whole(ms)
        ms.register_capability(_q('TARGET-WHOLE', deps=(whole,'C')))
        assert ms.compose(['TARGET-WHOLE']).status == 'COMPOSED_EPHEMERAL'
        stale = ms.change_capability_dependency('A', reason='I-GROWTH-PRIMITIVE-DRIFT')
        assert whole in stale and 'TARGET-WHOLE' in stale
        out = ms.compose(['TARGET-WHOLE'])
        assert out.status == 'NO_PATH'
    finally:
        _close(ms, td)
