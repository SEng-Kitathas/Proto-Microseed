from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import (
    derive_affordance_relative_referent_signature,
    nominate_by_boundary_coherence,
)
from scratch.ms1958_proto_referent_boundary_coherence import boundaries

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "research" / "substrate_shadow" / "referent_multi_trace_world_server.py"
MAP = (0, 0, 1, 1)
TRACE_ACTIONS = ("FX-MARK-A1", "FX-MARK-A2")


class MultiTraceWorld:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=str(ROOT),
        )
        assert self.proc.stdin and self.proc.stdout

    def call(self, op: str, **payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({"op": op, **payload}, separators=(",", ":")) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        assert line
        result = json.loads(line)
        assert result.get("status") == "OK", result
        return result

    def act(self, action_id: str) -> None:
        self.call("act", action_id=action_id)

    def observe(self) -> tuple[int, ...]:
        return tuple(self.call("observe")["channels"])

    def close(self) -> None:
        if self.proc.poll() is None:
            try:
                self.call("close")
            except Exception:
                pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)


def _collect_signatures(world: MultiTraceWorld, schedule: tuple[str, ...]):
    samples = [world.observe()]
    for action_id in schedule:
        world.act(action_id)
        samples.append(world.observe())
    traces = tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b = boundaries(traces)
    nominated = nominate_by_boundary_coherence(b)
    assert nominated.status == "REFERENT_PARTITION_NOMINATED", nominated
    rows = []
    for group in nominated.groups:
        signature = derive_affordance_relative_referent_signature(b, group, schedule)
        assert signature.status == "OPERATIONAL_REFERENT_SIGNATURE_DERIVED", signature
        rows.append(
            {
                "group": tuple(group),
                "signature": signature.signature_sha256,
                "latent_slot_for_evaluator_only": next(iter({MAP[i] for i in group})),
            }
        )
    return tuple(rows)


def _delta(group: tuple[int, ...], before: tuple[int, ...], after: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(after[i] - before[i] for i in group)


def _trace_digest(
    action_id: str,
    group: tuple[int, ...],
    before: tuple[int, ...],
    after: tuple[int, ...],
) -> str:
    payload = {
        "action_id": action_id,
        "group": list(group),
        "before": [before[i] for i in group],
        "after": [after[i] for i in group],
        "delta": list(_delta(group, before, after)),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _classify_retained_topology(
    observed_delta: tuple[int, ...],
    trace_basis: dict[str, tuple[int, ...]],
) -> tuple[str, ...] | None:
    names = tuple(trace_basis)
    candidates: dict[tuple[int, ...], tuple[str, ...]] = {(0,) * len(observed_delta): ()}
    for mask in range(1, 1 << len(names)):
        selected = tuple(names[i] for i in range(len(names)) if mask & (1 << i))
        summed = tuple(sum(trace_basis[name][j] for name in selected) for j in range(len(observed_delta)))
        if summed in candidates and candidates[summed] != selected:
            raise AssertionError("NON_UNIQUE_TRACE_TOPOLOGY")
        candidates[summed] = selected
    return candidates.get(observed_delta)


def run_variant(variant: str) -> dict[str, object]:
    world = MultiTraceWorld()
    try:
        world.call("reset")
        schedule = ("FX-A", "FX-B", "FX-G", "FX-A", "FX-B")
        pre_groups = _collect_signatures(world, schedule)
        pre_by_slot = {int(row["latent_slot_for_evaluator_only"]): row for row in pre_groups}
        target_group = tuple(pre_by_slot[0]["group"])
        nuisance_group = tuple(pre_by_slot[1]["group"])
        target_signature = str(pre_by_slot[0]["signature"])

        baseline = world.observe()
        trace_basis: dict[str, tuple[int, ...]] = {}
        trace_digests: dict[str, str] = {}
        cursor = baseline
        for action_id in TRACE_ACTIONS:
            world.act(action_id)
            after = world.observe()
            changed = tuple(i for i, (a, b) in enumerate(zip(cursor, after)) if a != b)
            assert changed == target_group, (action_id, changed, target_group)
            name = action_id.removeprefix("FX-MARK-")
            trace_basis[name] = _delta(target_group, cursor, after)
            trace_digests[name] = _trace_digest(action_id, target_group, cursor, after)
            cursor = after

        assert trace_basis["A1"] != trace_basis["A2"]
        assert all(any(v != 0 for v in delta) for delta in trace_basis.values())

        pre_generation = tuple(world.call("evaluator_identity")["generations"])
        world.call("gap")
        assert world.observe() == ()
        world.call("reappear", variant=variant)
        post_generation = tuple(world.call("evaluator_identity")["generations"])
        post_gap = world.observe()

        # Persistent marker terms are constant offsets, so represented action-effect
        # deltas stay unchanged and the existing signature can re-associate the group.
        post_groups = _collect_signatures(world, schedule)
        post_by_signature = {str(row["signature"]): row for row in post_groups}
        assert target_signature in post_by_signature
        reassociated_group = tuple(post_by_signature[target_signature]["group"])
        assert reassociated_group == target_group

        observed_target_delta = _delta(target_group, baseline, post_gap)
        retained = _classify_retained_topology(observed_target_delta, trace_basis)
        topology_known = retained is not None
        retained_set = set(retained or ())
        per_trace = {
            name: ("RETAINED" if name in retained_set else "LOST")
            for name in trace_basis
        } if topology_known else {name: "UNRESOLVED" for name in trace_basis}

        nuisance_delta = _delta(nuisance_group, baseline, post_gap)
        nuisance_changed = any(v != 0 for v in nuisance_delta)

        if not topology_known:
            support = "UNRESOLVED_TRACE_TOPOLOGY"
        elif len(retained_set) == len(trace_basis):
            support = "SUPPORTED_BY_ALL_OBSERVED_TRACES"
        elif not retained_set:
            support = "REFUTED_FOR_ALL_OBSERVED_TRACES"
        else:
            support = "MIXED_TRACE_EVIDENCE"

        evaluator_persistence = pre_generation == post_generation
        return {
            "variant": variant,
            "target_group": list(target_group),
            "nuisance_group": list(nuisance_group),
            "target_signature": target_signature,
            "trace_basis": {name: list(delta) for name, delta in trace_basis.items()},
            "trace_digests": trace_digests,
            "observed_target_delta": list(observed_target_delta),
            "retained_trace_topology": list(retained) if retained is not None else None,
            "per_trace_status": per_trace,
            "nuisance_delta": list(nuisance_delta),
            "nuisance_changed": nuisance_changed,
            "operational_persistence_support": support,
            "evaluator_persistence": evaluator_persistence,
            "pre_generation_for_evaluator_only": list(pre_generation),
            "post_generation_for_evaluator_only": list(post_generation),
            "numerical_identity_authority": "NONE",
            "semantic_reference_authority": "NONE",
            "language_authority": "NONE",
        }
    finally:
        world.close()


def run_ms1994() -> dict[str, object]:
    persistent = run_variant("PERSIST")
    unmarked = run_variant("REPLACE_UNMARKED")
    partial = run_variant("REPLACE_PARTIAL_A1")
    perfect = run_variant("REPLACE_PERFECT_COPY")
    nuisance = run_variant("REPLACE_NUISANCE_ONLY")
    persistent_nuisance = run_variant("PERSIST_NUISANCE_B")

    assert persistent["retained_trace_topology"] == ["A1", "A2"]
    assert persistent["operational_persistence_support"] == "SUPPORTED_BY_ALL_OBSERVED_TRACES"
    assert persistent["evaluator_persistence"] is True

    assert unmarked["retained_trace_topology"] == []
    assert unmarked["operational_persistence_support"] == "REFUTED_FOR_ALL_OBSERVED_TRACES"
    assert unmarked["evaluator_persistence"] is False

    assert partial["retained_trace_topology"] == ["A1"]
    assert partial["per_trace_status"] == {"A1": "RETAINED", "A2": "LOST"}
    assert partial["operational_persistence_support"] == "MIXED_TRACE_EVIDENCE"
    assert partial["evaluator_persistence"] is False

    assert perfect["retained_trace_topology"] == ["A1", "A2"]
    assert perfect["operational_persistence_support"] == "SUPPORTED_BY_ALL_OBSERVED_TRACES"
    assert perfect["evaluator_persistence"] is False

    assert nuisance["retained_trace_topology"] == []
    assert nuisance["nuisance_changed"] is True
    assert nuisance["operational_persistence_support"] == "REFUTED_FOR_ALL_OBSERVED_TRACES"
    assert nuisance["evaluator_persistence"] is False

    assert persistent_nuisance["retained_trace_topology"] == ["A1", "A2"]
    assert persistent_nuisance["nuisance_changed"] is True
    assert persistent_nuisance["operational_persistence_support"] == "SUPPORTED_BY_ALL_OBSERVED_TRACES"
    assert persistent_nuisance["evaluator_persistence"] is True

    for row in (persistent, unmarked, partial, perfect, nuisance, persistent_nuisance):
        assert row["target_group"] == [0, 1]
        assert row["nuisance_group"] == [2, 3]
        assert row["numerical_identity_authority"] == "NONE"
        assert row["semantic_reference_authority"] == "NONE"
        assert row["language_authority"] == "NONE"

    # All hidden variants keep the same affordance-relative re-association route.
    assert len({row["target_signature"] for row in (persistent, unmarked, partial, perfect, nuisance, persistent_nuisance)}) == 1

    return {
        "status": "BOUNDARY_CONFIRMED",
        "persistent": persistent,
        "unmarked_replacement": unmarked,
        "partial_copy_replacement": partial,
        "perfect_copy_replacement": perfect,
        "nuisance_replacement": nuisance,
        "persistent_with_unrelated_nuisance": persistent_nuisance,
        "earned": "MULTIPLE_INDEPENDENT_INTERVENTION_TRACES_CAN_PRESERVE_EXACT_OPERATIONAL_PERSISTENCE_EVIDENCE_TOPOLOGY_ACROSS_A_GAP_WITHOUT_PROMOTING_NUMERICAL_IDENTITY",
        "operational_persistence_authority": "TRACE_TOPOLOGY_RELATIVE_ONLY",
        "partial_conflict_policy": "PRESERVE_MIXED_EVIDENCE_NO_MAJORITY_COLLAPSE",
        "numerical_identity_authority": "NONE",
        "semantic_reference_authority": "NONE",
        "language_authority": "NONE",
        "remaining_boundary": "PERFECT_COPY_WITH_ALL_RETAINED_TRACES_REMAINS_OPERATIONALLY_INDISTINGUISHABLE_FROM_PERSISTENCE",
        "new_core_mechanism_required": "NO",
    }


def main() -> None:
    print(json.dumps(run_ms1994(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
