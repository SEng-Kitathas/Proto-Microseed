from tests.embodiment.test_lang_boundary_consumption_production import _setup,_obs,_close


def test_arbitrary_represented_non_token_evidence_can_still_segment_operand_window():
    td,m,world,seeded=_setup('SUBSTRATE-DELIMITER-REPRO')
    try:
        _obs(m,('R4','T9'),400000,'SUBSTRATE-DELIMITER-PRE')
        m.append_evidence(
            'E-SUBSTRATE-ARBITRARY-CALLER-NONTOKEN',
            {'kind':'ARBITRARY_CALLER_REPRESENTED_EVIDENCE','note':'no endogenous grouping authority'},
            __import__('microseed').EpistemicStatus.PRESSURE_SUPPORTED,
            source='ARBITRARY_CALLER',
        )
        _obs(m,('W3','K7'),400100,'SUBSTRATE-DELIMITER-POST')
        out=m._derive_current_store_aware_bounded_operand_window(max_events=65536,min_arity=2,max_arity=4)
        assert out['status']=='CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW',out
        assert out['derived_arity']==2,out
        assert out['last_boundary']['kind']=='REPRESENTED_NON_TOKEN_EVIDENCE',out
        assert out['last_boundary']['evidence_id']=='E-SUBSTRATE-ARBITRARY-CALLER-NONTOKEN',out
        assert out['caller_supplied_boundary']=='NO'  # API has no boundary arg, but caller controls evidence ingress.
    finally:
        _close(m);td.cleanup()
