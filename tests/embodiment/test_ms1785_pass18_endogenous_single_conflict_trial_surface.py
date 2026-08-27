from microseed import Authority, EpistemicStatus, Observation
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord, ActionOutcomeCoordinate, ActionOutcomeRecord
from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, act_ob
from tests.embodiment.test_ms1757_pass10_trial_from_admitted_history import install_history_surface, add_history_transition


def add_value_outcome(m,i,end,effect):
    cmt=RelationalCommitment(f'VC-{i}','action:A',TernaryCommitment.YES,reason='STRUCTURAL_VALUE_HISTORY_FIXTURE')
    intent=BoundedActionIntent(
        intent_id=f'VI-{i}',proposal_id=None,proposal_digest=None,action_commitment=cmt,capability_id='A',capability_epoch=0,
        start_state_id='s0',control_state_evidence_id=f'VS-{i}',expected_next_state_id=None,expected_value_effect=None,
        value_epoch=('V',0),obligation_id='Q',operational_scope_id='S',basis_kind='MULTI_VALUE_LICENSE',required_value_epochs=(('V',0),),
    )
    ex=ActionExecutionRecord(f'VX-{i}',intent.intent_id,'A',0,'s0','a'*64,execution_commitment_id=cmt.commitment_id)
    m.action_closure.add_intent(intent); m.action_closure.add_execution(ex)
    m.append_evidence(f'VE-{i}',{'kind':'STRUCTURAL_VALUE_OUTCOME_FIXTURE'},EpistemicStatus.PRESSURE_SUPPORTED,source='TEST')
    coord=ActionOutcomeCoordinate('V',0,-1.0+effect,effect,frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),))
    out=ActionOutcomeRecord(f'VO-{i}',ex.execution_id,f'VE-{i}',end,None,None,cmt,value_outcomes=(coord,))
    m.action_closure.add_outcome(out)


def add_background(m,rid,state,next_state,effect):
    m.action_outcome_learning.add_relation(QualifiedActionOutcomePredictiveRelation(
        relation_id=rid,candidate_id='C-'+rid,candidate_sha256=(rid[-1].lower() if rid[-1].lower() in 'abcdef' else 'a')*64,
        start_state_id=state,capability_id='B',next_state_id=next_state,value_effect=effect,
        support=12,consistency=1.0,source_evidence_ids=('E-'+rid,),qualification_evidence_ids=('Q-'+rid,),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=0,frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
    ))


def test_owned_outcome_conflict_plus_current_background_removes_external_relation_set_for_bounded_family():
    td,m,calls,world,_,_=fixture()
    try:
        outcomes=install_history_surface(m)
        for idx,row in enumerate((('s0','A','m0'),('m0','B','e0'),('s0','C','e0'),('s1','A','m1'),('m1','B','e1'),('s1','C','e1'))):
            add_history_transition(m,outcomes,idx,*row)
        # One recurrent value-bearing conflict locus for A at s0.
        add_value_outcome(m,0,'x',2.0); add_value_outcome(m,1,'x',2.0)
        add_value_outcome(m,2,'y',-1.0); add_value_outcome(m,3,'y',-1.0)
        # Shared qualified background: B is an alternative now and closes the A->B trace after either mode.
        add_background(m,'R-B0','s0','bx',0.5)
        add_background(m,'R-BX','x','ex',0.0)
        add_background(m,'R-BY','y','ey',0.0)
        m.observe_opaque_control_state(Observation('CS-1785','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-1785')
        surface=m.derive_bounded_action_outcome_epistemic_relation_sets()
        assert surface['status']=='SINGLE_CONFLICT_EPISODIC_MODEL_SURFACE'
        assert surface['conflict_slot']==('s0','A') and len(surface['relation_sets'])==2
        result=m.discover_and_arbitrate_endogenous_epistemic_trial_from_admitted_history_and_endogenous_alternatives(
            deficit_id='D',obligation=act_ob(),
        )
        assert result['status']=='EPISTEMIC_TRIAL_INSTANTIATED', result
        assert result['trial'].steps==('A','B')
        assert result['alternative_model_set_authority']=='PROPOSAL_ONLY_EPHEMERAL'
        assert result['world_model_authority']==result['causal_explanation_authority']=='NONE'
        assert calls==[]
    finally:
        td.cleanup()


def test_two_uncoupled_owned_conflicts_abstain_instead_of_inventing_cross_locus_coherence():
    td,m,_,_,_,_=fixture()
    try:
        add_value_outcome(m,0,'x',2.0); add_value_outcome(m,1,'x',2.0); add_value_outcome(m,2,'y',-1.0); add_value_outcome(m,3,'y',-1.0)
        # A second exact conflict group on another value ancestry is enough to exceed this bounded family.
        # Reuse structural records but alter their coordinate to a new current value would require a new value owner;
        # instead add a second state/action group by constructing B records directly.
        # The discovery function's no-cross-locus rule is already tested in Pass16; here just verify the entity surfaces the boundary.
        # Duplicate the first group with a different start state by editing the experiences through closure records.
        cmt=RelationalCommitment('BC','action:B',TernaryCommitment.YES,reason='SECOND_CONFLICT_FIXTURE')
        for j,(end,effect) in enumerate((('p',1.0),('p',1.0),('q',-1.0),('q',-1.0)),start=10):
            intent=BoundedActionIntent(f'BI-{j}',None,None,cmt,'B',0,'s9',f'BS-{j}',None,None,('V',0),'Q','S',basis_kind='MULTI_VALUE_LICENSE',required_value_epochs=(('V',0),))
            ex=ActionExecutionRecord(f'BX-{j}',intent.intent_id,'B',0,'s9','b'*64,execution_commitment_id=cmt.commitment_id)
            m.action_closure.add_intent(intent);m.action_closure.add_execution(ex)
            m.append_evidence(f'BE-{j}',{'kind':'SECOND_CONFLICT'},EpistemicStatus.PRESSURE_SUPPORTED,source='TEST')
            coord=ActionOutcomeCoordinate('V',0,-1.0+effect,effect,frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),))
            m.action_closure.add_outcome(ActionOutcomeRecord(f'BO-{j}',ex.execution_id,f'BE-{j}',end,None,None,cmt,value_outcomes=(coord,)))
        surface=m.derive_bounded_action_outcome_epistemic_relation_sets()
        assert surface['status']=='NO_SINGLE_CONFLICT_EPISODIC_MODEL_SURFACE'
        assert surface['relation_sets']==() and surface['model_set_authority']=='NONE'
    finally:
        td.cleanup()
