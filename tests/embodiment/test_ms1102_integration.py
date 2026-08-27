from __future__ import annotations
from pathlib import Path
import tempfile
import pytest
from microseed import (
    Microseed, Authority, QualificationState, CapabilityContract,
    OperationalCounterpartyContract, OperationalCoordinationContract,
    CapabilityCandidate, ExternalCapabilityQualifier, EpistemicStatus,
)

def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1102-'); return td,Microseed(Path(td.name))

def cp(cid='CP0'):
    c=OperationalCounterpartyContract(counterparty_id=cid,purpose='opaque-causal-source',signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1053-1077',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('HSP_EXTERNAL_COUNTERPARTY_QUALIFICATION',))
    c.signature_sha256=c.computed_signature_sha256(); return c

def rel(rid='R0',cid='CP0'):
    c=OperationalCoordinationContract(coordination_id=rid,purpose='opaque-mutual-action-contingency',participant_counterparty_epochs=((cid,0),),signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1078-1102',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('HSP_EXTERNAL_COORDINATION_QUALIFICATION',))
    c.signature_sha256=c.computed_signature_sha256(); return c

def cap(cid):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1078-1102',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1)

def test_coordination_contract_has_hard_semantic_authority_ceiling():
    td,ms=make_ms()
    try:
        ms.register_operational_counterparty(cp()); r=rel(); ms.register_operational_coordination(r)
        assert r.semantic_commitment_authority=='NONE' and r.intention_authority=='NONE'
        assert r.promise_authority=='NONE' and r.identity_authority=='NONE'
        bad=rel('RBAD'); bad.semantic_commitment_authority='PROMISE'; bad.signature_sha256=bad.computed_signature_sha256()
        with pytest.raises(ValueError,match='FORBIDDEN_AUTHORITY'):
            ms.register_operational_coordination(bad)
    finally: td.cleanup()

def test_coordination_specific_drift_stales_only_bound_relation_capability():
    td,ms=make_ms()
    try:
        ms.register_operational_counterparty(cp())
        ms.register_operational_coordination(rel('RA')); ms.register_operational_coordination(rel('RB'))
        ms.register_capability(cap('JA'),coordination_dependencies=(('RA',0),))
        ms.register_capability(cap('JB'),coordination_dependencies=(('RB',0),))
        stale=ms.change_operational_coordination('RA',reason='CONVENTION_A_DRIFT')
        assert 'JA' in stale and ms.capabilities.contracts['JA'].qualification==QualificationState.STALE
        assert ms.capabilities.contracts['JB'].qualification==QualificationState.SHADOW_QUALIFIED
        assert ms.counterparties.is_current('CP0',0)
    finally: td.cleanup()

def test_counterparty_drift_invalidates_all_relations_qualified_against_it():
    td,ms=make_ms()
    try:
        ms.register_operational_counterparty(cp())
        ms.register_operational_coordination(rel('RA')); ms.register_operational_coordination(rel('RB'))
        ms.register_capability(cap('JA'),coordination_dependencies=(('RA',0),))
        ms.register_capability(cap('JB'),coordination_dependencies=(('RB',0),))
        stale=ms.change_operational_counterparty('CP0',reason='COUNTERPARTY_DRIFT')
        assert {'JA','JB'}<=stale
        assert not ms.coordinations.is_current('RA') and not ms.coordinations.is_current('RB')
    finally: td.cleanup()

def test_pending_candidate_rechecks_coordination_epoch_after_ticket():
    td,ms=make_ms()
    try:
        ms.register_operational_counterparty(cp()); ms.register_operational_coordination(rel())
        pe=ms.append_evidence('P',{'proposal':1},EpistemicStatus.PRESSURE_SUPPORTED)
        qe=ms.append_evidence('Q',{'heldout':1},EpistemicStatus.PROVED)
        c=CapabilityContract('JC','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1078-1102',),'CANDIDATE',{},qualification=QualificationState.CANDIDATE)
        cand=CapabilityCandidate('JC',c,(pe,),operational_signature={'coordination_epochs':[['R0',0]]})
        ms.nominate_capability_candidate(cand); ticket=ExternalCapabilityQualifier(ms.evidence).qualify(cand,qualification_evidence=(qe,))
        ms.change_operational_coordination('R0',reason='DRIFT_AFTER_TICKET')
        with pytest.raises(ValueError,match='CANDIDATE_COORDINATION_EPOCH_DRIFT'):
            ms.admit_capability_candidate(ticket)
    finally: td.cleanup()

def test_capability_cannot_bind_stale_coordination_epoch():
    td,ms=make_ms()
    try:
        ms.register_operational_counterparty(cp()); ms.register_operational_coordination(rel())
        ms.change_operational_coordination('R0',reason='DRIFT')
        with pytest.raises(ValueError,match='CAPABILITY_COORDINATION_EPOCH_DRIFT'):
            ms.register_capability(cap('J'),coordination_dependencies=(('R0',0),))
    finally: td.cleanup()

def test_ms1102_status_preserves_prelingual_ceiling_and_hard_stop():
    td,ms=make_ms()
    try:
        s=ms.status(); assert s['research_terminal_ms']>=1152 and s['integration_evidence_through_ms']>=1152
        assert s['next_ms']>=1203 and s['next_ms'] >= 1278
        assert s['frontier'].startswith('ATTN-MS')
        assert s['coordination_semantic_commitment_authority']=='NONE'
        assert s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
        assert not hasattr(ms,'discover_operational_coordination')
    finally: td.cleanup()
