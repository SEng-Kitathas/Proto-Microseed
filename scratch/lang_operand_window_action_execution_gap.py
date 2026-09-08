from __future__ import annotations

from scratch.lang_arity_four_grounded_referents_fixture import fixture,_close,_observe_s0
from scratch.lang_c08c_native_owned_affordance_relation import ACT,_proposal
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(ms,tokens,phase,base):
    for i,t in enumerate(tokens):
        row=observe_opaque_token(ms,t,base+i,phase=phase)
        assert row['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',row


def _execute_without_outcome(ms,cid,serial):
    proposal=_proposal(ms,cid,serial)
    nomination=ms.nominate_bounded_action_intent(proposal.proposal_id,ACT)
    assert nomination['status']=='ACTION_INTENT_NOMINATED',nomination
    execution=ms.execute_bounded_action(nomination['intent']['intent_id'],ACT)
    assert execution['status']=='ACTION_EXECUTED',execution
    return execution


def run_gap() -> dict[str,object]:
    td,m,world,seeded=fixture(tokens=('R4','T9','W3','K7'))
    try:
        _observe_s0(m,'BOUNDARY-GAP-RESET')
        _obs(m,('R4','T9'),'BOUNDARY-GAP-PRE',20000)
        execution=_execute_without_outcome(m,'QA',200)
        execution_id=str(execution['execution']['execution_id'])
        # No action outcome/evidence is recorded here: only the organism-owned durable execution event exists.
        _obs(m,('W3','K7'),'BOUNDARY-GAP-POST',20100)
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        # Evidence-only suffix cannot see BOUNDED_ACTION_EXECUTED and therefore launders both token groups into arity4.
        assert out['derived_arity']==4,out
        events=m.store.events()
        exec_events=[row for row in events if row.get('kind')=='BOUNDED_ACTION_EXECUTED' and (row.get('payload') or {}).get('execution_id')==execution_id]
        assert len(exec_events)==1,exec_events
        return {
            'status':'STOP_EVIDENCE_ONLY_WINDOW_MISSES_OWNED_ACTION_EXECUTION_BOUNDARY',
            'execution_id':execution_id,
            'execution_store_seq':int(exec_events[0]['seq']),
            'action_outcome_recorded':'NO',
            'current_generalized_derived_arity':out['derived_arity'],
            'expected_post_execution_window_arity_if_execution_is_boundary':2,
            'localized_missing_mechanism':'CROSS_PLANE_TOKEN_EVIDENCE_TO_DURABLE_ACTION_EXECUTION_WINDOW_OWNER',
            'caller_supplied_boundary_marker':'NO',
            'execution_authority_gain_from_boundary_use':'NONE',
            'semantic_grouping_authority':'NONE',
        }
    finally:
        _close(m);td.cleanup()
