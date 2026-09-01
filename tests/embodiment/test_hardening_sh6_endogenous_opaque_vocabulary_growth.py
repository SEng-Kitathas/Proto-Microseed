
from __future__ import annotations

from microseed import Authority, CapabilityContract, EpistemicStatus, ExternalProjectionQualifier, ProjectionDiscoveryConfig, QualificationState
from scratch.ms1985_two_learned_bucket_composition_boundary import QUADS
from scratch.ms1986_owned_learned_bucket_composition import external_holdout
from tests.embodiment.test_ms1986_owned_learned_bucket_composition import _prepare_owned_sources
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _discover_second_stage(m,pa,pb):
    composed=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=2)
    assert composed['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES'
    samples=tuple(composed['samples'])
    cfg=ProjectionDiscoveryConfig(
        max_subset=2,min_train_support=32,min_key_action_support=3,
        min_validation_accuracy=.95,min_lift_over_action_baseline=.35,
        min_scope_accuracy=.95,max_candidates=8,
    )
    found=m.discover_epistemic_projection_candidates(samples[:48],samples[48:],cfg)
    candidates=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
    exact=[c for c in candidates if c.input_positions==(0,1) and c.digest() not in {pa.digest(),pb.digest()}]
    assert exact
    return composed,exact[-1]


def _qualify_second_stage(m,c,pa,pb):
    holdout=external_holdout(c,pa,pb)
    qe=m.append_evidence(
        'Q-SH6-SECOND',{'kind':'SH6_OWNED_BUCKET_COMPOSITION_HOLDOUT','candidate_sha256':c.digest(),'rows':holdout},
        EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-SH6-SECOND',
    )
    ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-SH6-SECOND').qualify(c,qualification_evidence=(qe,))
    return m.admit_epistemic_projection_candidate(ticket,projection_id='P-SH6-NOVEL')


def _register_request_base(m,calls):
    m.register_capability(CapabilityContract(
        'REQ-SH6','opaque request channel for discovered vocabulary',
        boundary={'request_target_binding_mode':'OPAQUE_PROJECTION_BUCKET_SPECIALIZABLE','local_means_owned_by_parent':False},
        interface={'target':'opaque','output':'request-receipt'},
        invariants=('REQUEST_CHANNEL_EFFECT_NE_SEMANTIC_DESIRED_STATE_AUTHORITY',),
        hazards=('DISCOVERED_BUCKET_REQUIRES_CURRENT_QUALIFIED_PROJECTION',),
        authority=Authority.EFFECT,lineage=('MS_SUBSTRATE_HARDENING_V1:SH6',),currentness='CURRENT',resources={},
        query_obligation_id='Q-SH6',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda *,target: calls.append(str(target)) or {'target':str(target)},operational_scope_id='S',
    ))


def test_existing_representation_growth_derives_new_opaque_bucket_vocabulary_candidate_without_caller_supplied_partition():
    td,world,m,pa,pb=_prepare_owned_sources('hardening-sh6-candidate-')
    try:
        composed,c=_discover_second_stage(m,pa,pb)
        assert composed['source_projection_ids']==('P-MS1986-A','P-MS1986-B')
        assert c.input_positions==(0,1)
        assert c.validation_accuracy==1.0
        assert c.lift>=.49
        buckets=tuple(sorted({b for _,b in c.key_to_bucket}))
        assert len(buckets)==2
        # The caller supplied source-count/search bounds, not the learned answer partition.
        assert all(b.startswith('bucket-') for b in buckets)
        assert c.candidate_id.startswith('proj-cand-')
        assert c.source_projection_epochs
        assert [x[0] for x in c.dependency_projection_epochs]==['P-MS1986-A','P-MS1986-B']
        # Candidate exists but has not been admitted/current as vocabulary yet.
        assert 'P-SH6-NOVEL' not in m.epistemic_projections.records
        assert c.assistance_ancestry
        assert not hasattr(c,'semantic_desired_state_authority')
    finally:
        _close(m);world.close();td.cleanup()


def test_externally_qualified_new_opaque_representation_can_supply_bound_request_atoms_without_semantic_or_execution_gain():
    td,world,m,pa,pb=_prepare_owned_sources('hardening-sh6-bind-');calls=[]
    try:
        _,c=_discover_second_stage(m,pa,pb)
        buckets=tuple(sorted({b for _,b in c.key_to_bucket}))
        rec=_qualify_second_stage(m,c,pa,pb)
        assert rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'
        assert rec.proposal_candidate_sha256==c.digest()
        assert rec.semantic_projection_authority=='NONE'
        assert rec.discovery_authority=='NONE'
        _register_request_base(m,calls)
        before_intents=len(m.action_closure.intents); before_exec=len(m.action_closure.executions)
        bound=tuple(m.derive_bound_request_specialization('REQ-SH6',rec.projection_id,b) for b in buckets)
        assert len({x.capability_id for x in bound})==2
        assert all(x.authority==Authority.EFFECT for x in bound)
        assert all(x.qualification==QualificationState.SHADOW_QUALIFIED for x in bound)
        # Specialization itself neither invokes the base handler nor creates intent/execution.
        assert calls==[]
        assert len(m.action_closure.intents)==before_intents
        assert len(m.action_closure.executions)==before_exec
        for x,b in zip(bound,buckets):
            assert x.boundary['target_token']==b
            assert x.boundary['target_projection_id']==rec.projection_id
            assert 'REQUEST_CHANNEL_EFFECT_NE_SEMANTIC_DESIRED_STATE_AUTHORITY' in x.invariants
            assert 'NO_SEMANTIC_DESIRED_STATE_AUTHORITY' in x.assistance_ancestry
        # The generated vocabulary remains exact-currentness-bound to the representation lineage.
        m.change_epistemic_projection('P-MS1986-A',new_signature_sha256='a'*64,reason='SH6-SOURCE-PROJECTION-DRIFT')
        assert not m.epistemic_projections.records[rec.projection_id].current
        assert all(not m.capabilities.is_current(x.capability_id) for x in bound)
        assert calls==[]
    finally:
        _close(m);world.close();td.cleanup()


def test_recursive_opaque_representation_growth_remains_bounded_and_presemantic():
    from scratch.ms1987_depth3_recursive_bucket_composition import run_ms1987
    from scratch.ms1988_depth4_recursive_bucket_genericity import run_ms1988
    r3=run_ms1987();r4=run_ms1988()
    assert r3['status']==r4['status']=='PASS'
    assert r3['new_projection_search_mechanism_added']=='NO'
    assert r3['new_representation_manager_added']=='NO'
    assert r4['core_mechanism_change']=='NO'
    assert r4['new_projection_search_mechanism']=='NO'
    assert r4['new_representation_manager']=='NO'
    assert r3['semantic_recursion_authority']==r3['semantic_symbol_authority']==r3['truth_authority']==r3['language_authority']=='NONE'
    assert r4['semantic_recursion_authority']==r4['semantic_symbol_authority']==r4['truth_authority']==r4['language_authority']=='NONE'
