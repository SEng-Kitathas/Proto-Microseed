from __future__ import annotations
import json, tempfile
from pathlib import Path

from microseed import Microseed, Authority, ReentryWarrant, Observation
from test_ms1527_integration import (
    seed, warrant, register_handle, reenter_all, current,
    cap, frame, value, episode, obligation, rows, opts,
)


def main():
    checks = {}

    # Restart preserves developmental history but does not restore current operational authority.
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state)
        p=m.historical_reentry_projection()
        checks['restart_history_survives_without_current_authority']=(
            {'CAP:A','CAP:B','CAP:C','TOPO:T','CP:CP','COORD:R'}.issubset(set(p.eligible_handles))
            and p.authority==Authority.NONE
            and not m.capabilities.contracts and not m.topologies.topologies
            and not m.counterparties.contracts and not m.coordinations.contracts
        )
        before=len(m.store.events())
        d=m.assess_historical_reentry(warrant(m,'CAP:A'),requested_scope='SCOPE')
        checks['ready_is_authority_none_nonpersistent_and_nonadmitting']=(
            d.status=='READY_FOR_EXISTING_REGISTRATION_PATH' and d.authority==Authority.NONE
            and len(m.store.events())==before and 'A' not in m.capabilities.contracts
            and all('REENTRY_READY' not in e.get('kind','') for e in m.store.events())
        )

    # Green metadata cannot override lifecycle/history/evidence-plane failures.
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); live,_=seed(state); live.invalidate_capability('A',reason='SCAR-TOMBSTONE')
        m=Microseed(state); r=m.historical_reentry_projection().record('CAP:A')
        w=ReentryWarrant('CAP:A',r.fingerprint_sha256,True,'P',True,'X',('SCOPE',),())
        checks['historical_tombstone_dominates_green_warrants']=(m.assess_historical_reentry(w,requested_scope='SCOPE').reason=='HISTORICAL_STALE')

    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); a=m.historical_reentry_projection().record('CAP:A')
        forged=ReentryWarrant('CAP:A',a.fingerprint_sha256,True,'SAME',True,'SAME',('SCOPE',),())
        gain=ReentryWarrant('CAP:A',a.fingerprint_sha256,True,'P',True,'X',('SCOPE',),(),Authority.EFFECT)
        checks['warrant_cannot_gain_authority_or_reuse_same_evidence_plane']=(
            m.assess_historical_reentry(forged,requested_scope='SCOPE').reason=='EVIDENCE_PLANE_OVERLAP'
            and m.assess_historical_reentry(gain,requested_scope='SCOPE').reason=='WARRANT_AUTHORITY_MUST_BE_NONE'
        )

    # Existing current registries, not request-carried claims, decide dependency currentness.
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); c=m.historical_reentry_projection().record('CAP:C')
        forged=ReentryWarrant('CAP:C',c.fingerprint_sha256,True,'P',True,'X',('SCOPE',),(('COORD:R',True),))
        d=m.assess_historical_reentry(forged,requested_scope='SCOPE')
        checks['forged_dependency_currentness_cannot_fool_entity']=(d.reason=='DEPENDENCY_NOT_CURRENT' and d.blocking_dependencies==('COORD:R',))

    # READY is not admission: TOCTOU changes are rechecked at the existing registration boundary.
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state)
        for h in ('CP:CP','COORD:R'):
            d=m.assess_historical_reentry(warrant(m,h),requested_scope='SCOPE'); assert d.status=='READY_FOR_EXISTING_REGISTRATION_PATH'; register_handle(m,h)
        d=m.assess_historical_reentry(warrant(m,'CAP:C'),requested_scope='SCOPE'); assert d.status=='READY_FOR_EXISTING_REGISTRATION_PATH'
        m.change_operational_coordination('R',reason='SCAR-TOCTOU')
        try:
            register_handle(m,'CAP:C'); blocked=False
        except ValueError:
            blocked=True
        checks['existing_registration_boundary_rechecks_toctou']=blocked and 'C' not in m.capabilities.contracts

    # Reality change blocks only dependent closure and old rehearsal; unrelated effect remains usable.
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); _,proposal=seed(state); m=Microseed(state)
        m.register_operational_frame(frame()); m.register_value_variable(value()); m.observe_value_state('V',0.0)
        reenter_all(m,stale={'COORD:R'})
        checks['stale_coordination_selectively_blocks_old_closure']=(
            current(m,'CAP:A') and current(m,'CAP:B') and not current(m,'CAP:C') and not current(m,'TOPO:T')
            and m.counterfactual_rehearsal_status(proposal.proposal_id)['status']=='UNKNOWN_INCOMPLETE'
        )
        checks['unrelated_effect_capability_survives_selective_block']=(m.capabilities.invoke('B',obligation())['status']=='CAPABILITY_RESULT')

    # No second authority owner or hidden snapshot/auto-restore substrate.
    with tempfile.TemporaryDirectory() as td:
        m=Microseed(Path(td))
        forbidden=('reentry_registry','reentry_manager','auto_reenter','restore_operational_state','persist_reentry_ready','self_qualify_reentry')
        checks['no_parallel_reentry_subsystem']=all(not hasattr(m,x) for x in forbidden)

    # End-goal bearing scar: lawful re-entry must reconnect to actual rehearsal/action/outcome/re-deliberation.
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); _,p=seed(state); m=Microseed(state)
        m.register_operational_frame(frame()); m.register_value_variable(value())
        order,decisions=reenter_all(m); assert all(d.status=='READY_FOR_EXISTING_REGISTRATION_PATH' for d in decisions.values())
        m.register_episode_schema(episode()); m.observe_value_state('V',0.0)
        assert m.counterfactual_rehearsal_status(p.proposal_id)['status']=='CURRENT_REHEARSAL_PROPOSAL'
        ir=m.nominate_bounded_action_intent(p.proposal_id,obligation()); er=m.execute_bounded_action(ir['intent']['intent_id'],obligation()); eid=er['execution']['execution_id']
        out=m.record_bounded_action_outcome(eid,Observation('R1','EXT',f'action-execution:{eid}',{'next_state_id':'S1','value_id':'V','observed_value':-.4},authority=Authority.OBSERVATION_ONLY),evidence_id='SCAR-ER1')
        p2=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S1',value_id='V')
        ir2=m.nominate_bounded_action_intent(p2.proposal_id,obligation()); er2=m.execute_bounded_action(ir2['intent']['intent_id'],obligation()); e2=er2['execution']['execution_id']
        m.record_bounded_action_outcome(e2,Observation('R2','EXT',f'action-execution:{e2}',{'next_state_id':'S2','value_id':'V','observed_value':2.2},authority=Authority.OBSERVATION_ONLY),evidence_id='SCAR-ER2')
        checks['reentry_buys_real_behavioral_continuity']=(
            out['requires_redeliberation'] and m.action_closure.current_state.state_id=='S2'
            and m.value_pressure('V')['pressure_magnitude']==0.0
        )

    # Existing post-reentry invalidation still owns currentness closure.
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); reenter_all(m)
        stale=m.invalidate_capability('C',reason='SCAR-POST-REENTRY-DRIFT')
        checks['existing_invalidation_still_stales_reentered_dependency_closure']=('C' in stale and not m.topologies.is_current('T'))

    with tempfile.TemporaryDirectory() as td:
        s=Microseed(Path(td)).status()
        checks['hard_stop_ms1528_not_started']=(s['research_terminal_ms']==1527 and s['integration_evidence_through_ms']==1527 and s['next_ms']==1528 and s['next_started'] is False)

    out={'schema':'microseed.ms1503-1527.integration.replay-scar.v1','passed':sum(bool(v) for v in checks.values()),'total':len(checks),'all_pass':all(checks.values()),'checks':checks}
    root=Path(__file__).resolve().parents[2]
    (root/'MS1503_1527_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if out['all_pass'] else 1

if __name__=='__main__': raise SystemExit(main())
