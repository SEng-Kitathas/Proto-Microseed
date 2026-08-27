from __future__ import annotations
import hashlib, json, tempfile, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from microseed import (
    Microseed, Authority, CapabilityContract, QualificationState,
    OperationalFrameContract, EpisodeSchemaContract, OperationalTrace,
    ExternalCapabilityQualifier, EpistemicStatus,
)


def q(cid, deps=()):
    return CapabilityContract(cid,"opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,
        ("MS903-927-REPLAY",),"CURRENT",{},dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED)


def frame():
    return OperationalFrameContract("F","opaque",hashlib.sha256(b"f").hexdigest(),
        Authority.DERIVED_READ_ONLY,("MS878-902",),"CURRENT",
        QualificationState.SHADOW_QUALIFIED,("EXTERNAL_FRAME_QUALIFICATION",),
        ("NO_SEMANTIC_IDENTITY_AUTHORITY",),())


def episode():
    return EpisodeSchemaContract(
        schema_id="EP", purpose="opaque", signature_sha256=hashlib.sha256(b"ep").hexdigest(),
        authority=Authority.DERIVED_READ_ONLY, lineage=("MS903-927",), currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXTERNAL_EPISODE_SCHEMA_QUALIFICATION",),
        frame_epochs=(("F",0),), value_epochs=(),
        invariants=("NO_SEMANTIC_EPISODE_OR_IDENTITY_AUTHORITY",), hazards=(),
    )


def build(ms):
    ms.register_operational_frame(frame()); ms.register_episode_schema(episode())
    ms.register_capability(q("A")); ms.register_capability(q("B"))
    for i in range(6):
        ms.record_operational_trace(OperationalTrace(f"a{i}",( "A",),((1.,0.),),"r0",frame_id="F",episode_schema_id="EP"))
        ms.record_operational_trace(OperationalTrace(f"b{i}",( "B",),((0.,1.),),"r0",frame_id="F",episode_schema_id="EP"))
    for scope in ("r0","r1"):
        for i in range(10):
            ms.record_operational_trace(OperationalTrace(f"m{scope}{i}",( "A","B"),((1.,0.),(0.,2.)),scope,frame_id="F",episode_schema_id="EP"))
    props=ms.discover_capability_candidates(); assert props
    return props[0]["candidate_id"]


def main():
    with tempfile.TemporaryDirectory(prefix="ms903-927-replay-") as td:
        root=Path(td); ms=Microseed(root); cid=build(ms); cand=ms.capability_candidates[cid]
        before=ms.compose([cid]).status
        ext=ms.append_evidence("HSP-MS927-REPLAY",{"heldout":.99},EpistemicStatus.PROVED,source="HSP_EXTERNAL")
        ticket=ExternalCapabilityQualifier(ms.evidence,qualifier_id="HSP-MS927-REPLAY").qualify(cand,qualification_evidence=(ext,))
        ms.admit_capability_candidate(ticket)
        ms.register_capability(q("N",deps=(cid,)))
        after=ms.compose([cid]).status; second=ms.compose(["N"]).status
        episode_epoch_before=ms.episodes.epochs["EP"]
        stale=ms.change_episode_schema("EP",reason="MS927_REPLAY_GROUPING_DRIFT")
        episode_epoch_after=ms.episodes.epochs["EP"]
        post=ms.compose(["N"]).status

        # Separate pending candidate to prove admission-time schema currentness.
        with tempfile.TemporaryDirectory(prefix="ms903-927-pending-") as td2:
            ms2=Microseed(Path(td2)); cid2=build(ms2); c2=ms2.capability_candidates[cid2]
            e2=ms2.append_evidence("HSP-MS927-PENDING",{"heldout":.99},EpistemicStatus.PROVED,source="HSP_EXTERNAL")
            t2=ExternalCapabilityQualifier(ms2.evidence,qualifier_id="HSP-MS927-REPLAY").qualify(c2,qualification_evidence=(e2,))
            ms2.change_episode_schema("EP",reason="PENDING_GROUPING_DRIFT")
            pending_rejected=False; pending_reason=None
            try: ms2.admit_capability_candidate(t2)
            except ValueError as exc: pending_rejected=True; pending_reason=str(exc)

        # Persisted trace keeps the episode provenance reference, not a selfhood claim.
        # One active writer per state directory: close the prior embodiment before restart.
        ms.store.conn.close(); ms.evidence.conn.close(); ms.biography.close()
        ms_restart=Microseed(root)
        sample=ms_restart.operational_traces[sorted(ms_restart.operational_traces)[0]]
        status=ms_restart.status()
        checks={
            "episode_epoch_bound_into_candidate": cand.operational_signature["episode_schema_epochs"] == [["EP",0]],
            "qualified_episode_schema_replaces_anonymous_trace_boundary_assistance": (
                "QUALIFIED_OPERATIONAL_EPISODE_SCHEMA:EP@0" in cand.assistance_ancestry
                and "SUPPLIED_TRACE_BOUNDARIES" not in cand.assistance_ancestry
            ),
            "proposal_not_admission": before == "NO_PATH",
            "external_admission_reuse": after == "COMPOSED_EPHEMERAL",
            "whole_becomes_part_again": second == "COMPOSED_EPHEMERAL",
            "episode_epoch_advances": episode_epoch_before == 0 and episode_epoch_after == 1,
            "episode_drift_stales_admitted_whole": cid in stale,
            "episode_drift_stales_second_order": "N" in stale,
            "post_drift_execution_conservative": post == "NO_PATH",
            "pending_episode_drift_rejected": pending_rejected and "CANDIDATE_EPISODE_SCHEMA_EPOCH_DRIFT" in (pending_reason or ""),
            "episode_provenance_persists": sample.episode_schema_id == "EP" and sample.episode_schema_epoch == 0,
            "persistence_not_selfhood": ms_restart.status()["identity_claim"] == "NOT_QUALIFIED",
            "episode_learner_not_promoted": not hasattr(ms,"record_operational_event") and not hasattr(ms,"propose_episode_grouping"),
            "prelingual_hard_stop": status["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE" and status["next_ms"] >= 1203 and status.get(f"ms{status['next_ms']}_started") is False,
        }
        out={
            "schema":"microseed.ms903-927-maindev-replay.v0.5","candidate_id":cid,
            "episode_epoch_before":episode_epoch_before,"episode_epoch_after":episode_epoch_after,
            "stale_after_episode_schema_drift":sorted(stale),"before_external_qualification":before,
            "after_external_admission":after,"second_order_before_drift":second,"second_order_after_drift":post,
            "pending_drift_rejected":pending_rejected,"pending_drift_reason":pending_reason,
            "persisted_episode_schema_id":sample.episode_schema_id,"persisted_episode_schema_epoch":sample.episode_schema_epoch,
            "status":status,"checks":checks,"all_pass":all(checks.values())}
        print(json.dumps(out,indent=2,sort_keys=True))
        return 0 if out["all_pass"] else 1

if __name__=="__main__": raise SystemExit(main())
