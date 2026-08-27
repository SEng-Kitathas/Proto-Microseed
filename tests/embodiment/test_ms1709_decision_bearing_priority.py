from dataclasses import replace
from pathlib import Path
import tempfile

from microseed import Authority, EpistemicStatus, FeasibilityState, Microseed, QualificationState, ValueVariableContract
from microseed.development.epistemic import EpistemicCurrentnessAnchor, EpistemicDeficitState
from microseed.development.epistemic_priority import derive_regulatory_decision_bearing_commitment
from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.commitment import TernaryCommitment


def rel(cap, effect):
    return RehearsalTransitionRelation('s0', cap, 'n' + cap, effect, 8, 1.0, (f'E-{cap}-{effect}',), 0, ('F', 0), ('EP', 0))


def fixture(value=-1.0):
    td = tempfile.TemporaryDirectory()
    m = Microseed(Path(td.name))
    m.register_value_variable(ValueVariableContract('V', 'reg', 0, 10, 'v' * 64, Authority.REFERENCE_ONLY, ('T',), 'CURRENT', qualification=QualificationState.SHADOW_QUALIFIED))
    m.observe_value_state('V', value)
    m.append_evidence('E-U', {'u': 1}, EpistemicStatus.UNKNOWN_INCOMPLETE)
    m.record_action_limited_unknown(
        deficit_id='D', question_key='Q', hypothesis_digest_sha256='a' * 64,
        unknown_evidence_id='E-U', missing_discriminator_signature_sha256='d' * 64,
        premise_anchors=(EpistemicCurrentnessAnchor('VALUE', 'V', 0),),
    )
    return td, m


def derive(m, sets, opts, *, deficit=None, current_capability_epochs=None, current_frame_epochs=None):
    return derive_regulatory_decision_bearing_commitment(
        deficit=m.epistemic_deficits.records['D'] if deficit is None else deficit,
        values=m.values,
        relation_sets=sets,
        options=opts,
        start_state_id='s0',
        current_capability_epochs={'A': 0, 'B': 0} if current_capability_epochs is None else current_capability_epochs,
        current_frame_epochs={'F': 0} if current_frame_epochs is None else current_frame_epochs,
        current_episode_epochs={'EP': 0},
    )


def alternatives():
    h1 = {('s0', 'A'): rel('A', 2), ('s0', 'B'): rel('B', 0)}
    h2 = {('s0', 'A'): rel('A', 0), ('s0', 'B'): rel('B', 2)}
    return h1, h2


def feasible_options():
    return (
        RecruitmentOption('A', FeasibilityState.FEASIBLE),
        RecruitmentOption('B', FeasibilityState.FEASIBLE),
    )


def test_different_executable_actions_under_live_alternatives_is_decision_bearing_yes():
    td, m = fixture(); h1, h2 = alternatives(); opts = feasible_options()
    try:
        r = derive(m, (h1, h2), opts)
        assert r.licenses_yes()
        assert r.reason == 'DISCRIMINATION_CAN_CHANGE_CURRENT_REGULATORY_ACTION'
        assert r.premise_ids == ('D', 'E-U', 'V')
    finally:
        td.cleanup()


def test_same_current_action_under_all_alternatives_is_not_priority():
    td, m = fixture(); opts = feasible_options()
    h = {('s0', 'A'): rel('A', 2), ('s0', 'B'): rel('B', 0)}
    try:
        r = derive(m, (h, h), opts)
        assert r.licenses_no()
        assert r.reason == 'DISCRIMINATION_CANNOT_CHANGE_CURRENT_EXECUTABLE_ACTION'
        assert r.premise_ids == ('D', 'E-U', 'V')
    finally:
        td.cleanup()


def test_zero_current_regulatory_pressure_is_not_priority_for_zero_pressure_reason():
    td, m = fixture(5); h1, h2 = alternatives(); opts = feasible_options()
    try:
        r = derive(m, (h1, h2), opts)
        assert r.licenses_no()
        assert r.reason == 'NO_CURRENT_REGULATORY_PRESSURE'
        assert r.premise_ids == ('D', 'V')
    finally:
        td.cleanup()


def test_stale_relational_frame_returns_unknown_from_frame_currentness_owner():
    td, m = fixture(); h1, h2 = alternatives(); opts = feasible_options()
    try:
        r = derive(m, (h1, h2), opts, current_frame_epochs={'F': 1})
        assert r.commitment == TernaryCommitment.UNKNOWN
        assert r.reason == 'RELATIONAL_ALTERNATIVE_FRAME_EPOCH_DRIFT:F'
        assert r.premise_ids == ('D',)
    finally:
        td.cleanup()


def test_stale_relational_capability_epoch_returns_unknown_from_capability_currentness_owner():
    td, m = fixture(); h1, h2 = alternatives(); opts = feasible_options()
    try:
        r = derive(m, (h1, h2), opts, current_capability_epochs={'A': 1, 'B': 0})
        assert r.commitment == TernaryCommitment.UNKNOWN
        assert r.reason == 'RELATIONAL_ALTERNATIVE_CAPABILITY_EPOCH_DRIFT:A'
        assert r.premise_ids == ('D',)
    finally:
        td.cleanup()


def test_noncurrent_value_anchor_returns_unknown_from_value_currentness_owner():
    td, m = fixture(); h1, h2 = alternatives(); opts = feasible_options()
    try:
        original = m.epistemic_deficits.records['D']
        m.change_value_variable('V', reason='MS1914_VALUE_CURRENTNESS_HOSTILE')
        # The registry callback may stale the owned record; this direct owner test keeps
        # the original ACTION_LIMITED carrier so the value-currentness guard itself must fire.
        carrier = replace(original, state=EpistemicDeficitState.ACTION_LIMITED)
        r = derive(m, (h1, h2), opts, deficit=carrier)
        assert r.commitment == TernaryCommitment.UNKNOWN
        assert r.reason == 'VALUE_PREMISE_NOT_CURRENT'
        assert r.premise_ids == ('D', 'V')
    finally:
        td.cleanup()


def test_non_action_limited_deficit_returns_unknown_from_need_state_owner():
    td, m = fixture(); h1, h2 = alternatives(); opts = feasible_options()
    try:
        carrier = replace(m.epistemic_deficits.records['D'], state=EpistemicDeficitState.REVISIT_REQUIRED)
        r = derive(m, (h1, h2), opts, deficit=carrier)
        assert r.commitment == TernaryCommitment.UNKNOWN
        assert r.reason == 'ACTION_LIMITED_DEFICIT_REQUIRED'
    finally:
        td.cleanup()


def test_unknown_feasibility_can_remove_decision_divergence_without_becoming_priority():
    td, m = fixture(); h1, h2 = alternatives()
    opts = (
        RecruitmentOption('A', FeasibilityState.FEASIBLE),
        RecruitmentOption('B', FeasibilityState.UNKNOWN),
    )
    try:
        assert not derive(m, (h1, h2), opts).licenses_yes()
    finally:
        td.cleanup()
