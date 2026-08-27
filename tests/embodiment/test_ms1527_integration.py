from __future__ import annotations
from pathlib import Path
import tempfile
import pytest

from microseed import (
    Microseed, Authority, QualificationState, FeasibilityState, CapabilityContract,
    OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract,
    RecruitmentTopologyContract, OperationalCounterpartyContract, OperationalCoordinationContract,
    RecruitmentOption, RehearsalTransitionObservation, QueryObligation, Observation,
    ReentryWarrant,
)


def cap(cid, *, effect=False, handler=None, coord=False):
    return CapabilityContract(
        cid,'opaque',{},{},(),(),Authority.EFFECT if effect else Authority.DERIVED_READ_ONLY,
        ('MS1503-1527-INTEGRATION',),'CURRENT',{},
        query_obligation_id='ACT' if effect else None,
        qualification=QualificationState.SHADOW_QUALIFIED,handler=handler,
        operational_scope_id='SCOPE' if effect else None,
    )


def cp():
    x=OperationalCounterpartyContract('CP','opaque-counterparty','',Authority.DERIVED_READ_ONLY,('MS1053-1077',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED)
    x.signature_sha256=x.computed_signature_sha256(); return x


def coord():
    x=OperationalCoordinationContract('R','opaque-coordination',(('CP',0),),'',Authority.DERIVED_READ_ONLY,('MS1078-1102',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED)
    x.signature_sha256=x.computed_signature_sha256(); return x


def topo():
    x=RecruitmentTopologyContract('T','opaque-topology',(('A','B'),('B','C')),(('A',0),('B',0),('C',0)),'',Authority.DERIVED_READ_ONLY,('MS1003-1027',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED)
    x.signature_sha256=x.computed_signature_sha256(); return x


def frame(): return OperationalFrameContract('F','opaque-frame','f'*64,Authority.DERIVED_READ_ONLY,('MS878-902',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED)
def value(): return ValueVariableContract('V','opaque-regulatory',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS953-977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'))
def episode(): return EpisodeSchemaContract('E','opaque-episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),coordination_epochs=(('R',0),))


def rows():
    out=[]; k=0
    for s,a,nxt,eff,cr in (('S0','A','SA',.8,None),('S0','B','S1',-.4,None),('S1','C','S2',2.6,'R'),('S1','A','SA',.8,None)):
        for _ in range(12):
            k+=1; out.append(RehearsalTransitionObservation(f'EV{k}',s,a,nxt,eff,0,'F',0,'E',0,'T',0,cr,0 if cr else None))
    return tuple(out)


def opts(): return (RecruitmentOption('A',FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption('B',FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption('C',FeasibilityState.FEASIBLE,local_cost=.1))
def obligation(): return QueryObligation('ACT','opaque-action',required_authority=Authority.EFFECT,operational_scope_id='SCOPE')


def seed(state: Path):
    m=Microseed(state)
    m.register_operational_frame(frame()); m.register_value_variable(value()); m.observe_value_state('V',0.0)
    m.register_operational_counterparty(cp()); m.register_operational_coordination(coord())
    m.register_capability(cap('A',effect=True,handler=lambda **_: {'receipt':'A'}))
    m.register_capability(cap('B',effect=True,handler=lambda **_: {'receipt':'B'}))
    m.register_capability(cap('C',effect=True,handler=lambda **_: {'receipt':'C'}),coordination_dependencies=(('R',0),))
    m.register_recruitment_topology(topo()); m.register_episode_schema(episode())
    m.observe_opaque_control_state(Observation('CS0','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS0')
    p=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V')
    assert p.sequence==('B','C')
    return m,p


def current(m,h):
    k,x=h.split(':',1)
    if k=='CAP':
        c=m.capabilities.contracts.get(x); return c is not None and c.qualification in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED}
    if k=='CP': return m.counterparties.is_current(x)
    if k=='COORD': return m.coordinations.is_current(x)
    if k=='TOPO': return m.topologies.is_current(x)
    return False


def warrant(m,h,*,provider=True,challenge=True,scope=('SCOPE',)):
    p=m.historical_reentry_projection(); r=p.record(h); assert r is not None
    return ReentryWarrant(
        handle=h,historical_fingerprint_sha256=r.fingerprint_sha256,
        provider_compatible=provider,provider_evidence_id='EXT-PROVIDER:'+h if provider is not None else None,
        executable_challenge_passed=challenge,executable_evidence_id='EXT-CHALLENGE:'+h if challenge is not None else None,
        diagnostic_scope=tuple(scope),dependency_currentness=tuple((d,current(m,d)) for d in r.dependencies),
    )


def register_handle(m,h):
    k,x=h.split(':',1)
    if k=='CAP':
        if x=='C': m.register_capability(cap('C',effect=True,handler=lambda **_: {'receipt':'C'}),coordination_dependencies=(('R',0),))
        else: m.register_capability(cap(x,effect=True,handler=lambda **_: {'receipt':x}))
    elif k=='CP': m.register_operational_counterparty(cp())
    elif k=='COORD': m.register_operational_coordination(coord())
    elif k=='TOPO': m.register_recruitment_topology(topo())
    else: raise KeyError(h)


def reenter_all(m,*,stale=()):
    p=m.historical_reentry_projection(); order=[]; decisions={}
    for layer in p.layers:
        for h in layer:
            if current(m,h): continue
            w=warrant(m,h,provider=False if h in stale else True)
            d=m.assess_historical_reentry(w,requested_scope='SCOPE'); decisions[h]=d
            if d.status=='READY_FOR_EXISTING_REGISTRATION_PATH': register_handle(m,h); order.append(h)
    return order,decisions


def test_restart_preserves_history_but_no_current_operational_authority():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state)
        assert not m.capabilities.contracts and not m.topologies.topologies and not m.counterparties.contracts and not m.coordinations.contracts
        p=m.historical_reentry_projection(); assert {'CAP:A','CAP:B','CAP:C','TOPO:T','CP:CP','COORD:R'}.issubset(set(p.eligible_handles)); assert p.authority==Authority.NONE


def test_projection_is_read_only_and_does_not_persist_readiness():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); n=len(m.store.events()); p=m.historical_reentry_projection(); assert len(m.store.events())==n
        assert all('REENTRY_READY' not in e['kind'] for e in m.store.events()) and p.authority==Authority.NONE


def test_equivalent_reregistration_collapses_but_divergent_live_repeat_conflicts():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); m.register_capability(cap('A',effect=True,handler=lambda **_:None))
        assert m.historical_reentry_projection().record('CAP:A').equivalent_repeat_count==1
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); x=cap('A',effect=True,handler=lambda **_:None); x.operational_scope_id='ALT'; m.register_capability(x)
        p=m.historical_reentry_projection(); assert p.record('CAP:A').status=='HISTORICAL_CONFLICT' and 'CAP:A' not in p.eligible_handles


def test_provider_executable_scope_and_dependency_planes_are_orthogonal():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); r=m.historical_reentry_projection().record('CAP:C')
        base=ReentryWarrant('CAP:C',historical_fingerprint_sha256=r.fingerprint_sha256)
        assert m.assess_historical_reentry(base,requested_scope='SCOPE').reason=='PROVIDER_COMPATIBILITY_UNRESOLVED'
        wp=ReentryWarrant('CAP:C',r.fingerprint_sha256,True,'P')
        assert m.assess_historical_reentry(wp,requested_scope='SCOPE').reason=='EXECUTABLE_COMPATIBILITY_UNRESOLVED'
        wx=ReentryWarrant('CAP:C',r.fingerprint_sha256,True,'P',True,'X',('OTHER',),())
        assert m.assess_historical_reentry(wx,requested_scope='SCOPE').reason=='OUTSIDE_DIAGNOSTIC_SCOPE'
        wd=ReentryWarrant('CAP:C',r.fingerprint_sha256,True,'P',True,'X',('SCOPE',),(('COORD:R',False),))
        d=m.assess_historical_reentry(wd,requested_scope='SCOPE'); assert d.reason=='DEPENDENCY_NOT_CURRENT' and d.blocking_dependencies==('COORD:R',)


def test_fingerprint_mismatch_cannot_be_overridden_by_green_external_planes():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state)
        w=ReentryWarrant('CAP:A','0'*64,True,'P',True,'X',('SCOPE',),())
        assert m.assess_historical_reentry(w,requested_scope='SCOPE').reason=='HISTORICAL_FINGERPRINT_MISMATCH'


def test_ready_result_is_authority_none_and_still_does_not_register():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); n=len(m.store.events())
        d=m.assess_historical_reentry(warrant(m,'CAP:A'),requested_scope='SCOPE')
        assert d.status=='READY_FOR_EXISTING_REGISTRATION_PATH' and d.authority==Authority.NONE
        assert 'A' not in m.capabilities.contracts and len(m.store.events())==n


def test_existing_registration_paths_remain_only_current_authority_owner():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); order,_=reenter_all(m)
        assert set(order)=={'CAP:A','CAP:B','CAP:C','CP:CP','COORD:R','TOPO:T'}
        assert {'A','B','C'}==set(m.capabilities.contracts) and m.topologies.is_current('T') and m.coordinations.is_current('R')
        assert not hasattr(m,'reentry_registry') and not hasattr(m,'reentry_manager')


def test_stale_coordination_selectively_blocks_dependent_closure_not_unrelated_capabilities():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); order,decisions=reenter_all(m,stale={'COORD:R'})
        assert {'CAP:A','CAP:B','CP:CP'}.issubset(set(order)); assert 'COORD:R' not in order and 'CAP:C' not in order and 'TOPO:T' not in order
        assert m.capabilities.invoke('B',obligation())['status']=='CAPABILITY_RESULT'
        assert decisions['COORD:R'].reason=='PROVIDER_INCOMPATIBLE'


def test_existing_invalidation_after_reentry_still_stales_dependency_closure():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); reenter_all(m)
        stale=m.invalidate_capability('C',reason='POST_REENTRY_DRIFT')
        assert 'C' in stale and not m.topologies.is_current('T')


def test_no_loader_snapshot_or_auto_reentry_api_is_promoted():
    with tempfile.TemporaryDirectory() as td:
        m=Microseed(Path(td))
        for name in ('load_capabilities','restore_operational_state','auto_reenter','reentry_manager','reentry_registry','persist_reentry_ready'):
            assert not hasattr(m,name)


def test_end_goal_restart_reentry_restores_real_rehearsal_action_outcome_reality_loop():
    """Not a toy registry test: re-entry must buy whole-organism behavioral continuity."""
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); _,p=seed(state); m=Microseed(state)
        # Re-establish current external anchors that this campaign did not claim to recover.
        m.register_operational_frame(frame()); m.register_value_variable(value())
        order,decisions=reenter_all(m); assert all(d.status=='READY_FOR_EXISTING_REGISTRATION_PATH' for d in decisions.values())
        m.register_episode_schema(episode()); m.observe_value_state('V',0.0)
        assert m.counterfactual_rehearsal_status(p.proposal_id)['status']=='CURRENT_REHEARSAL_PROPOSAL'
        ir=m.nominate_bounded_action_intent(p.proposal_id,obligation()); assert ir['status']=='ACTION_INTENT_NOMINATED'
        er=m.execute_bounded_action(ir['intent']['intent_id'],obligation()); eid=er['execution']['execution_id']
        out=m.record_bounded_action_outcome(eid,Observation('R1','EXT',f'action-execution:{eid}',{'next_state_id':'S1','value_id':'V','observed_value':-.4},authority=Authority.OBSERVATION_ONLY),evidence_id='ER1')
        assert out['requires_redeliberation'] and m.action_closure.current_state.state_id=='S1'
        p2=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S1',value_id='V'); assert p2.sequence==('C',)
        ir2=m.nominate_bounded_action_intent(p2.proposal_id,obligation()); er2=m.execute_bounded_action(ir2['intent']['intent_id'],obligation()); e2=er2['execution']['execution_id']
        m.record_bounded_action_outcome(e2,Observation('R2','EXT',f'action-execution:{e2}',{'next_state_id':'S2','value_id':'V','observed_value':2.2},authority=Authority.OBSERVATION_ONLY),evidence_id='ER2')
        assert m.value_pressure('V')['pressure_magnitude']==0.0 and m.action_closure.current_state.state_id=='S2'


def test_end_goal_changed_reality_blocks_old_rehearsal_but_preserves_independent_action():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); _,p=seed(state); m=Microseed(state); m.register_operational_frame(frame()); m.register_value_variable(value()); m.observe_value_state('V',0.0)
        reenter_all(m,stale={'COORD:R'})
        assert m.capabilities.invoke('B',obligation())['status']=='CAPABILITY_RESULT'
        st=m.counterfactual_rehearsal_status(p.proposal_id); assert st['status']=='UNKNOWN_INCOMPLETE'
        assert 'C' not in m.capabilities.contracts and not m.topologies.is_current('T')


def test_end_goal_recovery_after_stale_premise_can_restore_closure_without_snapshot_authority():
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); _,p=seed(state); m=Microseed(state); m.register_operational_frame(frame()); m.register_value_variable(value()); m.observe_value_state('V',0.0)
        reenter_all(m,stale={'COORD:R'}); assert 'C' not in m.capabilities.contracts
        reenter_all(m); m.register_episode_schema(episode())
        assert m.counterfactual_rehearsal_status(p.proposal_id)['status']=='CURRENT_REHEARSAL_PROPOSAL'


def test_status_advances_only_to_ms1527_and_ms1528_remains_unstarted():
    with tempfile.TemporaryDirectory() as td:
        m=Microseed(Path(td)); s=m.status()
        assert s['research_terminal_ms']==1527 and s['integration_evidence_through_ms']==1527 and s['next_ms']==1528 and s['next_started'] is False
