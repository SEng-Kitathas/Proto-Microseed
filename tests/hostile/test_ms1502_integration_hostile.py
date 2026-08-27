from __future__ import annotations
from pathlib import Path
import tempfile
import pytest

from microseed import (
    Microseed, Authority, QualificationState, CapabilityContract,
    RecruitmentTopologyContract, OperationalCounterpartyContract,
    OperationalCoordinationContract, OperationalTrace,
    ExternalCapabilityQualifier, EpistemicStatus,
)


def make_ms():
    td = tempfile.TemporaryDirectory(prefix='microseed-ms1502-hostile-')
    return td, Microseed(Path(td.name))


def cap(cid: str):
    return CapabilityContract(
        cid, 'opaque-effect', {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ('MS1478-1502-HOSTILE',), 'CURRENT', {},
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def cp(cid: str):
    c = OperationalCounterpartyContract(
        counterparty_id=cid, purpose='opaque-independent-causal-relation',
        signature_sha256='', authority=Authority.DERIVED_READ_ONLY,
        lineage=('MS1053-1077',), currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('HSP_EXTERNAL_COUNTERPARTY_QUALIFICATION',),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def coord(cid='R', cps=(('CPA',0),('CPB',0))):
    c = OperationalCoordinationContract(
        coordination_id=cid, purpose='opaque-mutual-action-contingency',
        participant_counterparty_epochs=tuple(cps), signature_sha256='',
        authority=Authority.DERIVED_READ_ONLY, lineage=('MS1078-1102',),
        currentness='CURRENT', qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('HSP_EXTERNAL_COORDINATION_QUALIFICATION',),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def topo(ms: Microseed, tid='T', nodes=('A','B')):
    a,b=nodes
    t = RecruitmentTopologyContract(
        topology_id=tid, purpose='opaque-operational-recruitment-topology',
        relations=((a,b),),
        capability_epochs=((a,ms.capabilities.epochs[a]),(b,ms.capabilities.epochs[b])),
        signature_sha256='', authority=Authority.DERIVED_READ_ONLY,
        lineage=('MS978-1027',), currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('HSP_EXTERNAL_TOPOLOGY_QUALIFICATION',),
        invariants=('NO_SEMANTIC_ROLE_AUTHORITY',),
    )
    t.signature_sha256=t.computed_signature_sha256()
    return t


def seeded(extra=False):
    td,ms=make_ms()
    for cid in ('A','B') + (('X','Y') if extra else ()):
        ms.register_capability(cap(cid))
    ms.register_operational_counterparty(cp('CPA')); ms.register_operational_counterparty(cp('CPB'))
    ms.register_operational_coordination(coord())
    ms.register_recruitment_topology(topo(ms,'T',('A','B')))
    if extra:
        ms.register_recruitment_topology(topo(ms,'U',('X','Y')))
    return td,ms


def seed_joint(ms: Microseed, *, topology='T', coordination='R', n=8, scope='s'):
    # Preserve the inherited residual-discovery precondition: the composite is
    # detected relative to single-capability baselines, not from joint rows alone.
    for i in range(5):
        ms.record_operational_trace(OperationalTrace(f'a-base-{i}', ('A',), ((1.0,0.0),), 'baseline'))
        ms.record_operational_trace(OperationalTrace(f'b-base-{i}', ('B',), ((0.0,1.0),), 'baseline'))
    for i in range(n):
        ms.record_operational_trace(OperationalTrace(
            f'ab-{scope}-{i}', ('A','B'), ((1.0,0.0),(0.0,2.0)), scope,
            topology_ids=((topology,) if topology else ()),
            coordination_ids=((coordination,) if coordination else ()),
        ))


def candidate(ms: Microseed):
    props=ms.discover_capability_candidates()
    assert props
    return ms.capability_candidates[props[0]['candidate_id']]


def qualify(ms: Microseed,c):
    e=ms.append_evidence('Q-HOST-'+c.candidate_id, {'heldout':'clean'}, EpistemicStatus.PROVED, source='HSP_EXTERNAL')
    return ExternalCapabilityQualifier(ms.evidence, qualifier_id='HSP-MS1502-HOSTILE').qualify(c, qualification_evidence=(e,))


def test_supplied_epoch_fields_are_not_trusted_and_are_rebound_from_current_registries():
    td,ms=seeded()
    try:
        t=ms.record_operational_trace(OperationalTrace(
            'forged',('A','B'),((1.0,),(2.0,)),'s',
            topology_ids=('T',),topology_epochs=(('T',999),),
            counterparty_ids=('CPA',),counterparty_epochs=(('CPA',999),),
            coordination_ids=('R',),coordination_epochs=(('R',999),),
        ))
        assert t.topology_epochs == (('T',0),)
        assert t.coordination_epochs == (('R',0),)
        assert t.counterparty_epochs == (('CPA',0),('CPB',0))
    finally: td.cleanup()


def test_unrelated_topology_cannot_be_claimed_as_joint_trace_ancestry():
    td,ms=seeded(extra=True)
    try:
        with pytest.raises(ValueError, match='TRACE_TOPOLOGY_NOT_BOUND_TO_STEPS:U'):
            ms.record_operational_trace(OperationalTrace(
                'false-ancestry',('A','B'),((1.0,),(2.0,)),'s', topology_ids=('U',)
            ))
    finally: td.cleanup()


def test_mixed_topology_ancestry_is_not_pooled_into_one_candidate():
    td,ms=seeded(extra=True)
    try:
        # T is bound to A/B; no-topology traces are also individually lawful.
        for i in range(4):
            ms.record_operational_trace(OperationalTrace(f't-{i}',('A','B'),((1.0,),(2.0,)),'s',topology_ids=('T',)))
            ms.record_operational_trace(OperationalTrace(f'n-{i}',('A','B'),((1.0,),(2.0,)),'s'))
        assert ms.discover_capability_candidates() == []
    finally: td.cleanup()


def test_mixed_coordination_ancestry_is_not_pooled_into_one_candidate():
    td,ms=seeded()
    try:
        for i in range(4):
            ms.record_operational_trace(OperationalTrace(f'r-{i}',('A','B'),((1.0,),(2.0,)),'s',coordination_ids=('R',)))
            ms.record_operational_trace(OperationalTrace(f'n-{i}',('A','B'),((1.0,),(2.0,)),'s'))
        assert ms.discover_capability_candidates() == []
    finally: td.cleanup()


def test_counterparty_drift_after_ticket_blocks_pending_candidate():
    td,ms=seeded()
    try:
        seed_joint(ms); c=candidate(ms); ticket=qualify(ms,c)
        ms.change_operational_counterparty('CPA',reason='PHENOTYPE_DRIFT')
        with pytest.raises(ValueError, match='CANDIDATE_COUNTERPARTY_EPOCH_DRIFT:CPA'):
            ms.admit_capability_candidate(ticket)
    finally: td.cleanup()


def test_topology_drift_after_admission_selectively_stales_composite_not_children():
    td,ms=seeded()
    try:
        seed_joint(ms); c=candidate(ms); admitted=ms.admit_capability_candidate(qualify(ms,c))
        stale=ms.change_recruitment_topology('T',reason='STRUCTURE_DRIFT')
        assert admitted.capability_id in stale
        assert ms.capabilities.contracts[admitted.capability_id].qualification == QualificationState.STALE
        assert ms.capabilities.contracts['A'].qualification == QualificationState.SHADOW_QUALIFIED
        assert ms.capabilities.contracts['B'].qualification == QualificationState.SHADOW_QUALIFIED
    finally: td.cleanup()


def test_candidate_digest_binds_composition_ancestry_and_tamper_fails_ticket():
    td,ms=seeded()
    try:
        seed_joint(ms); c=candidate(ms); ticket=qualify(ms,c)
        # frozen dataclass, but operational_signature is a mutable mapping: mutate it
        # to emulate transport/storage corruption after ticket issuance.
        c.operational_signature['coordination_epochs'] = []
        with pytest.raises(ValueError, match='CANDIDATE_DIGEST_MISMATCH'):
            ms.admit_capability_candidate(ticket)
    finally: td.cleanup()


def test_no_parallel_composition_authority_surface_was_added():
    td,ms=seeded()
    try:
        forbidden=(
            'multi_child_planner','multi_child_registry','semantic_child_registry',
            'auto_qualify_composition','auto_admit_composition','infer_transaction_semantics',
            'composition_truth','child_role_identity','parent_command_authority',
        )
        assert all(not hasattr(ms,n) for n in forbidden)
        s=ms.status()
        assert s['multi_child_planner_authority']=='NONE'
        assert s['composition_self_qualification_authority']=='NONE'
    finally: td.cleanup()
