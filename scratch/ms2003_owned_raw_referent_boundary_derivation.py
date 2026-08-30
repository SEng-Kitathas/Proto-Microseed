from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.cognition.referents import OperationalReferentSignature
from scratch.ms1995_crossing_occlusion_reassociation import CrossingWorld, SCHEDULE


def _close(ms: Microseed) -> None:
    ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def _raw(world: CrossingWorld, phase: str) -> tuple[tuple[int, ...], ...]:
    world.phase(phase)
    samples=[world.observe()]
    for action in SCHEDULE:
        world.act(action); samples.append(world.observe())
    return tuple(samples)


def _sig(row: dict[str, object]) -> OperationalReferentSignature:
    return OperationalReferentSignature(
        status="OPERATIONAL_REFERENT_SIGNATURE_DERIVED",
        signature_sha256=str(row["signature_sha256"]),
        action_response_rows=tuple(
            (str(a),tuple(bool(x) for x in bits))
            for a,bits in row["action_response_rows"]  # type: ignore[index]
        ),
        reason="AFFORDANCE_RELATIVE_BOUNDARY_RESPONSE_ONLY",
    )


def run_variant(variant: str) -> dict[str, object]:
    td=tempfile.TemporaryDirectory(prefix=f"ms2003-owned-raw-{variant.lower()}-")
    root=Path(td.name); world=CrossingWorld()
    try:
        world.call("reset")
        pre_samples=_raw(world,"PRE")
        ms=Microseed(root)
        try:
            pre=ms.derive_operational_referent_signatures_from_raw_trace(pre_samples,SCHEDULE)
            assert pre["status"]=="OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE",pre
            assert len(pre["signature_classes"])==2
            for i,row in enumerate(pre["signature_classes"]):
                ms.record_operational_referent_signature(f"MS2003-PRE-{variant}-{i}",_sig(row))
        finally:_close(ms)

        cross_samples=_raw(world,"CROSS")
        ms=Microseed(root)
        try:
            cross=ms.derive_operational_referent_signatures_from_raw_trace(cross_samples,SCHEDULE)
            assert cross["status"]=="OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE",cross
            pre_sigs=sorted(str(x["signature_sha256"]) for x in pre["signature_classes"])
            cross_sigs=sorted(str(x["signature_sha256"]) for x in cross["signature_classes"])
            assert cross_sigs==pre_sigs
            matches=[]
            for row in cross["signature_classes"]:
                m=ms.reassociate_operational_referent_signature(_sig(row),max_records=64)
                assert m["status"]=="OPERATIONAL_REFERENT_SIGNATURE_CLASS_REASSOCIATED",m
                matches.append(m)
        finally:_close(ms)

        # Occlusion/symmetry must remain unknown without caller fixing the partition.
        occluded_samples=_raw(world,"OCCLUDE_A")
        ms=Microseed(root)
        try:
            occluded=ms.derive_operational_referent_signatures_from_raw_trace(occluded_samples,SCHEDULE)
            assert occluded["status"]=="UNKNOWN_INCOMPLETE",occluded
            assert occluded["reason"]=="BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS"
        finally:_close(ms)

        world.call("gap"); assert world.observe()==()
        world.call("reappear",variant=variant)
        post_samples=_raw(world,"POST")
        ms=Microseed(root)
        try:
            post=ms.derive_operational_referent_signatures_from_raw_trace(post_samples,SCHEDULE)
            if variant=="ALIASED_POST":
                assert post["status"]=="UNKNOWN_INCOMPLETE",post
                assert post["reason"]=="BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS"
                return {"variant":variant,"status":"UNKNOWN_INCOMPLETE","reason":post["reason"],
                        "identity_authority":"NONE","semantic_reference_authority":"NONE"}
            assert post["status"]=="OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE",post
            post_sigs=sorted(str(x["signature_sha256"]) for x in post["signature_classes"])
            assert post_sigs==pre_sigs
            post_matches=[]
            for row in post["signature_classes"]:
                m=ms.reassociate_operational_referent_signature(_sig(row),max_records=64)
                assert m["status"]=="OPERATIONAL_REFERENT_SIGNATURE_CLASS_REASSOCIATED",m
                post_matches.append(m)
            return {
                "variant":variant,"status":"PASS","pre_signatures":pre_sigs,
                "cross_signatures":cross_sigs,"post_signatures":post_sigs,
                "cross_match_counts":sorted(int(x["match_count"]) for x in matches),
                "post_match_counts":sorted(int(x["match_count"]) for x in post_matches),
                "caller_supplied_boundaries":pre["caller_supplied_boundary_signatures"],
                "caller_supplied_groups":pre["caller_supplied_referent_groups"],
                "caller_supplied_classes":pre["caller_supplied_referent_classes"],
                "identity_authority":"NONE","semantic_reference_authority":"NONE",
            }
        finally:_close(ms)
    finally:
        world.close(); td.cleanup()


def run_malformed() -> dict[str, object]:
    td=tempfile.TemporaryDirectory(prefix="ms2003-malformed-"); ms=Microseed(Path(td.name))
    try:
        too_short=ms.derive_operational_referent_signatures_from_raw_trace(((0,1),),())
        ragged=ms.derive_operational_referent_signatures_from_raw_trace(((0,1),(1,)),("A",))
        action_mismatch=ms.derive_operational_referent_signatures_from_raw_trace(((0,1),(1,1),(1,0)),("A",))
        assert too_short["status"]==ragged["status"]==action_mismatch["status"]=="UNKNOWN_INCOMPLETE"
        return {"too_short":too_short["reason"],"ragged":ragged["reason"],"action_mismatch":action_mismatch["reason"]}
    finally:_close(ms); td.cleanup()


def run_ms2003_owned_raw_boundary() -> dict[str, object]:
    persistent=run_variant("PERSIST")
    copy=run_variant("REPLACE_BOTH_PERFECT_COPY")
    alias=run_variant("ALIASED_POST")
    malformed=run_malformed()
    assert persistent["status"]==copy["status"]=="PASS"
    assert persistent["pre_signatures"]==copy["pre_signatures"]
    assert persistent["post_signatures"]==copy["post_signatures"]
    assert alias["status"]=="UNKNOWN_INCOMPLETE"
    return {
        "status":"PASS","persistent":persistent,"perfect_copy":copy,"aliased":alias,"malformed":malformed,
        "perfect_copy_operationally_indistinguishable":True,
        "numerical_identity_authority":"NONE","semantic_reference_authority":"NONE",
        "boundary_derivation_owner":"MICROSEED_DETERMINISTIC_RAW_TRACE_DERIVATION",
        "new_referent_manager_required":"NO",
        "earned":"RAW_OBSERVATION_HISTORY_CAN_DERIVE_BOUNDARY_COHERENT_OPERATIONAL_SIGNATURE_CLASSES_INSIDE_MICROSEED_WITHOUT_CALLER_BOUNDARIES_GROUPS_CLASSES_OR_IDENTITY_AUTHORITY",
    }


def main() -> None: print(json.dumps(run_ms2003_owned_raw_boundary(),indent=2,sort_keys=True))
if __name__=="__main__": main()
