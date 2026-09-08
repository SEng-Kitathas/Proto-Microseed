from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import (
    OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,
    seed_four_current_native_referent_associations,_close,_observe_s0,
)
from scratch.lang_c08c_native_owned_affordance_relation import ACT,_proposal
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_operand_window_store_aware_prototype import derive_store_aware_bounded_composition_prototype,derive_store_aware_operand_window


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _bare_exec(m,cid,serial):
    p=_proposal(m,cid,serial);n=m.nominate_bounded_action_intent(p.proposal_id,ACT);assert n['status']=='ACTION_INTENT_NOMINATED',n
    x=m.execute_bounded_action(n['intent']['intent_id'],ACT);assert x['status']=='ACTION_EXECUTED',x
    return x


def test_preboot_action_boundary_has_no_current_window_authority_and_fresh_postboot_action_boundary_reappears():
    td=TemporaryDirectory(prefix='boundary-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'BOUNDARY-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens)
        records=seeded['records']
        _observe_s0(m1,'BOUNDARY-R1-RESET')
        _obs(m1,('R4','T9'),'BOUNDARY-R1-PRE',23000)
        _bare_exec(m1,'QA',230)
        _obs(m1,('W3','K7'),'BOUNDARY-R1-POST',23100)
        first=derive_store_aware_bounded_composition_prototype(m1)
        assert first['status']=='CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE' and first['derived_arity']==2,first
    finally:_close(m1)

    m2=Microseed(root)
    try:
        # All prior execution/token chronology is pre-boot and has no current window authority.
        stale=derive_store_aware_operand_window(m2)
        assert stale['status']=='DEFER_UNKNOWN' and stale['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM' and stale['derived_arity']==0,stale
        attach_four_runtime_surface(m2,world,'BOUNDARY-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='BOUNDARY-R2-FRESH',serial_base=24000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            current=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id']))
            assert current['status']=='CURRENTNESS_CONFIRMED',current
        _observe_s0(m2,'BOUNDARY-R2-RESET')
        _obs(m2,('R4','T9'),'BOUNDARY-R2-PRE',25000)
        x=_bare_exec(m2,'QB',250)
        _obs(m2,('W3','K7'),'BOUNDARY-R2-POST',25100)
        second=derive_store_aware_bounded_composition_prototype(m2)
        assert second['status']=='CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE' and second['derived_arity']==2,second
        assert second['last_boundary']['kind']=='BOUNDED_ACTION_EXECUTED'
        assert second['last_boundary']['execution_id']==x['execution']['execution_id']
    finally:_close(m2);td.cleanup()


def test_event_scan_budget_refuses_partial_current_runtime_chronology():
    td=TemporaryDirectory(prefix='boundary-budget-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-BUDGET')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        _observe_s0(m,'BOUNDARY-BUDGET-RESET')
        _obs(m,('R4','T9'),'BOUNDARY-BUDGET-PRE',26000)
        _bare_exec(m,'QA',260)
        _obs(m,('W3','K7'),'BOUNDARY-BUDGET-POST',26100)
        boot=m._current_runtime_boot_seq();current=[row for row in m.store.events() if int(row.get('seq',-1))>boot]
        assert len(current)>1
        out=derive_store_aware_operand_window(m,max_events=len(current)-1)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED',out
        assert out['reason']=='OPERAND_WINDOW_EVENT_HISTORY_EXCEEDS_SCAN_BUDGET'
        assert out['current_event_count']==len(current) and out['max_events']==len(current)-1
    finally:_close(m);td.cleanup()
