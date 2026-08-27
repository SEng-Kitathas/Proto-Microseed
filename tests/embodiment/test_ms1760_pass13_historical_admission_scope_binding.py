from __future__ import annotations

from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, nominate, ctx, act_ob
from tests.embodiment.test_ms1759_pass12_action_observation_scope_binding import install


def install_hist(m, scope: str, calls: list[str]) -> None:
    obs = m.capabilities.contracts['OBS-X']
    m.register_capability(CapabilityContract(
        'HIST-X','historical-admission',
        {'admission_premise_signatures': [['OBS-X', obs.computed_signature_sha256()]]},
        {},('HISTORICAL_ONLY','NO_TRUTH_AUTHORITY'),(),Authority.DERIVED_READ_ONLY,('MS1760',),'CURRENT',{},
        query_obligation_id='HIST-X-Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: calls.append('HIST') or {'claim':'ADMITTED_AT_ACQUISITION'},
        operational_scope_id=scope,
    ))


def close_hist(m, eid: str, *, obs_scope: str, hist_scope: str):
    return m.record_bounded_action_outcome_via_observation_basis(
        eid,
        observation_capability_id='OBS-X',
        observation_obligation=QueryObligation('OBS-X-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id=obs_scope),
        basis_capability_id='BASIS-X',
        basis_obligation=QueryObligation('BASIS-X-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id=obs_scope),
        admission_basis_capability_id='HIST-X',
        admission_basis_obligation=QueryObligation('HIST-X-Q','historical admission',Authority.DERIVED_READ_ONLY,operational_scope_id=hist_scope),
        evidence_id='E-HIST', capture_id='C-HIST',
    )


def test_historical_admission_cannot_bridge_action_scope_even_when_live_observation_matches():
    td,m,action_calls,w,t,dc=fixture(); route_calls=[]
    try:
        install(m,'S',route_calls); install_hist(m,'OTHER',route_calls)
        n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); eid=e['execution']['execution_id']
        r=close_hist(m,eid,obs_scope='S',hist_scope='OTHER')
        assert r=={'status':'OUTCOME_REJECTED','reason':'HISTORICAL_ADMISSION_ACTION_SCOPE_MISMATCH'}
        assert route_calls==[] and not m.action_closure.outcomes
    finally: td.cleanup()


def test_same_scope_historical_admission_still_closes_and_stamps_receipt():
    td,m,action_calls,w,t,dc=fixture(); route_calls=[]
    try:
        install(m,'S',route_calls); install_hist(m,'S',route_calls)
        n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); eid=e['execution']['execution_id']
        r=close_hist(m,eid,obs_scope='S',hist_scope='S')
        assert r['status']=='ACTION_OUTCOME_OBSERVED'
        assert route_calls==['BASIS','OBS','HIST']
        receipt=r['observation_admission_receipt']
        assert receipt['historical_admission_basis_capability_id']=='HIST-X'
        assert receipt['operational_scope_id']=='S'
        assert receipt['truth_authority']==receipt['evidence_independence_authority']=='NONE'
    finally: td.cleanup()
