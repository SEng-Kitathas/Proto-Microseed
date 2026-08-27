from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from microseed.development.relational_algebra import discover_opaque_transition_conflicts
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture


def _install_ingress(m, outcomes):
    m.register_capability(CapabilityContract(
        'OBS-1851','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1851',),'CURRENT',{},
        query_obligation_id='OBS-Q-1851',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda execution_id,**_: {'next_state_id': outcomes[execution_id]}, operational_scope_id='S',
    ))
    m.register_capability(CapabilityContract(
        'BASIS-1851','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1851',),'CURRENT',{},
        dependencies=('OBS-1851',),query_obligation_id='BASIS-Q-1851',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: {'claim':'BOUNDED_USE_ONLY'}, operational_scope_id='S',
    ))
    m.frames.bind_capability('F','A')
    m.frames.bind_capability('F','OBS-1851')


def _close(m, xid, tag):
    return m.record_bounded_action_outcome_via_observation_basis(
        xid,
        observation_capability_id='OBS-1851', observation_obligation=QueryObligation('OBS-Q-1851','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
        basis_capability_id='BASIS-1851', basis_obligation=QueryObligation('BASIS-Q-1851','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
        evidence_id=f'E-1851-{tag}', capture_id=f'C-1851-{tag}',
    )


def _add_structural_admitted_epistemic_transition(m, outcomes, idx, end):
    cmt=RelationalCommitment(f'C-1851-{idx}','action:A',TernaryCommitment.YES,reason='ADMITTED_HISTORY_FIXTURE')
    intent=BoundedActionIntent(
        intent_id=f'I-1851-{idx}', proposal_id=None, proposal_digest=None, action_commitment=cmt,
        capability_id='A', capability_epoch=0, start_state_id='s0', control_state_evidence_id=f'CS-1851-{idx}',
        expected_next_state_id=None, expected_value_effect=None, value_epoch=None,
        obligation_id='Q', operational_scope_id='S', basis_kind='EPISTEMIC_PROGRAM_STEP',
    )
    ex=ActionExecutionRecord(f'X-1851-{idx}',intent.intent_id,'A',0,'s0','a'*64,execution_commitment_id=cmt.commitment_id)
    m.action_closure.add_intent(intent); m.action_closure.add_execution(ex)
    m.store.append('BOUNDED_ACTION_EXECUTED',ex.serializable())
    outcomes[ex.execution_id]=end
    out=_close(m,ex.execution_id,f'H{idx}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED', out
    return ex.execution_id


def test_recurrent_admitted_state_only_transition_conflict_reuses_ms1777_owner_without_explaining_it():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        outcomes={}
        _install_ingress(m,outcomes)
        # Execute the current epistemic challenge first, before adding any extra history
        # that could legitimately change the current decision-bearing surface.
        nomination=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial,dc,act_ob())
        assert nomination['status']=='ACTION_INTENT_NOMINATED', nomination
        ctx=EpistemicStepExecutionContext(trial,decision_context=dc)
        execution=m.execute_bounded_action(nomination['intent']['intent_id'],act_ob(),epistemic_step_context=ctx)
        assert execution['status']=='ACTION_EXECUTED', execution
        xid=execution['execution']['execution_id']; outcomes[xid]='sx'
        out=_close(m,xid,'LIVE')
        assert out['status']=='ACTION_OUTCOME_OBSERVED', out
        advanced=advance_epistemic_program_trial(
            trial,intent=m.action_closure.intents[nomination['intent']['intent_id']],execution=m.action_closure.executions[xid],
            outcome=m.action_closure.outcomes[out['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs),
        )
        bearing=m.assess_epistemic_program_step_outcome_bearing(trial,advanced,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE', bearing

        # Independent admitted historical recurrence is then added only for the
        # structural conflict-owner test: two s1 endpoints and one prior sx.
        xids=[xid,
            _add_structural_admitted_epistemic_transition(m,outcomes,0,'s1'),
            _add_structural_admitted_epistemic_transition(m,outcomes,1,'s1'),
            _add_structural_admitted_epistemic_transition(m,outcomes,2,'sx'),
        ]
        samples=[]
        for exid in xids:
            row=m.derive_admitted_opaque_transition_sample(exid)
            assert row['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE', row
            samples.append(row['sample'])
        conflicts=discover_opaque_transition_conflicts(samples)
        assert len(conflicts)==1
        c=conflicts[0]
        assert (c.start_token,c.action_token)==('s0','A')
        assert c.outcome_supports==(('s1',2),('sx',2))
        assert c.state_alias_authority==c.generator_authority==c.truth_authority=='NONE'
        assert c.causal_explanation_authority==c.evidence_independence_authority=='NONE'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
        assert calls==['A']
    finally:
        td.cleanup()
