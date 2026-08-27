from __future__ import annotations
from pathlib import Path
import tempfile

from microseed import (
    Microseed, Authority, CapabilityContract, CapabilityCandidate,
    ExternalCapabilityQualifier, EpistemicStatus, QualificationState,
    RecruitmentTopologyContract, FeasibilityState,
)
from microseed.development.recruitment import RecruitmentOption


def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1027-')
    return td,Microseed(Path(td.name))


def cap(cid: str, deps=()):
    return CapabilityContract(
        capability_id=cid,purpose='opaque',boundary={},interface={},invariants=(),hazards=(),
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS1003-1027-TEST',),currentness='CURRENT',resources={},
        dependencies=tuple(deps),qualification=QualificationState.SHADOW_QUALIFIED,
    )


def topology(ms: Microseed, tid='T', relations=(('A','B'),)):
    nodes=sorted({x for e in relations for x in e})
    t=RecruitmentTopologyContract(
        topology_id=tid,purpose='opaque-operational-recruitment-topology',relations=tuple(tuple(sorted(e)) for e in relations),
        capability_epochs=tuple((cid,ms.capabilities.epochs[cid]) for cid in nodes),signature_sha256='',
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS1003-1027',),currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('HSP_EXTERNAL_TOPOLOGY_QUALIFICATION','PAIRWISE_CONSTRUCTOR_ASSISTANCE_ACCOUNTED'),
        invariants=('NO_SEMANTIC_ROLE_AUTHORITY','NO_IDENTITY_AUTHORITY'),
        hazards=('PAIRWISE_RELATION_LANGUAGE','SUPPLIED_INTERVENTION_BOUNDARIES'),
    )
    t.signature_sha256=t.computed_signature_sha256()
    return t


def seed_ab(ms: Microseed):
    ms.register_capability(cap('A')); ms.register_capability(cap('B'))


def test_externally_qualified_topology_is_first_class_but_grants_no_role_or_identity_authority():
    td,ms=make_ms()
    try:
        seed_ab(ms); t=topology(ms); ms.register_recruitment_topology(t)
        assert ms.topologies.is_current('T',0)
        snap=ms.topologies.snapshot()['T']['contract']
        assert snap['semantic_role_authority']=='NONE'
        assert snap['identity_authority']=='NONE'
        assert ms.status()['topology_identity_authority']=='NONE'
        assert not hasattr(ms,'discover_recruitment_topology')
    finally: td.cleanup()


def test_topology_signature_is_content_bound_and_mutation_cannot_reuse_old_signature():
    td,ms=make_ms()
    try:
        seed_ab(ms); t=topology(ms)
        t.relations=(('A','B'),('A','C'))
        try:
            ms.register_recruitment_topology(t)
        except ValueError as exc:
            assert 'TOPOLOGY_SIGNATURE_CONTENT_MISMATCH' in str(exc) or 'TOPOLOGY_RELATION_WITHOUT_CAPABILITY_EPOCH' in str(exc)
        else: raise AssertionError('mutated topology accepted under stale signature')
    finally: td.cleanup()


def test_unqualified_topology_cannot_enter_entity():
    td,ms=make_ms()
    try:
        seed_ab(ms); t=topology(ms); t.qualification=QualificationState.RESEARCH_ONLY
        t.signature_sha256=t.computed_signature_sha256()
        try: ms.register_recruitment_topology(t)
        except ValueError as exc: assert 'externally qualified' in str(exc)
        else: raise AssertionError('research-only topology promoted')
    finally: td.cleanup()


def test_qualified_topology_can_bind_recruitment_but_not_strengthen_authority():
    td,ms=make_ms()
    try:
        seed_ab(ms); ms.register_recruitment_topology(topology(ms))
        p=ms.nominate_recruitment((
            RecruitmentOption('A',FeasibilityState.FEASIBLE,resource_tags=('ra',)),
            RecruitmentOption('B',FeasibilityState.FEASIBLE,resource_tags=('rb',)),
        ),('A','B'),topology_id='T')
        assert p.topology_epoch==('T',0)
        assert p.role_topology_origin=='EXTERNALLY_QUALIFIED_OPERATIONAL_TOPOLOGY'
        assert p.semantic_goal_authority=='NONE'
        assert ms.recruitment_status(p.proposal_id)['status']=='CURRENT'
        out=ms.compose_recruitment(p.proposal_id)
        assert out['status']=='COMPOSED_EPHEMERAL'
        assert out['proposal_authority']==Authority.MODEL_OUTPUT_ONLY.value
    finally: td.cleanup()


def test_topology_drift_makes_bound_recruitment_unknown():
    td,ms=make_ms()
    try:
        seed_ab(ms); ms.register_recruitment_topology(topology(ms))
        p=ms.nominate_recruitment((
            RecruitmentOption('A',FeasibilityState.FEASIBLE,resource_tags=('ra',)),
            RecruitmentOption('B',FeasibilityState.FEASIBLE,resource_tags=('rb',)),
        ),('A','B'),topology_id='T')
        ms.change_recruitment_topology('T',reason='STRUCTURAL_RELATION_CHANGED')
        st=ms.recruitment_status(p.proposal_id)
        assert st['status']=='UNKNOWN_INCOMPLETE'
        assert st['reason']=='RECRUITMENT_TOPOLOGY_EPOCH_DRIFT:T'
    finally: td.cleanup()


def test_constituent_capability_drift_stales_topology_and_topology_bound_capability_closure():
    td,ms=make_ms()
    try:
        seed_ab(ms); ms.register_recruitment_topology(topology(ms))
        ms.register_capability(cap('X'),topology_dependencies=(('T',0),))
        ms.register_capability(cap('Y',deps=('X',)))
        ms.change_capability_dependency('A',reason='CONSTITUENT_POLICY_DRIFT')
        assert not ms.topologies.is_current('T')
        assert ms.capabilities.contracts['X'].qualification==QualificationState.STALE
        assert ms.capabilities.contracts['Y'].qualification==QualificationState.STALE
        assert ms.compose(['Y']).status=='NO_PATH'
        assert ms.development.records['T'].qualification==QualificationState.STALE
    finally: td.cleanup()


def test_pending_candidate_topology_epoch_drift_blocks_admission():
    td,ms=make_ms()
    try:
        seed_ab(ms); ms.register_recruitment_topology(topology(ms))
        proposal_ev=ms.append_evidence('P-TOPO',{'proposal':'x'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED_PROPOSAL')
        ccontract=CapabilityContract(
            'CAND-T','opaque-topology-bound',{}, {},('PROPOSAL_NOT_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,
            ('MS1003-1027',),'CANDIDATE',{},dependencies=('A','B'),qualification=QualificationState.CANDIDATE,
            assistance_ancestry=('QUALIFIED_OPERATIONAL_RECRUITMENT_TOPOLOGY:T@0',),
        )
        cand=CapabilityCandidate(
            candidate_id='CAND-T',proposed_contract=ccontract,evidence=(proposal_ev,),
            assistance_ancestry=ccontract.assistance_ancestry,nomination_basis='BOUNDED_TOPOLOGY_REUSE',
            operational_signature={'dependency_epochs':[['A',0],['B',0]],'topology_epochs':[['T',0]]},
        )
        ms.nominate_capability_candidate(cand)
        ext=ms.append_evidence('HSP-T-HELDOUT',{'heldout':1.0},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL')
        ticket=ExternalCapabilityQualifier(ms.evidence,qualifier_id='HSP-MS1027').qualify(cand,qualification_evidence=(ext,))
        ms.change_recruitment_topology('T',reason='STRUCTURAL_REWRITE')
        try: ms.admit_capability_candidate(ticket)
        except ValueError as exc: assert 'CANDIDATE_TOPOLOGY_EPOCH_DRIFT:T' in str(exc)
        else: raise AssertionError('topology-stale pending capability admitted')
    finally: td.cleanup()


def test_selected_frontier_is_structural_rewrite_identity_and_ms1028_hard_stop():
    td,ms=make_ms()
    try:
        s=ms.status()
        assert s['research_terminal_ms']>=1152
        assert s['integration_evidence_through_ms']>=1152
        assert s['next_ms']>=1203
        assert s['next_ms'] >= 1278
        assert s['frontier'].startswith('ATTN-MS')
        assert s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
        assert s['identity_claim']=='NOT_QUALIFIED'
        assert 'PAIRWISE_RESEARCH_MECHANISM_NOT_ENTITY_AUTHORITY' in s['topology_constructor']
    finally: td.cleanup()
