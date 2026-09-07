from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Callable, Iterable


def _sha256_token(value: str, *, error: str) -> str:
    v = str(value).lower()
    if len(v) != 64 or any(c not in "0123456789abcdef" for c in v):
        raise ValueError(error)
    return v


def _stable_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class OpaqueEvidenceAssociationState(str, Enum):
    CURRENT = "CURRENT"
    REVALIDATION_REQUIRED = "REVALIDATION_REQUIRED"
    STALE = "STALE"


@dataclass
class OpaqueEvidenceAssociationRecord:
    """Durable operational association with no semantic or execution authority.

    The two sides are opaque operational content.  `right_digest_sha256` is a
    content digest, not a predicate/meaning identifier.  Historical bytes and
    present currentness are deliberately separate: on process restart a replayed
    non-stale record enters REVALIDATION_REQUIRED until fresh evidence is
    assessed in the new runtime.
    """

    record_id: str
    left_opaque_id: str
    right_digest_sha256: str
    source_evidence_refs: tuple[tuple[str, str], ...]
    assistance_ancestry: tuple[str, ...] = ()
    state: OpaqueEvidenceAssociationState = OpaqueEvidenceAssociationState.CURRENT
    stale_reason: str | None = None
    stale_evidence_id: str | None = None
    authority: str = "EVIDENCE_BOUND_OPERATIONAL_ASSOCIATION_ONLY"
    truth_authority: str = "NONE"
    semantic_authority: str = "NONE"
    execution_authority: str = "NONE"
    language_authority: str = "NONE"

    def __post_init__(self) -> None:
        if not self.record_id or not self.left_opaque_id:
            raise ValueError("EMPTY_OPAQUE_EVIDENCE_ASSOCIATION_ID")
        self.right_digest_sha256 = _sha256_token(
            self.right_digest_sha256, error="INVALID_OPAQUE_EVIDENCE_ASSOCIATION_RIGHT_DIGEST"
        )
        refs = tuple((str(eid), _sha256_token(sig, error="INVALID_OPAQUE_EVIDENCE_ASSOCIATION_EVIDENCE_DIGEST")) for eid, sig in self.source_evidence_refs)
        if not refs or any(not eid for eid, _ in refs):
            raise ValueError("OPAQUE_EVIDENCE_ASSOCIATION_REQUIRES_SOURCE_EVIDENCE")
        self.source_evidence_refs = refs
        self.assistance_ancestry = tuple(str(x) for x in self.assistance_ancestry)
        self.state = OpaqueEvidenceAssociationState(self.state)
        if self.state == OpaqueEvidenceAssociationState.STALE and not self.stale_reason:
            raise ValueError("STALE_OPAQUE_EVIDENCE_ASSOCIATION_REQUIRES_REASON")
        if self.authority != "EVIDENCE_BOUND_OPERATIONAL_ASSOCIATION_ONLY" or any(
            x != "NONE" for x in (
                self.truth_authority,
                self.semantic_authority,
                self.execution_authority,
                self.language_authority,
            )
        ):
            raise ValueError("OPAQUE_EVIDENCE_ASSOCIATION_AUTHORITY_ESCALATION")

    def serializable(self) -> dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        d["source_evidence_refs"] = [list(x) for x in self.source_evidence_refs]
        d["assistance_ancestry"] = list(self.assistance_ancestry)
        return d

    @classmethod
    def from_serializable(cls, d: dict[str, Any]) -> "OpaqueEvidenceAssociationRecord":
        x = dict(d)
        x["state"] = OpaqueEvidenceAssociationState(x.get("state", "CURRENT"))
        x["source_evidence_refs"] = tuple((str(a), str(b)) for a, b in x.get("source_evidence_refs", ()))
        x["assistance_ancestry"] = tuple(str(v) for v in x.get("assistance_ancestry", ()))
        return cls(**x)


@dataclass(frozen=True)
class OpaqueEvidenceAssociationCurrentnessWitness:
    witness_id: str
    record_id: str
    evidence_id: str
    evidence_sha256: str
    expected_right_digest_sha256: str
    observed_right_digest_sha256: str
    status: str
    authority: str = "CURRENTNESS_EVIDENCE_ONLY"
    truth_authority: str = "NONE"
    semantic_authority: str = "NONE"
    execution_authority: str = "NONE"
    language_authority: str = "NONE"

    def __post_init__(self) -> None:
        if not self.witness_id or not self.record_id or not self.evidence_id:
            raise ValueError("EMPTY_OPAQUE_EVIDENCE_ASSOCIATION_WITNESS_ID")
        object.__setattr__(self, "evidence_sha256", _sha256_token(self.evidence_sha256, error="INVALID_ASSOCIATION_WITNESS_EVIDENCE_SHA"))
        object.__setattr__(self, "expected_right_digest_sha256", _sha256_token(self.expected_right_digest_sha256, error="INVALID_ASSOCIATION_WITNESS_EXPECTED_SHA"))
        object.__setattr__(self, "observed_right_digest_sha256", _sha256_token(self.observed_right_digest_sha256, error="INVALID_ASSOCIATION_WITNESS_OBSERVED_SHA"))
        if self.status not in {"CURRENTNESS_CONFIRMED", "DRIFT_WITNESS"}:
            raise ValueError("INVALID_OPAQUE_EVIDENCE_ASSOCIATION_WITNESS_STATUS")
        if self.status == "CURRENTNESS_CONFIRMED" and self.observed_right_digest_sha256 != self.expected_right_digest_sha256:
            raise ValueError("CONFIRMED_ASSOCIATION_WITNESS_DIGEST_MISMATCH")
        if self.status == "DRIFT_WITNESS" and self.observed_right_digest_sha256 == self.expected_right_digest_sha256:
            raise ValueError("DRIFT_ASSOCIATION_WITNESS_REQUIRES_MISMATCH")
        if self.authority != "CURRENTNESS_EVIDENCE_ONLY" or any(
            x != "NONE" for x in (
                self.truth_authority,
                self.semantic_authority,
                self.execution_authority,
                self.language_authority,
            )
        ):
            raise ValueError("OPAQUE_EVIDENCE_ASSOCIATION_WITNESS_AUTHORITY_ESCALATION")

    def serializable(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_serializable(cls, d: dict[str, Any]) -> "OpaqueEvidenceAssociationCurrentnessWitness":
        return cls(**dict(d))


@dataclass(frozen=True)
class OpaqueEvidenceAssociationPairWitness:
    """One exact opaque-left/content-digest-right co-occurrence; never qualification."""

    witness_id: str
    association_scope: str
    left_opaque_id: str
    right_digest_sha256: str
    source_evidence_refs: tuple[tuple[str, str], ...]
    assistance_ancestry: tuple[str, ...] = ()
    authority: str = "PAIR_OBSERVATION_EVIDENCE_ONLY"
    truth_authority: str = "NONE"
    semantic_authority: str = "NONE"
    execution_authority: str = "NONE"
    language_authority: str = "NONE"

    def __post_init__(self) -> None:
        if not self.witness_id or not self.association_scope or not self.left_opaque_id:
            raise ValueError("EMPTY_OPAQUE_ASSOCIATION_PAIR_WITNESS_ID_OR_SCOPE")
        object.__setattr__(self, "association_scope", str(self.association_scope))
        object.__setattr__(self, "right_digest_sha256", _sha256_token(self.right_digest_sha256, error="INVALID_OPAQUE_ASSOCIATION_PAIR_RIGHT_DIGEST"))
        refs=tuple((str(eid),_sha256_token(sig,error="INVALID_OPAQUE_ASSOCIATION_PAIR_EVIDENCE_DIGEST")) for eid,sig in self.source_evidence_refs)
        if not refs or any(not eid for eid,_ in refs):
            raise ValueError("OPAQUE_ASSOCIATION_PAIR_REQUIRES_SOURCE_EVIDENCE")
        object.__setattr__(self, "source_evidence_refs", refs)
        object.__setattr__(self, "assistance_ancestry", tuple(str(x) for x in self.assistance_ancestry))
        if self.authority != "PAIR_OBSERVATION_EVIDENCE_ONLY" or any(x != "NONE" for x in (self.truth_authority,self.semantic_authority,self.execution_authority,self.language_authority)):
            raise ValueError("OPAQUE_ASSOCIATION_PAIR_AUTHORITY_ESCALATION")

    def serializable(self) -> dict[str, Any]:
        d=asdict(self); d["source_evidence_refs"]=[list(x) for x in self.source_evidence_refs]; d["assistance_ancestry"]=list(self.assistance_ancestry); return d

    @classmethod
    def from_serializable(cls,d:dict[str,Any])->"OpaqueEvidenceAssociationPairWitness":
        x=dict(d); x["source_evidence_refs"]=tuple((str(a),str(b)) for a,b in x.get("source_evidence_refs",())); x["assistance_ancestry"]=tuple(str(v) for v in x.get("assistance_ancestry",())); return cls(**x)


@dataclass(frozen=True)
class OpaqueEvidenceAssociationQualificationWitness:
    """Evidence-closure adequacy witness; grants no truth, meaning, or effect authority."""

    qualification_id: str
    association_scope: str
    pair_witness_ids: tuple[str, ...]
    bindings: tuple[tuple[str, str], ...]
    method: str = "LEAVE_ONE_OUT_EXACT_BIJECTIVE_EVIDENCE_CLOSURE"
    status: str = "EPISTEMIC_ASSOCIATION_ADEQUACY_CONFIRMED"
    authority: str = "EPISTEMIC_ADEQUACY_EVIDENCE_ONLY"
    truth_authority: str = "NONE"
    semantic_authority: str = "NONE"
    execution_authority: str = "NONE"
    language_authority: str = "NONE"

    def __post_init__(self)->None:
        if not self.qualification_id or not self.association_scope or len(self.pair_witness_ids)<2:
            raise ValueError("OPAQUE_ASSOCIATION_QUALIFICATION_REQUIRES_SCOPE_AND_PAIR_EVIDENCE")
        object.__setattr__(self,"association_scope",str(self.association_scope))
        norm=tuple(sorted((str(a),_sha256_token(b,error="INVALID_QUALIFIED_ASSOCIATION_RIGHT_DIGEST")) for a,b in self.bindings))
        if len(norm)<2 or len({a for a,_ in norm})!=len(norm) or len({b for _,b in norm})!=len(norm):
            raise ValueError("QUALIFIED_OPAQUE_ASSOCIATION_REQUIRES_BIJECTION")
        object.__setattr__(self,"pair_witness_ids",tuple(str(x) for x in self.pair_witness_ids))
        object.__setattr__(self,"bindings",norm)
        if self.method!="LEAVE_ONE_OUT_EXACT_BIJECTIVE_EVIDENCE_CLOSURE" or self.status!="EPISTEMIC_ASSOCIATION_ADEQUACY_CONFIRMED":
            raise ValueError("INVALID_OPAQUE_ASSOCIATION_QUALIFICATION_METHOD_OR_STATUS")
        if self.authority!="EPISTEMIC_ADEQUACY_EVIDENCE_ONLY" or any(x!="NONE" for x in (self.truth_authority,self.semantic_authority,self.execution_authority,self.language_authority)):
            raise ValueError("OPAQUE_ASSOCIATION_QUALIFICATION_AUTHORITY_ESCALATION")

    def serializable(self)->dict[str,Any]:
        d=asdict(self); d["pair_witness_ids"]=list(self.pair_witness_ids); d["bindings"]=[list(x) for x in self.bindings]; return d

    @classmethod
    def from_serializable(cls,d:dict[str,Any])->"OpaqueEvidenceAssociationQualificationWitness":
        x=dict(d); x["pair_witness_ids"]=tuple(str(v) for v in x.get("pair_witness_ids",())); x["bindings"]=tuple((str(a),str(b)) for a,b in x.get("bindings",())); return cls(**x)


class OpaqueEvidenceAssociationRegistry:
    """Generic durable association/currentness surface; never a semantic registry."""

    def __init__(self) -> None:
        self.records: dict[str, OpaqueEvidenceAssociationRecord] = {}
        self.witnesses: dict[str, OpaqueEvidenceAssociationCurrentnessWitness] = {}
        self.pair_witnesses: dict[str, OpaqueEvidenceAssociationPairWitness] = {}
        self.qualifications: dict[str, OpaqueEvidenceAssociationQualificationWitness] = {}

    @staticmethod
    def derive_record_id(
        left_opaque_id: str,
        right_digest_sha256: str,
        source_evidence_refs: Iterable[tuple[str, str]],
    ) -> str:
        payload = {
            "left_opaque_id": str(left_opaque_id),
            "right_digest_sha256": _sha256_token(right_digest_sha256, error="INVALID_ASSOCIATION_RIGHT_DIGEST"),
            "source_evidence_refs": sorted((str(a), str(b).lower()) for a, b in source_evidence_refs),
        }
        return "opaque-assoc-" + _stable_digest(payload)[:24]

    def register(self, record: OpaqueEvidenceAssociationRecord, *, replay: bool = False) -> None:
        if record.record_id in self.records:
            raise ValueError("DUPLICATE_OPAQUE_EVIDENCE_ASSOCIATION")
        if replay and record.state != OpaqueEvidenceAssociationState.STALE:
            record.state = OpaqueEvidenceAssociationState.REVALIDATION_REQUIRED
            record.stale_reason = None
            record.stale_evidence_id = None
        self.records[record.record_id] = record

    def add_witness(self, witness: OpaqueEvidenceAssociationCurrentnessWitness, *, replay: bool = False) -> OpaqueEvidenceAssociationRecord:
        record = self.records.get(witness.record_id)
        if record is None:
            raise ValueError("OPAQUE_EVIDENCE_ASSOCIATION_NOT_FOUND")
        if witness.expected_right_digest_sha256 != record.right_digest_sha256:
            raise ValueError("ASSOCIATION_WITNESS_EXPECTED_DIGEST_MISMATCH")
        self.witnesses[witness.witness_id] = witness
        if witness.status == "DRIFT_WITNESS":
            record.state = OpaqueEvidenceAssociationState.STALE
            if not record.stale_reason:
                record.stale_reason = "EMPIRICAL_RELATION_DRIFT_WITNESS"
                record.stale_evidence_id = witness.evidence_id
            return record
        if replay:
            if record.state != OpaqueEvidenceAssociationState.STALE:
                record.state = OpaqueEvidenceAssociationState.REVALIDATION_REQUIRED
            return record
        if record.state == OpaqueEvidenceAssociationState.REVALIDATION_REQUIRED:
            record.state = OpaqueEvidenceAssociationState.CURRENT
        # A historical drift witness is durable and later positive evidence cannot reactivate it.
        return record

    def add_pair_witness(self, witness: OpaqueEvidenceAssociationPairWitness) -> None:
        if witness.witness_id in self.pair_witnesses:
            raise ValueError("DUPLICATE_OPAQUE_ASSOCIATION_PAIR_WITNESS")
        self.pair_witnesses[witness.witness_id]=witness

    @staticmethod
    def _exact_bijective_mapping(rows: list[tuple[str,str]]) -> dict[str,str] | None:
        l2r:dict[str,set[str]]={}; r2l:dict[str,set[str]]={}
        for left,right in rows:
            l2r.setdefault(left,set()).add(right); r2l.setdefault(right,set()).add(left)
        if len(l2r)<2 or len(l2r)!=len(r2l):
            return None
        if any(len(v)!=1 for v in l2r.values()) or any(len(v)!=1 for v in r2l.values()):
            return None
        return {left:next(iter(rights)) for left,rights in l2r.items()}

    def _closure_for_scope(
        self,
        association_scope: str,
        evidence_getter: Callable[[str], dict[str, Any] | None],
    ) -> dict[str, Any]:
        scope=str(association_scope)
        ids=tuple(sorted(wid for wid,w in self.pair_witnesses.items() if w.association_scope==scope))
        if len(ids)<2:
            return {"status":"DEFER_UNKNOWN","reason":"MULTIPLE_PAIR_EVIDENCE_REQUIRED","association_scope":scope,"pair_witness_count":len(ids)}
        pairs:list[tuple[str,str]]=[]
        provenance:set[tuple[tuple[str,str],...]]=set()
        for wid in ids:
            w=self.pair_witnesses[wid]
            exact=[]
            for eid,sha in w.source_evidence_refs:
                row=evidence_getter(eid)
                if row is None or str(row.get("sha256","")).lower()!=sha:
                    return {"status":"DEFER_UNKNOWN","reason":"PAIR_SOURCE_EVIDENCE_NOT_EXACT","association_scope":scope,"evidence_id":eid}
                exact.append((eid,sha))
            prov=tuple(sorted(exact))
            if prov in provenance:
                return {"status":"DEFER_UNKNOWN","reason":"DUPLICATED_PAIR_PROVENANCE_NOT_INDEPENDENT","association_scope":scope}
            provenance.add(prov)
            pairs.append((w.left_opaque_id,w.right_digest_sha256))

        full=self._exact_bijective_mapping(pairs)
        if full is None:
            return {"status":"DEFER_UNKNOWN","reason":"PAIR_EVIDENCE_NOT_EXACT_BIJECTION","association_scope":scope}
        for i,(held_left,held_right) in enumerate(pairs):
            rest=pairs[:i]+pairs[i+1:]
            m=self._exact_bijective_mapping(rest)
            if m is None or m.get(held_left)!=held_right:
                return {"status":"DEFER_UNKNOWN","reason":"LEAVE_ONE_OUT_ASSOCIATION_CLOSURE_FAILED","association_scope":scope,"held_out_pair_witness_id":ids[i]}
        return {"status":"EVIDENCE_CLOSURE_CONFIRMED","association_scope":scope,"pair_witness_ids":ids,"bindings":tuple(sorted(full.items()))}

    def derive_leave_one_out_qualification(
        self,
        association_scope: str,
        evidence_getter: Callable[[str], dict[str, Any] | None],
    ) -> dict[str, Any]:
        closure=self._closure_for_scope(association_scope,evidence_getter)
        if closure.get("status")!="EVIDENCE_CLOSURE_CONFIRMED":
            return closure
        ids=tuple(closure["pair_witness_ids"]); bindings=tuple(closure["bindings"]); scope=str(association_scope)
        qid="opaque-assoc-qualification-"+_stable_digest({"association_scope":scope,"pair_witness_ids":list(ids),"bindings":bindings,"method":"LEAVE_ONE_OUT_EXACT_BIJECTIVE_EVIDENCE_CLOSURE"})[:24]
        existing=self.qualifications.get(qid)
        if existing is not None:
            q=existing
        else:
            q=OpaqueEvidenceAssociationQualificationWitness(qualification_id=qid,association_scope=scope,pair_witness_ids=ids,bindings=bindings)
            self.qualifications[qid]=q
        return {"status":q.status,"qualification":q.serializable(),"truth_authority":"NONE","semantic_authority":"NONE","execution_authority":"NONE","language_authority":"NONE"}

    def qualification_status(
        self,
        qualification_id: str,
        evidence_getter: Callable[[str], dict[str, Any] | None],
    ) -> dict[str, Any]:
        q=self.qualifications.get(str(qualification_id))
        if q is None:
            return {"status":"UNKNOWN_INCOMPLETE","reason":"OPAQUE_ASSOCIATION_QUALIFICATION_NOT_FOUND"}
        closure=self._closure_for_scope(q.association_scope,evidence_getter)
        if closure.get("status")!="EVIDENCE_CLOSURE_CONFIRMED":
            return {"status":"REVALIDATION_REQUIRED_EPISTEMIC_ASSOCIATION_QUALIFICATION","reason":closure.get("reason","EVIDENCE_CLOSURE_NOT_CURRENT"),"association_scope":q.association_scope}
        current_ids=tuple(closure["pair_witness_ids"]); current_bindings=tuple(closure["bindings"])
        if current_ids!=tuple(q.pair_witness_ids) or current_bindings!=tuple(q.bindings):
            return {"status":"REVALIDATION_REQUIRED_EPISTEMIC_ASSOCIATION_QUALIFICATION","reason":"PAIR_EVIDENCE_SET_CHANGED_REQUALIFICATION_REQUIRED","association_scope":q.association_scope}
        return {"status":"CURRENT_EPISTEMIC_ASSOCIATION_ADEQUACY","qualification":q.serializable(),"truth_authority":"NONE","semantic_authority":"NONE","execution_authority":"NONE","language_authority":"NONE"}

    def currentness(
        self,
        record_id: str,
        evidence_getter: Callable[[str], dict[str, Any] | None],
    ) -> dict[str, Any]:
        record = self.records.get(record_id)
        if record is None:
            return {"status": "UNKNOWN_INCOMPLETE", "reason": "OPAQUE_EVIDENCE_ASSOCIATION_NOT_FOUND"}
        missing = []
        for evidence_id, signature in record.source_evidence_refs:
            row = evidence_getter(evidence_id)
            if row is None or str(row.get("sha256", "")).lower() != signature:
                missing.append(evidence_id)
        if missing:
            return {
                "status": "STALE_OPAQUE_EVIDENCE_ASSOCIATION",
                "reason": "SOURCE_EVIDENCE_NOT_EXACT",
                "record": record.serializable(),
                "missing_or_mismatched_evidence_ids": sorted(missing),
            }
        if record.state == OpaqueEvidenceAssociationState.STALE:
            status = "STALE_OPAQUE_EVIDENCE_ASSOCIATION"
            reason = record.stale_reason or "STALE"
        elif record.state == OpaqueEvidenceAssociationState.REVALIDATION_REQUIRED:
            status = "REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"
            reason = "FRESH_POST_RESTART_CURRENTNESS_EVIDENCE_REQUIRED"
        else:
            status = "CURRENT_OPAQUE_EVIDENCE_ASSOCIATION"
            reason = None
        return {
            "status": status,
            "reason": reason,
            "record": record.serializable(),
            "currentness_witness_ids": [
                wid for wid, witness in sorted(self.witnesses.items()) if witness.record_id == record_id
            ],
            "truth_authority": "NONE",
            "semantic_authority": "NONE",
            "execution_authority": "NONE",
            "language_authority": "NONE",
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "records": {k: v.serializable() for k, v in sorted(self.records.items())},
            "witnesses": {k: v.serializable() for k, v in sorted(self.witnesses.items())},
            "pair_witnesses": {k: v.serializable() for k, v in sorted(self.pair_witnesses.items())},
            "qualifications": {k: v.serializable() for k, v in sorted(self.qualifications.items())},
        }
