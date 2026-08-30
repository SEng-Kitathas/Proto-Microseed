from __future__ import annotations

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
SERVER = ROOT / "research" / "substrate_shadow" / "referent_crossing_occlusion_world_server.py"
PHASE_MAPS = {
    "PRE": (0, 0, 1, 1),
    "CROSS": (0, 1, 1, 0),
    "OCCLUDE_A": (1, 1),
    "POST": (1, 1, 0, 0),
}
SCHEDULE = ("FX-A", "FX-B", "FX-G", "FX-A", "FX-B")


class CrossingWorld:
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

    def phase(self, phase: str) -> None:
        self.call("phase", phase=phase)

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


def _collect(world: CrossingWorld, phase: str) -> dict[str, object]:
    world.phase(phase)
    samples = [world.observe()]
    for action_id in SCHEDULE:
        world.act(action_id)
        samples.append(world.observe())
    traces = tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b = boundaries(traces)
    nomination = nominate_by_boundary_coherence(b)
    result: dict[str, object] = {
        "phase": phase,
        "samples": [list(x) for x in samples],
        "boundaries": [list(x) for x in b],
        "nomination_status": nomination.status,
        "nomination_reason": nomination.reason,
        "identity_authority": nomination.identity_authority,
        "groups": [],
    }
    if nomination.status != "REFERENT_PARTITION_NOMINATED":
        return result

    mapping = PHASE_MAPS[phase]
    rows = []
    for group in nomination.groups:
        latent = {mapping[i] for i in group}
        assert len(latent) == 1, (phase, group, b, mapping)
        signature = derive_affordance_relative_referent_signature(b, group, SCHEDULE)
        assert signature.status == "OPERATIONAL_REFERENT_SIGNATURE_DERIVED", signature
        rows.append(
            {
                "group": list(group),
                "signature": signature.signature_sha256,
                "response_rows": [
                    [action, list(bits)] for action, bits in signature.action_response_rows
                ],
                "latent_slot_for_evaluator_only": next(iter(latent)),
            }
        )
    result["groups"] = rows
    return result


def _by_signature(result: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(row["signature"]): row for row in result["groups"]}  # type: ignore[index]


def _changed(before: tuple[int, ...], after: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(i for i, (a, b) in enumerate(zip(before, after)) if a != b)


def _mark(world: CrossingWorld, action_id: str) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    before = world.observe()
    world.act(action_id)
    after = world.observe()
    return before, after, _changed(before, after)


def run_variant(variant: str) -> dict[str, object]:
    world = CrossingWorld()
    try:
        world.call("reset")

        pre = _collect(world, "PRE")
        assert pre["nomination_status"] == "REFERENT_PARTITION_NOMINATED", pre
        pre_by = _by_signature(pre)
        assert len(pre_by) == 2
        pre_by_slot = {
            int(row["latent_slot_for_evaluator_only"]): row
            for row in pre["groups"]  # type: ignore[index]
        }
        sig_a = str(pre_by_slot[0]["signature"])
        sig_b = str(pre_by_slot[1]["signature"])
        assert sig_a != sig_b

        cross = _collect(world, "CROSS")
        assert cross["nomination_status"] == "REFERENT_PARTITION_NOMINATED", cross
        cross_by = _by_signature(cross)
        assert set(cross_by) == {sig_a, sig_b}
        assert pre_by[sig_a]["group"] != cross_by[sig_a]["group"]
        assert pre_by[sig_b]["group"] != cross_by[sig_b]["group"]

        # Create two content-bound idempotent traces while referents occupy crossed positions.
        _, _, mark_a_changed = _mark(world, "FX-MARK-A")
        _, _, mark_b_changed = _mark(world, "FX-MARK-B")
        assert list(mark_a_changed) == cross_by[sig_a]["group"]
        assert list(mark_b_changed) == cross_by[sig_b]["group"]

        pre_gap_eval = world.call("evaluator_state")

        # Full A occlusion leaves only B's coherent channels. One visible coherent group
        # is insufficient to nominate distinct referents; the correct local result is unknown.
        occluded = _collect(world, "OCCLUDE_A")
        assert occluded["nomination_status"] == "UNKNOWN_INCOMPLETE", occluded
        assert occluded["nomination_reason"] == "BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS"
        assert occluded["identity_authority"] == "NONE"

        world.call("gap")
        assert world.observe() == ()
        world.call("reappear", variant=variant)
        post_gap_eval = world.call("evaluator_state")

        post = _collect(world, "POST")
        if variant == "ALIASED_POST":
            assert post["nomination_status"] == "UNKNOWN_INCOMPLETE", post
            assert post["nomination_reason"] == "BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS"
            return {
                "variant": variant,
                "pre": pre,
                "cross": cross,
                "occluded": occluded,
                "post": post,
                "post_reassociation": "UNKNOWN_INCOMPLETE",
                "trace_test_status": "NOT_RUN_WITHOUT_UNIQUE_POST_REFERENT_PARTITION",
                "evaluator_generations_before_gap": pre_gap_eval["generations"],
                "evaluator_generations_after_gap": post_gap_eval["generations"],
                "numerical_identity_authority": "NONE",
                "semantic_reference_authority": "NONE",
                "language_authority": "NONE",
            }

        assert post["nomination_status"] == "REFERENT_PARTITION_NOMINATED", post
        post_by = _by_signature(post)
        assert set(post_by) == {sig_a, sig_b}
        assert post_by[sig_a]["group"] != pre_by[sig_a]["group"]
        assert post_by[sig_b]["group"] != pre_by[sig_b]["group"]
        assert post_by[sig_a]["group"] != cross_by[sig_a]["group"]
        assert post_by[sig_b]["group"] != cross_by[sig_b]["group"]

        # Reapplying an idempotent represented marker is an organism-visible retention test:
        # retained prior trace -> zero effect; lost trace -> effect localized to current group.
        _, _, reapply_a = _mark(world, "FX-MARK-A")
        _, _, reapply_b = _mark(world, "FX-MARK-B")
        trace_a = "RETAINED" if not reapply_a else "LOST"
        trace_b = "RETAINED" if not reapply_b else "LOST"
        if reapply_a:
            assert list(reapply_a) == post_by[sig_a]["group"]
        if reapply_b:
            assert list(reapply_b) == post_by[sig_b]["group"]

        return {
            "variant": variant,
            "sig_a": sig_a,
            "sig_b": sig_b,
            "pre_groups_by_signature": {sig: row["group"] for sig, row in pre_by.items()},
            "cross_groups_by_signature": {sig: row["group"] for sig, row in cross_by.items()},
            "post_groups_by_signature": {sig: row["group"] for sig, row in post_by.items()},
            "occlusion_nomination_status": occluded["nomination_status"],
            "trace_status": {"A": trace_a, "B": trace_b},
            "trace_reapply_changed_positions": {"A": list(reapply_a), "B": list(reapply_b)},
            "evaluator_generations_before_gap": pre_gap_eval["generations"],
            "evaluator_generations_after_gap": post_gap_eval["generations"],
            "post_reassociation": "AFFORDANCE_SIGNATURE_MATCHED_AFTER_CROSSING_OCCLUSION_AND_APPEARANCE_CHANGE",
            "numerical_identity_authority": "NONE",
            "semantic_reference_authority": "NONE",
            "language_authority": "NONE",
        }
    finally:
        world.close()


def run_ms1995() -> dict[str, object]:
    persistent = run_variant("PERSIST")
    replace_a = run_variant("REPLACE_A_UNMARKED")
    replace_b = run_variant("REPLACE_B_UNMARKED")
    perfect = run_variant("REPLACE_BOTH_PERFECT_COPY")
    aliased = run_variant("ALIASED_POST")

    assert persistent["trace_status"] == {"A": "RETAINED", "B": "RETAINED"}
    assert persistent["evaluator_generations_before_gap"] == persistent["evaluator_generations_after_gap"]

    assert replace_a["trace_status"] == {"A": "LOST", "B": "RETAINED"}
    assert replace_a["evaluator_generations_before_gap"] != replace_a["evaluator_generations_after_gap"]

    assert replace_b["trace_status"] == {"A": "RETAINED", "B": "LOST"}
    assert replace_b["evaluator_generations_before_gap"] != replace_b["evaluator_generations_after_gap"]

    assert perfect["trace_status"] == {"A": "RETAINED", "B": "RETAINED"}
    assert perfect["evaluator_generations_before_gap"] != perfect["evaluator_generations_after_gap"]

    # Persistent and perfect-copy worlds remain identical at the operational signature/trace level.
    for key in (
        "sig_a",
        "sig_b",
        "pre_groups_by_signature",
        "cross_groups_by_signature",
        "post_groups_by_signature",
        "trace_status",
    ):
        assert persistent[key] == perfect[key], key

    assert aliased["post_reassociation"] == "UNKNOWN_INCOMPLETE"
    assert aliased["trace_test_status"] == "NOT_RUN_WITHOUT_UNIQUE_POST_REFERENT_PARTITION"

    return {
        "status": "BOUNDARY_CONFIRMED",
        "persistent": persistent,
        "replace_a_unmarked": replace_a,
        "replace_b_unmarked": replace_b,
        "perfect_copy_both": perfect,
        "aliased_post": aliased,
        "earned": "AFFORDANCE_RELATIVE_REASSOCIATION_PLUS_IDEMPOTENT_INTERVENTION_TRACE_TESTS_CAN_PRESERVE_OPERATIONAL_MULTI_REFERENT_CONTINUITY_THROUGH_PRESENTATION_CROSSING_OCCLUSION_AND_APPEARANCE_CHANGE_WHILE_DEFERRING_ON_ALIASED_EVIDENCE",
        "crossing_authority": "OPERATIONAL_REASSOCIATION_ONLY",
        "occlusion_authority": "DEFER_DURING_INSUFFICIENT_VISIBLE_PARTITION_EVIDENCE",
        "ambiguous_evidence_policy": "UNKNOWN_INCOMPLETE_NO_GUESS",
        "numerical_identity_authority": "NONE",
        "semantic_reference_authority": "NONE",
        "language_authority": "NONE",
        "new_core_mechanism_required": "NO",
        "remaining_boundary": "LONGER_MULTI_REFERENT_PARTIAL_OBSERVABILITY_AND_ENDOGENOUS_INTERVENTION_CONSTRUCTION",
    }


def main() -> None:
    print(json.dumps(run_ms1995(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
