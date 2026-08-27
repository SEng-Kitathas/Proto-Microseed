from __future__ import annotations
import tempfile
from pathlib import Path
from microseed.runtime.entity import Microseed
from microseed.runtime.types import (
    OperationalCounterpartyContract, OperationalCoordinationContract,
    EpisodeSchemaContract, CapabilityContract, Authority, QualificationState,
)

def ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1127-'); return td,Microseed(Path(td.name))

def cp(cid='cp'):
    c=OperationalCounterpartyContract(counterparty_id=cid,purpose='opaque',signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1053-1077',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNAL_QUALIFICATION',));c.signature_sha256=c.computed_signature_sha256();return c

def coord(cid='coord',counterparty='cp',epoch=0):
    c=OperationalCoordinationContract(coordination_id=cid,purpose='opaque',participant_counterparty_epochs=((counterparty,epoch),),signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1078-1102',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNAL_QUALIFICATION',));c.signature_sha256=c.computed_signature_sha256();return c

def ep(sid='ep',coord_epochs=(),cp_epochs=()):
    return EpisodeSchemaContract(schema_id=sid,purpose='opaque distributed grouping',signature_sha256='e'*64,authority=Authority.DERIVED_READ_ONLY,lineage=('MS1103-1127',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('EXTERNAL_EPISODE_QUALIFICATION',),coordination_epochs=tuple(coord_epochs),counterparty_epochs=tuple(cp_epochs))

def cap(cid='cap'):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1)

def test_episode_schema_rejects_stale_coordination_dependency():
    td,m=ms()
    try:
        m.register_operational_counterparty(cp(),evidence=());m.register_operational_coordination(coord(),evidence=())
        m.change_operational_coordination('coord',reason='DRIFT')
        try:m.register_episode_schema(ep(coord_epochs=(('coord',0),)),evidence=());assert False
        except ValueError as e:assert 'EPISODE_SCHEMA_COORDINATION_EPOCH_DRIFT' in str(e)
    finally:td.cleanup()

def test_coordination_drift_stales_bound_episode_and_capability_but_not_unrelated_episode():
    td,m=ms()
    try:
        m.register_operational_counterparty(cp(),evidence=())
        m.register_operational_coordination(coord('ra'),evidence=());m.register_operational_coordination(coord('rb'),evidence=())
        m.register_episode_schema(ep('epa',coord_epochs=(('ra',0),)),evidence=())
        m.register_episode_schema(ep('epb',coord_epochs=(('rb',0),)),evidence=())
        for sid,cid in [('epa','ca'),('epb','cb')]:
            m.register_capability(cap(cid),evidence=(),extra_development_dependencies=(sid,));m.episodes.bind_capability(sid,cid)
        stale=m.change_operational_coordination('ra',reason='CONVENTION_CHANGED')
        assert not m.episodes.is_current('epa',0)
        assert m.episodes.is_current('epb',0)
        assert m.capabilities.contracts['ca'].qualification==QualificationState.STALE
        assert m.capabilities.contracts['cb'].qualification in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED}
        assert 'ca' in stale and 'cb' not in stale
    finally:td.cleanup()

def test_counterparty_drift_stales_relation_bound_episode_transitively():
    td,m=ms()
    try:
        m.register_operational_counterparty(cp(),evidence=());m.register_operational_coordination(coord(),evidence=())
        m.register_episode_schema(ep(coord_epochs=(('coord',0),)),evidence=())
        m.register_capability(cap('c1'),evidence=(),extra_development_dependencies=('ep',));m.episodes.bind_capability('ep','c1')
        m.register_capability(CapabilityContract('c2','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',{},dependencies=('c1',),qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1),evidence=())
        stale=m.change_operational_counterparty('cp',reason='COUNTERPARTY_CHANGED')
        assert not m.episodes.is_current('ep',0)
        assert m.capabilities.contracts['c1'].qualification==QualificationState.STALE
        assert m.capabilities.contracts['c2'].qualification==QualificationState.STALE
        assert {'c1','c2'} <= stale
    finally:td.cleanup()

def test_direct_counterparty_bound_episode_schema_is_supported_without_identity_authority():
    td,m=ms()
    try:
        m.register_operational_counterparty(cp(),evidence=())
        e=ep(cp_epochs=(('cp',0),));m.register_episode_schema(e,evidence=())
        assert m.episodes.is_current('ep',0)
        assert not hasattr(e,'semantic_joint_goal_authority')
        m.change_operational_counterparty('cp',reason='DRIFT')
        assert not m.episodes.is_current('ep',0)
    finally:td.cleanup()

def test_status_preserves_prelingual_ceiling_and_ms1128_hard_stop():
    td,m=ms()
    try:
        s=m.status();assert s['research_terminal_ms']>=1152 and s['integration_evidence_through_ms']>=1152
        assert s['next_ms']>=1203 and s['next_ms'] >= 1278
        assert s['frontier'].startswith('ATTN-MS')
        assert s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
        assert s['distributed_episode_semantic_joint_goal_authority']=='NONE'
    finally:td.cleanup()
