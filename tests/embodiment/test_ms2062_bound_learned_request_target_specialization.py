from pathlib import Path
import random, tempfile

import pytest

from microseed import (
    Microseed, Authority, EpistemicStatus, QualificationState, FeasibilityState,
    CapabilityContract, OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract,
    ProjectionSample, ProjectionDiscoveryConfig, ExternalProjectionQualifier,
    RecruitmentOption, RehearsalTransitionObservation, QueryObligation, Observation,
)


def new_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms2062-bound-learned-target-')
    return td,Microseed(Path(td.name))


def setup_projection(ms):
    ms.register_operational_frame(OperationalFrameContract(
        'F','opaque-target-discovery','f'*64,Authority.DERIVED_READ_ONLY,('MS2062-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    rng=random.Random(2062); rows=[]
    for i in range(900):
        x=str(rng.randint(0,1)); nuisance=str(rng.randint(0,5)); action='A' if rng.random()<.5 else 'B'
        # Two predictive equivalence classes, learned only as opaque buckets.
        effect=('E1' if action=='A' else 'E0') if x=='1' else ('E0' if action=='A' else 'E1')
        rows.append(ProjectionSample(f'P-{i}',(nuisance,x),action,effect,f'S-{i%3}','F',0))
    found=ms.discover_epistemic_projection_candidates(
        rows[:600],rows[600:],ProjectionDiscoveryConfig(
            max_subset=1,min_train_support=100,min_key_action_support=8,
            min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.90,
        )
    )
    assert found
    cid=found[0]['candidate_id']; c=ms.epistemic_projection_candidates[cid]
    assert c.input_positions==(1,)
    ev=ms.append_evidence('Q-P',{'independent_heldout':True},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL')
    ticket=ExternalProjectionQualifier(ms.evidence,qualifier_id='HSP-MS2062').qualify(c,qualification_evidence=(ev,))
    rec=ms.admit_epistemic_projection_candidate(ticket,projection_id='TARGET-P')
    buckets=tuple(sorted({b for _,b in c.key_to_bucket}))
    assert len(buckets)==2
    return rec,c,buckets


def setup_request_channel(ms,receipts):
    def handler(*,target):
        receipts.append(str(target)); return {'requested_target':str(target)}
    base=CapabilityContract(
        'REQ-BASE','opaque request channel',
        boundary={
            'request_target_binding_mode':'OPAQUE_PROJECTION_BUCKET_SPECIALIZABLE',
            'local_means_owned_by_parent':False,
        },
        interface={'target':'opaque','output':'request-receipt'},
        invariants=('REQUEST_CHANNEL_EFFECT_NE_LOCAL_MEANS_AUTHORITY',),hazards=('SUBORDINATE_MAY_REFUSE',),
        authority=Authority.EFFECT,lineage=('MS2062-RESEARCH',),currentness='CURRENT',resources={},
        query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=handler,operational_scope_id='REQUEST-SCOPE',
    )
    ms.register_capability(base)
    return base


def setup_action(ms):
    ms.register_value_variable(ValueVariableContract(
        'V','opaque-regulatory',1.0,10.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS2062-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
    ))
    ms.observe_value_state('V',0.0)
    ms.register_episode_schema(EpisodeSchemaContract(
        'E','opaque','e'*64,Authority.DERIVED_READ_ONLY,('MS2062-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),
    ))


def obl(): return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='REQUEST-SCOPE')


def intent_for(ms,cid,state):
    ms.observe_value_state('V',0.0)
    ms.observe_opaque_control_state(Observation(f'CS-{state}-{cid}','EXT','opaque-control',state,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-CS-{state}-{cid}')
    rows=tuple(RehearsalTransitionObservation(f'R-{state}-{cid}-{i}',state,cid,'WRONG',1.0,0,'F',0,'E',0) for i in range(8))
    p=ms.nominate_counterfactual_rehearsal(rows,(RecruitmentOption(cid,FeasibilityState.FEASIBLE),),start_state_id=state,value_id='V')
    assert p is not None
    out=ms.nominate_bounded_action_intent(p.proposal_id,obl()); assert out['status']=='ACTION_INTENT_NOMINATED'
    return out['intent']


def test_two_learned_projection_buckets_create_two_content_distinct_fixed_target_request_capabilities():
    td,ms=new_ms(); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms); base=setup_request_channel(ms,receipts)
        a=ms.derive_bound_request_specialization(base.capability_id,rec.projection_id,buckets[0])
        b=ms.derive_bound_request_specialization(base.capability_id,rec.projection_id,buckets[1])
        assert a.capability_id!=b.capability_id
        assert a.computed_signature_sha256()!=b.computed_signature_sha256()
        assert a.authority==b.authority==base.authority==Authority.EFFECT
        assert a.query_obligation_id==b.query_obligation_id==base.query_obligation_id
        assert a.operational_scope_id==b.operational_scope_id==base.operational_scope_id
        assert a.boundary['target_token']==buckets[0] and b.boundary['target_token']==buckets[1]
        assert 'AUTHORITY_INHERITED_NOT_INCREASED' in a.invariants
        assert a.boundary['local_means_owned_by_specialization'] is False
    finally: td.cleanup()


def test_specialization_rejects_arbitrary_target_and_supplied_projection():
    td,ms=new_ms(); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms); base=setup_request_channel(ms,receipts)
        with pytest.raises(ValueError,match='TARGET_NOT_IN_QUALIFIED_PROJECTION_VOCABULARY'):
            ms.derive_bound_request_specialization(base.capability_id,rec.projection_id,'CALLER-INVENTED')
        supplied=ms.register_epistemic_projection('SUPPLIED-P','a'*64,assistance_ancestry=('EXTERNAL',))
        with pytest.raises(ValueError,match='REQUIRES_ENDOGENOUS_EXTERNALLY_QUALIFIED_PROJECTION'):
            ms.derive_bound_request_specialization(base.capability_id,supplied.projection_id,buckets[0])
    finally: td.cleanup()


def test_bound_target_cannot_be_overridden_at_runtime_and_handler_receives_only_bound_token():
    td,ms=new_ms(); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms); base=setup_request_channel(ms,receipts)
        bound=ms.derive_bound_request_specialization(base.capability_id,rec.projection_id,buckets[0])
        value=ms.capabilities.invoke(bound.capability_id,obl())
        assert value['status']=='CAPABILITY_RESULT'
        assert value['value']['requested_target']==buckets[0] and receipts==[buckets[0]]
        with pytest.raises(ValueError,match='RUNTIME_ARGUMENT_OVERRIDE_FORBIDDEN'):
            ms.capabilities.invoke(bound.capability_id,obl(),target=buckets[1])
        assert receipts==[buckets[0]]
    finally: td.cleanup()


def test_bound_target_is_part_of_action_identity_before_intent_and_does_not_collapse_learning_slot():
    td,ms=new_ms(); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms); setup_request_channel(ms,receipts); setup_action(ms)
        a=ms.derive_bound_request_specialization('REQ-BASE',rec.projection_id,buckets[0])
        b=ms.derive_bound_request_specialization('REQ-BASE',rec.projection_id,buckets[1])
        ia=intent_for(ms,a.capability_id,'H')
        # Need a fresh state witness ID for the second intent but identical opaque state.
        ms.observe_opaque_control_state(Observation('CS-H-B','EXT','opaque-control','H',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-H-B')
        rows=tuple(RehearsalTransitionObservation(f'RB-{i}','H',b.capability_id,'WRONG',1.0,0,'F',0,'E',0) for i in range(8))
        p=ms.nominate_counterfactual_rehearsal(rows,(RecruitmentOption(b.capability_id,FeasibilityState.FEASIBLE),),start_state_id='H',value_id='V'); assert p is not None
        ib=ms.nominate_bounded_action_intent(p.proposal_id,obl())['intent']
        assert ia['capability_id']==a.capability_id and ib['capability_id']==b.capability_id
        assert a.computed_signature_sha256()!=b.computed_signature_sha256()
        assert ia['capability_epoch']==ib['capability_epoch']==0
        assert ia['intent_id']!=ib['intent_id']
    finally: td.cleanup()


def test_projection_change_stales_bound_specialization_without_staling_base_request_channel():
    td,ms=new_ms(); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms); setup_request_channel(ms,receipts)
        bound=ms.derive_bound_request_specialization('REQ-BASE',rec.projection_id,buckets[0])
        assert ms.capabilities.is_current(bound.capability_id) and ms.capabilities.is_current('REQ-BASE')
        out=ms.change_epistemic_projection(rec.projection_id,new_signature_sha256='b'*64,reason='TARGET_REPRESENTATION_DRIFT')
        assert bound.capability_id in out['stale_capability_ids']
        assert not ms.capabilities.is_current(bound.capability_id)
        assert ms.capabilities.is_current('REQ-BASE')
    finally: td.cleanup()


def test_base_request_channel_drift_stales_bound_specialization_transitively():
    td,ms=new_ms(); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms); setup_request_channel(ms,receipts)
        bound=ms.derive_bound_request_specialization('REQ-BASE',rec.projection_id,buckets[0])
        stale=ms.change_capability_dependency('REQ-BASE',reason='REQUEST_CHANNEL_CHANGED')
        assert 'REQ-BASE' in stale and bound.capability_id in stale
        assert not ms.capabilities.is_current(bound.capability_id)
    finally: td.cleanup()


def test_ordinary_non_specializable_effect_capability_cannot_be_recast_as_bound_request_channel():
    td,ms=new_ms(); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms)
        ms.register_capability(CapabilityContract(
            'MOTOR','ordinary effect',{}, {},(),(),Authority.EFFECT,('MS2062-RESEARCH',),'CURRENT',{},
            query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {'ok':True},operational_scope_id='REQUEST-SCOPE',
        ))
        with pytest.raises(ValueError,match='BASE_INTERFACE_NOT_SPECIALIZABLE'):
            ms.derive_bound_request_specialization('MOTOR',rec.projection_id,buckets[0])
    finally: td.cleanup()


def test_restart_requires_explicit_base_channel_reregistration_but_rederives_same_specialization_identity_and_dependency():
    td,ms=new_ms(); root=Path(td.name); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms); setup_request_channel(ms,receipts)
        first=ms.derive_bound_request_specialization('REQ-BASE',rec.projection_id,buckets[0])
        first_id=first.capability_id; first_sig=first.computed_signature_sha256()
        # Restart does not resurrect executable contracts/handlers.
        ms2=Microseed(root)
        assert 'REQ-BASE' not in ms2.capabilities.contracts
        assert first_id not in ms2.capabilities.contracts
        assert rec.projection_id in ms2.epistemic_projections.records
        # Explicitly restore the operational request channel, then re-derive from persisted learned representation.
        receipts2=[]; setup_request_channel(ms2,receipts2)
        second=ms2.derive_bound_request_specialization('REQ-BASE',rec.projection_id,buckets[0])
        assert second.capability_id==first_id
        assert second.computed_signature_sha256()==first_sig
        assert first_id in ms2.epistemic_projections.capability_dependents[rec.projection_id]
        assert ms2.capabilities.is_current(first_id)
    finally: td.cleanup()


def test_restart_does_not_allow_rederivation_from_projection_that_was_staled_before_shutdown():
    td,ms=new_ms(); root=Path(td.name); receipts=[]
    try:
        rec,c,buckets=setup_projection(ms); setup_request_channel(ms,receipts)
        bound=ms.derive_bound_request_specialization('REQ-BASE',rec.projection_id,buckets[0])
        ms.change_epistemic_projection(rec.projection_id,new_signature_sha256='c'*64,reason='TARGET_DRIFT_BEFORE_RESTART')
        assert not ms.capabilities.is_current(bound.capability_id)
        ms2=Microseed(root)
        receipts2=[]; setup_request_channel(ms2,receipts2)
        with pytest.raises(ValueError,match='PROJECTION_VERSION_REQUIRES_FRESH_EXTERNAL_REQUALIFICATION'):
            ms2.derive_bound_request_specialization('REQ-BASE',rec.projection_id,buckets[0])
    finally: td.cleanup()
