from pathlib import Path
import tempfile

from microseed import (
    Microseed, Authority, QualificationState, FeasibilityState, EpistemicStatus,
    CapabilityContract, OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract,
    RecruitmentOption, RehearsalTransitionObservation, QueryObligation, Observation,
    ExternalActionOutcomeRelationQualifier,
)


def new_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms2057-hierarchy-transfer-')
    return td,Microseed(Path(td.name))


def cap(cid):
    return CapabilityContract(
        cid,'opaque-subordinate-request',{},{},(),(),Authority.EFFECT,('MS2057-RESEARCH',),'CURRENT',{},
        query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda _cid=cid, **_: {'subordinate_receipt':_cid},operational_scope_id='SCOPE'
    )


def setup(ms):
    ms.register_operational_frame(OperationalFrameContract(
        'F','opaque-two-level-transfer','f'*64,Authority.DERIVED_READ_ONLY,('MS2057-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED
    ))
    ms.register_value_variable(ValueVariableContract(
        'V','opaque-higher-regulatory-coordinate',1.0,10.0,'v'*64,Authority.DERIVED_READ_ONLY,
        ('MS2057-RESEARCH',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')
    ))
    ms.observe_value_state('V',0.0)
    ms.register_capability(cap('U1')); ms.register_capability(cap('U2'))
    ms.register_episode_schema(EpisodeSchemaContract(
        'E','opaque-two-level-transfer-episode','e'*64,Authority.DERIVED_READ_ONLY,('MS2057-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)
    ))


def obl():
    return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='SCOPE')


def opts():
    # Experimental-B decision surface: no supplied predicted effect.
    return (
        RecruitmentOption('U1',FeasibilityState.FEASIBLE),
        RecruitmentOption('U2',FeasibilityState.FEASIBLE),
    )


def exposure_proposal(ms, *, state_id, capability_id, idx):
    # Experimental exposure scheduling only. The predicted row is deliberately
    # wrong/non-informative and is never the learned label.
    rows=tuple(
        RehearsalTransitionObservation(
            f'SCHED-{state_id}-{capability_id}-{idx}-{j}',state_id,capability_id,
            f'WRONG-{state_id}-{capability_id}',1.0,0,'F',0,'E',0
        )
        for j in range(8)
    )
    return ms.nominate_counterfactual_rehearsal(
        rows,(RecruitmentOption(capability_id,FeasibilityState.FEASIBLE),),
        start_state_id=state_id,value_id='V'
    )


def execute_observed(ms, *, state_id, capability_id, idx, next_state, observed_value):
    ms.observe_value_state('V',0.0)
    ms.observe_opaque_control_state(
        Observation(f'CS-{state_id}-{capability_id}-{idx}','EXT','opaque-control',state_id,authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-CS-{state_id}-{capability_id}-{idx}'
    )
    p=exposure_proposal(ms,state_id=state_id,capability_id=capability_id,idx=idx)
    assert p is not None
    intent=ms.nominate_bounded_action_intent(p.proposal_id,obl())
    assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],obl())
    assert ex['status']=='ACTION_EXECUTED'
    execution_id=ex['execution']['execution_id']
    out=ms.record_bounded_action_outcome(
        execution_id,
        Observation(
            f'OUT-{state_id}-{capability_id}-{idx}','EXT',f'action-execution:{execution_id}',
            {'next_state_id':next_state,'value_id':'V','observed_value':observed_value},
            authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id=f'E-OUT-{state_id}-{capability_id}-{idx}'
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return out


def holdout_refs(ms,candidate, *, n=12, prefix='H'):
    base={
        'kind':'ACTION_OUTCOME_HOLDOUT',
        'start_state_id':candidate.start_state_id,
        'capability_id':candidate.capability_id,
        'capability_epoch':candidate.capability_epoch,
        'frame_epochs':[list(x) for x in candidate.frame_epochs],
        'episode_schema_epochs':[list(x) for x in candidate.episode_schema_epochs],
        'value_epoch':list(candidate.value_epoch),
        'topology_epochs':[list(x) for x in candidate.topology_epochs],
        'coordination_epochs':[list(x) for x in candidate.coordination_epochs],
        'evidence_premise_epochs':[list(x) for x in candidate.evidence_premise_epochs],
        'evidence_premise_signatures':[list(x) for x in candidate.evidence_premise_signatures],
        'actual_next_state_id':candidate.next_state_id,
        'actual_value_effect':candidate.value_effect,
    }
    return tuple(
        ms.append_evidence(f'{prefix}-{i}',{**base,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT')
        for i in range(n)
    )


def qualify_all(ms):
    candidates=ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)
    out={}
    for i,c in enumerate(candidates):
        ticket=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(
            c,qualification_evidence=holdout_refs(ms,c,prefix=f'H-{i}')
        )
        q=ms.qualify_action_outcome_predictive_relation(ticket)
        assert q['status']=='CURRENT_PREDICTIVE_RELATION'
        out[(c.start_state_id,c.capability_id)]=q['relation']
    return candidates,out


def populate_context_dependent_world(ms):
    # Same higher regulatory coordinate. Which subordinate request is useful depends
    # on opaque current state. U1 is useful in HA and harmful in HB; U2 reverses.
    table={
        ('HA','U1'):('HA-GOOD',+2.0),
        ('HA','U2'):('HA-BAD',-2.0),
        ('HB','U1'):('HB-BAD',-2.0),
        ('HB','U2'):('HB-GOOD',+2.0),
    }
    outs=[]
    for (state,capid),(next_state,effect) in table.items():
        for i in range(8):
            outs.append(execute_observed(ms,state_id=state,capability_id=capid,idx=i,next_state=next_state,observed_value=effect))
    return table,outs


def test_experimental_b_learns_context_dependent_subordinate_effect_from_actual_outcomes_only():
    td,ms=new_ms()
    try:
        setup(ms); table,outs=populate_context_dependent_world(ms)
        candidates,relations=qualify_all(ms)
        assert len(candidates)==4 and len(relations)==4
        got={(c.start_state_id,c.capability_id):(c.next_state_id,c.value_effect,c.support,c.consistency) for c in candidates}
        for key,(ns,effect) in table.items():
            assert got[key]==(ns,effect,8,1.0)
        # Every scheduling prediction was intentionally wrong, so learned labels must
        # have come from actual outcomes rather than intended/supplied effects.
        assert all(o['outcome']['prediction_commitment']['commitment']=='NO' for o in outs)
        for rel in relations.values():
            assert rel['truth_authority']=='NONE' and rel['causal_theorem_authority']=='NONE'
            assert rel['execution_authority']=='NONE' and rel['semantic_goal_authority']=='NONE'
    finally:
        td.cleanup()


def test_learned_relations_choose_different_means_by_current_state_without_supplied_predicted_effect():
    td,ms=new_ms()
    try:
        setup(ms); populate_context_dependent_world(ms); qualify_all(ms)
        for state,expected in [('HA','U1'),('HB','U2')]:
            ms.observe_value_state('V',0.0)
            ms.observe_opaque_control_state(
                Observation(f'QUERY-{state}','EXT','opaque-control',state,authority=Authority.OBSERVATION_ONLY),
                evidence_id=f'E-QUERY-{state}'
            )
            proposal=ms.nominate_counterfactual_rehearsal((),opts(),start_state_id=state,value_id='V')
            assert proposal is not None
            assert proposal.sequence==(expected,)
            assert proposal.predicted_step_value_effects==(2.0,)
    finally:
        td.cleanup()


def test_hidden_context_mixture_abstains_instead_of_fabricating_fixed_inverse():
    td,ms=new_ms()
    try:
        setup(ms)
        # Same opaque state/request produces two equally recurrent incompatible outcomes.
        for i in range(12):
            execute_observed(
                ms,state_id='HAMB',capability_id='U1',idx=i,
                next_state='G1' if i%2==0 else 'G2',observed_value=2.0 if i%2==0 else -2.0,
            )
        candidates=ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)
        assert candidates==()
        ms.observe_value_state('V',0.0)
        ms.observe_opaque_control_state(
            Observation('QUERY-HAMB','EXT','opaque-control','HAMB',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-QUERY-HAMB'
        )
        assert ms.nominate_counterfactual_rehearsal((),opts(),start_state_id='HAMB',value_id='V') is None
    finally:
        td.cleanup()


def test_subordinate_capability_drift_stales_learned_request_effect_relation_and_restart_does_not_restore_it():
    td,ms=new_ms()
    root=Path(td.name)
    try:
        setup(ms); populate_context_dependent_world(ms); _,relations=qualify_all(ms)
        rid=relations[('HA','U1')]['relation_id']
        assert ms.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        ms.change_capability_dependency('U1',reason='SUBORDINATE_POLICY_DRIFT')
        assert ms.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION'
        assert rid in ms.action_outcome_learning.relations
        ms2=Microseed(root)
        assert rid in ms2.action_outcome_learning.relations
        assert ms2.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION'
    finally:
        td.cleanup()


def test_subordinate_refusal_and_unknown_remain_authoritative_over_higher_level_request():
    td,ms=new_ms()
    try:
        setup(ms)
        for state in (FeasibilityState.REFUSED,FeasibilityState.UNKNOWN):
            try:
                ms.nominate_recruitment((RecruitmentOption('U1',state),),('U1',))
            except ValueError as exc:
                assert f'RECRUITMENT_NOT_FEASIBLE:U1:{state.value}' in str(exc)
            else:
                raise AssertionError('higher-level proposal overrode subordinate feasibility')
    finally:
        td.cleanup()


def test_representability_requires_no_new_production_hierarchy_owner():
    # The experimental packet should be research/tests only. This is also checked
    # from Git in the methodology receipt, but keep a semantic guard here.
    td,ms=new_ms()
    try:
        setup(ms)
        assert hasattr(ms,'nominate_action_outcome_predictive_candidates')
        assert hasattr(ms,'nominate_counterfactual_rehearsal')
        assert hasattr(ms,'recruitment_status')
        assert not hasattr(ms,'parent_manager')
        assert not hasattr(ms,'hierarchy_manager')
        assert not hasattr(ms,'learn_parent_child_inverse')
    finally:
        td.cleanup()
