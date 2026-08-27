from pathlib import Path
import tempfile
import pytest

from microseed import (
    Microseed, Authority, QualificationState, FeasibilityState, EpistemicStatus,
    CapabilityContract, OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract,
    RecruitmentOption, RehearsalTransitionObservation, QueryObligation, Observation,
    ExternalActionOutcomeRelationQualifier, ActionOutcomeRelationQualificationTicket,
)
from microseed.runtime.types import EvidenceRef


def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1427-reconstructed-')
    return td,Microseed(Path(td.name))


def cap(cid='A'):
    return CapabilityContract(
        cid,'opaque',{},{},(),(),Authority.EFFECT,('MS1403-1427',),'CURRENT',{},
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


def bad_prediction_rows(n=10):
    return tuple(RehearsalTransitionObservation(f'PRED{i}','S0','A','SX',9.0,0,'F',0,'E',0) for i in range(n))


def opts(): return (RecruitmentOption('A',FeasibilityState.FEASIBLE),)
def obl(): return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='SCOPE')


def execute_actual(ms, proposal, i, *, next_state='S1', post=1.5):
    if i:
        ms.observe_value_state('V',0.0)
        ms.observe_opaque_control_state(Observation(f'RST{i}','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-RST{i}')
    intent=ms.nominate_bounded_action_intent(proposal.proposal_id,obl())
    assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],obl())
    assert ex['status']=='ACTION_EXECUTED'
    eid=ex['execution']['execution_id']
    out=ms.record_bounded_action_outcome(
        eid,Observation(f'OUT{i}','EXT',f'action-execution:{eid}',{'next_state_id':next_state,'value_id':'V','observed_value':post},authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-OUT{i}'
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return out


def populate(ms,n=12,*,mixed=False):
    p=ms.nominate_counterfactual_rehearsal(bad_prediction_rows(),opts(),start_state_id='S0',value_id='V')
    assert p is not None and p.predicted_state_path==('S0','SX')
    outs=[]
    for i in range(n):
        if mixed:
            outs.append(execute_actual(ms,p,i,next_state='S1' if i%2==0 else 'S2',post=1.0 if i%2==0 else -1.0))
        else:
            outs.append(execute_actual(ms,p,i,next_state='S1',post=1.5))
    return p,outs


def holdout_refs(ms,candidate,n=20,*,next_state='S1',effect=1.5,prefix='HQ'):
    refs=[]
    payload_base={
        'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':candidate.start_state_id,'capability_id':candidate.capability_id,
        'capability_epoch':candidate.capability_epoch,'frame_epochs':[list(x) for x in candidate.frame_epochs],
        'episode_schema_epochs':[list(x) for x in candidate.episode_schema_epochs],'value_epoch':list(candidate.value_epoch),
        'topology_epochs':[list(x) for x in candidate.topology_epochs],'coordination_epochs':[list(x) for x in candidate.coordination_epochs],
    }
    for i in range(n):
        payload={**payload_base,'actual_next_state_id':next_state,'actual_value_effect':effect,'holdout_index':i}
        refs.append(ms.append_evidence(f'{prefix}{i}',payload,EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT'))
    return tuple(refs)


def test_failed_intentions_train_actual_consequence_not_intended_label():
    td,ms=make_ms()
    try:
        setup(ms); p,outs=populate(ms,12)
        assert all(o['outcome']['prediction_commitment']['commitment']=='NO' for o in outs)
        c=ms.nominate_action_outcome_predictive_candidates()[0]
        assert (c.start_state_id,c.capability_id,c.next_state_id,c.value_effect)==('S0','A','S1',1.5)
        assert c.consistency==1.0 and c.support==12
        assert p.predicted_state_path[1]=='SX' and p.predicted_step_value_effects[0]==9.0
    finally: td.cleanup()


def test_one_outcome_is_not_a_law():
    td,ms=make_ms()
    try:
        setup(ms); populate(ms,1)
        assert ms.nominate_action_outcome_predictive_candidates()==()
    finally: td.cleanup()


def test_hidden_context_mixture_abstains_instead_of_averaging():
    td,ms=make_ms()
    try:
        setup(ms); populate(ms,12,mixed=True)
        assert ms.nominate_action_outcome_predictive_candidates()==()
    finally: td.cleanup()


def test_actual_outcome_evidence_keeps_intention_as_provenance_only():
    td,ms=make_ms()
    try:
        setup(ms); _,outs=populate(ms,1)
        eid=outs[0]['outcome']['evidence_id']; row=ms.evidence.get(eid); payload=row['payload']
        assert payload['actual_value_effect']==1.5 and payload['next_state_id']=='S1'
        assert payload['intended_next_state_id']=='SX' and payload['intended_value_effect']==9.0
    finally: td.cleanup()


def test_independent_holdout_qualification_accepts_actual_relation_and_rejects_intention_decoy():
    td,ms=make_ms()
    try:
        setup(ms); populate(ms,12); c=ms.nominate_action_outcome_predictive_candidates()[0]
        refs=holdout_refs(ms,c,20)
        t=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs)
        assert t.state==QualificationState.SHADOW_QUALIFIED and t.holdout_accuracy==1.0
        r=ms.qualify_action_outcome_predictive_relation(t)
        assert r['status']=='CURRENT_PREDICTIVE_RELATION' and r['truth_authority']=='NONE' and r['causal_theorem_authority']=='NONE'
    finally: td.cleanup()


def test_proposal_evidence_cannot_self_qualify():
    td,ms=make_ms()
    try:
        setup(ms); populate(ms,12); c=ms.nominate_action_outcome_predictive_candidates()[0]
        refs=[]
        for eid in c.source_evidence_ids:
            row=ms.evidence.get(eid)
            refs.append(EvidenceRef(eid,row['sha256'],EpistemicStatus.PRESSURE_SUPPORTED,False))
        t=ActionOutcomeRelationQualificationTicket(c.candidate_id,c.digest(),QualificationState.SHADOW_QUALIFIED,'HSP-EXTERNAL', 'fake',tuple(refs),len(refs),1.0)
        assert ms.qualify_action_outcome_predictive_relation(t)['reason']=='PROPOSAL_QUALIFICATION_EVIDENCE_OVERLAP'
    finally: td.cleanup()


def test_proposal_only_candidate_cannot_enter_rehearsal_but_qualified_relation_can():
    td,ms=make_ms()
    try:
        setup(ms); populate(ms,12); c=ms.nominate_action_outcome_predictive_candidates()[0]
        ms.observe_value_state('V',0.0); ms.observe_opaque_control_state(Observation('RESET','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-RESET')
        assert ms.nominate_counterfactual_rehearsal((),opts(),start_state_id='S0',value_id='V') is None
        refs=holdout_refs(ms,c,20); ticket=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs)
        assert ms.qualify_action_outcome_predictive_relation(ticket)['status']=='CURRENT_PREDICTIVE_RELATION'
        p=ms.nominate_counterfactual_rehearsal((),opts(),start_state_id='S0',value_id='V')
        assert p is not None and p.predicted_state_path==('S0','S1') and p.predicted_step_value_effects==(1.5,)
    finally: td.cleanup()


def test_capability_drift_stales_learned_relation_without_erasing_history():
    td,ms=make_ms()
    try:
        setup(ms); populate(ms,12); c=ms.nominate_action_outcome_predictive_candidates()[0]; refs=holdout_refs(ms,c,20)
        r=ms.qualify_action_outcome_predictive_relation(ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs))['relation']
        assert ms.action_outcome_predictive_relation_status(r['relation_id'])['status']=='CURRENT_PREDICTIVE_RELATION'
        ms.change_capability_dependency('A',reason='DRIFT')
        assert ms.action_outcome_predictive_relation_status(r['relation_id'])['status']=='STALE_PREDICTIVE_RELATION'
        assert r['relation_id'] in ms.action_outcome_learning.relations
    finally: td.cleanup()


def test_restart_preserves_candidate_and_relation_history_without_recreating_current_contracts():
    td,ms=make_ms()
    try:
        setup(ms); populate(ms,12); c=ms.nominate_action_outcome_predictive_candidates()[0]; refs=holdout_refs(ms,c,20)
        r=ms.qualify_action_outcome_predictive_relation(ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs))['relation']
        ms2=Microseed(Path(td.name))
        assert c.candidate_id in ms2.action_outcome_learning.candidates and r['relation_id'] in ms2.action_outcome_learning.relations
        assert ms2.action_outcome_predictive_relation_status(r['relation_id'])['status']=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()


def test_candidate_and_relation_gain_no_truth_causal_or_self_qualification_authority():
    td,ms=make_ms()
    try:
        setup(ms); populate(ms,12); c=ms.nominate_action_outcome_predictive_candidates()[0]
        assert c.truth_authority==c.causal_theorem_authority==c.qualification_authority=='NONE'
        st=ms.action_outcome_learning_status(); assert st['general_causal_learner_authority']=='NONE' and st['self_qualification_authority']=='NONE'
        assert not hasattr(ms,'self_qualify_action_outcome_relation') and not hasattr(ms,'rewrite_world_model_from_prediction_error')
    finally: td.cleanup()


def test_ms1427_integration_survives_later_main_dev_evolution():
    td,ms=make_ms()
    try:
        st=ms.status()
        assert st['research_terminal_ms']>=1427 and st['integration_evidence_through_ms']>=1427 and st['next_ms']>=1428
        assert st['ms1428_started'] is True
        assert hasattr(ms,'nominate_action_outcome_predictive_candidates')
    finally: td.cleanup()
