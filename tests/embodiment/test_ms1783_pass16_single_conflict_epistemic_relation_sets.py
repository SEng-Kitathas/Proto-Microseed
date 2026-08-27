from dataclasses import replace

from microseed.development.action_learning import (
    ActionOutcomeExperience, assemble_single_conflict_epistemic_relation_sets,
    discover_action_outcome_alternative_hypotheses,
)


def row(i,end,effect,*,state='s0',action='A',value='V',premise=True):
    return ActionOutcomeExperience(
        evidence_id=f'E-{state}-{action}-{i}',execution_id=f'X-{state}-{action}-{i}',start_state_id=state,
        capability_id=action,actual_next_state_id=end,actual_value_effect=effect,capability_epoch=0,
        frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),value_epoch=(value,0),
        evidence_premise_epochs=((('BASIS',0),) if premise else ()),
        evidence_premise_signatures=((('BASIS','b'*64),) if premise else ()),
    )


def conflict(*,state='s0',action='A',offset=0):
    rows=(
        row(offset+0,'x',1,state=state,action=action),row(offset+1,'x',1,state=state,action=action),
        row(offset+2,'y',-1,state=state,action=action),row(offset+3,'y',-1,state=state,action=action),
    )
    return discover_action_outcome_alternative_hypotheses(rows)


def test_one_conflict_locus_projects_one_proposal_only_relation_set_per_recurrent_mode_with_full_ancestry():
    sets=assemble_single_conflict_epistemic_relation_sets(conflict())
    assert len(sets)==2 and all(len(s)==1 for s in sets)
    edges=[s[0] for s in sets]
    assert {(r.next_state_id,r.value_effect) for r in edges}=={('x',1.0),('y',-1.0)}
    assert all(r.authority=='PROPOSAL_ONLY_RELATIONAL_ALTERNATIVE' for r in edges)
    assert all(r.truth_authority==r.semantic_state_authority=='NONE' for r in edges)
    assert all(r.value_epoch==('V',0) for r in edges)
    assert all(r.evidence_premise_epochs==(('BASIS',0),) for r in edges)
    assert all(r.evidence_premise_signatures==(('BASIS','b'*64),) for r in edges)


def test_two_uncoupled_conflict_loci_do_not_cross_product_into_invented_world_models():
    hypotheses=conflict(state='s0',action='A')+conflict(state='s9',action='B',offset=10)
    assert assemble_single_conflict_epistemic_relation_sets(hypotheses)==()
