from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture
from tests.embodiment.test_ms1757_pass10_trial_from_admitted_history import install_history_surface, add_history_transition


def test_authenticated_admitted_transition_does_not_by_itself_supply_constructor_raw_history_or_episode_boundary():
    td,m,_,_,_,_=fixture()
    try:
        outcomes=install_history_surface(m)
        add_history_transition(m,outcomes,0,'s0','A','s1')
        r=m.derive_admitted_opaque_transition_sample('HX-0')
        assert r['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        p=r['sample_serializable']
        assert set(p)=={'sample_id','origin_id','start_token','action_token','end_token','frame_id','frame_epoch'}
        for absent in ('raw_history','episode_schema_id','episode_schema_epoch','raw_tokens'):
            assert absent not in p
        # Inventing a history slice or raw coordinate from this compact transition
        # would be a new representational choice, not provenance already carried by
        # the admitted sample.
        assert r['truth_authority']==r['evidence_independence_authority']=='NONE'
    finally: td.cleanup()
