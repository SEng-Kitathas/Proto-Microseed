from microseed.cognition.operator_language import BASE_OPS, ResearchOperator, base_closure, compose, op_apply


def test_old_cortex_lab_already_owns_extensional_fixpoint_mechanism_but_not_current_action_grounding():
    K=3
    inc=tuple(op_apply('INC',s,K) for s in range(K))
    dec=tuple(op_apply('DEC',s,K) for s in range(K))
    assert compose(inc,dec)==tuple(range(K))
    closure=base_closure(K)
    assert inc in closure and dec in closure and tuple(range(K)) in closure
    # Re-closing the already closed set under the same extensional composition adds nothing.
    recl=set(closure)
    for f in tuple(closure):
        for g in tuple(closure):
            recl.add(compose(f,g))
    assert recl==closure

    donor=ResearchOperator('DONOR',1)
    assert donor.status=='RESEARCH_ONLY'
    assert 'STATE_IDENTITY_SUPPLIED' in donor.assistance_ancestry
    assert 'TRANSITION_BOUNDARIES_SUPPLIED' in donor.assistance_ancestry
    # The old closure mechanism therefore transfers as a stripped algorithmic invariant,
    # not as evidence that BASE_OPS or supplied state identity are current Microseed affordances.
    assert set(BASE_OPS)
