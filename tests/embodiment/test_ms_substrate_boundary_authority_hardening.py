from microseed import Authority, EpistemicStatus, Observation
from microseed.development.action_closure import OpaqueControlStateWitness
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_obs,_close


def test_arbitrary_exact_non_token_evidence_no_longer_has_grouping_boundary_authority():
    td,m,world,seeded=_setup('SUBSTRATE-BOUNDARY-NO-CALLER')
    try:
        state=m.observe_opaque_control_state(
            Observation('CAP-SUBSTRATE-BASELINE','EXTERNAL','opaque-control','S-BASELINE',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-SUBSTRATE-BASELINE-BOUNDARY',
        )
        assert state['status']=='CURRENT_OPAQUE_CONTROL_STATE',state
        _obs(m,('R4','T9'),420000,'SUBSTRATE-BOUNDARY-PRE')
        m.append_evidence(
            'E-ARBITRARY-NON-TOKEN-NO-BOUNDARY',
            {'kind':'ARBITRARY_CALLER_REPRESENTED_EVIDENCE','runtime_boot_seq':m._current_runtime_boot_seq()},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source='ARBITRARY_CALLER',
        )
        _obs(m,('W3','K7'),420100,'SUBSTRATE-BOUNDARY-POST')
        out=m._derive_current_store_aware_bounded_operand_window(max_events=65536,min_arity=2,max_arity=4)
        assert out['status']=='CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW',out
        assert out['derived_arity']==4,out
        assert tuple((r[1].get('payload') or {}).get('opaque_token') for r in out['selected'])==('R4','T9','W3','K7')
        assert out['last_boundary']['kind']=='OPAQUE_CONTROL_STATE_OBSERVED'
        assert out['last_boundary']['evidence_id']=='E-SUBSTRATE-BASELINE-BOUNDARY'
        assert out['last_boundary']['boundary_authentication']=='OBSERVATION_EVIDENCE_CONTROL_STATE_CHAIN'
        assert out['caller_evidence_grouping_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_authenticated_opaque_control_state_observation_remains_operational_boundary():
    td,m,world,seeded=_setup('SUBSTRATE-BOUNDARY-CONTROL')
    try:
        _obs(m,('R4','T9'),421000,'SUBSTRATE-CONTROL-PRE')
        state=m.observe_opaque_control_state(
            Observation('CAP-SUBSTRATE-STATE','EXTERNAL','opaque-control','S-BOUNDARY',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-SUBSTRATE-STATE-BOUNDARY',
        )
        assert state['status']=='CURRENT_OPAQUE_CONTROL_STATE',state
        _obs(m,('W3','K7'),421100,'SUBSTRATE-CONTROL-POST')
        out=m._derive_current_store_aware_bounded_operand_window(max_events=65536,min_arity=2,max_arity=4)
        assert out['status']=='CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW',out
        assert out['derived_arity']==2,out
        assert tuple((r[1].get('payload') or {}).get('opaque_token') for r in out['selected'])==('W3','K7')
        assert out['last_boundary']['kind']=='OPAQUE_CONTROL_STATE_OBSERVED'
        assert out['last_boundary']['state_id']=='S-BOUNDARY'
        assert out['last_boundary']['evidence_id']=='E-SUBSTRATE-STATE-BOUNDARY'
        assert out['last_boundary']['boundary_authentication']=='OBSERVATION_EVIDENCE_CONTROL_STATE_CHAIN'
    finally:_close(m);td.cleanup()


def test_naked_forged_control_state_store_event_without_observation_evidence_chain_fails_closed():
    td,m,world,seeded=_setup('SUBSTRATE-BOUNDARY-FORGED-STATE')
    try:
        _obs(m,('R4','T9'),422000,'SUBSTRATE-FORGED-PRE')
        fake_eid='E-FAKE-CONTROL-EVIDENCE'
        m.append_evidence(
            fake_eid,
            {'capture_id':'CAP-FAKE','state_id':'S-FAKE','referent':'opaque-control'},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source='ARBITRARY_CALLER',
        )
        # Direct low-level store injection has the right serialized witness shape but no prior OBSERVATION chain.
        m.store.append('OPAQUE_CONTROL_STATE_OBSERVED',OpaqueControlStateWitness('S-FAKE',fake_eid).serializable())
        _obs(m,('W3','K7'),422100,'SUBSTRATE-FORGED-POST')
        out=m._derive_current_store_aware_bounded_operand_window(max_events=65536,min_arity=2,max_arity=4)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='CONTROL_STATE_BOUNDARY_OBSERVATION_CHAIN_NOT_AUTHENTICATED',out
        assert out['evidence_id']==fake_eid
    finally:_close(m);td.cleanup()


def test_malformed_control_state_store_event_fails_closed_before_becoming_boundary():
    td,m,world,seeded=_setup('SUBSTRATE-BOUNDARY-MALFORMED-STATE')
    try:
        _obs(m,('R4','T9'),423000,'SUBSTRATE-MALFORMED-PRE')
        m.store.append('OPAQUE_CONTROL_STATE_OBSERVED',{
            'state_id':'S-X','evidence_id':'E-MISSING','authority':'EFFECT','semantic_state_authority':'NONE'
        })
        _obs(m,('W3','K7'),423100,'SUBSTRATE-MALFORMED-POST')
        out=m._derive_current_store_aware_bounded_operand_window(max_events=65536,min_arity=2,max_arity=4)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='CONTROL_STATE_BOUNDARY_WITNESS_SHAPE_NOT_AUTHENTICATED',out
    finally:_close(m);td.cleanup()


def test_authenticated_action_execution_boundary_semantics_remain_separate_and_unchanged():
    # Existing action-boundary suites cover behavior; this audit pins the owner distinction.
    from microseed import Microseed
    import inspect
    src=inspect.getsource(Microseed._derive_current_store_aware_bounded_operand_window)
    assert 'BOUNDED_ACTION_EXECUTED' in src
    assert 'ACTION_EXECUTION_BOUNDARY_NOT_AUTHENTICATED' in src
    assert 'OPAQUE_CONTROL_STATE_OBSERVED' in src
    assert 'CALLER_EVIDENCE_INGRESS_HAS_NO_GROUPING_AUTHORITY' in src
