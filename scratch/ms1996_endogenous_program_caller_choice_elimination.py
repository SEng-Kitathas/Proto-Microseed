from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from microseed import Authority, CapabilityContract, Observation, QualificationState, QueryObligation
from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, derive_current_generated_epistemic_program_candidates
from microseed.development.rehearsal import RehearsalTransitionRelation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture
from tests.embodiment.test_ms1820_pass13_owned_three_locus_surface_generates_program import _add_value_step


OBLIGATION = QueryObligation(
    'Q', 'opaque-developmental-trial', required_authority=Authority.EFFECT, operational_scope_id='S'
)

MAIN = ('K-17', 'M-23', 'R-41')
ALT_MIDDLE = 'M-29'
FALLBACK = 'F-83'
DISTRACTORS = ('A', 'B', 'N-61', 'N-67')


def _fob(capability_id: str) -> QueryObligation:
    return QueryObligation(
        'QF-' + capability_id,
        'feasibility:' + capability_id,
        required_authority=Authority.DERIVED_READ_ONLY,
        operational_scope_id='S',
    )


def _register_effect_and_feasibility(m, calls: list[str], capability_id: str) -> None:
    m.register_capability(CapabilityContract(
        capability_id, 'opaque-primitive', {}, {}, (), (), Authority.EFFECT, ('MS1996',), 'CURRENT', {},
        query_obligation_id='Q', qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda _cid=capability_id, **_: calls.append(_cid) or {'receipt': _cid},
        operational_scope_id='S',
    ))
    m.register_capability(CapabilityContract(
        'FEAS-' + capability_id, 'opaque-feasibility', {'target_capability_id': capability_id}, {}, (), (),
        Authority.DERIVED_READ_ONLY, ('MS1996',), 'CURRENT', {}, dependencies=(capability_id,),
        query_obligation_id='QF-' + capability_id, qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: {'feasibility': 'FEASIBLE', 'reason': 'CURRENT_BOUNDED_ROUTE'},
        operational_scope_id='S',
    ))


def _add_chain(m, prefix: str, effect: float, final_state: str) -> None:
    e1 = _add_value_step(
        m, xid=f'{prefix}-1', action=MAIN[0], start='s0', end='s1', effect=effect,
        control_evidence=f'E-ROOT-{prefix}',
    )
    e2 = _add_value_step(
        m, xid=f'{prefix}-2', action=MAIN[1], start='s1', end='s2', effect=effect,
        control_evidence=e1,
    )
    _add_value_step(
        m, xid=f'{prefix}-3', action=MAIN[2], start='s2', end=final_state, effect=effect,
        control_evidence=e2,
    )


def _add_shared_relation(m, *, relation_id: str, action: str, start: str, end: str, effect: float = 0.0) -> None:
    m.action_outcome_learning.add_relation(QualifiedActionOutcomePredictiveRelation(
        relation_id=relation_id,
        candidate_id='C-' + relation_id,
        candidate_sha256=(relation_id.lower().replace('-', '') + '0' * 64)[:64],
        start_state_id=start,
        capability_id=action,
        next_state_id=end,
        value_effect=float(effect),
        support=12,
        consistency=1.0,
        source_evidence_ids=('E-' + relation_id,),
        qualification_evidence_ids=('Q-' + relation_id,),
        holdout_support=12,
        holdout_accuracy=1.0,
        capability_epoch=0,
        frame_epochs=(('F', 0),),
        episode_schema_epochs=(('EP', 0),),
        value_epoch=('V', 0),
    ))


def _build(*, order: tuple[str, ...] = ('P1', 'P2', 'N1', 'N2')):
    td, m, calls, _, _, _ = fixture()
    for cid in MAIN + (FALLBACK,) + ('N-61', 'N-67'):
        _register_effect_and_feasibility(m, calls, cid)

    # Four recurrent organism-owned histories create two represented alternatives.
    rows = {
        'P1': (+1.0, 'u'), 'P2': (+1.0, 'u'),
        'N1': (-1.0, 'v'), 'N2': (-1.0, 'v'),
    }
    for prefix in order:
        effect, final_state = rows[prefix]
        _add_chain(m, prefix, effect, final_state)

    # A currently qualified shared fallback gives the regulatory decision a live alternative.
    _add_shared_relation(m, relation_id='R-F83-S0', action=FALLBACK, start='s0', end='sf', effect=0.0)

    m.observe_opaque_control_state(
        Observation('CS-MS1996', 'EXT', 'opaque-control', 's0', authority=Authority.OBSERVATION_ONLY),
        evidence_id='E-CS-MS1996',
    )
    return td, m, calls


def _close(td, m) -> None:
    try:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close()
    finally:
        td.cleanup()


def run_unique(order: tuple[str, ...] = ('P1', 'P2', 'N1', 'N2')) -> dict[str, object]:
    td, m, calls = _build(order=order)
    try:
        before_intents = len(m.action_closure.intents)
        before_exec = len(m.action_closure.executions)
        generated = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=OBLIGATION, max_nodes=64,
        )
        assert generated['status'] == 'REPRESENTED_INFORMATIVE_PROGRAMS_FOUND', generated
        assert MAIN in tuple(tuple(x) for x in generated['programs'])
        assert tuple(generated['generator_tokens']) == tuple(sorted(set(generated['generator_tokens'])))
        assert all(cid in generated['generator_tokens'] for cid in MAIN)
        assert all(cid in generated['generator_tokens'] for cid in DISTRACTORS)
        assert generated['generator_surface_authority'] == 'CURRENT_CAPABILITY_CONTRACTS_ONLY'
        assert generated['truth_authority'] == generated['execution_authority'] == 'NONE'

        result = m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(
            deficit_id='D', obligation=OBLIGATION, max_nodes=64,
        )
        assert result['status'] == 'EPISTEMIC_TRIAL_INSTANTIATED', result
        trial = result['trial']
        assert trial.steps == MAIN, trial.steps
        assert trial.execution_authority == trial.truth_authority == trial.qualification_authority == 'NONE'
        assert result['priority']['commitment'] == 'YES'
        assert result['information']['commitment'] == 'YES'
        assert result['generated_program_authority'] == 'PROPOSAL_ONLY_EPHEMERAL'
        assert result['world_model_authority'] == result['closure_authority'] == result['execution_authority'] == 'NONE'
        assert len(m.action_closure.intents) == before_intents
        assert len(m.action_closure.executions) == before_exec
        assert calls == []
        chosen = next(c for c in generated['candidates'] if c.steps == MAIN)

        budget = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=OBLIGATION, max_nodes=1,
        )
        assert budget['status'] == 'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED', budget
        assert budget['reason'] == 'REPRESENTED_PROGRAM_NODE_BUDGET_EXHAUSTED'
        assert budget['candidates'] == ()
        assert budget['truth_authority'] == budget['execution_authority'] == 'NONE'

        # Currentness hostile: a stale required primitive disappears from the current
        # generator alphabet; fresh generation must not reuse the old proposal.
        m.capabilities.contracts[MAIN[2]].currentness = 'STALE'
        stale_generated = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=OBLIGATION, max_nodes=64,
        )
        stale_programs = {tuple(x) for x in stale_generated.get('programs', ())}
        assert MAIN not in stale_programs
        assert stale_generated['status'] == 'REPRESENTED_REACHABILITY_INCOMPLETE', stale_generated
        stale_admitted = m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(
            deficit_id='D', obligation=OBLIGATION, max_nodes=64,
        )
        assert stale_admitted['status'] == 'ABSTAIN', stale_admitted
        assert stale_admitted['reason'] == 'CURRENT_GENERATOR_TRANSITION_UNREPRESENTED'
        assert stale_admitted['execution_authority'] == 'NONE'
        assert len(m.action_closure.intents) == before_intents
        assert len(m.action_closure.executions) == before_exec
        assert calls == []

        return {
            'status': 'PASS',
            'history_order': list(order),
            'candidate_id': chosen.candidate_id,
            'candidate_sha256': chosen.digest(),
            'generated_program': list(trial.steps),
            'generator_tokens': list(generated['generator_tokens']),
            'caller_supplied_preferred_action_or_program': 'NO',
            'intents_added_during_generation_and_arbitration': len(m.action_closure.intents) - before_intents,
            'executions_added_during_generation_and_arbitration': len(m.action_closure.executions) - before_exec,
            'priority': result['priority']['commitment'],
            'information': result['information']['commitment'],
            'budget_status': budget['status'],
            'stale_generated_status': stale_generated['status'],
            'stale_admission_status': stale_admitted['status'],
            'stale_admission_reason': stale_admitted['reason'],
            'proposal_authority': trial.proposal_authority,
            'execution_authority': trial.execution_authority,
            'truth_authority': trial.truth_authority,
            'semantic_action_authority': trial.semantic_action_authority,
        }
    finally:
        _close(td, m)


def _rel(state: str, action: str, nxt: str, effect: float) -> RehearsalTransitionRelation:
    return RehearsalTransitionRelation(
        state_id=state, capability_id=action, next_state_id=nxt, value_effect=float(effect),
        support=8, consistency=1.0, source_evidence_ids=(f'E-TIE-{state}-{action}-{nxt}-{effect}',),
        capability_epoch=0, frame_epoch=('F', 0), episode_schema_epoch=('EP', 0), value_epoch=('V', 0),
    )


def run_tie() -> dict[str, object]:
    # Separate arbitration hostile: two genuinely distinct discriminating actions emerge
    # from the registry-owned alphabet after the same first primitive.  Equal model
    # partitions must remain a tie; caller order may not pick one.
    td, m, calls, _, _, _ = fixture()
    try:
        for cid in ('K-17', 'R-41', 'R-43', FALLBACK):
            _register_effect_and_feasibility(m, calls, cid)
        m.observe_opaque_control_state(
            Observation('CS-MS1996-TIE', 'EXT', 'opaque-control', 's0', authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-CS-MS1996-TIE',
        )
        positive = (
            _rel('s0', 'K-17', 's1', +1.0), _rel('s0', FALLBACK, 'sf', 0.0),
            _rel('s1', 'R-41', 'u', 0.0), _rel('s1', 'R-43', 'x', 0.0),
        )
        negative = (
            _rel('s0', 'K-17', 's1', -1.0), _rel('s0', FALLBACK, 'sf', 0.0),
            _rel('s1', 'R-41', 'v', 0.0), _rel('s1', 'R-43', 'y', 0.0),
        )
        dc = EpistemicDecisionBearingContext((positive, negative), ())
        generated = derive_current_generated_epistemic_program_candidates(
            decision_context=dc, start_state_id='s0', capabilities=m.capabilities,
            obligation=OBLIGATION, max_nodes=64,
        )
        programs = {tuple(x) for x in generated.get('programs', ())}
        expected_a = ('K-17', 'R-41')
        expected_b = ('K-17', 'R-43')
        assert expected_a in programs and expected_b in programs, generated
        candidates = tuple(c for c in generated['candidates'] if c.steps in {expected_a, expected_b})
        assert len(candidates) == 2, candidates

        before_intents = len(m.action_closure.intents)
        before_exec = len(m.action_closure.executions)
        result = m.arbitrate_endogenous_epistemic_trial_candidates(
            candidates, deficit_id='D', decision_context=dc, obligation=OBLIGATION,
        )
        assert result['status'] == 'MULTIPLE_CURRENT_EPISTEMIC_OPPORTUNITIES', result
        assert result['reason'] == 'NO_UNIQUE_STRICT_PARTITION_REFINEMENT'
        assert result['selection_authority'] == result['execution_authority'] == result['truth_authority'] == 'NONE'
        assert len(result['candidate_ids']) == 2
        assert len(m.action_closure.intents) == before_intents
        assert len(m.action_closure.executions) == before_exec
        assert calls == []
        return {
            'status': 'PASS',
            'programs': [list(x) for x in sorted(programs)],
            'arbitration_status': result['status'],
            'arbitration_reason': result['reason'],
            'candidate_ids': list(result['candidate_ids']),
            'partitions': [[cid, [list(block) for block in part]] for cid, part in result['partitions']],
            'selection_authority': result['selection_authority'],
            'execution_authority': result['execution_authority'],
            'truth_authority': result['truth_authority'],
            'caller_order_selection': 'NO',
        }
    finally:
        _close(td, m)


def run_ms1996() -> dict[str, object]:
    left = run_unique(('P1', 'P2', 'N1', 'N2'))
    right = run_unique(('N2', 'P2', 'N1', 'P1'))
    assert left['generated_program'] == right['generated_program'] == list(MAIN)
    assert left['candidate_id'] == right['candidate_id']
    assert left['candidate_sha256'] == right['candidate_sha256']
    assert left['intents_added_during_generation_and_arbitration'] == right['intents_added_during_generation_and_arbitration'] == 0
    assert left['executions_added_during_generation_and_arbitration'] == right['executions_added_during_generation_and_arbitration'] == 0
    tie = run_tie()
    return {
        'status': 'BOUNDARY_CONFIRMED',
        'left': left,
        'right': right,
        'tie': tie,
        'caller_supplied_program_sequence': 'NO',
        'caller_supplied_preferred_action': 'NO',
        'history_insertion_order_selection': 'NO',
        'stale_primitive_policy': 'REGENERATE_CURRENT_SURFACE_AND_ABSTAIN',
        'earned': 'OWNED_OPAQUE_HISTORY_PLUS_CURRENT_QUALIFIED_EFFECT_CONTRACTS_CAN_GENERATE_AND_ARBITRATE_DECISION_BEARING_PROGRAM_CANDIDATES_WITHOUT_CALLER_NAMED_ACTION_OR_PROGRAM_CHOICE_WHILE_PRESERVING_INSERTION_ORDER_CURRENTNESS_BUDGET_TIE_AND_EXECUTION_AUTHORITY_BOUNDARIES',
        'new_core_mechanism_required': 'NO',
        'candidate_construction_authority': 'PROPOSAL_ONLY_EPHEMERAL',
        'selection_authority': 'NONE_UNLESS_UNIQUE_STRICT_PARTITION_REFINEMENT',
        'execution_authority': 'NONE',
        'truth_authority': 'NONE',
        'semantic_action_authority': 'NONE',
        'remaining_boundary': 'RICH_WORLD_LIFETIME_COMPOSITION_AND_MANY_REFERENT_SCALING',
    }


def main() -> None:
    print(json.dumps(run_ms1996(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
