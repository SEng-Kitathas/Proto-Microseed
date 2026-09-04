
from __future__ import annotations

import importlib.util
from pathlib import Path
import types

from microseed import FeasibilityState


def _m():
    path = Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec = importlib.util.spec_from_file_location('_c_scale_ms2063', path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _execute_top(m, fx, raw, tag):
    p = m.current_proposal(fx, raw, tag)
    assert p is not None
    intent = fx['ms'].nominate_bounded_action_intent(p.proposal_id, m.act_ob())
    assert intent['status'] == 'ACTION_INTENT_NOMINATED'
    ex = fx['ms'].execute_bounded_action(intent['intent']['intent_id'], m.act_ob())
    assert ex['status'] == 'ACTION_EXECUTED'
    return p, intent, ex


def _install_nested_middle(m, top_fx, middle_fx):
    top_world = top_fx['world']
    middle_ms = middle_fx['ms']
    middle_world = middle_fx['world']
    log = []
    counter = {'n': 0}

    def nested_request(self, target):
        target = str(target)
        f = self.target_feasibility(target)
        if f != FeasibilityState.FEASIBLE:
            receipt = {'status': f.value, 'target': target, 'nested': True}
            self.receipts.append(receipt)
            return receipt
        top_idx = self.targets.index(target)
        # This mapping is the explicit assistance ceiling: L2's opaque request
        # determines an L1 current context, but it does NOT specify L0's action.
        middle_raw = (
            ('MID-N0', 'H0', 'C0', 'MID-M0') if top_idx == 0
            else ('MID-N1', 'H0', 'C1', 'MID-M1')
        )
        tag = f'NESTED-{counter["n"]}-{top_idx}'
        counter['n'] += 1
        before_mid_intents = len(middle_ms.action_closure.intents)
        before_mid_exec = len(middle_ms.action_closure.executions)
        before_leaf_receipts = len(middle_world.receipts)
        proposal = m.current_proposal(middle_fx, middle_raw, tag)
        if proposal is None:
            self.last_next = 'HIGHER-BAD'; self.last_effect = -2.0
            receipt = {'status': 'REFUSED', 'target': target, 'nested': True, 'reason': 'MIDDLE_NO_CURRENT_PROPOSAL'}
            self.receipts.append(receipt)
            log.append({'top_target': target, 'top_idx': top_idx, 'middle_proposal': None})
            return receipt
        # The middle controller, not L2/harness, chooses the leaf bound request.
        mid_intent = middle_ms.nominate_bounded_action_intent(proposal.proposal_id, m.act_ob())
        if mid_intent['status'] != 'ACTION_INTENT_NOMINATED':
            self.last_next = 'HIGHER-BAD'; self.last_effect = -2.0
            receipt = {'status': 'REFUSED', 'target': target, 'nested': True, 'reason': 'MIDDLE_ABSTAIN'}
            self.receipts.append(receipt)
            log.append({'top_target': target, 'top_idx': top_idx, 'middle_proposal': proposal.proposal_id, 'middle_intent_status': mid_intent['status']})
            return receipt
        mid_ex = middle_ms.execute_bounded_action(mid_intent['intent']['intent_id'], m.act_ob())
        assert mid_ex['status'] == 'ACTION_EXECUTED'
        leaf_receipt = mid_ex['handler_value']
        assert len(middle_ms.action_closure.intents) == before_mid_intents + 1
        assert len(middle_ms.action_closure.executions) == before_mid_exec + 1
        assert len(middle_world.receipts) == before_leaf_receipts + 1
        assert proposal.sequence == (middle_fx['bound'][top_idx].capability_id,)
        assert leaf_receipt['target'] == middle_fx['target_tokens'][top_idx]
        assert middle_world.last_effect == 2.0

        wanted = self.class_index()
        good = wanted is not None and top_idx == wanted
        self.last_next = 'HIGHER-GOOD' if good else 'HIGHER-BAD'
        self.last_effect = 2.0 if good else -2.0
        # L2 sees only an opaque L1 receipt. L0 target/local means remain in the
        # separate red-team log, not in the handler surface returned to L2.
        receipt = {
            'status': 'WORKABLE', 'target': target, 'nested': True,
            'child_state': self.child_state, 'local_mean': 'OPAQUE-MIDDLE-CONTROLLER',
            'higher_context': self.higher,
        }
        self.receipts.append(receipt)
        log.append({
            'top_target': target, 'top_idx': top_idx,
            'middle_raw': list(middle_raw),
            'middle_proposal_id': proposal.proposal_id,
            'middle_capability_id': proposal.sequence[0],
            'leaf_target': leaf_receipt['target'],
            'leaf_local_mean': leaf_receipt['local_mean'],
            'middle_effect': middle_world.last_effect,
            'top_effect': self.last_effect,
        })
        return receipt

    top_world.request = types.MethodType(nested_request, top_world)
    return log


def test_two_canonical_two_level_controllers_compose_into_one_bounded_three_level_execution_chain():
    m = _m()
    flat = m.build_integrated()
    top = m.build_integrated()
    middle = m.build_integrated()
    try:
        # Flattened OARR control: the ordinary two-level handler produces the same
        # top request choices/effects for the two learned query classes.
        flat_rows = [('F0','H0','C0','FM0'), ('F1','H0','C1','FM1')]
        flat_obs = []
        for idx, raw in enumerate(flat_rows):
            p, _, ex = _execute_top(m, flat, raw, f'FLAT-{idx}')
            flat_obs.append((p.sequence[0], ex['handler_value']['target'], flat['world'].last_effect))
        assert [x[2] for x in flat_obs] == [2.0, 2.0]

        nested_log = _install_nested_middle(m, top, middle)
        top_rows = [('T0','H0','C0','TM0'), ('T1','H0','C1','TM1')]
        top_intents_before = len(top['ms'].action_closure.intents)
        top_exec_before = len(top['ms'].action_closure.executions)
        for idx, raw in enumerate(top_rows):
            p, _, ex = _execute_top(m, top, raw, f'TOP-{idx}')
            assert p.sequence == (top['bound'][idx].capability_id,)
            assert ex['handler_value']['target'] == top['target_tokens'][idx]
            assert ex['handler_value']['local_mean'] == 'OPAQUE-MIDDLE-CONTROLLER'
            assert 'leaf_target' not in ex['handler_value']
            assert 'leaf_local_mean' not in ex['handler_value']
            assert top['world'].last_effect == flat_obs[idx][2] == 2.0
        assert len(top['ms'].action_closure.intents) == top_intents_before + 2
        assert len(top['ms'].action_closure.executions) == top_exec_before + 2
        assert len(nested_log) == 2
        assert [x['top_idx'] for x in nested_log] == [0, 1]
        assert [x['leaf_target'] for x in nested_log] == list(middle['target_tokens'])
        assert {x['leaf_local_mean'] for x in nested_log}.issubset({'M0','M1'})
        assert all(x['middle_effect'] == x['top_effect'] == 2.0 for x in nested_log)

        # Separate registries own their own executable contracts even when some
        # content-addressed capability IDs happen to be numerically equal.
        for cid in middle['cap_ids']:
            assert middle['ms'].capabilities.contracts[cid] is not top['ms'].capabilities.contracts[cid]
        for ms in (top['ms'], middle['ms']):
            assert not hasattr(ms, 'hierarchy_manager')
            assert not hasattr(ms, 'parent_manager')
            assert not hasattr(ms, 'desired_state_registry')
    finally:
        flat['td'].cleanup(); top['td'].cleanup(); middle['td'].cleanup()


def test_middle_refusal_blocks_leaf_execution_without_giving_top_leaf_choice_authority():
    m = _m()
    top = m.build_integrated()
    middle = m.build_integrated()
    try:
        nested_log = _install_nested_middle(m, top, middle)
        middle['world'].set_feasibility(middle['target_tokens'][0], FeasibilityState.REFUSED)
        leaf_receipts_before = len(middle['world'].receipts)
        p, _, ex = _execute_top(m, top, ('R0','H0','C0','RM0'), 'TOP-REFUSE')
        assert p.sequence == (top['bound'][0].capability_id,)
        assert ex['handler_value']['status'] == 'REFUSED'
        assert ex['handler_value']['reason'] == 'MIDDLE_ABSTAIN'
        assert top['world'].last_effect == -2.0
        assert len(middle['world'].receipts) == leaf_receipts_before
        assert nested_log[-1]['middle_proposal'] is not None
        assert nested_log[-1]['middle_intent_status'] == 'ABSTAIN'
        # Top request execution occurred; leaf execution did not. This is ordinary
        # subordinate refusal, not upward transfer of leaf execution authority.
        assert len(top['ms'].action_closure.executions) >= 1
    finally:
        top['td'].cleanup(); middle['td'].cleanup()
