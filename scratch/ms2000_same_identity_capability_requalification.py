from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import json
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.development.capability_admission import ExternalCapabilityQualifier
from microseed.runtime.types import (
    Authority,
    CapabilityContract,
    EpistemicStatus,
    QualificationState,
    QueryObligation,
)


def _effect(cid: str, deps: tuple[str, ...] = ()) -> CapabilityContract:
    return CapabilityContract(
        capability_id=cid,
        purpose="opaque-effect",
        boundary={},
        interface={},
        invariants=("NO_SEMANTIC_AUTHORITY",),
        hazards=(),
        authority=Authority.EFFECT,
        lineage=("MS2000",),
        currentness="CURRENT",
        resources={},
        dependencies=deps,
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda token=cid: token,
    )


def _fresh_support(ms: Microseed, eid: str):
    return ms.append_evidence(
        eid,
        {"fresh_currentness_support": True},
        EpistemicStatus.PROVED,
        source="MS2000-HSP",
    )


def _negative(ms: Microseed, eid: str):
    return ms.append_evidence(
        eid,
        {"contradiction": True},
        EpistemicStatus.VIOLATED,
        negative=True,
        source="MS2000-HSP",
    )


def run_ms2000() -> dict[str, object]:
    with tempfile.TemporaryDirectory() as td:
        ms = Microseed(Path(td))
        try:
            for c in (
                _effect("RQ-ROOT"),
                _effect("RQ-MID", ("RQ-ROOT",)),
                _effect("RQ-LEAF", ("RQ-MID",)),
            ):
                ms.register_capability(c)

            original_signatures = {
                cid: ms.capabilities.contracts[cid].computed_signature_sha256()
                for cid in ("RQ-ROOT", "RQ-MID", "RQ-LEAF")
            }
            original_authorities = {
                cid: ms.capabilities.contracts[cid].authority.value
                for cid in ("RQ-ROOT", "RQ-MID", "RQ-LEAF")
            }

            stale = ms.change_capability_dependency("RQ-ROOT", reason="MS2000_LOCAL_DRIFT")
            stale_epochs = {cid: ms.capabilities.epochs[cid] for cid in sorted(stale)}
            assert stale == {"RQ-ROOT", "RQ-MID", "RQ-LEAF"}
            assert all(not ms.capabilities.is_current(cid) for cid in stale)

            hsp = ExternalCapabilityQualifier(ms.evidence, qualifier_id="MS2000-HSP-EXTERNAL")
            support = {
                cid: _fresh_support(ms, f"MS2000-SUPPORT-{cid}")
                for cid in ("RQ-ROOT", "RQ-MID", "RQ-LEAF")
            }
            tickets = {
                cid: hsp.requalify(
                    ms.capabilities.contracts[cid],
                    stale_epoch=ms.capabilities.epochs[cid],
                    qualification_evidence=(support[cid],),
                )
                for cid in ("RQ-ROOT", "RQ-MID", "RQ-LEAF")
            }

            # Dependent cannot jump ahead of stale ancestry.
            dependent_before_root = None
            try:
                ms.requalify_capability(tickets["RQ-MID"])
            except ValueError as exc:
                dependent_before_root = str(exc)
            assert dependent_before_root and dependent_before_root.startswith(
                "CAPABILITY_REACTIVATION_DEPENDENCY_NOT_CURRENT:RQ-ROOT:"
            )

            # Signature forgery cannot reactivate.
            forged = replace(tickets["RQ-ROOT"], contract_signature_sha256="f" * 64)
            forged_result = None
            try:
                ms.requalify_capability(forged)
            except ValueError as exc:
                forged_result = str(exc)
            assert forged_result == "REQUALIFICATION_CONTRACT_SIGNATURE_MISMATCH"

            # Stale-epoch replay cannot reactivate.
            replay = replace(tickets["RQ-ROOT"], stale_epoch=tickets["RQ-ROOT"].stale_epoch - 1)
            replay_result = None
            try:
                ms.requalify_capability(replay)
            except ValueError as exc:
                replay_result = str(exc)
            assert replay_result == "REQUALIFICATION_STALE_EPOCH_MISMATCH"

            # Negative evidence cannot produce an admissible requalification.
            neg = _negative(ms, "MS2000-NEGATIVE-ROOT")
            negative_ticket = hsp.requalify(
                ms.capabilities.contracts["RQ-ROOT"],
                stale_epoch=ms.capabilities.epochs["RQ-ROOT"],
                qualification_evidence=(neg,),
            )
            negative_result = None
            try:
                ms.requalify_capability(negative_ticket)
            except ValueError as exc:
                negative_result = str(exc)
            assert negative_result == "REQUALIFICATION_NOT_ADMISSIBLE:REJECTED"

            root_stale_epoch = ms.capabilities.epochs["RQ-ROOT"]
            ms.requalify_capability(tickets["RQ-ROOT"])
            root_current_epoch = ms.capabilities.epochs["RQ-ROOT"]
            assert root_current_epoch == root_stale_epoch + 1
            assert ms.capabilities.is_current("RQ-ROOT")
            assert not ms.capabilities.is_current("RQ-MID")
            assert not ms.capabilities.is_current("RQ-LEAF")

            # Old exact ticket is now replay-stale because the capability is already current.
            second_use_result = None
            try:
                ms.requalify_capability(tickets["RQ-ROOT"])
            except ValueError as exc:
                second_use_result = str(exc)
            assert second_use_result == "CAPABILITY_REQUALIFICATION_REQUIRES_STALE:RQ-ROOT"

            ms.requalify_capability(tickets["RQ-MID"])
            assert ms.capabilities.is_current("RQ-MID")
            assert not ms.capabilities.is_current("RQ-LEAF")
            ms.requalify_capability(tickets["RQ-LEAF"])
            assert ms.capabilities.is_current("RQ-LEAF")

            q = QueryObligation("MS2000-Q", "opaque")
            invoked = ms.capabilities.invoke("RQ-LEAF", q)
            assert invoked["status"] == "CAPABILITY_RESULT"
            assert invoked["authority"] == Authority.EFFECT.value

            assert {
                cid: ms.capabilities.contracts[cid].computed_signature_sha256()
                for cid in original_signatures
            } == original_signatures
            assert {
                cid: ms.capabilities.contracts[cid].authority.value
                for cid in original_authorities
            } == original_authorities

            # Cycle cannot bootstrap itself through pairwise requalification.
            ms.register_capability(_effect("RQ-CYCLE-A", ("RQ-CYCLE-B",)))
            ms.register_capability(_effect("RQ-CYCLE-B", ("RQ-CYCLE-A",)))
            cyc_stale = ms.invalidate_capability("RQ-CYCLE-A", reason="MS2000_CYCLE_STALE")
            assert cyc_stale == {"RQ-CYCLE-A", "RQ-CYCLE-B"}
            cyc_support_a = _fresh_support(ms, "MS2000-SUPPORT-CYCLE-A")
            cyc_support_b = _fresh_support(ms, "MS2000-SUPPORT-CYCLE-B")
            cyc_ticket_a = hsp.requalify(
                ms.capabilities.contracts["RQ-CYCLE-A"],
                stale_epoch=ms.capabilities.epochs["RQ-CYCLE-A"],
                qualification_evidence=(cyc_support_a,),
            )
            cyc_ticket_b = hsp.requalify(
                ms.capabilities.contracts["RQ-CYCLE-B"],
                stale_epoch=ms.capabilities.epochs["RQ-CYCLE-B"],
                qualification_evidence=(cyc_support_b,),
            )
            cycle_errors = []
            for ticket in (cyc_ticket_a, cyc_ticket_b):
                try:
                    ms.requalify_capability(ticket)
                except ValueError as exc:
                    cycle_errors.append(str(exc))
            assert len(cycle_errors) == 2
            assert all("CAPABILITY_REACTIVATION_DEPENDENCY_NOT_CURRENT" in x for x in cycle_errors)
            assert not ms.capabilities.is_current("RQ-CYCLE-A")
            assert not ms.capabilities.is_current("RQ-CYCLE-B")

            events = [e for e in ms.store.events() if e["kind"] == "CAPABILITY_REQUALIFIED"]
            assert [e["payload"]["capability_id"] for e in events] == [
                "RQ-ROOT", "RQ-MID", "RQ-LEAF"
            ]
            assert all(e["payload"]["authority_gain"] == "NONE" for e in events)
            assert all(e["payload"]["dependent_auto_reactivation"] == "NONE" for e in events)

            return {
                "status": "PASS",
                "stale_set": sorted(stale),
                "stale_epochs": stale_epochs,
                "current_epochs": {
                    cid: ms.capabilities.epochs[cid]
                    for cid in ("RQ-ROOT", "RQ-MID", "RQ-LEAF")
                },
                "dependent_before_root": dependent_before_root,
                "forged_signature": forged_result,
                "stale_epoch_replay": replay_result,
                "negative_evidence": negative_result,
                "second_ticket_use": second_use_result,
                "cycle_errors": cycle_errors,
                "final_invoke": invoked,
                "same_identity_signatures_preserved": True,
                "authority_preserved": original_authorities,
                "ticket_authority_field": "ABSENT",
                "dependent_auto_reactivation": "NONE",
                "new_manager_required": "NO",
                "self_qualification_authority": "NONE",
            }
        finally:
            ms.biography.close()
            ms.evidence.conn.close()
            ms.store.conn.close()


def main() -> None:
    print(json.dumps(run_ms2000(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
