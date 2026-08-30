from __future__ import annotations

import itertools
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.cognition.referents import OperationalReferentSignature
from microseed.runtime.entity import action_result_digest
from scratch.ms2003_operational_referent_class_set_routing import CONTEXT_A, CONTEXT_B, ACTIONS


def _close(ms: Microseed) -> None:
    ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def _sig(row: dict[str, Any]) -> OperationalReferentSignature:
    return OperationalReferentSignature(
        "OPERATIONAL_REFERENT_SIGNATURE_DERIVED",
        str(row["signature_sha256"]),
        tuple((str(a),tuple(bool(x) for x in bits)) for a,bits in row["action_response_rows"]),
        "AFFORDANCE_RELATIVE_BOUNDARY_RESPONSE_ONLY",
    )


def _persist_context(ms: Microseed, tag: str, samples) -> dict[str, Any]:
    derived=ms.derive_operational_referent_signatures_from_raw_trace(samples,ACTIONS)
    assert derived["status"]=="OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE",derived
    for i,row in enumerate(derived["signature_classes"]):
        out=ms.record_operational_referent_signature(f"MS2005-{tag}-{i}",_sig(row))
        assert out["status"]=="OPERATIONAL_REFERENT_SIGNATURE_WITNESS_RECORDED",out
    context=ms.derive_current_operational_referent_class_set_context(samples,ACTIONS,max_records=128)
    assert context["status"]=="CURRENT_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SET_CONTEXT",context
    return context


def _scan_owned_signature_classes(ms: Microseed, *, max_records: int) -> dict[str, Any]:
    bound=int(max_records)
    if bound <= 0:
        return {"status":"SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED","classes":{},"authority":"NONE"}
    total=ms.evidence.count(); rows=ms.evidence.recent(bound); complete=total <= bound
    classes: dict[str, tuple[tuple[str,tuple[bool,...]],...]]={}
    conflicts=[]
    for row in rows:
        payload=row.get("payload",{})
        if not isinstance(payload,dict) or payload.get("kind")!="OPERATIONAL_REFERENT_SIGNATURE_WITNESS" or row.get("negative"):
            continue
        sha=str(payload.get("signature_sha256",""))
        response=tuple((str(a),tuple(bool(x) for x in bits)) for a,bits in payload.get("action_response_rows",()))
        if len(sha)!=64 or not response:
            continue
        prior=classes.get(sha)
        if prior is not None and prior!=response:
            conflicts.append(sha)
        classes[sha]=response
    if conflicts:
        return {"status":"OPERATIONAL_REFERENT_SIGNATURE_CONTENT_CONFLICT","conflicting_classes":tuple(sorted(set(conflicts))),"authority":"NONE"}
    if not complete:
        return {"status":"SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED","scanned_records":len(rows),"total_records":total,"classes":{},"authority":"NONE"}
    return {"status":"SATURATED_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SCAN","classes":classes,"authority":"NONE"}


def _bucket_for_classes(ms: Microseed, classes: Iterable[str]) -> str:
    coordinate=ms.operational_referent_class_set_projection_signature_sha256()
    return "refset-"+action_result_digest({
        "coordinate_signature_sha256":coordinate,
        "operational_signature_classes":list(sorted(set(str(x) for x in classes))),
    })[:20]


def reconstruct_class_set_for_bucket(
    ms: Microseed, bucket_id: str, *, max_records: int=4096,
    max_unique_classes: int=16, max_subset_size: int=6,
) -> dict[str, Any]:
    scan=_scan_owned_signature_classes(ms,max_records=max_records)
    if scan.get("status")!="SATURATED_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SCAN":
        return {"status":scan.get("status","UNKNOWN_INCOMPLETE"),"reason":"OWNED_SIGNATURE_CLASS_SCAN_NOT_SATURATED","authority":"NONE"}
    classes=tuple(sorted(scan["classes"]))
    if len(classes)>int(max_unique_classes):
        return {"status":"SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED","reason":"UNIQUE_SIGNATURE_CLASS_BUDGET_EXCEEDED","class_count":len(classes),"authority":"NONE"}
    matches=[]; tested=0
    upper=min(len(classes),int(max_subset_size))
    for size in range(1,upper+1):
        for subset in itertools.combinations(classes,size):
            tested+=1
            if _bucket_for_classes(ms,subset)==str(bucket_id): matches.append(subset)
    if not matches:
        if len(classes)>upper:
            return {"status":"SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED","reason":"SUBSET_SIZE_BUDGET_MAY_HIDE_PREIMAGE","tested_subsets":tested,"authority":"NONE"}
        return {"status":"UNKNOWN_INCOMPLETE","reason":"NO_OWNED_CLASS_SET_PREIMAGE","tested_subsets":tested,"authority":"NONE"}
    if len(matches)>1:
        return {"status":"OPERATIONAL_REFERENT_CLASS_SET_PREIMAGE_AMBIGUOUS","candidate_class_sets":tuple(matches),"tested_subsets":tested,"authority":"NONE"}
    return {"status":"OPERATIONAL_REFERENT_CLASS_SET_RECONSTRUCTED","operational_signature_classes":matches[0],"tested_subsets":tested,"authority":"NONE","identity_authority":"NONE","semantic_reference_authority":"NONE"}


def _response_multiset(class_set: Iterable[str], classes: dict[str,tuple[tuple[str,tuple[bool,...]],...]], action_id: str) -> tuple[tuple[bool,...],...]:
    out=[]
    for sha in class_set:
        rows=dict(classes[str(sha)])
        if str(action_id) not in rows:
            raise KeyError(f"ACTION_RESPONSE_NOT_OWNED:{action_id}:{sha}")
        out.append(tuple(rows[str(action_id)]))
    return tuple(sorted(out))


def derive_informative_probe_candidates(
    ms: Microseed, alternative_buckets: Iterable[str], action_ids: Iterable[str], *, max_records: int=4096,
) -> dict[str, Any]:
    scan=_scan_owned_signature_classes(ms,max_records=max_records)
    if scan.get("status")!="SATURATED_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SCAN":
        return {"status":scan.get("status","UNKNOWN_INCOMPLETE"),"authority":"NONE"}
    alternatives=[]
    for bucket in tuple(str(x) for x in alternative_buckets):
        r=reconstruct_class_set_for_bucket(ms,bucket,max_records=max_records)
        if r.get("status")!="OPERATIONAL_REFERENT_CLASS_SET_RECONSTRUCTED":
            return {"status":"DEFER_UNKNOWN","reason":r.get("status","CLASS_SET_NOT_RECONSTRUCTED"),"bucket_id":bucket,"authority":"NONE"}
        alternatives.append((bucket,tuple(r["operational_signature_classes"])))
    candidates=[]
    for action in tuple(sorted(set(str(x) for x in action_ids))):
        partition=[]
        for bucket,class_set in alternatives:
            partition.append((bucket,_response_multiset(class_set,scan["classes"],action)))
        unique={response for _,response in partition}
        if len(unique)>1:
            candidates.append({"action_id":action,"predicted_response_partition":tuple(partition)})
    base={
        "alternative_buckets":tuple(bucket for bucket,_ in alternatives),
        "reconstructed_class_sets":tuple(alternatives),
        "informative_candidates":tuple(candidates),
        "selection_authority":"NONE","execution_authority":"NONE","truth_authority":"NONE",
        "identity_authority":"NONE","semantic_reference_authority":"NONE",
    }
    if not candidates: return {**base,"status":"NO_CURRENT_INFORMATIVE_REFERENT_PROBE"}
    if len(candidates)>1: return {**base,"status":"CURRENT_REFERENT_PROBE_AMBIGUOUS"}
    return {**base,"status":"CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE","probe_action_id":candidates[0]["action_id"]}


def run_ms2005() -> dict[str, Any]:
    td=tempfile.TemporaryDirectory(prefix="ms2005-refprobe-")
    root=Path(td.name)
    ms=Microseed(root)
    try:
        ca=_persist_context(ms,"A",CONTEXT_A); cb=_persist_context(ms,"B",CONTEXT_B)
        bucket_a=str(ca["projection_bucket_id"]); bucket_b=str(cb["projection_bucket_id"])
        expected_a=tuple(ca["operational_signature_classes"]); expected_b=tuple(cb["operational_signature_classes"])
    finally:
        _close(ms)
    # Restart: only durable evidence remains available to reconstruction.
    ms2=Microseed(root)
    try:
        ra=reconstruct_class_set_for_bucket(ms2,bucket_a,max_records=128)
        rb=reconstruct_class_set_for_bucket(ms2,bucket_b,max_records=128)
        assert ra["status"]==rb["status"]=="OPERATIONAL_REFERENT_CLASS_SET_RECONSTRUCTED",(ra,rb)
        assert tuple(ra["operational_signature_classes"])==expected_a
        assert tuple(rb["operational_signature_classes"])==expected_b
        probes=derive_informative_probe_candidates(ms2,(bucket_a,bucket_b),ACTIONS,max_records=128)
        assert probes["status"]=="CURRENT_REFERENT_PROBE_AMBIGUOUS",probes
        ids=tuple(x["action_id"] for x in probes["informative_candidates"])
        assert ids==("P2","P4"),ids
        zero=reconstruct_class_set_for_bucket(ms2,bucket_a,max_records=0)
        assert zero["status"]=="SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED",zero
        return {
            "status":"PASS","bucket_a":bucket_a,"bucket_b":bucket_b,
            "reconstructed_a":list(ra["operational_signature_classes"]),
            "reconstructed_b":list(rb["operational_signature_classes"]),
            "informative_probe_ids":list(ids),"probe_status":probes["status"],
            "false_information_from_class_labels_rejected":"YES__RESPONSE_MULTISET_ONLY",
            "restart_reconstruction":"PASS","bounded_zero_scan":zero["status"],
            "new_durable_bucket_class_map_required":"NO",
            "new_probe_selector_required":"NO",
            "selection_authority":"NONE","execution_authority":"NONE","truth_authority":"NONE",
            "identity_authority":"NONE","semantic_reference_authority":"NONE",
        }
    finally:
        _close(ms2); td.cleanup()



def _samples_from_boundaries(boundary_sets: tuple[tuple[int,...],...], action_count: int) -> tuple[tuple[int,...],...]:
    vals=[0 for _ in boundary_sets]; rows=[tuple(vals)]
    for t in range(1,action_count+1):
        for i,b in enumerate(boundary_sets):
            if t in b: vals[i]=1-vals[i]
        rows.append(tuple(vals))
    return tuple(rows)


UNIQUE_A=_samples_from_boundaries(((1,),(1,),(2,),(2,)),len(ACTIONS))
UNIQUE_B=_samples_from_boundaries(((1,),(1,),(2,3),(2,3)),len(ACTIONS))


def run_ms2005_unique_probe() -> dict[str, Any]:
    td=tempfile.TemporaryDirectory(prefix="ms2005-refprobe-unique-")
    root=Path(td.name); ms=Microseed(root)
    try:
        ca=_persist_context(ms,"UNIQUE-A",UNIQUE_A); cb=_persist_context(ms,"UNIQUE-B",UNIQUE_B)
        ba=str(ca["projection_bucket_id"]); bb=str(cb["projection_bucket_id"])
    finally:
        _close(ms)
    ms2=Microseed(root)
    try:
        out=derive_informative_probe_candidates(ms2,(ba,bb),ACTIONS,max_records=128)
        assert out["status"]=="CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE",out
        assert out["probe_action_id"]=="P2",out
        return {
            "status":"PASS","probe_status":out["status"],"probe_action_id":out["probe_action_id"],
            "alternative_buckets":list(out["alternative_buckets"]),
            "informative_probe_ids":[x["action_id"] for x in out["informative_candidates"]],
            "restart_reconstruction":"PASS","caller_supplied_probe_schedule":"NO",
            "probe_selection_authority":"NONE","execution_authority":"NONE","truth_authority":"NONE",
            "identity_authority":"NONE","semantic_reference_authority":"NONE",
        }
    finally:
        _close(ms2); td.cleanup()

def main() -> None:
    print(json.dumps({"ambiguous_case":run_ms2005(),"unique_case":run_ms2005_unique_probe()},indent=2,sort_keys=True))

if __name__=="__main__": main()
