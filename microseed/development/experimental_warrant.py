from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any


def _digest(payload: object) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


@dataclass(frozen=True)
class ConstitutionalExperimentalWarrant:
    """Exact one-shot N1A carrier; it owns no selector, safety claim, or handler."""

    warrant_id: str
    subject_id: str
    capability_id: str
    capability_epoch: int
    capability_signature_sha256: str
    obligation_id: str
    operational_scope_id: str | None
    issue_state_id: str
    issue_state_evidence_id: str
    value_frame_digest_sha256: str
    value_frame_rows: tuple[tuple[str, int, float, str], ...]
    max_invocations: int = 1
    authority: str = "NAKED_EXPERIMENTAL_EFFECT_ONCE"
    purpose: str = "FIRST_UNMODELED_PHYSICAL_SAMPLE"
    residual_risk_status: str = "UNKNOWN_INCOMPLETE_ACCEPTED_BY_N1A_CONSTITUTION"
    selection_authority: str = "UNIQUE_ELIGIBILITY_ONLY"
    truth_authority: str = "NONE"
    semantic_goal_authority: str = "NONE"
    information_value_authority: str = "NONE"

    def serializable(self) -> dict[str, Any]:
        d = asdict(self)
        d["value_frame_rows"] = [list(x) for x in self.value_frame_rows]
        return d

    @classmethod
    def from_serializable(cls, d: dict[str, Any]) -> "ConstitutionalExperimentalWarrant":
        return cls(
            warrant_id=str(d["warrant_id"]), subject_id=str(d["subject_id"]),
            capability_id=str(d["capability_id"]), capability_epoch=int(d["capability_epoch"]),
            capability_signature_sha256=str(d["capability_signature_sha256"]),
            obligation_id=str(d["obligation_id"]), operational_scope_id=d.get("operational_scope_id"),
            issue_state_id=str(d["issue_state_id"]), issue_state_evidence_id=str(d["issue_state_evidence_id"]),
            value_frame_digest_sha256=str(d["value_frame_digest_sha256"]),
            value_frame_rows=tuple((str(x[0]), int(x[1]), float(x[2]), str(x[3])) for x in d.get("value_frame_rows", ())),
            max_invocations=int(d.get("max_invocations", 1)), authority=str(d.get("authority", "NAKED_EXPERIMENTAL_EFFECT_ONCE")),
            purpose=str(d.get("purpose", "FIRST_UNMODELED_PHYSICAL_SAMPLE")),
            residual_risk_status=str(d.get("residual_risk_status", "UNKNOWN_INCOMPLETE_ACCEPTED_BY_N1A_CONSTITUTION")),
            selection_authority=str(d.get("selection_authority", "UNIQUE_ELIGIBILITY_ONLY")),
            truth_authority=str(d.get("truth_authority", "NONE")), semantic_goal_authority=str(d.get("semantic_goal_authority", "NONE")),
            information_value_authority=str(d.get("information_value_authority", "NONE")),
        )


def subject_id(*, capability_id: str, capability_epoch: int, capability_signature_sha256: str, obligation_id: str, operational_scope_id: str | None) -> str:
    return "N1A-SUBJECT-" + _digest({
        "capability_id": capability_id, "capability_epoch": int(capability_epoch),
        "capability_signature_sha256": capability_signature_sha256,
        "obligation_id": obligation_id, "operational_scope_id": operational_scope_id,
    })[:24]


def issue_warrant(*, capability_id: str, capability_epoch: int, capability_signature_sha256: str,
                  obligation_id: str, operational_scope_id: str | None,
                  issue_state_id: str, issue_state_evidence_id: str,
                  value_frame_digest_sha256: str,
                  value_frame_rows: tuple[tuple[str, int, float, str], ...]) -> ConstitutionalExperimentalWarrant:
    sid = subject_id(
        capability_id=capability_id, capability_epoch=capability_epoch,
        capability_signature_sha256=capability_signature_sha256,
        obligation_id=obligation_id, operational_scope_id=operational_scope_id,
    )
    payload = {
        "subject_id": sid, "capability_id": capability_id, "capability_epoch": int(capability_epoch),
        "capability_signature_sha256": capability_signature_sha256, "obligation_id": obligation_id,
        "operational_scope_id": operational_scope_id, "issue_state_id": issue_state_id,
        "issue_state_evidence_id": issue_state_evidence_id,
        "value_frame_digest_sha256": value_frame_digest_sha256,
        "value_frame_rows": value_frame_rows, "max_invocations": 1,
    }
    return ConstitutionalExperimentalWarrant(
        warrant_id="N1A-WARRANT-" + _digest(payload)[:24], subject_id=sid,
        capability_id=capability_id, capability_epoch=int(capability_epoch),
        capability_signature_sha256=capability_signature_sha256,
        obligation_id=obligation_id, operational_scope_id=operational_scope_id,
        issue_state_id=issue_state_id, issue_state_evidence_id=issue_state_evidence_id,
        value_frame_digest_sha256=value_frame_digest_sha256, value_frame_rows=value_frame_rows,
    )
