from __future__ import annotations

from microseed import Authority, QueryObligation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, nominate, ctx, act_ob
from tests.embodiment.test_ms1756_pass09_ordinary_execution_event_binding import install_observation
from tests.embodiment.test_ms1759_pass12_action_observation_scope_binding import install as install_x
from tests.embodiment.test_ms1760_pass13_historical_admission_scope_binding import install_hist, close_hist


def ordinary_sample_world():
    td,m,calls,w,t,dc=fixture(); install_observation(m)
    n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); eid=e['execution']['execution_id']
    r=m.record_bounded_action_outcome_via_observation_basis(
        eid,observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
        basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
        evidence_id='E-OUT',capture_id='C-OUT')
    assert r['status']=='ACTION_OUTCOME_OBSERVED'
    return td,m,eid


def test_same_epoch_action_content_change_invalidates_relational_sample():
    td,m,eid=ordinary_sample_world()
    try:
        assert m.derive_admitted_opaque_transition_sample(eid)['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        m.capabilities.contracts['A'].boundary={'same-id-epoch':'changed-action-contract'}
        r=m.derive_admitted_opaque_transition_sample(eid)
        assert r=={'status':'ABSTAIN','reason':'ACTION_CAPABILITY_NOT_CURRENT_FOR_RELATIONAL_SAMPLE','authority':'NONE'}
    finally: td.cleanup()


def test_same_epoch_live_observation_content_change_invalidates_nonhistorical_sample():
    td,m,eid=ordinary_sample_world()
    try:
        assert m.derive_admitted_opaque_transition_sample(eid)['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        m.capabilities.contracts['OBS'].boundary={'same-id-epoch':'changed-live-mapping'}
        r=m.derive_admitted_opaque_transition_sample(eid)
        assert r=={'status':'ABSTAIN','reason':'LIVE_OBSERVATION_ADMISSION_NOT_CURRENT','authority':'NONE'}
    finally: td.cleanup()


def test_prospective_live_mapping_change_does_not_erase_historically_admitted_sample():
    td,m,calls,w,t,dc=fixture(); route_calls=[]
    try:
        install_x(m,'S',route_calls); install_hist(m,'S',route_calls); m.frames.bind_capability('F','A'); m.frames.bind_capability('F','OBS-X')
        n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); eid=e['execution']['execution_id']
        assert close_hist(m,eid,obs_scope='S',hist_scope='S')['status']=='ACTION_OUTCOME_OBSERVED'
        assert m.derive_admitted_opaque_transition_sample(eid)['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        # Same handle/epoch, new prospective mapping content. Historical admission
        # remains bound to what was admitted at acquisition, not future live access.
        m.capabilities.contracts['OBS-X'].boundary={'prospective':'new-live-mapping'}
        r=m.derive_admitted_opaque_transition_sample(eid)
        assert r['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        assert r['truth_authority']==r['evidence_independence_authority']=='NONE'
    finally: td.cleanup()
