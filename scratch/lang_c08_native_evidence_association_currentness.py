from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from microseed import Microseed,EpistemicStatus
from scratch.lang_c02_multi_token_restart_revalidation import build_two_relations
from scratch.lang_c07_observed_token_relation_binding import (
    paired_relation_token_episode,derive_observed_token_relation_bindings,
)


def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def _build_c07_binding(ms,world,token_a="K7",token_b="M2"):
    train=[]; hold=[]
    for i in range(20):
        mode="PQ" if i%2==0 else "QP"; token=token_a if mode=="PQ" else token_b
        train.append(paired_relation_token_episode(ms,world,"A" if i%3 else "B",i,mode,token))
    for i in range(10):
        mode="QP" if i%2==0 else "PQ"; token=token_b if mode=="QP" else token_a
        hold.append(paired_relation_token_episode(ms,world,"B" if i%3 else "A",100+i,mode,token))
    binding=derive_observed_token_relation_bindings(ms,tuple(train),tuple(hold))
    assert binding["status"]=="OBSERVED_OPAQUE_TOKEN_RELATION_BINDINGS_RESEARCH_ONLY",binding
    return binding


def _register_native_records(ms,binding):
    action_ids_before=set(ms.capabilities.contracts)
    refs=((binding["binding_evidence_id"],binding["binding_evidence_sha256"]),)
    records={}
    for row in binding["bindings"]:
        right_digest=_sha(row["relation_order"])
        rec=ms.register_opaque_evidence_association(
            left_opaque_id=row["opaque_token"],right_digest_sha256=right_digest,
            source_evidence_refs=refs,
            assistance_ancestry=("C07_CONTENT_BOUND_BINDING_EVIDENCE","C08_RESEARCH_ADMISSION"),
        )
        records[row["opaque_token"]]=rec
    assert set(ms.capabilities.contracts)==action_ids_before
    return records


def _append_external_currentness_witness(ms,record,observed_digest,evidence_id):
    # Deliberately explicit assistance surface: C08A does not claim this digest was
    # organism-derived. It tests only the native record/currentness lifecycle.
    payload={
        "kind":"OPAQUE_ASSOCIATION_CURRENTNESS_OBSERVATION",
        "record_id":record["record_id"],"left_opaque_id":record["left_opaque_id"],
        "observed_right_digest_sha256":str(observed_digest),
        "assistance_ancestry":"HARNESS_SUPPLIED_CURRENT_RELATION_DIGEST_FOR_C08A_ONLY",
    }
    ref=ms.append_evidence(evidence_id,payload,EpistemicStatus.PRESSURE_SUPPORTED,source="C08A-EXTERNAL-CURRENTNESS-WITNESS")
    return ref


def run_campaign():
    with tempfile.TemporaryDirectory(prefix="lang-c08-") as td:
        state=Path(td)
        ms,world,rx,ry=build_two_relations(state)
        try:
            action_ids_before=set(ms.capabilities.contracts)
            binding=_build_c07_binding(ms,world)
            records=_register_native_records(ms,binding)
            tokens=sorted(records)
            a,b=tokens[0],tokens[1]
            ra,rb=records[a],records[b]
            initial_a=ms.opaque_evidence_association_status(ra["record_id"])
            initial_b=ms.opaque_evidence_association_status(rb["record_id"])
            assert initial_a["status"]==initial_b["status"]=="CURRENT_OPAQUE_EVIDENCE_ASSOCIATION"

            # The native registry can selectively stale one association from a durable witness.
            _append_external_currentness_witness(ms,ra,rb["right_digest_sha256"],"E-C08A-DRIFT-A")
            drift_a=ms.assess_opaque_evidence_association_currentness(ra["record_id"],witness_evidence_id="E-C08A-DRIFT-A")
            assert drift_a["status"]=="DRIFT_WITNESS"
            stale_a=ms.opaque_evidence_association_status(ra["record_id"])
            still_b=ms.opaque_evidence_association_status(rb["record_id"])
            assert stale_a["status"]=="STALE_OPAQUE_EVIDENCE_ASSOCIATION"
            assert still_b["status"]=="CURRENT_OPAQUE_EVIDENCE_ASSOCIATION"
            action_ids_after=set(ms.capabilities.contracts)
        finally:
            ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()

        # Restart: history survives, but non-stale bytes do not self-authorize currentness.
        ms2=Microseed(state)
        try:
            restart_a=ms2.opaque_evidence_association_status(ra["record_id"])
            restart_b=ms2.opaque_evidence_association_status(rb["record_id"])
            assert restart_a["status"]=="STALE_OPAQUE_EVIDENCE_ASSOCIATION"
            assert restart_b["status"]=="REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"

            # A fresh externally-authored matching digest can exercise the native revalidation
            # lifecycle, but this is explicitly NOT accepted as full organism-owned C08 currentness.
            _append_external_currentness_witness(ms2,rb,rb["right_digest_sha256"],"E-C08A-ASSISTED-REVALIDATE-B")
            assisted_b=ms2.assess_opaque_evidence_association_currentness(rb["record_id"],witness_evidence_id="E-C08A-ASSISTED-REVALIDATE-B")
            assert assisted_b["status"]=="CURRENTNESS_CONFIRMED"
            after_assisted_b=ms2.opaque_evidence_association_status(rb["record_id"])
            assert after_assisted_b["status"]=="CURRENT_OPAQUE_EVIDENCE_ASSOCIATION"

            # Staleness is durable: later matching witness cannot reactivate A.
            _append_external_currentness_witness(ms2,ra,ra["right_digest_sha256"],"E-C08A-LATE-GREEN-A")
            late_a=ms2.assess_opaque_evidence_association_currentness(ra["record_id"],witness_evidence_id="E-C08A-LATE-GREEN-A")
            after_late_a=ms2.opaque_evidence_association_status(ra["record_id"])
            assert late_a["status"]=="CURRENTNESS_CONFIRMED"
            assert after_late_a["status"]=="STALE_OPAQUE_EVIDENCE_ASSOCIATION"

            snapshot=ms2.opaque_evidence_association_state()
            assert snapshot["stale_count"]==1 and snapshot["current_count"]==1
            assert not hasattr(ms2,"predicate_registry")
            assert not hasattr(ms2,"meaning_registry")
            assert not hasattr(ms2,"language_module")
            assert not hasattr(ms2,"faculty_registry")
        finally:
            ms2.biography.close();ms2.evidence.conn.close();ms2.store.conn.close()

    return {
        "status":"STOP_C08_PARTIAL_NATIVE_MECHANISM__FULL_CURRENTNESS_NOT_EARNED",
        "native_record_lifecycle":"PASS",
        "initial_current":[initial_a["status"],initial_b["status"]],
        "selective_drift":{"affected":stale_a["status"],"unrelated":still_b["status"]},
        "restart":{"drifted":restart_a["status"],"nonstale":restart_b["status"]},
        "assisted_revalidation":after_assisted_b["status"],
        "late_green_does_not_reactivate_stale":after_late_a["status"],
        "new_action_contracts_registered":sorted(action_ids_after-action_ids_before),
        "localized_missing_mechanism":"NATIVE_C06_B1_RELATION_CURRENTNESS_EVIDENCE_OWNER",
        "reason_full_c08_not_earned":"CURRENTNESS_WITNESS_OBSERVED_RIGHT_DIGEST_IS_STILL_AUTHORED_BY_EXTERNAL_RESEARCH_HARNESS",
        "earned_bounded":"DURABLE_C07_ASSOCIATION_CAN_BE_EMBODIED_AS_A_GENERIC_NATIVE_EVIDENCE_BOUND_RECORD_WITH_SELECTIVE_STALENESS_AND_RESTART_REVALIDATION_REQUIRED_WITHOUT_SEMANTIC_EXECUTION_OR_LANGUAGE_AUTHORITY",
        "not_earned":["ORGANISM_OWNED_C06_RELATION_CURRENTNESS","SEMANTIC_PREDICATE","TOKEN_MEANING","LANGUAGE_FACULTY","GENERIC_CAPABILITY","EXECUTION_AUTHORITY","CANON_PROMOTION"],
        "next":"C08B_NATIVE_C06_B1_RELATION_CURRENTNESS_OWNER_FROM_ORGANISM_OWNED_EVIDENCE_BEFORE_TOKEN_ASSOCIATION_REVALIDATION",
    }

if __name__=="__main__": print(json.dumps(run_campaign(),indent=2,sort_keys=True))
