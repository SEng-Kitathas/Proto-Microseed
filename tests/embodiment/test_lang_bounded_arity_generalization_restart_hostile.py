from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Authority,Microseed,Observation
from scratch.lang_arity_four_grounded_referents_fixture import (
    OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,
    seed_four_current_native_referent_associations,_close,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def test_restart_requires_fresh_operand_window_and_live_leaf_revalidation_before_arity4_reappears():
    td=TemporaryDirectory(prefix='prod-arity4-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'ARITY4-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens)
        records=seeded['records'];profiles=seeded['profiles']
        _obs(m1,tokens,'ARITY4-R1-WINDOW',15000)
        first=m1.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert first['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',first
        assert first['derived_arity']==4
        digest=str(first['composition_content_digest_sha256'])
    finally:
        _close(m1)

    m2=Microseed(root)
    try:
        nofresh=m2.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert nofresh['status']=='DEFER_UNKNOWN' and nofresh['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM',nofresh
        assert nofresh['derived_arity']==0
        attach_four_runtime_surface(m2,world,'ARITY4-R2')
        profiles2=fresh_four_owned_profiles(m2,world,tag='R2-FRESH',serial_base=16000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            current=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles2[key]['evidence_id']))
            assert current['status']=='CURRENTNESS_CONFIRMED',current
        _obs(m2,tokens,'ARITY4-R2-WINDOW',17000)
        second=m2.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert second['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',second
        assert second['derived_arity']==4 and second['composition_content_digest_sha256']==digest
        # Composition output evidence is grouping-neutral; repeated derivation is idempotent.
        repeated=m2.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert repeated['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',repeated
        assert repeated['composition_content_digest_sha256']==second['composition_content_digest_sha256']
        assert repeated['composition_record_status']=='COMPOSITION_EVIDENCE_ALREADY_PRESENT'
        # A new experiment begins only after an actual operational boundary.
        reset=m2.observe_opaque_control_state(
            Observation('CAP-ARITY4-R2-FRAME-DRIFT','EXTERNAL','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-ARITY4-R2-FRAME-DRIFT-WINDOW',
        )
        assert reset['status']=='CURRENT_OPAQUE_CONTROL_STATE',reset
        _obs(m2,tokens,'ARITY4-R2-FRAME-DRIFT',17100)
        m2.change_operational_frame('F',reason='ARITY4-R2-FRAME-DRIFT')
        stale=m2.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert stale['status']=='DEFER_UNKNOWN' and stale['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED',stale
    finally:
        _close(m2);td.cleanup()


def test_bounded_owner_refuses_truncated_evidence_scan_budget_before_reading_partial_window():
    td=TemporaryDirectory(prefix='prod-arity-budget-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'ARITY-BUDGET')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        _obs(m,('R4','T9','W3','K7'),'ARITY-BUDGET-WINDOW',18000)
        total=m.evidence.count()
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=total-1)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED',out
        assert out['reason']=='BOUNDED_COMPOSITION_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET'
        assert out['total_records']==total and out['max_records']==total-1
    finally:
        _close(m);td.cleanup()
