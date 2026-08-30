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
SERVER = ROOT / "research" / "substrate_shadow" / "referent_intervention_trace_world_server.py"
MAP = (0, 0, 1, 1)


class TraceWorld:
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


def _collect_signatures(world: TraceWorld, schedule: tuple[str, ...]):
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


def _trace_digest(group: tuple[int, ...], before: tuple[int, ...], after: tuple[int, ...]) -> str:
    payload = {
        "group": list(group),
        "before": [before[i] for i in group],
        "after": [after[i] for i in group],
        "delta": [after[i] - before[i] for i in group],
        "action_id": "FX-MARK-A",
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_variant(variant: str) -> dict[str, object]:
    world = TraceWorld()
    try:
        world.call("reset")
        schedule = ("FX-A", "FX-B", "FX-G", "FX-A", "FX-B")
        pre_groups = _collect_signatures(world, schedule)
        pre_by_slot = {int(row["latent_slot_for_evaluator_only"]): row for row in pre_groups}
        target_group = tuple(pre_by_slot[0]["group"])
        target_signature = str(pre_by_slot[0]["signature"])

        before_mark = world.observe()
        world.act("FX-MARK-A")
        after_mark = world.observe()
        changed = tuple(i for i, (a, b) in enumerate(zip(before_mark, after_mark)) if a != b)
        assert changed == target_group, (changed, target_group)
        trace_digest = _trace_digest(target_group, before_mark, after_mark)

        pre_generation = tuple(world.call("evaluator_identity")["generations"])
        world.call("gap")
        assert world.observe() == ()
        world.call("reappear", variant=variant)
        post_generation = tuple(world.call("evaluator_identity")["generations"])
        post_gap = world.observe()

        # Re-association remains affordance-relative: the persistent mark is an additive
        # channel offset, so action-effect deltas and therefore signatures are unchanged.
        post_groups = _collect_signatures(world, schedule)
        post_by_signature = {str(row["signature"]): row for row in post_groups}
        assert target_signature in post_by_signature
        reassociated_group = tuple(post_by_signature[target_signature]["group"])
        assert reassociated_group == target_group

        trace_retained = tuple(post_gap[i] for i in target_group) == tuple(after_mark[i] for i in target_group)
        operational_support = "SUPPORTED" if trace_retained else "REFUTED_FOR_THIS_TRACE"
        evaluator_persistence = pre_generation == post_generation

        return {
            "variant": variant,
            "target_group": list(target_group),
            "target_signature": target_signature,
            "trace_digest": trace_digest,
            "trace_retained": trace_retained,
            "operational_persistence_support": operational_support,
            "evaluator_persistence": evaluator_persistence,
            "pre_generation_for_evaluator_only": list(pre_generation),
            "post_generation_for_evaluator_only": list(post_generation),
            "numerical_identity_authority": "NONE",
            "semantic_reference_authority": "NONE",
            "language_authority": "NONE",
        }
    finally:
        world.close()


def run_ms1993() -> dict[str, object]:
    persistent = run_variant("PERSIST")
    replacement = run_variant("REPLACE_UNMARKED")
    perfect_copy = run_variant("REPLACE_PERFECT_COPY")

    assert persistent["trace_retained"] is True
    assert persistent["evaluator_persistence"] is True
    assert replacement["trace_retained"] is False
    assert replacement["evaluator_persistence"] is False
    assert perfect_copy["trace_retained"] is True
    assert perfect_copy["evaluator_persistence"] is False

    # Organism-visible retained trace separates the unmarked replacement from the
    # other two worlds, but cannot distinguish persistence from a perfect copy that
    # carries the same intervention-bound trace.
    assert persistent["target_signature"] == replacement["target_signature"] == perfect_copy["target_signature"]
    assert persistent["target_group"] == replacement["target_group"] == perfect_copy["target_group"]

    return {
        "status": "BOUNDARY_CONFIRMED",
        "persistent": persistent,
        "unmarked_replacement": replacement,
        "perfect_copy_replacement": perfect_copy,
        "earned": "INTERVENTION_BOUND_CAUSAL_TRACE_CAN_SUPPORT_OPERATIONAL_PERSISTENCE_ACROSS_AN_OBSERVATION_GAP_WITHOUT_ESTABLISHING_NUMERICAL_IDENTITY",
        "operational_persistence_authority": "TRACE_RELATIVE_ONLY",
        "numerical_identity_authority": "NONE",
        "semantic_reference_authority": "NONE",
        "language_authority": "NONE",
        "remaining_boundary": "PERFECT_COPY_WITH_RETAINED_TRACE_REMAINS_OPERATIONALLY_INDISTINGUISHABLE_FROM_PERSISTENCE",
        "new_core_mechanism_required": "NO",
    }


def main() -> None:
    print(json.dumps(run_ms1993(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
