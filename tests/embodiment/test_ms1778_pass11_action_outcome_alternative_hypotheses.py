from dataclasses import replace

from microseed.development.action_learning import ActionOutcomeExperience, discover_action_outcome_alternative_hypotheses


def row(i, end, effect, *, execution=None, frame='F'):
    return ActionOutcomeExperience(
        evidence_id=f'E{i}', execution_id=execution or f'X{i}', start_state_id='s0', capability_id='A',
        actual_next_state_id=end, actual_value_effect=effect, capability_epoch=0,
        frame_epochs=((frame,0),), episode_schema_epochs=(('EP',0),), value_epoch=('V',0),
    )


def test_one_surprise_does_not_generate_alternative_hypotheses_but_two_recurrent_modes_do():
    weak=(row(0,'x',1),row(1,'x',1),row(2,'y',-1))
    assert discover_action_outcome_alternative_hypotheses(weak)==()
    strong=weak+(row(3,'y',-1),)
    out=discover_action_outcome_alternative_hypotheses(strong)
    assert {(h.next_state_id,h.value_effect,h.mode_support) for h in out}=={('x',1.0,2),('y',-1.0,2)}
    assert all(h.group_support==4 for h in out)
    assert all(h.truth_authority==h.qualification_authority==h.causal_explanation_authority=='NONE' for h in out)
    assert all(h.evidence_independence_authority=='NONE' for h in out)


def test_duplicate_execution_does_not_inflate_recurrence_and_ancestry_groups_do_not_pool():
    dup=(row(0,'x',1),row(1,'x',1),row(2,'y',-1,execution='SAME'),row(3,'y',-1,execution='SAME'))
    assert discover_action_outcome_alternative_hypotheses(dup)==()
    cross=(row(0,'x',1,frame='F1'),row(1,'x',1,frame='F1'),row(2,'y',-1,frame='F2'),row(3,'y',-1,frame='F2'))
    assert discover_action_outcome_alternative_hypotheses(cross)==()
