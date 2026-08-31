from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import derive_affordance_relative_referent_signature, nominate_by_boundary_coherence
from scratch.ms1958_proto_referent_boundary_coherence import boundaries

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "research" / "substrate_shadow" / "referent_four_way_partial_observability_world_server.py"
SCHEDULE = ("FX-A", "FX-B", "FX-C", "FX-D", "FX-G", "FX-A", "FX-B", "FX-C", "FX-D")
PHASE_MAPS = {
    "PRE": (0, 0, 1, 1, 2, 2, 3, 3),
    "CROSS": (0, 2, 1, 3, 3, 1, 2, 0),
    "OCCLUDE_AC": (1, 3, 1, 3),
    "OCCLUDE_BD": (0, 2, 2, 0),
    "POST": (3, 1, 0, 2, 2, 0, 1, 3),
}
LABELS = {0: "A", 1: "B", 2: "C", 3: "D"}


class FourReferentWorld:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1, cwd=str(ROOT),
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
            try: self.call("close")
            except Exception: pass
        try: self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill(); self.proc.wait(timeout=5)


def _collect(world: FourReferentWorld, phase: str) -> dict[str, object]:
    world.phase(phase)
    samples = [world.observe()]
    for action_id in SCHEDULE:
        world.act(action_id); samples.append(world.observe())
    traces = tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b = boundaries(traces)
    nomination = nominate_by_boundary_coherence(b)
    mapping = PHASE_MAPS[phase]
    rows = []
    for group in nomination.groups:
        sources = tuple(sorted({mapping[i] for i in group}))
        sig = derive_affordance_relative_referent_signature(b, group, SCHEDULE)
        assert sig.status == "OPERATIONAL_REFERENT_SIGNATURE_DERIVED", sig
        rows.append({
            "group": list(group),
            "evaluator_sources_for_test_only": [LABELS[x] for x in sources],
            "signature": sig.signature_sha256,
            "response_rows": [[a, list(bits)] for a, bits in sig.action_response_rows],
        })
    return {
        "phase": phase,
        "nomination_status": nomination.status,
        "nomination_reason": nomination.reason,
        "identity_authority": nomination.identity_authority,
        "groups": rows,
    }


def _singleton_by_label(result: dict[str, object]) -> dict[str, dict[str, object]]:
    out = {}
    for row in result["groups"]:  # type: ignore[index]
        labels = row["evaluator_sources_for_test_only"]
        if len(labels) == 1:
            out[str(labels[0])] = row
    return out


def _changed(before: tuple[int, ...], after: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(i for i, (a, b) in enumerate(zip(before, after)) if a != b)


def _mark(world: FourReferentWorld, label: str):
    before = world.observe(); world.act(f"FX-MARK-{label}"); after = world.observe()
    return _changed(before, after)


def run_variant(variant: str) -> dict[str, object]:
    world = FourReferentWorld()
    try:
        world.call("reset")
        pre = _collect(world, "PRE")
        assert pre["nomination_status"] == "REFERENT_PARTITION_NOMINATED"
        pre_by = _singleton_by_label(pre)
        assert set(pre_by) == {"A", "B", "C", "D"}
        signatures = {label: str(pre_by[label]["signature"]) for label in pre_by}
        assert len(set(signatures.values())) == 4

        cross = _collect(world, "CROSS")
        cross_by = _singleton_by_label(cross)
        assert set(cross_by) == {"A", "B", "C", "D"}
        assert {label: cross_by[label]["signature"] for label in cross_by} == signatures
        assert all(cross_by[label]["group"] != pre_by[label]["group"] for label in signatures)

        marked_positions = {}
        for label in ("A", "B", "C", "D"):
            changed = _mark(world, label)
            marked_positions[label] = list(changed)
            assert list(changed) == cross_by[label]["group"]

        eval_before = world.call("evaluator_state")

        ac_hidden = _collect(world, "OCCLUDE_AC")
        ac_by = _singleton_by_label(ac_hidden)
        assert set(ac_by) == {"B", "D"}
        assert {label: ac_by[label]["signature"] for label in ac_by} == {label: signatures[label] for label in ("B", "D")}

        bd_hidden = _collect(world, "OCCLUDE_BD")
        bd_by = _singleton_by_label(bd_hidden)
        assert set(bd_by) == {"A", "C"}
        assert {label: bd_by[label]["signature"] for label in bd_by} == {label: signatures[label] for label in ("A", "C")}

        world.call("gap"); assert world.observe() == ()
        world.call("reappear", variant=variant)
        eval_after = world.call("evaluator_state")
        post = _collect(world, "POST")

        if variant == "ALIAS_CD_POST":
            post_by = _singleton_by_label(post)
            assert set(post_by) == {"A", "B"}, post
            ambiguous = [row for row in post["groups"] if set(row["evaluator_sources_for_test_only"]) == {"C", "D"}]  # type: ignore[index]
            assert len(ambiguous) == 1, post
            assert len(ambiguous[0]["group"]) == 4
            return {
                "variant": variant,
                "pre_group_count": len(pre["groups"]),
                "cross_group_count": len(cross["groups"]),
                "occlude_ac_visible_labels": sorted(ac_by),
                "occlude_bd_visible_labels": sorted(bd_by),
                "post_group_count": len(post["groups"]),
                "post_unambiguous_labels": sorted(post_by),
                "localized_ambiguous_sources": ambiguous[0]["evaluator_sources_for_test_only"],
                "ambiguous_group_size": len(ambiguous[0]["group"]),
                "trace_replay": "NOT_RUN_FOR_AMBIGUOUS_CD_PARTITION",
                "numerical_identity_authority": "NONE",
                "semantic_reference_authority": "NONE",
                "language_authority": "NONE",
            }

        post_by = _singleton_by_label(post)
        assert set(post_by) == {"A", "B", "C", "D"}, post
        assert {label: post_by[label]["signature"] for label in post_by} == signatures
        assert all(post_by[label]["group"] != pre_by[label]["group"] for label in signatures)
        assert all(post_by[label]["group"] != cross_by[label]["group"] for label in signatures)

        trace_status = {}
        trace_changed = {}
        for label in ("A", "B", "C", "D"):
            changed = _mark(world, label)
            trace_changed[label] = list(changed)
            trace_status[label] = "RETAINED" if not changed else "LOST"
            if changed:
                assert list(changed) == post_by[label]["group"]

        return {
            "variant": variant,
            "signatures": signatures,
            "pre_groups": {k: v["group"] for k, v in pre_by.items()},
            "cross_groups": {k: v["group"] for k, v in cross_by.items()},
            "post_groups": {k: v["group"] for k, v in post_by.items()},
            "occlude_ac_visible_labels": sorted(ac_by),
            "occlude_bd_visible_labels": sorted(bd_by),
            "cross_mark_changed_positions": marked_positions,
            "trace_status": trace_status,
            "trace_replay_changed_positions": trace_changed,
            "evaluator_generations_before_gap": eval_before["generations"],
            "evaluator_generations_after_gap": eval_after["generations"],
            "numerical_identity_authority": "NONE",
            "semantic_reference_authority": "NONE",
            "language_authority": "NONE",
        }
    finally:
        world.close()


def run_ms2043() -> dict[str, object]:
    persist = run_variant("PERSIST")
    replace_c = run_variant("REPLACE_C_UNMARKED")
    replace_ac = run_variant("REPLACE_AC_UNMARKED")
    perfect = run_variant("REPLACE_ALL_PERFECT_COPY")
    alias = run_variant("ALIAS_CD_POST")

    assert persist["trace_status"] == {"A": "RETAINED", "B": "RETAINED", "C": "RETAINED", "D": "RETAINED"}
    assert replace_c["trace_status"] == {"A": "RETAINED", "B": "RETAINED", "C": "LOST", "D": "RETAINED"}
    assert replace_ac["trace_status"] == {"A": "LOST", "B": "RETAINED", "C": "LOST", "D": "RETAINED"}
    assert perfect["trace_status"] == persist["trace_status"]
    for key in ("signatures", "pre_groups", "cross_groups", "post_groups", "trace_status"):
        assert perfect[key] == persist[key], key
    assert perfect["evaluator_generations_after_gap"] != persist["evaluator_generations_after_gap"]
    assert alias["post_unambiguous_labels"] == ["A", "B"]
    assert alias["localized_ambiguous_sources"] == ["C", "D"]

    return {
        "status": "FOUR_REFERENT_PARTIAL_OBSERVABILITY_SCALE_EARNED",
        "persist": persist,
        "replace_c_unmarked": replace_c,
        "replace_ac_unmarked": replace_ac,
        "perfect_copy_all": perfect,
        "alias_cd_post": alias,
        "earned": "AFFORDANCE_RELATIVE_REFERENT_PARTITIONING_SCALES_TO_FOUR_REFERENTS_UNDER_CROSSING_STAGGERED_OCCLUSION_AND_APPEARANCE_CHANGE_WHILE_LOCALIZING_AMBIGUITY_INSTEAD_OF_GUESSING",
        "numerical_identity_authority": "NONE",
        "semantic_reference_authority": "NONE",
        "language_authority": "NONE",
        "new_tracker_required": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2043(), indent=2, sort_keys=True, default=str))
