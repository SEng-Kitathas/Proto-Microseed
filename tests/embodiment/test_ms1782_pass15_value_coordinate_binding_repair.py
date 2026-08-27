from microseed import Authority, EpistemicStatus, FeasibilityState, QualificationState, ValueVariableContract
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_priority import derive_regulatory_decision_bearing_commitment
from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.commitment import TernaryCommitment
from tests.embodiment.test_ms1477_integration import make_ms, setup

LEGACY_DIGEST='0e23c40dede961645c0690fcf85a5859aa4bfca3a445091cd2364977b7e3b1da'


def test_learned_relation_only_enters_rehearsal_for_its_own_value_coordinate_and_legacy_digest_stays_stable():
    td,m=make_ms()
    try:
        _,new=setup(m)
        m.register_value_variable(ValueVariableContract('W','other',0,10,'w'*64,Authority.DERIVED_READ_ONLY,('MS1782',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
        m.observe_value_state('W',-1.0)
        opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE),)
        assert m.nominate_counterfactual_rehearsal((),opts,start_state_id='S0',value_id='W') is None
        # The same learned relation remains usable for the coordinate it actually owns.
        m.observe_value_state('V',-1.0)
        p=m.nominate_counterfactual_rehearsal((),opts,start_state_id='S0',value_id='V')
        assert p is not None and p.value_epoch==('V',0) and p.predicted_value_effect==new.value_effect
        legacy=RehearsalTransitionRelation('s0','A','s1',1.0,8,1.0,('E',),0,('F',0),('EP',0))
        assert legacy.digest()==LEGACY_DIGEST
    finally:
        td.cleanup()


def test_priority_rejects_explicit_alternative_from_wrong_value_coordinate():
    td,m=make_ms()
    try:
        setup(m)
        m.observe_value_state('V',-11.0)
        m.append_evidence('E-U-X',{'u':1},EpistemicStatus.UNKNOWN_INCOMPLETE)
        m.record_action_limited_unknown(deficit_id='D-X',question_key='Q-X',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U-X',missing_discriminator_signature_sha256='d'*64,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),))
        def r(effect,value):
            return RehearsalTransitionRelation('S0','A','S1',effect,8,1.0,('E',),0,('F',0),('E',0),value_epoch=(value,0))
        out=derive_regulatory_decision_bearing_commitment(
            deficit=m.epistemic_deficits.records['D-X'],values=m.values,
            relation_sets=({('S0','A'):r(1.0,'V')},{('S0','A'):r(-1.0,'W')}),
            options=(RecruitmentOption('A',FeasibilityState.FEASIBLE),),start_state_id='S0',
            current_capability_epochs={'A':0},current_frame_epochs={'F':0},current_episode_epochs={'E':0},
        )
        assert out.commitment==TernaryCommitment.UNKNOWN
        assert out.reason=='RELATIONAL_ALTERNATIVE_VALUE_COORDINATE_MISMATCH:W'
    finally:
        td.cleanup()
