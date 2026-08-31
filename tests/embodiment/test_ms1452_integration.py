from __future__ import annotations

from pathlib import Path
import tempfile

from microseed.runtime.entity import Microseed
from microseed.runtime.types import (
    Authority, CapabilityContract, EpistemicStatus, FeasibilityState, Observation,
    OperationalFrameContract, EpisodeSchemaContract, QualificationState, QueryObligation,
    ValueVariableContract,
)
from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import RehearsalTransitionObservation
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier
from microseed.development.predictive_adaptation import PredictiveCurrentnessConfig


def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1452-')
    return td,Microseed(Path(td.name))


def cap(cid='A'):
    return CapabilityContract(
        cid,'opaque',{},{},(),(),Authority.EFFECT,('MS1428-1452',),'CURRENT',{},
        query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: {'receipt':cid},operational_scope_id='SCOPE'
    )


def setup(ms):
    ms.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS878-902',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    ms.register_value_variable(ValueVariableContract('V','opaque',8.0,10.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS953-977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')))
    ms.observe_value_state('V',0.0)
    ms.register_capability(cap('A'))
    ms.register_episode_schema(EpisodeSchemaContract('E','opaque','e'*64,Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    ms.observe_opaque_control_state(Observation('CS0','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS0')


def seed_rows(n=10):
    return tuple(RehearsalTransitionObservation(f'PRED{i}','S0','A','SX',9.0,0,'F',0,'E',0) for i in range(n))


def opts(): return (RecruitmentOption('A',FeasibilityState.FEASIBLE),)
def obl(): return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='SCOPE')


def execute_actual(ms, proposal, i, *, next_state='S1', post=1.5, prefix='D'):
    ms.observe_value_state('V',0.0)
    ms.observe_opaque_control_state(Observation(f'{prefix}-RST{i}','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-{prefix}-RST{i}')
    intent=ms.nominate_bounded_action_intent(proposal.proposal_id,obl())
    assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],obl())
    assert ex['status']=='ACTION_EXECUTED'
    eid=ex['execution']['execution_id']
    out=ms.record_bounded_action_outcome(
        eid,Observation(f'{prefix}-OUT{i}','EXT',f'action-execution:{eid}',{'next_state_id':next_state,'value_id':'V','observed_value':post},authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-{prefix}-OUT{i}'
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return out


def holdout_refs(ms,candidate,n=12,*,next_state='S1',effect=1.5,prefix='HQ',one_miss=False):
    refs=[]
    payload_base={
        'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':candidate.start_state_id,'capability_id':candidate.capability_id,
        'capability_epoch':candidate.capability_epoch,'frame_epochs':[list(x) for x in candidate.frame_epochs],
        'episode_schema_epochs':[list(x) for x in candidate.episode_schema_epochs],'value_epoch':list(candidate.value_epoch),
        'topology_epochs':[list(x) for x in candidate.topology_epochs],'coordination_epochs':[list(x) for x in candidate.coordination_epochs],
    }
    for i in range(n):
        ns,ef=(('S1',1.5) if one_miss and i==n-1 else (next_state,effect))
        payload={**payload_base,'actual_next_state_id':ns,'actual_value_effect':ef,'holdout_index':i}
        refs.append(ms.append_evidence(f'{prefix}{i}',payload,EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT'))
    return tuple(refs)


def establish_old_law(ms):
    p=ms.nominate_counterfactual_rehearsal(seed_rows(),opts(),start_state_id='S0',value_id='V')
    assert p is not None
    for i in range(12): execute_actual(ms,p,i,next_state='S1',post=1.5,prefix='TRAIN')
    c=ms.nominate_action_outcome_predictive_candidates()[0]
    ticket=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout_refs(ms,c,12,prefix='QA'))
    res=ms.qualify_action_outcome_predictive_relation(ticket)
    assert res['status']=='CURRENT_PREDICTIVE_RELATION'
    return ms.action_outcome_learning.relations[res['relation']['relation_id']]


def current_proposal(ms):
    tag=len(ms.counterfactual_rehearsals.proposals)
    ms.observe_value_state('V',0.0)
    ms.observe_opaque_control_state(Observation(f'CUR{tag}','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-CUR{tag}')
    p=ms.nominate_counterfactual_rehearsal((),opts(),start_state_id='S0',value_id='V')
    assert p is not None
    return p


def test_isolated_miss_does_not_stale_relation():
    td,ms=make_ms()
    try:
        setup(ms); r=establish_old_law(ms); p=current_proposal(ms)
        execute_actual(ms,p,0,next_state='S2',post=2.5,prefix='ISO')
        for i in range(1,8): execute_actual(ms,p,i,next_state='S1',post=1.5,prefix='ISO')
        w=ms.assess_action_outcome_predictive_currentness(r.relation_id)
        assert w['status']=='CURRENT_WITHIN_BOUNDS' and w['witness']['window_accuracies']==[0.875]
        assert ms.action_outcome_predictive_relation_status(r.relation_id)['status']=='CURRENT_PREDICTIVE_RELATION'
    finally: td.cleanup()


def test_transient_bad_window_followed_by_recovery_does_not_stale():
    td,ms=make_ms()
    try:
        setup(ms); r=establish_old_law(ms); p=current_proposal(ms)
        for i in range(8): execute_actual(ms,p,i,next_state='S2',post=2.5,prefix='TRB')
        for i in range(8): execute_actual(ms,p,8+i,next_state='S1',post=1.5,prefix='TRG')
        w=ms.assess_action_outcome_predictive_currentness(r.relation_id)
        assert w['status']=='CURRENT_WITHIN_BOUNDS' and w['witness']['window_accuracies']==[0.0,1.0]
    finally: td.cleanup()


def test_two_bad_windows_create_drift_witness_without_switch_authority():
    td,ms=make_ms()
    try:
        setup(ms); r=establish_old_law(ms); p=current_proposal(ms)
        for i in range(16): execute_actual(ms,p,i,next_state='S2',post=2.5,prefix='SW')
        w=ms.assess_action_outcome_predictive_currentness(r.relation_id)
        assert w['status']=='DRIFT_WITNESS' and w['witness']['window_accuracies']==[0.0,0.0]
        assert w['model_switch_authority']==w['drift_cause_authority']==w['semantic_regime_authority']=='NONE'
        st=ms.action_outcome_predictive_relation_status(r.relation_id)
        assert st['status']=='STALE_PREDICTIVE_RELATION' and st['reason']=='EMPIRICAL_DRIFT_WITNESS'
        assert r.relation_id in ms.action_outcome_learning.relations
    finally: td.cleanup()


def test_ambiguous_mixture_stales_old_law_but_nominates_no_replacement():
    td,ms=make_ms()
    try:
        setup(ms); r=establish_old_law(ms); p=current_proposal(ms)
        for i in range(16):
            execute_actual(ms,p,i,next_state='S1' if i%2==0 else 'S2',post=1.5 if i%2==0 else 2.5,prefix='MIX')
        w=ms.assess_action_outcome_predictive_currentness(r.relation_id)
        assert w['status']=='DRIFT_WITNESS' and w['witness']['window_accuracies']==[0.5,0.5]
        assert ms.nominate_action_outcome_replacement_candidates(r.relation_id,w['witness']['witness_id'])==()
    finally: td.cleanup()


def test_drift_scoped_actual_outcomes_nominate_replacement_with_lineage():
    td,ms=make_ms()
    try:
        setup(ms); r=establish_old_law(ms); p=current_proposal(ms)
        for i in range(16): execute_actual(ms,p,i,next_state='S2',post=2.5,prefix='REP')
        w=ms.assess_action_outcome_predictive_currentness(r.relation_id)
        cs=ms.nominate_action_outcome_replacement_candidates(r.relation_id,w['witness']['witness_id'])
        assert len(cs)==1 and cs[0].next_state_id=='S2' and cs[0].value_effect==2.5 and cs[0].consistency==1.0
        link=ms.action_outcome_learning.replacement_links[cs[0].candidate_id]
        assert link.replacement_of_relation_id==r.relation_id and link.model_switch_authority=='NONE'
    finally: td.cleanup()


def test_replacement_requires_fresh_independent_qualification_before_rehearsal_resume():
    td,ms=make_ms()
    try:
        setup(ms); old=establish_old_law(ms); p=current_proposal(ms)
        for i in range(16): execute_actual(ms,p,i,next_state='S2',post=2.5,prefix='RQ')
        w=ms.assess_action_outcome_predictive_currentness(old.relation_id)
        c=ms.nominate_action_outcome_replacement_candidates(old.relation_id,w['witness']['witness_id'])[0]
        ms.observe_value_state('V',0.0); ms.observe_opaque_control_state(Observation('PREQ','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-PREQ')
        assert ms.nominate_counterfactual_rehearsal((),opts(),start_state_id='S0',value_id='V') is None
        ticket=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout_refs(ms,c,12,next_state='S2',effect=2.5,prefix='QB',one_miss=True))
        assert round(ticket.holdout_accuracy,6)==round(11/12,6)
        q=ms.qualify_action_outcome_predictive_relation(ticket)
        assert q['status']=='CURRENT_PREDICTIVE_RELATION' and q['replacement_of']==old.relation_id
        p2=current_proposal(ms)
        assert p2.predicted_state_path==('S0','S2') and p2.predicted_step_value_effects==(2.5,)
    finally: td.cleanup()


def test_recovery_after_drift_does_not_reactivate_old_relation():
    td,ms=make_ms()
    try:
        setup(ms); old=establish_old_law(ms); p=current_proposal(ms)
        for i in range(16): execute_actual(ms,p,i,next_state='S2',post=2.5,prefix='DR')
        w=ms.assess_action_outcome_predictive_currentness(old.relation_id)
        assert w['status']=='DRIFT_WITNESS'
        # Even if later observations happen to match again, the historical drift witness remains currentness-negative.
        # Recovery sampling is explicitly assisted: the learned zero-row proposal
        # is no longer a lawful execution premise after empirical drift, so use
        # the original supplied-row seed proposal retained from establish_old_law().
        assisted = next(
            proposal for pid, proposal in ms.counterfactual_rehearsals.proposals.items()
            if pid != p.proposal_id
        )
        assert ms.counterfactual_rehearsal_status(p.proposal_id)['status'] == 'UNKNOWN_INCOMPLETE'
        assert ms.counterfactual_rehearsal_status(assisted.proposal_id)['status'] == 'CURRENT_REHEARSAL_PROPOSAL'
        for i in range(16): execute_actual(ms,assisted,16+i,next_state='S1',post=1.5,prefix='REC-ASSISTED')
        w2=ms.assess_action_outcome_predictive_currentness(old.relation_id)
        assert w2['status']=='DRIFT_WITNESS'
        assert ms.action_outcome_predictive_relation_status(old.relation_id)['status']=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()


def test_structural_premise_drift_is_separate_and_does_not_mint_empirical_witness():
    td,ms=make_ms()
    try:
        setup(ms); old=establish_old_law(ms)
        ms.change_capability_dependency('A',reason='STRUCTURAL-DRIFT')
        out=ms.assess_action_outcome_predictive_currentness(old.relation_id)
        assert out['status']=='STALE_STRUCTURAL_PREMISE' and out['drift_witness'] is None
        assert old.relation_id not in ms.action_outcome_learning.currentness_witnesses
    finally: td.cleanup()


def test_restart_preserves_drift_and_replacement_history_without_restoring_runtime_authority():
    td,ms=make_ms()
    try:
        setup(ms); old=establish_old_law(ms); p=current_proposal(ms)
        for i in range(16): execute_actual(ms,p,i,next_state='S2',post=2.5,prefix='RST')
        w=ms.assess_action_outcome_predictive_currentness(old.relation_id)
        c=ms.nominate_action_outcome_replacement_candidates(old.relation_id,w['witness']['witness_id'])[0]
        ms2=Microseed(Path(td.name))
        assert old.relation_id in ms2.action_outcome_learning.relations
        assert old.relation_id in ms2.action_outcome_learning.currentness_witnesses
        assert c.candidate_id in ms2.action_outcome_learning.candidates
        assert c.candidate_id in ms2.action_outcome_learning.replacement_links
        assert ms2.action_outcome_predictive_relation_status(old.relation_id)['status']=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()


def test_adaptation_adds_no_general_switch_cause_or_self_qualification_authority():
    td,ms=make_ms()
    try:
        st=ms.action_outcome_learning_status()
        assert st['model_switch_authority']==st['drift_cause_authority']==st['self_qualification_authority']=='NONE'
        assert not hasattr(ms,'auto_switch_action_outcome_relation')
        assert not hasattr(ms,'classify_action_outcome_drift_cause')
        assert not hasattr(ms,'self_qualify_action_outcome_relation')
    finally: td.cleanup()


def test_ms1452_hard_stop_and_next_frontier():
    td,ms=make_ms()
    try:
        st=ms.status()
        # Historical MS1452 floor remains true in later descendants; later integrations
        # may lawfully advance the current hard stop/frontier without rewriting MS1452.
        assert st['research_terminal_ms']>=1452 and st['integration_evidence_through_ms']>=1452
        assert st['next_ms']>=1453
        assert st['ms1428_started'] is True
    finally: td.cleanup()
