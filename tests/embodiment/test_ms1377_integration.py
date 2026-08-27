from microseed import (
    TernaryCommitment, RelationalCommitment,
    FeasibilityState, EpistemicStatus, QualificationState,
    project_feasibility, project_epistemic_status, project_qualification_state,
    project_epistemic_deficit_state,
)
from microseed.development.epistemic import EpistemicDeficitState, EpistemicBearingKind
from microseed.runtime.types import Authority, ResourceMode


def test_commitment_primitive_is_premise_licensing_not_truth():
    c = RelationalCommitment('c1','opaque:P',TernaryCommitment.YES, qualifiers=(('truth_authority','NONE'),))
    assert c.licenses_yes() is True
    assert c.qualifier('truth_authority') == 'NONE'


def test_binding_and_applicability_are_orthogonal_and_each_can_abstain():
    b = RelationalCommitment('b','opaque:P',TernaryCommitment.YES,binding=TernaryCommitment.UNKNOWN)
    a = RelationalCommitment('a','opaque:P',TernaryCommitment.YES,applicability=TernaryCommitment.NO)
    assert b.gate_unknown and b.abstains() and not b.coarse_null
    assert a.coarse_null and a.abstains() and not a.evaluable


def test_feasibility_is_exact_ternary_projection_without_replacing_enum():
    assert project_feasibility(FeasibilityState.FEASIBLE, commitment_id='f1', target_id='cap:X').commitment == TernaryCommitment.YES
    assert project_feasibility(FeasibilityState.REFUSED, commitment_id='f2', target_id='cap:X').commitment == TernaryCommitment.NO
    assert project_feasibility(FeasibilityState.UNKNOWN, commitment_id='f3', target_id='cap:X').commitment == TernaryCommitment.UNKNOWN
    assert {x.value for x in FeasibilityState} == {'FEASIBLE','REFUSED','UNKNOWN'}


def test_epistemic_status_axis_mix_is_losslessly_split():
    na = project_epistemic_status(EpistemicStatus.NOT_APPLICABLE, commitment_id='e1', target_id='q:X')
    unk = project_epistemic_status(EpistemicStatus.UNKNOWN_INCOMPLETE, commitment_id='e2', target_id='q:X')
    no = project_epistemic_status(EpistemicStatus.VIOLATED, commitment_id='e3', target_id='q:X')
    assert na.commitment == TernaryCommitment.UNKNOWN and na.applicability == TernaryCommitment.NO and na.reason == 'NOT_APPLICABLE'
    assert unk.commitment == TernaryCommitment.UNKNOWN and unk.applicability == TernaryCommitment.YES and unk.reason == 'UNKNOWN_INCOMPLETE'
    assert no.commitment == TernaryCommitment.NO and no.applicability == TernaryCommitment.YES


def test_qualification_lifecycle_currentness_are_not_commitment_values():
    q = project_qualification_state(QualificationState.QUALIFIED, commitment_id='q1', target_id='cand:X')
    s = project_qualification_state(QualificationState.STALE, commitment_id='q2', target_id='cand:X')
    r = project_qualification_state(QualificationState.REJECTED, commitment_id='q3', target_id='cand:X')
    assert q.commitment == TernaryCommitment.YES and q.qualifier('currentness') == 'CURRENT'
    assert s.commitment == TernaryCommitment.UNKNOWN and s.qualifier('currentness') == 'STALE'
    assert r.commitment == TernaryCommitment.NO and r.qualifier('lifecycle') == 'REJECTED'


def test_epistemic_deficit_lifecycle_stays_unknown_but_remains_behaviorally_distinguishable():
    projected = [project_epistemic_deficit_state(x, commitment_id=f'd{i}', target_id='def:X') for i,x in enumerate(EpistemicDeficitState)]
    assert all(x.commitment == TernaryCommitment.UNKNOWN for x in projected)
    assert {x.qualifier('epistemic_lifecycle') for x in projected} == {x.value for x in EpistemicDeficitState}


def test_sidecar_difference_changes_behavior_without_fourth_commitment_value():
    ignorance = RelationalCommitment('u1','P',TernaryCommitment.UNKNOWN,reason='IGNORANCE',qualifiers=(('next_pressure','SEEK_EVIDENCE'),))
    conflict = RelationalCommitment('u2','P',TernaryCommitment.UNKNOWN,reason='CONFLICT',qualifiers=(('next_pressure','DISCRIMINATE_CONFLICT'),))
    assert ignorance.commitment == conflict.commitment == TernaryCommitment.UNKNOWN
    assert ignorance.qualifier('next_pressure') != conflict.qualifier('next_pressure')


def test_recursive_reification_is_reference_with_ancestry_not_authority_gain():
    base = RelationalCommitment('base','opaque:P',TernaryCommitment.UNKNOWN)
    meta = RelationalCommitment('meta','commitment:base:has-current-evidence',TernaryCommitment.YES,premise_ids=(base.commitment_id,),qualifiers=(('authority_gain','NONE'),))
    rebuilt = RelationalCommitment.from_serializable(meta.serializable())
    assert rebuilt == meta and rebuilt.premise_ids == ('base',) and rebuilt.qualifier('authority_gain') == 'NONE'


def test_authority_and_resource_mode_are_not_projected_as_truth_stances():
    import microseed.development.commitment_adapters as a
    assert not hasattr(a, 'project_authority')
    assert not hasattr(a, 'project_resource_mode')
    assert Authority.EFFECT.value == 'EFFECT' and ResourceMode.FEDERATED.value == 'FEDERATED'


def test_bearing_kind_is_not_erased_into_stance():
    assert EpistemicBearingKind.MODEL_SPACE_CHALLENGE != EpistemicBearingKind.DISCRIMINATES_LIVE_SET
    import microseed.development.commitment_adapters as a
    assert not hasattr(a, 'project_bearing_kind')


def test_serialization_preserves_orthogonal_axes_and_sidecar():
    c = RelationalCommitment('s','T',TernaryCommitment.UNKNOWN,binding=TernaryCommitment.YES,applicability=TernaryCommitment.NO,reason='NOT_APPLICABLE',qualifiers=(('source','E17'),('epoch','4')),premise_ids=('p1','p2'))
    assert RelationalCommitment.from_serializable(c.serializable()) == c


def test_no_bulk_native_enum_replacement_occurred():
    assert 'STALE' in {x.value for x in QualificationState}
    assert 'ACTION_LIMITED' in {x.value for x in EpistemicDeficitState}
    assert 'NOT_APPLICABLE' in {x.value for x in EpistemicStatus}


def test_ms1377_architectural_floor_survives_later_main_dev(tmp_path):
    from microseed import Microseed
    ms = Microseed(tmp_path / 'state')
    st = ms.status()
    assert st['research_terminal_ms'] >= 1377
    assert st['integration_evidence_through_ms'] >= 1377
    assert st['next_ms'] > 1377
    # Historical MS1377 ceiling: TRCH remains a premise-licensing adapter layer,
    # not a truth logic or bulk enum replacement, even after later campaigns.
    assert hasattr(ms, 'derive_bounded_action_commitment')
    assert not hasattr(ms, 'settle_truth')
    assert 'STALE' in {x.value for x in QualificationState}
    assert 'ACTION_LIMITED' in {x.value for x in EpistemicDeficitState}
