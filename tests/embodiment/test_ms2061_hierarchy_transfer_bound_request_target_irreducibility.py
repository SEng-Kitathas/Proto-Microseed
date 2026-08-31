from pathlib import Path
import tempfile

import pytest

from microseed import (
    Microseed, Authority, QualificationState, FeasibilityState, EpistemicStatus,
    CapabilityContract, OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract,
    RecruitmentOption, RehearsalTransitionObservation, QueryObligation, Observation,
    CapabilityCandidate, ExternalCapabilityQualifier,
)


def new_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms2061-bound-target-')
    return td,Microseed(Path(td.name))


def setup_generic(ms, receipts):
    ms.register_operational_frame(OperationalFrameContract(
        'F','opaque-generic-request','f'*64,Authority.DERIVED_READ_ONLY,('MS2061-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    ms.register_value_variable(ValueVariableContract(
        'V','opaque-regulatory',1.0,10.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS2061-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
    ))
    ms.observe_value_state('V',0.0)
    def handler(*,target):
        receipts.append(str(target)); return {'target':str(target)}
    ms.register_capability(CapabilityContract(
        'REQ','generic opaque request channel',
        boundary={'target_parameter':'OPAQUE_RUNTIME_ARGUMENT'},
        interface={'target':'opaque'},invariants=('NO_SEMANTIC_GOAL_AUTHORITY',),hazards=('TARGET_SUBSTITUTION_IF_UNBOUND',),
        authority=Authority.EFFECT,lineage=('MS2061-RESEARCH',),currentness='CURRENT',resources={},
        query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=handler,
        operational_scope_id='REQUEST-SCOPE',
    ))
    ms.register_episode_schema(EpisodeSchemaContract(
        'E','opaque','e'*64,Authority.DERIVED_READ_ONLY,('MS2061-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),
    ))


def obl(): return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='REQUEST-SCOPE')


def nominate(ms,state='H'):
    ms.observe_value_state('V',0.0)
    ms.observe_opaque_control_state(Observation('CS-'+state,'EXT','opaque-control',state,authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-'+state)
    rows=tuple(RehearsalTransitionObservation(f'S-{state}-{i}',state,'REQ','WRONG',1.0,0,'F',0,'E',0) for i in range(8))
    proposal=ms.nominate_counterfactual_rehearsal(rows,(RecruitmentOption('REQ',FeasibilityState.FEASIBLE),),start_state_id=state,value_id='V')
    assert proposal is not None
    intent=ms.nominate_bounded_action_intent(proposal.proposal_id,obl())
    assert intent['status']=='ACTION_INTENT_NOMINATED'
    return intent['intent']


def record(ms,execution_id,next_state,effect,evidence_suffix):
    return ms.record_bounded_action_outcome(
        execution_id,
        Observation('OUT-'+evidence_suffix,'EXT',f'action-execution:{execution_id}',
                    {'next_state_id':next_state,'value_id':'V','observed_value':effect},
                    authority=Authority.OBSERVATION_ONLY),
        evidence_id='E-OUT-'+evidence_suffix,
    )


def test_bounded_action_intent_has_no_bound_execution_argument_surface():
    td,ms=new_ms(); receipts=[]
    try:
        setup_generic(ms,receipts); intent=nominate(ms)
        assert 'target' not in intent
        assert 'invocation_args' not in intent
        assert 'bound_execution_kwargs' not in intent
        assert 'invocation_payload_digest' not in intent
    finally: td.cleanup()


def test_same_nominal_intent_identity_can_be_followed_by_different_caller_targets_in_separate_replays():
    ids=[]; results=[]
    for target in ('T0','T1'):
        td,ms=new_ms(); receipts=[]
        try:
            setup_generic(ms,receipts); intent=nominate(ms)
            ids.append(intent['intent_id'])
            ex=ms.execute_bounded_action(intent['intent_id'],obl(),target=target)
            assert ex['status']=='ACTION_EXECUTED'
            results.append(ex['handler_value']['target'])
        finally: td.cleanup()
    # Target is not part of the intent identity or commitment, yet changes the effect call.
    assert ids[0]==ids[1]
    assert results==['T0','T1']


def test_parameterized_targets_collapse_into_one_action_outcome_relation_identity_and_become_ambiguous():
    td,ms=new_ms(); receipts=[]
    try:
        setup_generic(ms,receipts)
        # Repeatedly execute same REQ capability from same H, but alternate unbound target.
        # Actual effects differ by target. Since learning keys capability_id, target is lost.
        for i in range(16):
            target='T0' if i%2==0 else 'T1'
            # Need fresh control evidence/id per execution because one action intent is one-shot.
            state='H'
            ms.observe_value_state('V',0.0)
            ms.observe_opaque_control_state(Observation(f'CS-{i}','EXT','opaque-control',state,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-CS-{i}')
            rows=tuple(RehearsalTransitionObservation(f'S-{i}-{j}',state,'REQ','WRONG',1.0,0,'F',0,'E',0) for j in range(8))
            proposal=ms.nominate_counterfactual_rehearsal(rows,(RecruitmentOption('REQ',FeasibilityState.FEASIBLE),),start_state_id=state,value_id='V')
            assert proposal is not None
            intent=ms.nominate_bounded_action_intent(proposal.proposal_id,obl()); assert intent['status']=='ACTION_INTENT_NOMINATED'
            ex=ms.execute_bounded_action(intent['intent']['intent_id'],obl(),target=target); assert ex['status']=='ACTION_EXECUTED'
            out=record(ms,ex['execution']['execution_id'],'GOOD' if target=='T0' else 'BAD',2.0 if target=='T0' else -2.0,str(i))
            assert out['status']=='ACTION_OUTCOME_OBSERVED'
        # Two target-conditioned laws exist in reality, but current learner sees one capability/action slot.
        assert ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)==()
        experiences=ms._action_outcome_experiences()
        assert {x.capability_id for x in experiences}=={'REQ'}
        assert all(not hasattr(x,'invocation_payload_digest') for x in experiences)
    finally: td.cleanup()


def test_existing_capability_candidate_admission_cannot_mint_new_effect_request_variant():
    td,ms=new_ms(); receipts=[]
    try:
        setup_generic(ms,receipts)
        proposal_ev=ms.append_evidence('E-PROP',{'opaque_target':'T-LEARNED'},EpistemicStatus.PRESSURE_SUPPORTED,source='EXPERIMENT')
        qual_ev=ms.append_evidence('E-QUAL',{'independent':'support'},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL')
        candidate=CapabilityCandidate(
            candidate_id='REQ-T-LEARNED',
            proposed_contract=CapabilityContract(
                'REQ-T-LEARNED','content-bound request variant',
                boundary={'request_target_handle':'T-LEARNED'},interface={},invariants=(),hazards=(),
                authority=Authority.EFFECT,lineage=('MS2061-RESEARCH',),currentness='CANDIDATE',resources={},
                query_obligation_id='ACT',qualification=QualificationState.CANDIDATE,operational_scope_id='REQUEST-SCOPE',
            ),
            evidence=(proposal_ev,),nomination_basis='LEARNED_OPAQUE_TARGET_REUSE',
        )
        ms.nominate_capability_candidate(candidate)
        ticket=ExternalCapabilityQualifier(ms.evidence,qualifier_id='HSP-MS2061').qualify(candidate,qualification_evidence=(qual_ev,))
        # Fixed qualification bridge never admits EFFECT authority by design.
        with pytest.raises(ValueError) as exc:
            ms.admit_capability_candidate(ticket,handler=lambda: {'target':'T-LEARNED'})
        assert str(exc.value) in {'NOT_ADMISSIBLE:RESEARCH_ONLY','EFFECT_AUTHORITY_NOT_ADMISSIBLE_BY_THIS_BRIDGE'}
    finally: td.cleanup()


def test_pre_registered_one_capability_per_target_works_but_is_finite_supplied_assistance_not_endogenous_target_construction():
    td,ms=new_ms(); receipts=[]
    try:
        setup_generic(ms,receipts)
        assert set(ms.capabilities.contracts)=={'REQ'}
        assert not hasattr(ms,'bind_request_target_to_intent')
        assert not hasattr(ms,'construct_subordinate_desired_state')
        assert not hasattr(ms,'admit_effect_request_variant_from_learned_state')
    finally: td.cleanup()
