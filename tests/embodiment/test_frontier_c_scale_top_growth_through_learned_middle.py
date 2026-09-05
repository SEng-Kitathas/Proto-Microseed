from __future__ import annotations

import importlib.util
from pathlib import Path
import types
import random
from collections import Counter


def _load(name: str):
    path = Path(__file__).with_name(name)
    spec = importlib.util.spec_from_file_location(f"_c_scale_growth_{path.stem}", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _install_repeated_growth_middle(c, m, top, middle):
    """Repeated nested execution path with one current selection per middle class.

    C_SCALE's original nested helper is intentionally one-shot per class.  For
    developmental sampling we preserve its authority boundary but reuse SH1's
    lawful pattern: select a current middle capability once, then execute unique
    episodes to gather actual outcomes.  This avoids duplicate deterministic
    rehearsal IDs without weakening the registry.
    """
    top_world = top["world"]
    middle_ms = middle["ms"]
    middle_world = middle["world"]
    selected = {}
    counter = {"n": 0}
    log = []

    def nested_request(self, target):
        target = str(target)
        f = self.target_feasibility(target)
        if f != c.FeasibilityState.FEASIBLE:
            receipt = {"status": f.value, "target": target, "nested": True}
            self.receipts.append(receipt)
            return receipt

        top_idx = self.targets.index(target)
        middle_raw = (
            ("MID-N0", "H0", "C0", "MID-M0")
            if top_idx == 0
            else ("MID-N1", "H0", "C1", "MID-M1")
        )

        if top_idx not in selected:
            proposal = m.current_proposal(middle, middle_raw, f"GROW-MID-SELECT-{top_idx}")
            if proposal is None:
                self.last_next = "HIGHER-BAD"
                self.last_effect = -2.0
                receipt = {
                    "status": "REFUSED",
                    "target": target,
                    "nested": True,
                    "reason": "MIDDLE_NO_CURRENT_PROPOSAL",
                }
                self.receipts.append(receipt)
                return receipt
            selected[top_idx] = proposal.sequence[0]
            assert selected[top_idx] == middle["bound"][top_idx].capability_id

        cid = selected[top_idx]
        assert middle_ms.capabilities.is_current(cid)
        assert middle_ms.projection_conditioned_relation_routing_status(middle["routing_id"])["status"] == "CURRENT_PROJECTION_CONDITIONED_ROUTING"

        n = counter["n"]
        counter["n"] += 1
        leaf_receipt, outcome = m.execute_episode(middle_ms, middle_world, cid, middle_raw, 20000 + n)
        assert outcome["status"] == "ACTION_OUTCOME_OBSERVED"
        assert leaf_receipt["target"] == middle["target_tokens"][top_idx]
        assert middle_world.last_effect == 2.0

        wanted = self.class_index()
        good = wanted is not None and top_idx == wanted
        self.last_next = "HIGHER-GOOD" if good else "HIGHER-BAD"
        self.last_effect = 2.0 if good else -2.0

        receipt = {
            "status": "WORKABLE",
            "target": target,
            "nested": True,
            "child_state": self.child_state,
            "local_mean": "OPAQUE-MIDDLE-CONTROLLER",
            "higher_context": self.higher,
        }
        self.receipts.append(receipt)
        log.append(
            {
                "top_target": target,
                "top_idx": top_idx,
                "middle_raw": list(middle_raw),
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


def _discover_context_projection_sample_id_invariant(m, ms):
    owned = ms.derive_admitted_projection_samples_from_owned_raw_observations()
    assert owned["status"] == "ADMITTED_OWNED_RAW_PROJECTION_SAMPLES"
    assert owned["sample_count"] >= 64
    assert not owned["receipt_rejections"] and not owned["sample_rejections"]

    # The original MS2063 research harness shuffled the registry-return order.
    # Nested execution changes opaque sample IDs/order without changing the
    # semantic sample multiset.  Make the split invariant to those incidental IDs.
    # Crucially, the ordering key excludes effect_token (the label/outcome).
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
        "C-SCALE-GROWTH-CTX-PROJ-QUAL",
        {
            "kind": "OWNED_RAW_CONTEXT_PROJECTION_HOLDOUT",
            "candidate_sha256": candidate.digest(),
            "heldout_contexts": [list(x) for x in m.phase_rows(0, 4) + m.phase_rows(1, 4)],
            "split_rule": "SEMANTIC_CONTENT_EXCLUDING_EFFECT_LABEL_AND_SAMPLE_ID",
        },
        m.EpistemicStatus.PRESSURE_SUPPORTED,
        source="EXTERNAL-C-SCALE-GROWTH-CTX",
    )
    ticket = m.ExternalProjectionQualifier(
        ms.evidence, qualifier_id="EXTERNAL-C-SCALE-GROWTH-CTX"
    ).qualify(candidate, qualification_evidence=(q,))
    rec = ms.admit_epistemic_projection_candidate(ticket, projection_id="CTX-P")
    b0 = candidate.project(("NX", "H0", "C0", "MX"))
    b1 = candidate.project(("NY", "H0", "C1", "MY"))
    assert b0 and b1 and b0 != b1
    assert candidate.project(("NZ", "H1", "C1", "MZ")) == b0
    assert candidate.project(("NW", "H1", "C0", "MW")) == b1
    return owned, rec, candidate, b0, b1


def _grow_top_through_middle(c, m, middle):
    td, ms, world = m.new_ms()
    m.register_runtime(ms, world)

    # Assistance still exists at the representation/interface boundary: discover and
    # externally qualify the opaque request-token projection, then derive the two
    # bound request specializations.  What is intentionally absent is a learned
    # higher request/effect relation or context-routing binding.
    target_rec, target_candidate, target_tokens = m.learn_target_projection(ms)
    bound = m.derive_bound_requests(ms, world, target_rec, target_tokens)
    cap_ids = tuple(x.capability_id for x in bound)

    top = {
        "td": td,
        "ms": ms,
        "world": world,
        "target_rec": target_rec,
        "target_candidate": target_candidate,
        "target_tokens": target_tokens,
        "bound": bound,
        "cap_ids": cap_ids,
    }
    nested_log = _install_repeated_growth_middle(c, m, top, middle)

    # Hard developmental control: the top has request interfaces but has not yet
    # learned their outcome law or a context-conditioned selector.
    assert not ms.action_outcome_learning.relations
    assert not ms.action_outcome_learning.projection_conditioned_bindings

    idx = 0
    phase0_receipts = []
    for cid in cap_ids:
        for raw in m.phase_rows(0, 16):
            receipt, _ = m.execute_episode(ms, world, cid, raw, idx)
            assert receipt["nested"] is True
            assert receipt["local_mean"] == "OPAQUE-MIDDLE-CONTROLLER"
            assert "leaf_target" not in receipt and "leaf_local_mean" not in receipt
            phase0_receipts.append(receipt)
            idx += 1

    initial = ms.nominate_action_outcome_predictive_candidates(min_support=8, min_consistency=.78)
    assert {x.capability_id for x in initial} == set(cap_ids)
    old_rel = m.qualify_candidates(ms, initial, "C-SCALE-GROWTH-OLD-QUAL")

    # The second lived phase reverses the useful request law at the top boundary.
    # Replacement relations must be earned from these nested outcomes, not copied
    # from a separately trained flat controller.
    phase1_receipts = []
    for cid in cap_ids:
        for raw in m.phase_rows(1, 16):
            receipt, _ = m.execute_episode(ms, world, cid, raw, idx)
            assert receipt["nested"] is True
            phase1_receipts.append(receipt)
            idx += 1

    new_rel = {}
    for cid in cap_ids:
        old_id = old_rel[cid]
        witness = ms.assess_action_outcome_predictive_currentness(old_id)
        assert witness["status"] == "DRIFT_WITNESS", witness
        replacements = ms.nominate_action_outcome_replacement_candidates(old_id, witness["witness"]["witness_id"])
        assert len(replacements) == 1 and replacements[0].capability_id == cid
        new_rel.update(m.qualify_candidates(ms, replacements, f"C-SCALE-GROWTH-NEW-{cid[-6:]}"))
        assert ms.action_outcome_predictive_relation_status(old_id)["status"] == "STALE_PREDICTIVE_RELATION"
        assert ms.action_outcome_predictive_relation_status(new_rel[cid])["status"] == "CURRENT_PREDICTIVE_RELATION"

    # Context projection and routing are then discovered/qualified from the top's
    # own bounded raw observations and top-boundary outcome history.
    owned, ctx_rec, ctx_candidate, b0, b1 = _discover_context_projection_sample_id_invariant(m, ms)
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
            "phase0_receipts": phase0_receipts,
            "phase1_receipts": phase1_receipts,
            "owned": owned,
        }
    )
    return top, nested_log


def _execute_current_top(m, fx, raw, tag):
    proposal = m.current_proposal(fx, raw, tag)
    assert proposal is not None
    intent = fx["ms"].nominate_bounded_action_intent(proposal.proposal_id, m.act_ob())
    assert intent["status"] == "ACTION_INTENT_NOMINATED"
    execution = fx["ms"].execute_bounded_action(intent["intent"]["intent_id"], m.act_ob())
    assert execution["status"] == "ACTION_EXECUTED"
    return proposal, execution


def test_top_request_effect_policy_and_context_routing_can_grow_from_actual_nested_experience():
    c = _load("test_frontier_c_scale_nested_three_level_execution.py")
    m = c._m()
    middle = m.build_integrated()
    top = None
    try:
        top, nested_log = _grow_top_through_middle(c, m, middle)

        assert top["ms"].projection_conditioned_relation_routing_status(top["routing_id"])["status"] == "CURRENT_PROJECTION_CONDITIONED_ROUTING"
        assert len(top["phase0_receipts"]) == 32
        assert len(top["phase1_receipts"]) == 32
        assert len(nested_log) == 64
        assert all(x["middle_effect"] == 2.0 for x in nested_log)

        # No flat top controller exists.  Query two learned top contexts and execute
        # through the same learned middle that generated the top's developmental
        # outcome history.
        p0, x0 = _execute_current_top(m, top, ("G0", "H0", "C0", "GM0"), "GROW-0")
        assert p0.sequence == (top["bound"][0].capability_id,)
        assert x0["handler_value"]["target"] == top["target_tokens"][0]
        assert x0["handler_value"]["local_mean"] == "OPAQUE-MIDDLE-CONTROLLER"
        assert top["world"].last_effect == 2.0

        p1, x1 = _execute_current_top(m, top, ("G1", "H0", "C1", "GM1"), "GROW-1")
        assert p1.sequence == (top["bound"][1].capability_id,)
        assert x1["handler_value"]["target"] == top["target_tokens"][1]
        assert x1["handler_value"]["local_mean"] == "OPAQUE-MIDDLE-CONTROLLER"
        assert top["world"].last_effect == 2.0

        # Leaf-local means remain below the middle boundary even though the top
        # learned its policy from nested effects.
        assert "leaf_target" not in x0["handler_value"] and "leaf_local_mean" not in x0["handler_value"]
        assert "leaf_target" not in x1["handler_value"] and "leaf_local_mean" not in x1["handler_value"]
        assert nested_log[-2]["leaf_target"] in middle["target_tokens"]
        assert nested_log[-1]["leaf_target"] in middle["target_tokens"]

        for ms in (top["ms"], middle["ms"]):
            assert not hasattr(ms, "hierarchy_manager")
            assert not hasattr(ms, "parent_manager")
            assert not hasattr(ms, "desired_state_registry")
    finally:
        if top is not None:
            top["td"].cleanup()
        middle["td"].cleanup()


def test_growth_claim_stays_bounded_to_top_policy_not_full_unassisted_three_level_learning():
    c = _load("test_frontier_c_scale_nested_three_level_execution.py")
    m = c._m()
    middle = m.build_integrated()
    top = None
    try:
        top, nested_log = _grow_top_through_middle(c, m, middle)

        # The middle existed as a separately learned/current controller before top
        # development began.  The harness also still maps each top request token to
        # one opaque current middle context.  Those assistance surfaces are explicit
        # and prevent promotion to full simultaneous three-level end-to-end learning.
        assert middle["routing_id"] in middle["ms"].action_outcome_learning.projection_conditioned_bindings
        assert top["routing_id"] in top["ms"].action_outcome_learning.projection_conditioned_bindings
        assert len(nested_log) == 64
        assert all("middle_raw" in row for row in nested_log)
        assert all(row["middle_capability_id"] for row in nested_log)

        # Growth did not mint a reusable atomic hierarchy whole or a new execution
        # owner on the top controller.
        assert not hasattr(top["ms"], "hierarchy_manager")
        assert not hasattr(top["ms"], "recursive_planner")
        assert not hasattr(top["ms"], "atomic_hierarchy_whole")
    finally:
        if top is not None:
            top["td"].cleanup()
        middle["td"].cleanup()


def _projection_sample_semantics(sample):
    return (
        tuple(sample.raw_tokens),
        sample.action_token,
        sample.effect_token,
        sample.operational_scope_id,
        sample.frame_id,
        sample.frame_epoch,
        tuple(sample.source_projection_epochs),
    )


def test_nested_growth_preserves_flat_projection_evidence_geometry_despite_opaque_sample_id_reordering():
    c = _load("test_frontier_c_scale_nested_three_level_execution.py")
    m = c._m()
    flat = m.build_integrated()
    middle = m.build_integrated()
    top = None
    try:
        top, _ = _grow_top_through_middle(c, m, middle)
        flat_samples = list(flat["owned"]["samples"])
        nested_samples = list(top["owned"]["samples"])

        assert len(flat_samples) == len(nested_samples) == 64
        assert Counter(_projection_sample_semantics(x) for x in flat_samples) == Counter(
            _projection_sample_semantics(x) for x in nested_samples
        )

        # The same semantics arrived through different execution ancestry, so opaque
        # sample IDs/order are allowed to differ.  Discovery therefore must not make
        # scientific conclusions depend on those incidental IDs.
        assert [x.sample_id for x in flat_samples] != [x.sample_id for x in nested_samples]
        assert [x.input_positions for x in (flat["ctx_candidate"], top["ctx_candidate"])] == [(1, 2), (1, 2)]
        assert flat["ctx_candidate"].validation_accuracy == top["ctx_candidate"].validation_accuracy == 1.0
    finally:
        if top is not None:
            top["td"].cleanup()
        flat["td"].cleanup()
        middle["td"].cleanup()
