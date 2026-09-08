from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import (
    OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,
    seed_four_current_native_referent_associations,_close,_observe_s0,
)
from scratch.lang_c08c_native_owned_affordance_relation import ACT,_proposal
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _bare_exec(m,cid,serial):
    p=_proposal(m,cid,serial);n=m.nominate_bounded_action_intent(p.proposal_id,ACT);assert n['status']=='ACTION_INTENT_NOMINATED',n
    x=m.execute_bounded_action(n['intent']['intent_id'],ACT);assert x['status']=='ACTION_EXECUTED',x
    return x


def test_production_action_boundary_is_current_boot_scoped_across_restart():
    td=TemporaryDirectory(prefix='prod-boundary-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'PROD-BOUNDARY-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens);records=seeded['records']
        _observe_s0(m1,'PROD-BOUNDARY-R1-RESET')
        _obs(m1,('R4','T9'),'PROD-BOUNDARY-R1-PRE',36000)
        _bare_exec(m1,'QA',360)
        _obs(m1,('W3','K7'),'PROD-BOUNDARY-R1-POST',36100)
        first=m1.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert first['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED' and first['derived_arity']==2,first
        digest=str(first['composition_content_digest_sha256'])
    finally:_close(m1)
    m2=Microseed(root)
    try:
        old=m2.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM' and old['derived_arity']==0,old
        attach_four_runtime_surface(m2,world,'PROD-BOUNDARY-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='PROD-BOUNDARY-R2-FRESH',serial_base=37000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id']))
            assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _observe_s0(m2,'PROD-BOUNDARY-R2-RESET')
        _obs(m2,('R4','T9'),'PROD-BOUNDARY-R2-PRE',38000)
        x=_bare_exec(m2,'QB',380)
        _obs(m2,('W3','K7'),'PROD-BOUNDARY-R2-POST',38100)
        second=m2.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert second['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED' and second['derived_arity']==2,second
        assert second['composition_content_digest_sha256']==digest
        assert second['last_window_boundary']['execution_id']==x['execution']['execution_id']
    finally:_close(m2);td.cleanup()


def test_production_event_budget_refuses_partial_store_scan():
    td=TemporaryDirectory(prefix='prod-boundary-budget-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'PROD-BOUNDARY-BUDGET')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        _observe_s0(m,'PROD-BOUNDARY-BUDGET-RESET')
        _obs(m,('R4','T9'),'PROD-BOUNDARY-BUDGET-PRE',39000)
        _bare_exec(m,'QA',390)
        _obs(m,('W3','K7'),'PROD-BOUNDARY-BUDGET-POST',39100)
        boot=m._current_runtime_boot_seq();current=[row for row in m.store.events() if int(row.get('seq',-1))>boot]
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=len(current)-1)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED',out
        assert out['reason']=='OPERAND_WINDOW_EVENT_HISTORY_EXCEEDS_SCAN_BUDGET'
    finally:_close(m);td.cleanup()
