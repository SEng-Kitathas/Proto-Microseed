from microseed import Authority, CapabilityContract, QualificationState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_current_step_feasibility_route_disagreement_preserves_unknown_and_blocks_b():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        m.register_capability(CapabilityContract(
            'FEAS-B2','feas-alt',{'target_capability_id':'B'},{},(),(),Authority.DERIVED_READ_ONLY,('T',),'CURRENT',{},
            dependencies=('B',),query_obligation_id='QF-B2',qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_:{'feasibility':'REFUSED','reason':'SECOND_ROUTE_REFUSES'},operational_scope_id='S',
        ))
        t2 = _execute_first_and_advance(m, trial, dc, next_state='s1', evidence_id='E-OUT-1834-A')
        bearing = m.assess_epistemic_program_step_outcome_bearing(trial, t2, dc)
        assert bearing['status']=='CONSENSUS_NONDISCRIMINATING'
        n2 = m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(t2, dc, act_ob())
        assert n2['status']=='ABSTAIN', n2
        assert n2['feasibility_basis']['reason']=='CURRENT_FEASIBILITY_ROUTE_DISAGREEMENT'
        assert n2['feasibility_basis']['feasibility']=='UNKNOWN'
        assert set(n2['feasibility_basis']['route_ids'])=={'FEAS-B','FEAS-B2'}
        assert calls==['A']
    finally:
        td.cleanup()
