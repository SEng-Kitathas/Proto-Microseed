from __future__ import annotations

import importlib.util
import random
import types
from pathlib import Path


def _load(name: str):
    path = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(f"_c_scale_03b_{path.stem}", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _new_top_interface(m):
    td, ms, world = m.new_ms()
    m.register_runtime(ms, world)
    target_rec, target_candidate, target_tokens = m.learn_target_projection(ms)
    bound = m.derive_bound_requests(ms, world, target_rec, target_tokens)
    cap_ids = tuple(x.capability_id for x in bound)
    assert not ms.action_outcome_learning.relations
    assert not ms.action_outcome_learning.projection_conditioned_bindings
    return {
        "td": td,
        "ms": ms,
        "world": world,
        "target_rec": target_rec,
        "target_candidate": target_candidate,
        "target_tokens": tuple(target_tokens),
        "bound": tuple(bound),
        "cap_ids": cap_ids,
    }


def _signal_phase_rows(signal_tokens, kind: int, n: int = 16):
    s0, s1 = signal_tokens
    base = (
        (("SN0", s0, "C0", "SM0"), ("SN1", s1, "C1", "SM1"))
        if kind == 0
        else (("SN2", s0, "C1", "SM2"), ("SN3", s1, "C0", "SM3"))
    )
    return tuple(base[i % 2] for i in range(n))


def _new_signal_middle_world(m, signal_tokens):
    signal_tokens = tuple(signal_tokens)
    assert len(signal_tokens) == 2 and signal_tokens[0] != signal_tokens[1]

    class SignalMiddleWorld(m.TwoLevelWorld):
        def __init__(self):
            super().__init__()
            self.signal_tokens = signal_tokens

        def class_index(self):
            sb = {self.signal_tokens[0]: 0, self.signal_tokens[1]: 1}.get(self.higher)
            cb = {"C0": 0, "C1": 1}.get(self.child_state)
            if sb is None or cb is None:
                return None
            return sb ^ cb

    return SignalMiddleWorld()


def _discover_signal_context_projection(m, ms, signal_tokens):
    owned = ms.derive_admitted_projection_samples_from_owned_raw_observations()
    assert owned["status"] == "ADMITTED_OWNED_RAW_PROJECTION_SAMPLES"
    assert owned["sample_count"] >= 64
    assert not owned["receipt_rejections"] and not owned["sample_rejections"]

    # Research split is invariant to opaque sample IDs and excludes effect_token.
    rows = sorted(
        owned["samples"],
        key=lambda x: (
            tuple(x.raw_tokens),
            x.action_token,
            x.operational_scope_id,
            x.frame_id,
            x.frame_epoch,
            tuple(x.source_projection_epochs),
        ),
    )
    random.Random(2063001).shuffle(rows)
    found = ms.discover_epistemic_projection_candidates(
        tuple(rows[:44]),
        tuple(rows[44:]),
        m.ProjectionDiscoveryConfig(
            max_subset=2,
            min_train_support=32,
            min_key_action_support=4,
            min_validation_accuracy=.95,
            min_lift_over_action_baseline=.35,
            min_scope_accuracy=.90,
            max_candidates=12,
        ),
    )
    assert found
    candidates = [ms.epistemic_projection_candidates[x["candidate_id"]] for x in found]
    exact = [x for x in candidates if x.input_positions == (1, 2)]
    assert len(exact) == 1, [(x.input_positions, x.validation_accuracy, x.lift) for x in candidates]
    candidate = exact[0]
    assert candidate.validation_accuracy >= .99

    q = ms.append_evidence(
        "C-SCALE-03B-MIDDLE-SIGNAL-PROJ-QUAL",
        {
            "kind": "OWNED_RAW_OPAQUE_SIGNAL_CONTEXT_PROJECTION_HOLDOUT",
            "candidate_sha256": candidate.digest(),
            "heldout_contexts": [
                list(x) for x in _signal_phase_rows(signal_tokens, 0, 4) + _signal_phase_rows(signal_tokens, 1, 4)
            ],
            "split_rule": "SEMANTIC_CONTENT_EXCLUDING_EFFECT_LABEL_AND_SAMPLE_ID",
        },
        m.EpistemicStatus.PRESSURE_SUPPORTED,
        source="EXTERNAL-C-SCALE-03B-MIDDLE-SIGNAL-PROJECTION",
    )
    ticket = m.ExternalProjectionQualifier(
        ms.evidence, qualifier_id="EXTERNAL-C-SCALE-03B-MIDDLE-SIGNAL-PROJECTION"
    ).qualify(candidate, qualification_evidence=(q,))
    rec = ms.admit_epistemic_projection_candidate(ticket, projection_id="CTX-P")

    s0, s1 = signal_tokens
    b0 = candidate.project(("NX", s0, "C0", "MX"))
    b1 = candidate.project(("NY", s0, "C1", "MY"))
    assert b0 and b1 and b0 != b1
    assert candidate.project(("NZ", s1, "C1", "MZ")) == b0
    assert candidate.project(("NW", s1, "C0", "MW")) == b1
    return owned, rec, candidate, b0, b1


def _build_middle_from_opaque_top_request_signals(m, signal_tokens):
    td = m.tempfile.TemporaryDirectory(prefix="microseed-c-scale-03b-middle-")
    ms = m.Microseed(m.Path(td.name))
    world = _new_signal_middle_world(m, signal_tokens)
    m.register_runtime(ms, world)

    target_rec, target_candidate, target_tokens = m.learn_target_projection(ms)
    bound = m.derive_bound_requests(ms, world, target_rec, target_tokens)
    cap_ids = tuple(x.capability_id for x in bound)

    # Hard control: the middle begins with no learned request/effect law and no
    # signal-conditioned routing.  The only cross-level input available later is
    # the opaque top request token itself.
    assert not ms.action_outcome_learning.relations
    assert not ms.action_outcome_learning.projection_conditioned_bindings

    idx = 0
    for cid in cap_ids:
        for raw in _signal_phase_rows(signal_tokens, 0, 16):
            m.execute_episode(ms, world, cid, raw, 30000 + idx)
            idx += 1
    initial = ms.nominate_action_outcome_predictive_candidates(min_support=8, min_consistency=.78)
    assert {x.capability_id for x in initial} == set(cap_ids)
    old_rel = m.qualify_candidates(ms, initial, "C-SCALE-03B-MIDDLE-OLD")

    for cid in cap_ids:
        for raw in _signal_phase_rows(signal_tokens, 1, 16):
            m.execute_episode(ms, world, cid, raw, 30000 + idx)
            idx += 1

    new_rel = {}
    for cid in cap_ids:
        old_id = old_rel[cid]
        witness = ms.assess_action_outcome_predictive_currentness(old_id)
        assert witness["status"] == "DRIFT_WITNESS", witness
        replacements = ms.nominate_action_outcome_replacement_candidates(old_id, witness["witness"]["witness_id"])
        assert len(replacements) == 1 and replacements[0].capability_id == cid
        new_rel.update(m.qualify_candidates(ms, replacements, f"C-SCALE-03B-MIDDLE-NEW-{cid[-6:]}"))

    owned, ctx_rec, ctx_candidate, b0, b1 = _discover_signal_context_projection(m, ms, signal_tokens)
    routing_id = m.qualify_routing(ms, ctx_rec, b0, b1, cap_ids, old_rel, new_rel)
    assert ms.projection_conditioned_relation_routing_status(routing_id)["status"] == "CURRENT_PROJECTION_CONDITIONED_ROUTING"

    return {
        "td": td,
        "ms": ms,
        "world": world,
        "signal_tokens": tuple(signal_tokens),
        "target_rec": target_rec,
        "target_candidate": target_candidate,
        "target_tokens": tuple(target_tokens),
        "bound": tuple(bound),
        "cap_ids": cap_ids,
        "old_rel": old_rel,
        "new_rel": new_rel,
        "ctx_rec": ctx_rec,
        "ctx_candidate": ctx_candidate,
        "bucket0": b0,
        "bucket1": b1,
        "routing_id": routing_id,
        "owned": owned,
    }


def _install_direct_opaque_signal_middle(m, top, middle):
    top_world = top["world"]
    middle_ms = middle["ms"]
    middle_world = middle["world"]
    selected_by_bucket = {}
    counter = {"n": 0}
    log = []

    def nested_request(self, target):
        target = str(target)
        f = self.target_feasibility(target)
        if f != m.FeasibilityState.FEASIBLE:
            receipt = {"status": f.value, "target": target, "nested": True}
            self.receipts.append(receipt)
            return receipt
        assert target in middle["signal_tokens"]

        n = counter["n"]
        counter["n"] += 1
        child_state = "C0" if (n % 2) == 0 else "C1"

        # No token->context lookup table: the exact opaque request token is the
        # middle's observed signal coordinate.  Only local child state is added.
        middle_raw = (f"RUN-N-{n}", target, child_state, f"RUN-M-{n}")
        bucket = middle["ctx_candidate"].project(middle_raw)
        assert bucket in (middle["bucket0"], middle["bucket1"])

        if bucket not in selected_by_bucket:
            proposal = m.current_proposal(middle, middle_raw, f"03B-MIDDLE-SELECT-{len(selected_by_bucket)}")
            if proposal is None:
                self.last_next = "HIGHER-BAD"
                self.last_effect = -2.0
                receipt = {
                    "status": "REFUSED",
                    "target": target,
                    "nested": True,
                    "reason": "MIDDLE_NO_CURRENT_SIGNAL_RESPONSE",
                }
                self.receipts.append(receipt)
                return receipt
            selected_by_bucket[bucket] = proposal.sequence[0]

        cid = selected_by_bucket[bucket]
        assert middle_ms.capabilities.is_current(cid)
        leaf_receipt, outcome = m.execute_episode(
            middle_ms, middle_world, cid, middle_raw, 50000 + n
        )
        assert outcome["status"] == "ACTION_OUTCOME_OBSERVED"
        assert middle_world.last_effect == 2.0

        top_idx = self.targets.index(target)
        wanted = self.class_index()
        good = wanted is not None and top_idx == wanted
        self.last_next = "HIGHER-GOOD" if good else "HIGHER-BAD"
        self.last_effect = 2.0 if good else -2.0

        receipt = {
            "status": "WORKABLE",
            "target": target,
            "nested": True,
            "child_state": self.child_state,
            "local_mean": "OPAQUE-MIDDLE-SIGNAL-RESPONSE",
            "higher_context": self.higher,
        }
        self.receipts.append(receipt)
        log.append(
            {
                "top_target": target,
                "transported_signal": middle_raw[1],
                "middle_child_state": child_state,
                "middle_raw": list(middle_raw),
                "middle_projection_bucket": bucket,
                "middle_capability_id": cid,
                "leaf_target": leaf_receipt["target"],
                "leaf_local_mean": leaf_receipt["local_mean"],
                "middle_effect": middle_world.last_effect,
                "top_effect": self.last_effect,
            }
        )
        return receipt

    top_world.request = types.MethodType(nested_request, top_world)
    return log


def _grow_top_policy_after_direct_signal_binding(g, m, top):
    ms = top["ms"]
    world = top["world"]
    cap_ids = top["cap_ids"]
    idx = 0

    assert not ms.action_outcome_learning.relations
    assert not ms.action_outcome_learning.projection_conditioned_bindings

    for cid in cap_ids:
        for raw in m.phase_rows(0, 16):
            m.execute_episode(ms, world, cid, raw, 60000 + idx)
            idx += 1
    initial = ms.nominate_action_outcome_predictive_candidates(min_support=8, min_consistency=.78)
    assert {x.capability_id for x in initial} == set(cap_ids)
    old_rel = m.qualify_candidates(ms, initial, "C-SCALE-03B-TOP-OLD")

    for cid in cap_ids:
        for raw in m.phase_rows(1, 16):
            m.execute_episode(ms, world, cid, raw, 60000 + idx)
            idx += 1
    new_rel = {}
    for cid in cap_ids:
        old_id = old_rel[cid]
        witness = ms.assess_action_outcome_predictive_currentness(old_id)
        assert witness["status"] == "DRIFT_WITNESS", witness
        replacements = ms.nominate_action_outcome_replacement_candidates(old_id, witness["witness"]["witness_id"])
        assert len(replacements) == 1 and replacements[0].capability_id == cid
        new_rel.update(m.qualify_candidates(ms, replacements, f"C-SCALE-03B-TOP-NEW-{cid[-6:]}"))

    owned, ctx_rec, ctx_candidate, b0, b1 = g._discover_context_projection_sample_id_invariant(m, ms)
    routing_id = m.qualify_routing(ms, ctx_rec, b0, b1, cap_ids, old_rel, new_rel)
    top.update(
        {
            "old_rel": old_rel,
            "new_rel": new_rel,
            "ctx_rec": ctx_rec,
            "ctx_candidate": ctx_candidate,
            "bucket0": b0,
            "bucket1": b1,
            "routing_id": routing_id,
            "owned": owned,
        }
    )
    return top


def _execute_current_top(m, top, raw, tag):
    proposal = m.current_proposal(top, raw, tag)
    assert proposal is not None
    intent = top["ms"].nominate_bounded_action_intent(proposal.proposal_id, m.act_ob())
    assert intent["status"] == "ACTION_INTENT_NOMINATED"
    execution = top["ms"].execute_bounded_action(intent["intent"]["intent_id"], m.act_ob())
    assert execution["status"] == "ACTION_EXECUTED"
    return proposal, execution


def test_middle_learns_opaque_top_request_response_binding_without_evaluator_context_map():
    c = _load("test_frontier_c_scale_nested_three_level_execution.py")
    g = _load("test_frontier_c_scale_top_growth_through_learned_middle.py")
    m = c._m()
    top = _new_top_interface(m)
    middle = None
    try:
        # Top request tokens exist as opaque interface symbols, but top policy is
        # still unlearned when the middle develops its response law.
        assert not top["ms"].action_outcome_learning.relations
        middle = _build_middle_from_opaque_top_request_signals(m, top["target_tokens"])
        assert not top["ms"].action_outcome_learning.relations
        assert middle["ctx_candidate"].input_positions == (1, 2)
        assert middle["ctx_candidate"].validation_accuracy == 1.0

        nested_log = _install_direct_opaque_signal_middle(m, top, middle)
        _grow_top_policy_after_direct_signal_binding(g, m, top)

        assert top["ms"].projection_conditioned_relation_routing_status(top["routing_id"])["status"] == "CURRENT_PROJECTION_CONDITIONED_ROUTING"
        assert len(nested_log) == 64
        assert all(row["transported_signal"] == row["top_target"] for row in nested_log)
        assert all(row["middle_raw"][1] == row["top_target"] for row in nested_log)
        assert all(row["middle_effect"] == 2.0 for row in nested_log)
        assert all("leaf_target" in row and "leaf_local_mean" in row for row in nested_log)

        # Execute through the learned top after both levels' policies are current.
        p0, x0 = _execute_current_top(m, top, ("Q0", "H0", "C0", "QM0"), "03B-Q0")
        p1, x1 = _execute_current_top(m, top, ("Q1", "H0", "C1", "QM1"), "03B-Q1")
        assert p0.sequence == (top["bound"][0].capability_id,)
        assert p1.sequence == (top["bound"][1].capability_id,)
        assert x0["handler_value"]["target"] == top["target_tokens"][0]
        assert x1["handler_value"]["target"] == top["target_tokens"][1]
        assert x0["handler_value"]["local_mean"] == "OPAQUE-MIDDLE-SIGNAL-RESPONSE"
        assert x1["handler_value"]["local_mean"] == "OPAQUE-MIDDLE-SIGNAL-RESPONSE"
        assert "leaf_target" not in x0["handler_value"] and "leaf_local_mean" not in x0["handler_value"]
        assert "leaf_target" not in x1["handler_value"] and "leaf_local_mean" not in x1["handler_value"]

        # No hierarchy/binding manager was added.  The middle's admitted projection
        # and routing are the learned operational binding.
        for ms in (top["ms"], middle["ms"]):
            assert not hasattr(ms, "hierarchy_manager")
            assert not hasattr(ms, "request_context_map")
            assert not hasattr(ms, "signal_meaning_registry")
            assert not hasattr(ms, "desired_state_registry")
    finally:
        if middle is not None:
            middle["td"].cleanup()
        top["td"].cleanup()


def test_direct_opaque_transport_and_middle_learning_do_not_promote_meaning_or_full_codevelopment():
    c = _load("test_frontier_c_scale_nested_three_level_execution.py")
    g = _load("test_frontier_c_scale_top_growth_through_learned_middle.py")
    m = c._m()
    top = _new_top_interface(m)
    middle = None
    try:
        middle = _build_middle_from_opaque_top_request_signals(m, top["target_tokens"])
        nested_log = _install_direct_opaque_signal_middle(m, top, middle)
        _grow_top_policy_after_direct_signal_binding(g, m, top)

        # The top tokens are physically transported unchanged; their response law is
        # learned by the middle.  This is not token meaning/reference and the direct
        # transport channel itself is still supplied by the harness.
        assert middle["signal_tokens"] == top["target_tokens"]
        assert all(row["transported_signal"] in top["target_tokens"] for row in nested_log)
        assert middle["ctx_candidate"].input_positions == (1, 2)
        assert middle["routing_id"] in middle["ms"].action_outcome_learning.projection_conditioned_bindings
        assert top["routing_id"] in top["ms"].action_outcome_learning.projection_conditioned_bindings

        # Unknown signal does not acquire a caller fallback or invented meaning.
        assert m.current_proposal(
            middle, ("UNK-N", "UNSEEN-OPAQUE-SIGNAL", "C0", "UNK-M"), "03B-UNSEEN"
        ) is None

        for ms in (top["ms"], middle["ms"]):
            assert not hasattr(ms, "signal_meaning_registry")
            assert not hasattr(ms, "reference_store")
            assert not hasattr(ms, "semantic_goal_registry")
            assert not hasattr(ms, "hierarchy_manager")

        # Development remains staged: signal tokens/interface existed first; the
        # middle learned the response binding next; only then did the top policy grow.
        assert len(nested_log) == 64
    finally:
        if middle is not None:
            middle["td"].cleanup()
        top["td"].cleanup()



def test_middle_opaque_signal_binding_survives_convention_reversal():
    c = _load("test_frontier_c_scale_nested_three_level_execution.py")
    m = c._m()
    top = _new_top_interface(m)
    middle = None
    try:
        # Reverse the externally observable opaque-token convention before the
        # middle learns.  Nothing downstream may assume token 0/1 carries fixed
        # semantic meaning from the top interface ordering.
        reversed_signals = tuple(reversed(top["target_tokens"]))
        middle = _build_middle_from_opaque_top_request_signals(m, reversed_signals)
        assert middle["signal_tokens"] == reversed_signals
        assert middle["signal_tokens"] != top["target_tokens"]

        raw_class0 = ("REV-N0", reversed_signals[0], "C0", "REV-M0")
        raw_class1 = ("REV-N1", reversed_signals[1], "C0", "REV-M1")
        assert middle["ctx_candidate"].project(raw_class0) == middle["bucket0"]
        assert middle["ctx_candidate"].project(raw_class1) == middle["bucket1"]

        p0 = m.current_proposal(middle, raw_class0, "03B-REV-0")
        p1 = m.current_proposal(middle, raw_class1, "03B-REV-1")
        assert p0 is not None and p1 is not None
        assert p0.sequence == (middle["bound"][0].capability_id,)
        assert p1.sequence == (middle["bound"][1].capability_id,)
        assert p0.predicted_step_value_effects == (2.0,)
        assert p1.predicted_step_value_effects == (2.0,)

        # A signal outside the learned opaque alphabet does not inherit a default
        # response or guessed meaning.
        assert m.current_proposal(
            middle,
            ("REV-UNK", "UNSEEN-OPAQUE-SIGNAL", "C0", "REV-UNK-M"),
            "03B-REV-UNKNOWN",
        ) is None

        assert not hasattr(middle["ms"], "signal_meaning_registry")
        assert not hasattr(middle["ms"], "request_context_map")
    finally:
        if middle is not None:
            middle["td"].cleanup()
        top["td"].cleanup()
