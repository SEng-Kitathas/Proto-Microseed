from __future__ import annotations

from microseed import Authority, QueryObligation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, nominate, ctx, act_ob
from tests.embodiment.test_ms1756_pass09_ordinary_execution_event_binding import install_observation


def close(m,eid,evidence,capture):
    return m.record_bounded_action_outcome_via_observation_basis(
        eid,observation_capability_id='OBS',
        observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
        basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
        evidence_id=evidence,capture_id=capture)


def test_one_execution_cannot_gain_multiple_transition_samples_from_reobservation():
    td,m,calls,w,t,dc=fixture()
    try:
        install_observation(m)
        n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); eid=e['execution']['execution_id']
        first=close(m,eid,'E-ONE','C-ONE'); assert first['status']=='ACTION_OUTCOME_OBSERVED'
        second=close(m,eid,'E-TWO','C-TWO'); assert second['status']!='ACTION_OUTCOME_OBSERVED'
        receipts=[row for row in m.store.events() if row['kind']=='OBSERVATION_ADMISSION_RECEIPT' and row['payload']['execution_id']==eid]
        assert len(receipts)==1
        surface=m.discover_admitted_opaque_action_composition_candidates()
        assert surface['admitted_sample_count']==1
        assert surface['evidence_independence_authority']=='NONE'
    finally: td.cleanup()


def test_authenticated_execution_identity_remains_only_a_structural_origin_handle():
    td,m,calls,w,t,dc=fixture()
    try:
        install_observation(m)
        n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); eid=e['execution']['execution_id']
        assert close(m,eid,'E-ONE','C-ONE')['status']=='ACTION_OUTCOME_OBSERVED'
        p=m.derive_admitted_opaque_transition_sample(eid)
        assert p['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        assert p['sample'].origin_id==eid
        assert p['evidence_independence_authority']=='NONE'
        assert p['truth_authority']==p['qualification_authority']=='NONE'
    finally: td.cleanup()
