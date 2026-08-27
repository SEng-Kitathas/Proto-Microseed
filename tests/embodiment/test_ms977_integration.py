from __future__ import annotations
from pathlib import Path
import hashlib, tempfile

from microseed import (
    Microseed, Authority, CapabilityContract, CapabilityCandidate, EpisodeSchemaContract,
    ExternalCapabilityQualifier, EpistemicStatus, QualificationState, ValueVariableContract,
)


def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms977-')
    return td, Microseed(Path(td.name))


def value_contract(vid='V0', lo=.4, hi=.8):
    return ValueVariableContract(
        value_id=vid, purpose='opaque-regulatory-variable', viable_low=lo, viable_high=hi,
        signature_sha256=hashlib.sha256(f'{vid}:{lo}:{hi}'.encode()).hexdigest(),
        authority=Authority.DERIVED_READ_ONLY, lineage=('MS953-977',), currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
        invariants=('NO_SEMANTIC_GOAL_AUTHORITY','NO_SELF_MODIFIABLE_VALUE_AUTHORITY'),
    )


def cap(cid,deps=()):
    return CapabilityContract(
        cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS977-TEST',),'CURRENT',{},
        dependencies=tuple(deps),qualification=QualificationState.SHADOW_QUALIFIED,
    )


def test_signed_bipolar_pressure_is_internally_derived_from_current_state():
    td,ms=make_ms()
    try:
        ms.register_value_variable(value_contract())
        assert ms.value_pressure('V0')['status']=='UNKNOWN_INCOMPLETE'
        ms.observe_value_state('V0',.2)
        low=ms.value_pressure('V0')
        assert low['status']=='CURRENT' and low['signed_pressure']>0
        assert low['semantic_goal_authority']=='NONE'
        ms.observe_value_state('V0',1.0)
        high=ms.value_pressure('V0')
        assert high['signed_pressure']<0
        ms.observe_value_state('V0',.6)
        inside=ms.value_pressure('V0')
        assert inside['signed_pressure']==0.0
    finally:
        td.cleanup()


def test_value_contract_must_be_externally_qualified_and_is_not_self_rewritable():
    td,ms=make_ms()
    try:
        c=value_contract(); c.qualification=QualificationState.CANDIDATE
        try: ms.register_value_variable(c)
        except ValueError as exc: assert 'externally qualified' in str(exc)
        else: raise AssertionError('unqualified value contract registered')
        assert not hasattr(ms,'set_value_viable_interval')
        assert not hasattr(ms,'rewrite_constitutional_value')
    finally: td.cleanup()


def test_value_contract_drift_makes_pressure_unknown():
    td,ms=make_ms()
    try:
        ms.register_value_variable(value_contract())
        ms.observe_value_state('V0',.2)
        assert ms.value_pressure('V0')['status']=='CURRENT'
        ms.change_value_variable('V0',reason='CALIBRATION_OR_CONSTITUTION_CHANGED')
        p=ms.value_pressure('V0')
        assert p['status']=='UNKNOWN_INCOMPLETE'
        assert p['reason']=='VALUE_VARIABLE_NOT_CURRENT'
    finally: td.cleanup()


def test_value_bound_capability_stales_transitively():
    td,ms=make_ms()
    try:
        ms.register_value_variable(value_contract())
        ms.register_capability(cap('M'), value_dependencies=(('V0',0),))
        ms.register_capability(cap('N',('M',)))
        stale=ms.change_value_variable('V0',reason='VALUE_CONTRACT_DRIFT')
        assert stale=={'M','N'}
        assert ms.capabilities.contracts['M'].qualification==QualificationState.STALE
        assert ms.capabilities.contracts['N'].qualification==QualificationState.STALE
        assert ms.compose(['N']).status=='NO_PATH'
    finally: td.cleanup()


def test_value_bound_episode_schema_stales_without_claiming_semantic_goal_identity():
    td,ms=make_ms()
    try:
        ms.register_value_variable(value_contract())
        ep=EpisodeSchemaContract(
            schema_id='EPV', purpose='opaque-goal-relative-grouping',
            signature_sha256=hashlib.sha256(b'epv').hexdigest(),
            authority=Authority.DERIVED_READ_ONLY,lineage=('MS953-977',),currentness='CURRENT',
            qualification=QualificationState.SHADOW_QUALIFIED,
            assistance_ancestry=('EXTERNAL_EPISODE_SCHEMA_QUALIFICATION',),
            value_epochs=(('V0',0),),
            invariants=('NO_SEMANTIC_GOAL_AUTHORITY',),
        )
        ms.register_episode_schema(ep)
        assert ms.episodes.is_current('EPV')
        ms.change_value_variable('V0',reason='VALUE_RELATION_CHANGED')
        assert not ms.episodes.is_current('EPV')
        assert ms.development.records['EPV'].qualification==QualificationState.STALE
    finally: td.cleanup()


def test_status_preserves_assistance_ceiling_and_next_hard_stop():
    td,ms=make_ms()
    try:
        s=ms.status()
        assert s['research_terminal_ms']>=1152
        assert s['next_ms']>=1203 and s['next_ms'] >= 1278
        assert s['goal_formation']=='NOT_QUALIFIED'
        assert 'NOT_VALUE_ORIGIN' in s['regulatory_value_pressure']
        assert s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
        assert s['identity_claim']=='NOT_QUALIFIED'
        assert 'CONSTITUTIONAL-VALUE-PRIOR-ORIGIN' in s['deferred_frontiers']
    finally: td.cleanup()



def test_pending_candidate_value_epoch_drift_blocks_admission():
    td,ms=make_ms()
    try:
        ms.register_value_variable(value_contract())
        proposal_ref=ms.append_evidence(
            'MS977-CANDIDATE-PROPOSAL', {'candidate':'CV','basis':'opaque-operational-trace'},
            EpistemicStatus.UNKNOWN_INCOMPLETE, source='MICROSEED_PROPOSAL',
        )
        proposed=CapabilityContract(
            'CV','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS953-977',),'CANDIDATE',{},
            qualification=QualificationState.CANDIDATE,
        )
        candidate=CapabilityCandidate(
            candidate_id='CV', proposed_contract=proposed, evidence=(proposal_ref,),
            assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
            nomination_basis='VALUE_RELEVANT_OPERATIONAL_COMPOSITION',
            operational_signature={'value_epochs': (('V0',0),)},
        )
        ms.nominate_capability_candidate(candidate)
        ext=ms.append_evidence(
            'HSP-MS977-HOLDOUT', {'heldout_transfer':1.0}, EpistemicStatus.PROVED,
            source='HSP_EXTERNAL',
        )
        ticket=ExternalCapabilityQualifier(ms.evidence,qualifier_id='HSP-MS977').qualify(
            candidate, qualification_evidence=(ext,)
        )
        ms.change_value_variable('V0',reason='VALUE_CONTRACT_CHANGED_AFTER_NOMINATION')
        try:
            ms.admit_capability_candidate(ticket)
        except ValueError as exc:
            assert 'CANDIDATE_VALUE_EPOCH_DRIFT:V0' in str(exc)
        else:
            raise AssertionError('candidate admitted after value ancestry drift')
    finally:
        td.cleanup()
