import pytest

from microseed.development.action_learning import (
    ActionOutcomeExperience,
    ActionOutcomeSuccessorCouplingCandidate,
    ActionOutcomeThreeLocusChainCandidate,
    discover_action_outcome_alternative_hypotheses,
    discover_action_outcome_successor_couplings,
    discover_action_outcome_three_locus_chains,
    assemble_successor_coupled_epistemic_relation_sets,
    assemble_three_locus_chain_epistemic_relation_sets,
)


def row(xid, state, action, end, effect, *, frame='F', value='V'):
    return ActionOutcomeExperience(
        evidence_id=f'E-{xid}', execution_id=xid, start_state_id=state, capability_id=action,
        actual_next_state_id=end, actual_value_effect=effect, capability_epoch=0,
        frame_epochs=((frame,0),), episode_schema_epochs=(('EP',0),), value_epoch=(value,0),
    )


def two_locus_rows():
    return (
        row('X1','s0','A','s1',+1), row('X2','s0','A','s1',+1),
        row('X3','s0','A','s1',-1), row('X4','s0','A','s1',-1),
        row('X11','s1','B','s2',+1), row('X12','s1','B','s2',+1),
        row('X13','s1','B','s2',-1), row('X14','s1','B','s2',-1),
    )


def three_locus_rows():
    return two_locus_rows() + (
        row('X21','s2','C','u',+1), row('X22','s2','C','u',+1),
        row('X23','s2','C','v',-1), row('X24','s2','C','v',-1),
    )


def test_recurrent_successor_floor_and_zero_authority():
    hs=discover_action_outcome_alternative_hypotheses(two_locus_rows())
    assert len(hs)==4
    assert discover_action_outcome_successor_couplings(hs,(('X1','X11'),))==()
    cs=discover_action_outcome_successor_couplings(hs,(('X1','X11'),('X2','X12'),('X3','X13'),('X4','X14')))
    assert len(cs)==2 and {c.support for c in cs}=={2}
    assert all(c.truth_authority==c.causal_explanation_authority==c.evidence_independence_authority==c.model_set_authority=='NONE' for c in cs)


def test_two_locus_only_observed_pairs_no_cartesian_product():
    hs=discover_action_outcome_alternative_hypotheses(two_locus_rows())
    cs=discover_action_outcome_successor_couplings(hs,(('X1','X11'),('X2','X12'),('X3','X13'),('X4','X14')))
    sets=assemble_successor_coupled_epistemic_relation_sets(hs,cs)
    assert len(sets)==2
    assert all(len(model)==2 for model in sets)
    assert {(m[0].value_effect,m[1].value_effect) for m in sets}=={(1.0,1.0),(-1.0,-1.0)}


def test_branching_pair_coupling_preserves_ambiguity():
    hs=discover_action_outcome_alternative_hypotheses(two_locus_rows())
    pairs=(('X1','X11'),('X2','X12'),('X1','X13'),('X2','X14'),('X3','X13'),('X4','X14'))
    cs=discover_action_outcome_successor_couplings(hs,pairs)
    assert len(cs)>=3
    assert assemble_successor_coupled_epistemic_relation_sets(hs,cs)==()


def test_visible_state_action_does_not_collapse_frame_ancestry():
    rows=(
        row('A1','s0','A','x',1,frame='F1'), row('A2','s0','A','x',1,frame='F1'),
        row('A3','s0','A','y',-1,frame='F1'), row('A4','s0','A','y',-1,frame='F1'),
        row('Z1','s0','A','x',1,frame='F2'), row('Z2','s0','A','x',1,frame='F2'),
        row('Z3','s0','A','y',-1,frame='F2'), row('Z4','s0','A','y',-1,frame='F2'),
        row('B1','s1','B','p',1), row('B2','s1','B','p',1),
        row('B3','s1','B','q',-1), row('B4','s1','B','q',-1),
    )
    hs=discover_action_outcome_alternative_hypotheses(rows)
    cs=discover_action_outcome_successor_couplings(hs,(('A1','B1'),('A2','B2'),('A3','B3'),('A4','B4')))
    assert assemble_successor_coupled_epistemic_relation_sets(hs,cs)==()


def test_pairwise_recurrence_without_support_stitching_is_not_three_locus_coherence():
    rows=three_locus_rows() + (
        row('X15','s1','B','s2',+1), row('X16','s1','B','s2',+1),
        row('X17','s1','B','s2',-1), row('X18','s1','B','s2',-1),
    )
    hs=discover_action_outcome_alternative_hypotheses(rows)
    # AB and BC each recur for the same B mode hypotheses, but use disjoint B executions.
    pairs=(('X1','X11'),('X2','X12'),('X3','X13'),('X4','X14'),
           ('X15','X21'),('X16','X22'),('X17','X23'),('X18','X24'))
    cs=discover_action_outcome_successor_couplings(hs,pairs)
    assert len(cs)==4
    chains=discover_action_outcome_three_locus_chains(hs,cs)
    assert chains==()


def test_complete_execution_triples_earn_exact_bounded_three_locus_surface():
    hs=discover_action_outcome_alternative_hypotheses(three_locus_rows())
    pairs=(('X1','X11'),('X2','X12'),('X3','X13'),('X4','X14'),
           ('X11','X21'),('X12','X22'),('X13','X23'),('X14','X24'))
    cs=discover_action_outcome_successor_couplings(hs,pairs)
    chains=discover_action_outcome_three_locus_chains(hs,cs)
    assert len(chains)==2 and {c.support for c in chains}=={2}
    sets=assemble_three_locus_chain_epistemic_relation_sets(hs,chains)
    assert len(sets)==2 and all(len(model)==3 for model in sets)
    assert all(c.truth_authority==c.causal_explanation_authority==c.evidence_independence_authority==c.model_set_authority=='NONE' for c in chains)


def test_four_conflict_loci_do_not_silently_truncate_to_three():
    rows=three_locus_rows()+(
        row('X31','u','D','m',1),row('X32','u','D','m',1),
        row('X33','u','D','n',-1),row('X34','u','D','n',-1),
    )
    hs=discover_action_outcome_alternative_hypotheses(rows)
    pairs=(('X1','X11'),('X2','X12'),('X3','X13'),('X4','X14'),
           ('X11','X21'),('X12','X22'),('X13','X23'),('X14','X24'))
    cs=discover_action_outcome_successor_couplings(hs,pairs)
    chains=discover_action_outcome_three_locus_chains(hs,cs)
    assert len(chains)==2
    assert assemble_three_locus_chain_epistemic_relation_sets(hs,chains)==()


def test_coupling_authority_escalation_is_constructor_rejected():
    with pytest.raises(ValueError, match='AUTHORITY_ESCALATION'):
        ActionOutcomeSuccessorCouplingCandidate('c','a','b',2,(('x1','y1'),('x2','y2')),truth_authority='YES')


def test_chain_authority_escalation_is_constructor_rejected():
    with pytest.raises(ValueError, match='AUTHORITY_ESCALATION'):
        ActionOutcomeThreeLocusChainCandidate('c',('a','b','c'),2,(('x1','y1','z1'),('x2','y2','z2')),causal_explanation_authority='YES')
