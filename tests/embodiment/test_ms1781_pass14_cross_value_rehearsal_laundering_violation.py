from microseed import Authority, FeasibilityState, QualificationState, ValueVariableContract
from microseed.development.recruitment import RecruitmentOption
from tests.embodiment.test_ms1477_integration import make_ms, setup


def test_cross_value_learned_relation_is_rejected_after_value_coordinate_binding_repair():
    td,m=make_ms()
    try:
        _,new=setup(m)
        assert new.value_epoch==('V',0)
        m.register_value_variable(ValueVariableContract(
            'W','other-coordinate',0,10,'w'*64,Authority.DERIVED_READ_ONLY,('MS1781',),'CURRENT',
            qualification=QualificationState.SHADOW_QUALIFIED,
        ))
        m.observe_value_state('W',-1.0)
        proposal=m.nominate_counterfactual_rehearsal(
            (),(RecruitmentOption('A',FeasibilityState.FEASIBLE),),start_state_id='S0',value_id='W',
        )
        assert proposal is None
    finally:
        td.cleanup()
