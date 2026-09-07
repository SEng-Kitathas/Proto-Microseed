from microseed.development.evidence_relation import (
    OpaqueEvidenceAssociationRecord, OpaqueEvidenceAssociationState,
)
from scratch.ms2014_endogenous_referent_opportunity_enumeration import _base_fixture
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob


def _close(m, td):
    m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def _targets(m):
    op=m._current_owned_referent_epistemic_opportunities(act_ob())[0]
    live=m.derive_current_partial_operational_referent_ambiguity(op['binding_id'])
    sets=[]
    for bucket in live['surviving_bucket_ids']:
        r=m.reconstruct_operational_referent_class_set_for_bucket(bucket)
        assert r['status']=='OPERATIONAL_REFERENT_CLASS_SET_RECONSTRUCTED',r
        sets.append(set(r['operational_signature_classes']))
    shared=set.intersection(*sets)
    split=set.union(*sets)-shared
    assert shared and split
    return op, sorted(split)[0], sorted(shared)[0]


def _register(m, target, *, replay=True, scope='NATIVE_TOKEN_REFERENT', record_id='ASSOC-ACTIVE-ACQ'):
    source=next(row for row in m.evidence.list() if not row.get('negative'))
    rec=OpaqueEvidenceAssociationRecord(
        record_id=record_id,
        left_opaque_id='OPAQUE-TOKEN-ACTIVE-ACQ',
        right_digest_sha256=target,
        source_evidence_refs=((str(source['evidence_id']),str(source['sha256'])),),
        assistance_ancestry=(f'QUALIFICATION_SCOPE:{scope}','TEST_REPLAY_PRESSURE_ONLY'),
    )
    m.opaque_evidence_associations.register(rec,replay=replay)
    return rec


def test_revalidation_required_native_referent_association_binds_unique_existing_information_bearing_probe_read_only():
    td,m,*_=_base_fixture()
    try:
        op,target,_shared=_targets(m)
        rec=_register(m,target,replay=True)
        before=(len(m.epistemic_deficits.records),len(m.action_closure.intents),len(m.action_closure.executions),m.evidence.count())
        r=m.derive_current_native_referent_association_revalidation_opportunity_surface(rec.record_id,act_ob())
        after=(len(m.epistemic_deficits.records),len(m.action_closure.intents),len(m.action_closure.executions),m.evidence.count())
        assert r['status']=='CURRENT_UNIQUE_NATIVE_REFERENT_ASSOCIATION_REVALIDATION_OPPORTUNITY',r
        assert r['selected_probe_action_id']=='P2'
        assert r['selected_opportunity_content_signature_sha256']==op['content_signature_sha256']
        assert r['expected_right_digest_sha256']==target
        assert r['association_pressure']=='FRESH_CURRENTNESS_EVIDENCE_REQUIRED'
        assert r['currentness_evidence_owner']=='OWNED_AFFORDANCE_EFFECT_PROFILE_WITNESS'
        assert r['selection_authority']=='CONTENT_UNIQUENESS_ONLY'
        assert r['execution_authority']==r['effect_authority']=='NONE'
        assert r['remaining_token_presentation']=='EXOGENOUS'
        assert before==after
    finally:_close(m,td)


def test_shared_or_absent_target_digest_does_not_launder_generic_information_value_into_association_relevance():
    for mode in ('shared','absent'):
        td,m,*_=_base_fixture()
        try:
            _op,split,shared=_targets(m)
            target=shared if mode=='shared' else 'f'*64
            rec=_register(m,target,replay=True,record_id=f'ASSOC-{mode}')
            r=m.derive_current_native_referent_association_revalidation_opportunity_surface(rec.record_id,act_ob())
            assert r['status']=='NO_CURRENT_INFORMATION_BEARING_ASSOCIATION_REVALIDATION_OPPORTUNITY',r
            assert r['opportunity_count']==0 and r['probe_action_ids']==()
            assert r['selection_authority']==r['execution_authority']==r['effect_authority']=='NONE'
        finally:_close(m,td)


def test_current_association_has_no_revalidation_pressure_even_if_informative_probe_exists():
    td,m,*_=_base_fixture()
    try:
        _op,target,_shared=_targets(m)
        rec=_register(m,target,replay=False)
        r=m.derive_current_native_referent_association_revalidation_opportunity_surface(rec.record_id,act_ob())
        assert r['status']=='NO_CURRENT_ASSOCIATION_REVALIDATION_PRESSURE',r
        assert r['reason']=='ASSOCIATION_ALREADY_CURRENT'
        assert r['selection_authority']==r['execution_authority']=='NONE'
    finally:_close(m,td)


def test_relation_scope_is_not_silently_promoted_into_referent_acquisition_path():
    td,m,*_=_base_fixture()
    try:
        _op,target,_shared=_targets(m)
        rec=_register(m,target,replay=True,scope='NATIVE_TOKEN_RELATION')
        r=m.derive_current_native_referent_association_revalidation_opportunity_surface(rec.record_id,act_ob())
        assert r['status']=='DEFER_UNKNOWN' and r['reason']=='NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED',r
        assert r['execution_authority']==r['effect_authority']=='NONE'
    finally:_close(m,td)


def test_probe_capability_drift_erases_revalidation_opportunity_instead_of_minting_authority_from_need():
    td,m,*_=_base_fixture()
    try:
        _op,target,_shared=_targets(m)
        rec=_register(m,target,replay=True)
        before=m.derive_current_native_referent_association_revalidation_opportunity_surface(rec.record_id,act_ob())
        assert before['status']=='CURRENT_UNIQUE_NATIVE_REFERENT_ASSOCIATION_REVALIDATION_OPPORTUNITY',before
        m.change_capability_dependency('P2',reason='ACTIVE_ACQ_P2_DRIFT')
        after=m.derive_current_native_referent_association_revalidation_opportunity_surface(rec.record_id,act_ob())
        assert after['status']=='NO_CURRENT_INFORMATION_BEARING_ASSOCIATION_REVALIDATION_OPPORTUNITY',after
        assert after['selection_authority']==after['execution_authority']==after['effect_authority']=='NONE'
    finally:_close(m,td)


def test_stale_association_cannot_be_reactivated_by_acquisition_pressure():
    td,m,*_=_base_fixture()
    try:
        _op,target,_shared=_targets(m)
        rec=_register(m,target,replay=True)
        rec.state=OpaqueEvidenceAssociationState.STALE
        rec.stale_reason='HOSTILE_DRIFT'
        r=m.derive_current_native_referent_association_revalidation_opportunity_surface(rec.record_id,act_ob())
        assert r['status']=='DEFER_UNKNOWN' and r['reason']=='STALE_ASSOCIATION_CANNOT_BE_REVALIDATED',r
        assert r['selection_authority']==r['execution_authority']=='NONE'
    finally:_close(m,td)
