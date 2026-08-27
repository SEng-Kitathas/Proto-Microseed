from __future__ import annotations
import json, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'tests'/'embodiment'))
from microseed import Microseed, Authority, ReentryWarrant
from test_ms1527_integration import seed, warrant, register_handle, reenter_all, cap, current, frame, value, episode, obligation


def main():
    checks={}
    details={}
    # 1 no history cannot be manufactured into readiness
    with tempfile.TemporaryDirectory() as td:
        m=Microseed(Path(td)); w=ReentryWarrant('CAP:NOPE','0'*64,True,'P',True,'X',('SCOPE',),())
        d=m.assess_historical_reentry(w,requested_scope='SCOPE'); checks['NO_HISTORY__DEFER']=d.reason=='NO_HISTORICAL_REGISTRATION'
    # common seeded restart
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); p=m.historical_reentry_projection(); a=p.record('CAP:A'); c=p.record('CAP:C')
        d=m.assess_historical_reentry(ReentryWarrant('CAP:A','f'*64,True,'P',True,'X',('SCOPE',),()),requested_scope='SCOPE')
        checks['FORGED_HISTORY_FINGERPRINT__DEFER']=d.reason=='HISTORICAL_FINGERPRINT_MISMATCH'
        d=m.assess_historical_reentry(ReentryWarrant('CAP:A',a.fingerprint_sha256,True,'P',True,'X',('SCOPE',),(),Authority.EFFECT),requested_scope='SCOPE')
        checks['WARRANT_AUTHORITY_GAIN__DEFER']=d.reason=='WARRANT_AUTHORITY_MUST_BE_NONE'
        d=m.assess_historical_reentry(ReentryWarrant('CAP:A',a.fingerprint_sha256,True,'SAME',True,'SAME',('SCOPE',),()),requested_scope='SCOPE')
        checks['EVIDENCE_PLANE_OVERLAP__DEFER']=d.reason=='EVIDENCE_PLANE_OVERLAP'
        # lie that R is current inside the warrant; entity must re-read its own registry and reject C
        forged=ReentryWarrant('CAP:C',c.fingerprint_sha256,True,'P',True,'X',('SCOPE',),(('COORD:R',True),))
        d=m.assess_historical_reentry(forged,requested_scope='SCOPE')
        checks['FORGED_DEPENDENCY_CURRENTNESS__CANNOT_FOOL_ENTITY']=d.reason=='DEPENDENCY_NOT_CURRENT' and d.blocking_dependencies==('COORD:R',)
        before=len(m.store.events()); d=m.assess_historical_reentry(warrant(m,'CAP:A'),requested_scope='SCOPE')
        checks['READY__NO_WRITE_NO_REGISTRATION']=d.status=='READY_FOR_EXISTING_REGISTRATION_PATH' and len(m.store.events())==before and 'A' not in m.capabilities.contracts
        checks['READY__AUTHORITY_NONE']=d.authority==Authority.NONE
    # lifecycle tombstone dominates later green metadata
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); live,_=seed(state); live.invalidate_capability('A',reason='HOSTILE_TOMBSTONE'); m=Microseed(state); r=m.historical_reentry_projection().record('CAP:A')
        w=ReentryWarrant('CAP:A',r.fingerprint_sha256,True,'P',True,'X',('SCOPE',),())
        checks['INVALIDATED_HISTORY__CANNOT_REENTER']=m.assess_historical_reentry(w,requested_scope='SCOPE').reason=='HISTORICAL_STALE'
    # divergent live registration conflict dominates green warrants
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); x=cap('A',effect=True,handler=lambda **_:None); x.operational_scope_id='ALT'; m.register_capability(x); m2=Microseed(state); r=m2.historical_reentry_projection().record('CAP:A')
        w=ReentryWarrant('CAP:A',None,True,'P',True,'X',('SCOPE',),())
        checks['HISTORICAL_CONFLICT__DOMINATES_GREEN_EXTERNAL_PLANES']=m2.assess_historical_reentry(w,requested_scope='SCOPE').reason=='HISTORICAL_CONFLICT'
    # TOCTOU: ready is not admission. Existing register path rechecks current dependency.
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state)
        for h in ('CP:CP','COORD:R'):
            d=m.assess_historical_reentry(warrant(m,h),requested_scope='SCOPE'); assert d.status=='READY_FOR_EXISTING_REGISTRATION_PATH'; register_handle(m,h)
        d=m.assess_historical_reentry(warrant(m,'CAP:C'),requested_scope='SCOPE'); assert d.status=='READY_FOR_EXISTING_REGISTRATION_PATH'
        m.change_operational_coordination('R',reason='HOSTILE_TOCTOU')
        try:
            register_handle(m,'CAP:C'); blocked=False
        except ValueError:
            blocked=True
        checks['READY_TO_REGISTRATION_TOCTOU__EXISTING_ADMISSION_RECHECK_BLOCKS']=blocked and 'C' not in m.capabilities.contracts
    # selective reality-bound closure
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); _,proposal=seed(state); m=Microseed(state); m.register_operational_frame(frame());m.register_value_variable(value());m.observe_value_state('V',0.0)
        order,ds=reenter_all(m,stale={'COORD:R'})
        checks['STALE_COORDINATION__DOES_NOT_GLOBAL_RESET']=current(m,'CAP:A') and current(m,'CAP:B') and not current(m,'CAP:C') and not current(m,'TOPO:T')
        checks['STALE_COORDINATION__INDEPENDENT_EFFECT_CAPABILITY_STILL_EXECUTES']=m.capabilities.invoke('B',obligation())['status']=='CAPABILITY_RESULT'
        checks['STALE_COORDINATION__OLD_REHEARSAL_NOT_CURRENT']=m.counterfactual_rehearsal_status(proposal.proposal_id)['status']=='UNKNOWN_INCOMPLETE'
    # no hidden persistence/subsystem surfaces
    with tempfile.TemporaryDirectory() as td:
        m=Microseed(Path(td))
        forbidden=('reentry_registry','reentry_manager','auto_reenter','restore_operational_state','persist_reentry_ready','self_qualify_reentry')
        checks['NO_PARALLEL_REENTRY_SUBSYSTEM']=all(not hasattr(m,x) for x in forbidden)
    # ready result itself is not durable across restart; only history persists
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); d=m.assess_historical_reentry(warrant(m,'CAP:A'),requested_scope='SCOPE'); assert d.status=='READY_FOR_EXISTING_REGISTRATION_PATH'
        m2=Microseed(state)
        checks['READY_NOT_PERSISTED_ACROSS_RESTART']=all('REENTRY_READY' not in e.get('kind','') for e in m2.store.events()) and 'A' not in m2.capabilities.contracts
    # scope cannot be promoted by all other green planes
    with tempfile.TemporaryDirectory() as td:
        state=Path(td); seed(state); m=Microseed(state); w=warrant(m,'CAP:A',scope=('S1',)); d=m.assess_historical_reentry(w,requested_scope='S2')
        checks['CHALLENGE_SCOPE__NO_GLOBAL_PROMOTION']=d.reason=='OUTSIDE_DIAGNOSTIC_SCOPE'
    details['check_count']=len(checks)
    out={'schema':'microseed.ms1503-1527.integration.hostile.v1','checks':checks,'all_pass':all(checks.values()),'details':details,
         'disposition':'HOSTILE_REENTRY_SURFACE_GREEN__NO_AUTHORITY_LAUNDERING_OR_TOY_AUTO_RESTORE'}
    print(json.dumps(out,indent=2,sort_keys=True))
    if not out['all_pass']: raise SystemExit(1)
if __name__=='__main__': main()
