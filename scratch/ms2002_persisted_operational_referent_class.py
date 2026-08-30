from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.cognition.referents import OperationalReferentSignature
from microseed.runtime.types import EpistemicStatus
from scratch.ms1995_crossing_occlusion_reassociation import CrossingWorld, _collect, _mark, _by_signature


def _close(ms: Microseed) -> None:
    ms.biography.close()
    ms.evidence.conn.close()
    ms.store.conn.close()


def _signature(row: dict[str, object]) -> OperationalReferentSignature:
    return OperationalReferentSignature(
        status="OPERATIONAL_REFERENT_SIGNATURE_DERIVED",
        signature_sha256=str(row["signature"]),
        action_response_rows=tuple(
            (str(action), tuple(bool(x) for x in bits))
            for action, bits in row["response_rows"]  # type: ignore[index]
        ),
        reason="AFFORDANCE_RELATIVE_BOUNDARY_RESPONSE_ONLY",
    )


def run_variant(variant: str) -> dict[str, object]:
    td = tempfile.TemporaryDirectory(prefix=f"ms2002-{variant.lower()}-")
    root = Path(td.name)
    world = CrossingWorld()
    try:
        world.call("reset")
        pre = _collect(world, "PRE")
        assert pre["nomination_status"] == "REFERENT_PARTITION_NOMINATED"
        assert len(pre["groups"]) == 2

        ms = Microseed(root)
        try:
            pre_witness_ids = []
            for idx, row in enumerate(pre["groups"]):  # type: ignore[index]
                sig = _signature(row)
                rec = ms.record_operational_referent_signature(
                    f"MS2002-PRE-{variant}-{idx}", sig
                )
                assert rec["status"] == "OPERATIONAL_REFERENT_SIGNATURE_WITNESS_RECORDED"
                assert rec["identity_authority"] == "NONE"
                pre_witness_ids.append(rec["evidence_id"])
            # Duplicate one exact class witness to prove class/set return rather than identity pick.
            duplicate_sig = _signature(pre["groups"][0])  # type: ignore[index]
            dup = ms.record_operational_referent_signature(
                f"MS2002-PRE-{variant}-DUP", duplicate_sig
            )
            assert dup["status"] == "OPERATIONAL_REFERENT_SIGNATURE_WITNESS_RECORDED"
        finally:
            _close(ms)

        # Process restart: operational class evidence must survive without an in-memory registry.
        cross = _collect(world, "CROSS")
        assert cross["nomination_status"] == "REFERENT_PARTITION_NOMINATED"
        ms = Microseed(root)
        try:
            cross_matches = {}
            for row in cross["groups"]:  # type: ignore[index]
                sig = _signature(row)
                matched = ms.reassociate_operational_referent_signature(sig, max_records=64)
                assert matched["status"] == "OPERATIONAL_REFERENT_SIGNATURE_CLASS_REASSOCIATED", matched
                assert matched["identity_authority"] == "NONE"
                assert matched["semantic_reference_authority"] == "NONE"
                cross_matches[str(row["signature"])] = matched
            duplicate_class = cross_matches[str(cross["groups"][0]["signature"])]  # type: ignore[index]
            assert duplicate_class["match_count"] == 2
        finally:
            _close(ms)

        # Create intervention traces and then occlude one referent exactly as MS1995.
        _mark(world, "FX-MARK-A")
        _mark(world, "FX-MARK-B")
        occluded = _collect(world, "OCCLUDE_A")
        assert occluded["nomination_status"] == "UNKNOWN_INCOMPLETE"
        assert occluded["identity_authority"] == "NONE"

        world.call("gap")
        assert world.observe() == ()
        world.call("reappear", variant=variant)
        post = _collect(world, "POST")

        if variant == "ALIASED_POST":
            assert post["nomination_status"] == "UNKNOWN_INCOMPLETE"
            return {
                "variant": variant,
                "status": "UNKNOWN_INCOMPLETE",
                "reason": post["nomination_reason"],
                "identity_authority": "NONE",
                "semantic_reference_authority": "NONE",
                "persistent_referent_registry": "NONE",
            }

        assert post["nomination_status"] == "REFERENT_PARTITION_NOMINATED"
        ms = Microseed(root)
        try:
            post_matches = {}
            for row in post["groups"]:  # type: ignore[index]
                sig = _signature(row)
                matched = ms.reassociate_operational_referent_signature(sig, max_records=64)
                assert matched["status"] == "OPERATIONAL_REFERENT_SIGNATURE_CLASS_REASSOCIATED", matched
                assert matched["identity_authority"] == "NONE"
                assert matched["semantic_reference_authority"] == "NONE"
                post_matches[str(row["signature"])] = matched
            return {
                "variant": variant,
                "status": "PASS",
                "pre_signatures": sorted(_by_signature(pre)),
                "cross_signatures": sorted(cross_matches),
                "post_signatures": sorted(post_matches),
                "cross_match_counts": {k: int(v["match_count"]) for k, v in cross_matches.items()},
                "post_match_counts": {k: int(v["match_count"]) for k, v in post_matches.items()},
                "identity_authority": "NONE",
                "semantic_reference_authority": "NONE",
                "truth_authority": "NONE",
                "execution_authority": "NONE",
                "persistent_referent_registry": "NONE__EVIDENCE_LEDGER_ONLY",
            }
        finally:
            _close(ms)
    finally:
        world.close()
        td.cleanup()


def run_budget_hostile() -> dict[str, object]:
    td = tempfile.TemporaryDirectory(prefix="ms2002-budget-")
    root = Path(td.name)
    world = CrossingWorld()
    try:
        world.call("reset")
        pre = _collect(world, "PRE")
        sig = _signature(pre["groups"][0])  # type: ignore[index]
        ms = Microseed(root)
        try:
            ms.record_operational_referent_signature("MS2002-OLD-WITNESS", sig)
            for i in range(32):
                ms.append_evidence(
                    f"MS2002-NOISE-{i}",
                    {"kind": "UNRELATED_NOISE", "i": i},
                    EpistemicStatus.PRESSURE_SUPPORTED,
                    source="MS2002-NOISE",
                )
        finally:
            _close(ms)
        ms = Microseed(root)
        try:
            exhausted = ms.reassociate_operational_referent_signature(sig, max_records=8)
            assert exhausted["status"] == "SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED", exhausted
            complete = ms.reassociate_operational_referent_signature(sig, max_records=64)
            assert complete["status"] == "OPERATIONAL_REFERENT_SIGNATURE_CLASS_REASSOCIATED", complete
            return {
                "bounded_status": exhausted["status"],
                "bounded_reason": exhausted["reason"],
                "complete_status": complete["status"],
                "identity_authority": "NONE",
            }
        finally:
            _close(ms)
    finally:
        world.close()
        td.cleanup()


def run_ms2002() -> dict[str, object]:
    same = run_variant("PERSIST")
    replacement = run_variant("REPLACE_BOTH_PERFECT_COPY")
    aliased = run_variant("ALIASED_POST")
    budget = run_budget_hostile()
    assert same["status"] == replacement["status"] == "PASS"
    assert same["pre_signatures"] == replacement["pre_signatures"]
    assert same["post_signatures"] == replacement["post_signatures"]
    assert same["post_match_counts"] == replacement["post_match_counts"]
    assert aliased["status"] == "UNKNOWN_INCOMPLETE"
    return {
        "status": "PASS",
        "persistent_variant": same,
        "perfect_copy_replacement_variant": replacement,
        "aliased_post": aliased,
        "budget_hostile": budget,
        "persistent_vs_perfect_copy_replacement_operationally_indistinguishable": True,
        "numerical_identity_authority": "NONE",
        "semantic_reference_authority": "NONE",
        "new_referent_manager_required": "NO__EXISTING_EVIDENCE_LEDGER_ONLY",
        "earned": "PERSISTED_OPERATIONAL_REFERENT_SIGNATURE_CLASSES_CAN_REASSOCIATE_AFTER_RESTART_CROSSING_AND_OCCLUSION_WITHOUT_NUMERICAL_IDENTITY_OR_SEMANTIC_REFERENCE_AUTHORITY",
    }


def main() -> None:
    print(json.dumps(run_ms2002(), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
