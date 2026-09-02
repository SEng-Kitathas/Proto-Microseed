
from __future__ import annotations

import importlib.util
from pathlib import Path
import types

from microseed import FeasibilityState


def _ms2063():
    path = Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec = importlib.util.spec_from_file_location('_frontier_ms2063_fixture', path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _install_hidden_phenotype(world, *, preserve_effect: bool) -> None:
    def request(self, target):
        target = str(target)
        f = self.target_feasibility(target)
        if f != FeasibilityState.FEASIBLE:
            receipt = {'status': f.value, 'target': target, 'child_state': self.child_state, 'local_mean': None}
            self.receipts.append(receipt)
            return receipt
        idx = self.targets.index(target)
        child_bit = 0 if self.child_state == 'C0' else 1
        # Deliberately different subordinate-local phenotype from the MS2063 fixture.
        mean = 'Z0' if idx == child_bit else 'Z1'
        wanted = self.class_index()
        good = wanted is not None and idx == wanted
        if preserve_effect:
            self.last_next = 'HIGHER-GOOD' if good else 'HIGHER-BAD'
            self.last_effect = 2.0 if good else -2.0
        else:
            # Same request handle/metadata and same target, but the hidden child
            # phenotype now produces the opposite higher-level consequence.
            self.last_next = 'HIGHER-BAD' if good else 'HIGHER-GOOD'
            self.last_effect = -2.0 if good else 2.0
        receipt = {
            'status': 'WORKABLE', 'target': target, 'child_state': self.child_state,
            'local_mean': mean, 'higher_context': self.higher,
            'hidden_phenotype': 'V2-PRESERVE' if preserve_effect else 'V2-FLIP',
        }
        self.receipts.append(receipt)
        return receipt
    world.request = types.MethodType(request, world)


def _current_relation_for_phase1(fx):
    # Phase-1 contexts are class-1, therefore target/capability index 1 is the
    # currently useful request under the qualified routing.
    cid = fx['cap_ids'][1]
    rid = fx['new_rel'][cid]
    return cid, rid


def test_hidden_effect_preserving_subordinate_swap_needs_no_identity_primitive() -> None:
    m = _ms2063()
    fx = m.build_integrated(); ms = fx['ms']; world = fx['world']
    try:
        cid, rid = _current_relation_for_phase1(fx)
        base_sig = ms.capabilities.contracts['REQ-BASE'].computed_signature_sha256()
        bound_sig = ms.capabilities.contracts[cid].computed_signature_sha256()
        assert ms.action_outcome_predictive_relation_status(rid)['status'] == 'CURRENT_PREDICTIVE_RELATION'
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status'] == 'CURRENT_PROJECTION_CONDITIONED_ROUTING'

        _install_hidden_phenotype(world, preserve_effect=True)
        before = len(world.receipts)
        for i, raw in enumerate(m.phase_rows(1, 16), start=3000):
            receipt, _ = m.execute_episode(ms, world, cid, raw, i)
            assert receipt['local_mean'] in {'Z0', 'Z1'}
            assert receipt['hidden_phenotype'] == 'V2-PRESERVE'
        assert len(world.receipts) > before

        # Parent-visible operational premises did not change.
        assert ms.capabilities.contracts['REQ-BASE'].computed_signature_sha256() == base_sig
        assert ms.capabilities.contracts[cid].computed_signature_sha256() == bound_sig
        witness = ms.assess_action_outcome_predictive_currentness(rid)
        assert witness['status'] == 'CURRENT_WITHIN_BOUNDS'
        assert witness['witness']['window_accuracies'] == [1.0, 1.0]
        assert ms.action_outcome_predictive_relation_status(rid)['status'] == 'CURRENT_PREDICTIVE_RELATION'
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status'] == 'CURRENT_PROJECTION_CONDITIONED_ROUTING'
        assert not hasattr(ms, 'subordinate_identity_registry')
    finally:
        fx['td'].cleanup()


def test_hidden_effect_changing_swap_is_not_preobservable_but_actual_outcomes_stale_relation() -> None:
    m = _ms2063()
    fx = m.build_integrated(); ms = fx['ms']; world = fx['world']
    try:
        cid, rid = _current_relation_for_phase1(fx)
        base_sig = ms.capabilities.contracts['REQ-BASE'].computed_signature_sha256()
        bound_sig = ms.capabilities.contracts[cid].computed_signature_sha256()
        # Hidden replacement alone cannot be observed through any owned premise.
        _install_hidden_phenotype(world, preserve_effect=False)
        assert ms.capabilities.contracts['REQ-BASE'].computed_signature_sha256() == base_sig
        assert ms.capabilities.contracts[cid].computed_signature_sha256() == bound_sig
        assert ms.action_outcome_predictive_relation_status(rid)['status'] == 'CURRENT_PREDICTIVE_RELATION'
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status'] == 'CURRENT_PROJECTION_CONDITIONED_ROUTING'

        # Actual post-swap outcomes supply the missing reality contact. Two full
        # eight-row failure windows are enough for the existing empirical owner.
        for i, raw in enumerate(m.phase_rows(1, 16), start=4000):
            receipt, _ = m.execute_episode(ms, world, cid, raw, i)
            assert receipt['hidden_phenotype'] == 'V2-FLIP'
            assert receipt['local_mean'] in {'Z0', 'Z1'}
        witness = ms.assess_action_outcome_predictive_currentness(rid)
        assert witness['status'] == 'DRIFT_WITNESS'
        assert witness['witness']['window_accuracies'] == [0.0, 0.0]
        assert witness['witness']['drift_cause_authority'] == 'NONE'
        status = ms.action_outcome_predictive_relation_status(rid)
        assert status['status'] == 'STALE_PREDICTIVE_RELATION'
        assert status['reason'] == 'EMPIRICAL_DRIFT_WITNESS'
        # The evidence says the relation is stale; it does not identify a child,
        # phenotype, regime, or replacement cause.
        replacements = ms.nominate_action_outcome_replacement_candidates(
            rid, witness['witness']['witness_id']
        )
        assert len(replacements) == 1
        assert replacements[0].capability_id == cid
    finally:
        fx['td'].cleanup()


def test_explicit_request_channel_dependency_drift_stales_immediately_before_new_outcome() -> None:
    m = _ms2063()
    fx = m.build_integrated(); ms = fx['ms']
    try:
        cid, rid = _current_relation_for_phase1(fx)
        assert ms.action_outcome_predictive_relation_status(rid)['status'] == 'CURRENT_PREDICTIVE_RELATION'
        stale = ms.change_capability_dependency('REQ-BASE', reason='FRONTIER-B-OBSERVABLE-REQUEST-CHANNEL-DRIFT')
        assert cid in stale
        rel = ms.action_outcome_predictive_relation_status(rid)
        assert rel['status'] == 'STALE_PREDICTIVE_RELATION'
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status'] == 'STALE_PROJECTION_CONDITIONED_ROUTING'
    finally:
        fx['td'].cleanup()
