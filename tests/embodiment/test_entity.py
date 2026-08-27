from pathlib import Path
import tempfile
from microseed import Microseed
from microseed.runtime.types import (
    Authority, CapabilityContract, EpistemicStatus, QualificationState,
    QueryObligation, Observation, ResourceMode,
)
from microseed.cognition.operator_language import base_closure, swap_pair
from microseed.cognition.predicates import change, rise


def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-test-')
    return td, Microseed(Path(td.name))


def test_self_test():
    td,ms=make_ms()
    try: assert ms.self_test()['all_pass']
    finally: td.cleanup()


def test_dependency_currentness_stales_dependent():
    td,ms=make_ms()
    try:
        a=CapabilityContract('A','base',{}, {},(),(),Authority.DERIVED_READ_ONLY,('TEST',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda:1)
        b=CapabilityContract('B','derived',{}, {},(),(),Authority.DERIVED_READ_ONLY,('TEST',),'CURRENT',{},dependencies=('A',),qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda:2)
        ms.register_capability(a);ms.register_capability(b)
        ms.capabilities.change_dependency('A')
        assert ms.capabilities.contracts['B'].qualification==QualificationState.STALE
    finally: td.cleanup()


def test_query_obligation_binding():
    td,ms=make_ms()
    try:
        c=CapabilityContract('C','scoped',{}, {},(),(),Authority.DERIVED_READ_ONLY,('TEST',),'CURRENT',{},query_obligation_id='Q1',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda x:x+1)
        ms.register_capability(c)
        bad=ms.capabilities.invoke('C',QueryObligation('Q2','wrong'),x=1)
        good=ms.capabilities.invoke('C',QueryObligation('Q1','right'),x=1)
        assert bad['status']=='UNKNOWN_INCOMPLETE'
        assert good['value']==2
    finally:td.cleanup()


def test_persistence_is_not_selfhood():
    td,ms=make_ms()
    try:
        assert ms.continuity_assessment().identity_claim=='NOT_QUALIFIED'
        assert 'CONTINUITY' in ms.continuity_assessment().status
    finally: td.cleanup()


def test_research_operator_closure_delta():
    # MS702 lineage: choose a K where SWAP_PAIR lies outside old base closure.
    found=False
    for K in range(3,8):
        cl=base_closure(K)
        for a in range(K):
            for b in range(a+1,K):
                if swap_pair(K,a,b) not in cl:
                    found=True;break
            if found:break
        if found:break
    assert found


def test_temporal_predicates_are_frame_scoped_research_only():
    c=change([0,0,1,1,0]);r=rise([0,0,1,1,0])
    assert c.qualification=='RESEARCH_ONLY' and r.qualification=='RESEARCH_ONLY'
    assert c.frame_scope=='SAMPLE_ADJACENT'


def test_observation_resource_mode_and_unknown_currentness():
    td,ms=make_ms()
    try:
        o=Observation('X','provider','thing',123,observed_at=None,resource_mode=ResourceMode.FEDERATED)
        p=ms.observe(o,now_iso='2026-08-20T00:00:00Z')
        assert p['currentness']=='UNKNOWN_INCOMPLETE'
        assert p['resource_mode']=='FEDERATED'
    finally:td.cleanup()


def test_ms1003_hard_stop():
    td,ms=make_ms()
    try:
        s=ms.status()
        assert s['ancestral_entity_baseline_ms']==801
        assert s['research_terminal_ms']>=1152
        assert s['next_ms']>=1203
        assert s['next_ms'] >= 1278
        assert s['frontier'].startswith('ATTN-MS')
    finally:td.cleanup()

def test_composition_does_not_create_authority():
    td,ms=make_ms()
    try:
        a=CapabilityContract('READ','read',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS251',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda:1)
        b=CapabilityContract('EFFECTISH','effect',{}, {},(),(),Authority.EFFECT,('TEST',),'CURRENT',{},dependencies=('READ',),qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda:2)
        ms.register_capability(a);ms.register_capability(b)
        r=ms.compose(['EFFECTISH'])
        assert r.status=='COMPOSED_EPHEMERAL'
        assert r.authority==Authority.NONE
    finally:td.cleanup()
