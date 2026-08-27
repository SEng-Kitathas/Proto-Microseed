from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Any, Iterable, Mapping

from ..evidence.authority import FixedQualifier
from ..evidence.ledger import EvidenceLedger
from ..runtime.types import Authority, EvidenceRef, QualificationState
from .rehearsal import RehearsalTransitionRelation


def _digest(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@dataclass(frozen=True)
class ActionOutcomeExperience:
    """One executed-action/actual-outcome learning row.

    Intended/predicted effects are deliberately absent from the consequence label.
    They may exist elsewhere as provenance on the originating intent/proposal.
    """
    evidence_id: str
    execution_id: str
    start_state_id: str
    capability_id: str
    actual_next_state_id: str
    actual_value_effect: float
    capability_epoch: int
    frame_epochs: tuple[tuple[str, int], ...]
    episode_schema_epochs: tuple[tuple[str, int], ...]
    value_epoch: tuple[str, int]
    topology_epochs: tuple[tuple[str, int], ...] = ()
    coordination_epochs: tuple[tuple[str, int], ...] = ()
    evidence_premise_epochs: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        if not self.execution_id:
            raise ValueError("ACTION_OUTCOME_EXPERIENCE_REQUIRES_EXECUTION_ID")
        if not math.isfinite(float(self.actual_value_effect)):
            raise ValueError("ACTION_OUTCOME_EXPERIENCE_NONFINITE_EFFECT")
        object.__setattr__(self, "frame_epochs", tuple((str(a), int(b)) for a, b in self.frame_epochs))
        object.__setattr__(self, "episode_schema_epochs", tuple((str(a), int(b)) for a, b in self.episode_schema_epochs))
        object.__setattr__(self, "topology_epochs", tuple((str(a), int(b)) for a, b in self.topology_epochs))
        object.__setattr__(self, "coordination_epochs", tuple((str(a), int(b)) for a, b in self.coordination_epochs))
        object.__setattr__(self, "evidence_premise_epochs", tuple((str(a), int(b)) for a, b in self.evidence_premise_epochs))
        object.__setattr__(self, "value_epoch", (str(self.value_epoch[0]), int(self.value_epoch[1])))

    def serializable(self) -> dict[str, Any]:
        d = asdict(self)
        for key in ("frame_epochs", "episode_schema_epochs", "topology_epochs", "coordination_epochs", "evidence_premise_epochs"):
            d[key] = [list(x) for x in d[key]]
        d["value_epoch"] = list(d["value_epoch"])
        return d


@dataclass(frozen=True)
class ActionOutcomePredictiveCandidate:
    candidate_id: str
    start_state_id: str
    capability_id: str
    next_state_id: str
    value_effect: float
    support: int
    consistency: float
    source_evidence_ids: tuple[str, ...]
    capability_epoch: int
    frame_epochs: tuple[tuple[str, int], ...]
    episode_schema_epochs: tuple[tuple[str, int], ...]
    value_epoch: tuple[str, int]
    topology_epochs: tuple[tuple[str, int], ...] = ()
    coordination_epochs: tuple[tuple[str, int], ...] = ()
    evidence_premise_epochs: tuple[tuple[str, int], ...] = ()
    authority: str = Authority.MODEL_OUTPUT_ONLY.value
    truth_authority: str = "NONE"
    causal_theorem_authority: str = "NONE"
    qualification_authority: str = "NONE"
    semantic_goal_authority: str = "NONE"

    def signature_payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("candidate_id", None)
        d["source_evidence_ids"] = []  # evidence identifies ancestry, not candidate semantics
        return d

    def digest(self) -> str:
        return _digest(self.signature_payload())

    def serializable(self) -> dict[str, Any]:
        d = asdict(self)
        for key in ("frame_epochs", "episode_schema_epochs", "topology_epochs", "coordination_epochs", "evidence_premise_epochs"):
            d[key] = [list(x) for x in d[key]]
        d["value_epoch"] = list(d["value_epoch"])
        d["candidate_sha256"] = self.digest()
        return d

    @classmethod
    def from_serializable(cls, d: dict[str, Any]) -> "ActionOutcomePredictiveCandidate":
        x = dict(d)
        x.pop("candidate_sha256", None)
        for key in ("frame_epochs", "episode_schema_epochs", "topology_epochs", "coordination_epochs", "evidence_premise_epochs"):
            x[key] = tuple((str(a), int(b)) for a, b in x.get(key, ()))
        x["value_epoch"] = (str(x["value_epoch"][0]), int(x["value_epoch"][1]))
        x["source_evidence_ids"] = tuple(str(v) for v in x.get("source_evidence_ids", ()))
        return cls(**x)


@dataclass(frozen=True)
class ActionOutcomeRelationQualificationTicket:
    candidate_id: str
    candidate_sha256: str
    state: QualificationState
    qualifier_id: str
    reason: str
    qualification_evidence: tuple[EvidenceRef, ...]
    holdout_support: int
    holdout_accuracy: float


@dataclass(frozen=True)
class QualifiedActionOutcomePredictiveRelation:
    relation_id: str
    candidate_id: str
    candidate_sha256: str
    start_state_id: str
    capability_id: str
    next_state_id: str
    value_effect: float
    support: int
    consistency: float
    source_evidence_ids: tuple[str, ...]
    qualification_evidence_ids: tuple[str, ...]
    holdout_support: int
    holdout_accuracy: float
    capability_epoch: int
    frame_epochs: tuple[tuple[str, int], ...]
    episode_schema_epochs: tuple[tuple[str, int], ...]
    value_epoch: tuple[str, int]
    topology_epochs: tuple[tuple[str, int], ...] = ()
    coordination_epochs: tuple[tuple[str, int], ...] = ()
    evidence_premise_epochs: tuple[tuple[str, int], ...] = ()
    authority: str = "EVIDENCE_BOUND_PREDICTIVE_RELATION_ONLY"
    truth_authority: str = "NONE"
    causal_theorem_authority: str = "NONE"
    execution_authority: str = "NONE"
    semantic_goal_authority: str = "NONE"

    def serializable(self) -> dict[str, Any]:
        d = asdict(self)
        for key in ("frame_epochs", "episode_schema_epochs", "topology_epochs", "coordination_epochs", "evidence_premise_epochs"):
            d[key] = [list(x) for x in d[key]]
        d["value_epoch"] = list(d["value_epoch"])
        return d

    @classmethod
    def from_serializable(cls, d: dict[str, Any]) -> "QualifiedActionOutcomePredictiveRelation":
        x = dict(d)
        for key in ("frame_epochs", "episode_schema_epochs", "topology_epochs", "coordination_epochs", "evidence_premise_epochs"):
            x[key] = tuple((str(a), int(b)) for a, b in x.get(key, ()))
        x["value_epoch"] = (str(x["value_epoch"][0]), int(x["value_epoch"][1]))
        x["source_evidence_ids"] = tuple(str(v) for v in x.get("source_evidence_ids", ()))
        x["qualification_evidence_ids"] = tuple(str(v) for v in x.get("qualification_evidence_ids", ()))
        return cls(**x)

    def as_rehearsal_relation(self) -> RehearsalTransitionRelation | None:
        # Current Microseed rehearsal relation has one frame + one episode anchor per edge.
        # More complex ancestry remains unpromoted rather than silently collapsed.
        if len(self.frame_epochs) != 1 or len(self.episode_schema_epochs) != 1 or self.evidence_premise_epochs:
            return None
        if len(self.topology_epochs) > 1 or len(self.coordination_epochs) > 1:
            return None
        return RehearsalTransitionRelation(
            state_id=self.start_state_id,
            capability_id=self.capability_id,
            next_state_id=self.next_state_id,
            value_effect=float(self.value_effect),
            support=int(self.support),
            consistency=float(self.consistency),
            source_evidence_ids=tuple(self.source_evidence_ids) + tuple(self.qualification_evidence_ids),
            capability_epoch=int(self.capability_epoch),
            frame_epoch=self.frame_epochs[0],
            episode_schema_epoch=self.episode_schema_epochs[0],
            topology_epoch=self.topology_epochs[0] if self.topology_epochs else None,
            coordination_epoch=self.coordination_epochs[0] if self.coordination_epochs else None,
        )


class ActionOutcomeLearningRegistry:
    def __init__(self) -> None:
        self.candidates: dict[str, ActionOutcomePredictiveCandidate] = {}
        self.relations: dict[str, QualifiedActionOutcomePredictiveRelation] = {}
        self.currentness_witnesses: dict[str, Any] = {}
        self.replacement_links: dict[str, Any] = {}
        self.relation_replacement_lineage: dict[str, dict[str, str]] = {}
        # MS1453-1477 extends the existing v1.7+ projection lineage rather than
        # creating a second predictive-state registry. These are only bindings
        # from an already-qualified EpistemicProjectionRecord to learned action
        # outcome relations.
        self.projection_routing_candidates: dict[str, Any] = {}
        self.projection_conditioned_bindings: dict[str, Any] = {}

    def add_candidate(self, c: ActionOutcomePredictiveCandidate) -> None:
        if c.authority != Authority.MODEL_OUTPUT_ONLY.value or any(
            x != "NONE" for x in (c.truth_authority, c.causal_theorem_authority, c.qualification_authority, c.semantic_goal_authority)
        ):
            raise ValueError("ACTION_OUTCOME_CANDIDATE_AUTHORITY_ESCALATION")
        self.candidates.setdefault(c.candidate_id, c)

    def add_relation(self, r: QualifiedActionOutcomePredictiveRelation) -> None:
        if any(x != "NONE" for x in (r.truth_authority, r.causal_theorem_authority, r.execution_authority, r.semantic_goal_authority)):
            raise ValueError("ACTION_OUTCOME_RELATION_AUTHORITY_ESCALATION")
        self.relations[r.relation_id] = r

    def add_projection_routing_candidate(self, candidate: Any) -> None:
        if getattr(candidate, "authority", None) != Authority.MODEL_OUTPUT_ONLY.value or any(
            getattr(candidate, name, "NONE") != "NONE"
            for name in ("truth_authority", "semantic_regime_authority", "model_switch_authority", "qualification_authority")
        ):
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_CANDIDATE_AUTHORITY_ESCALATION")
        self.projection_routing_candidates.setdefault(candidate.candidate_id, candidate)

    def add_projection_conditioned_binding(self, binding: Any) -> None:
        if any(
            getattr(binding, name, "NONE") != "NONE"
            for name in ("truth_authority", "semantic_regime_authority", "model_switch_authority", "execution_authority", "self_qualification_authority")
        ):
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_BINDING_AUTHORITY_ESCALATION")
        self.projection_conditioned_bindings[binding.binding_id] = binding


def nominate_action_outcome_candidates(
    experiences: Iterable[ActionOutcomeExperience], *, min_support: int = 8, min_consistency: float = 0.78,
    effect_round_digits: int = 3,
) -> tuple[ActionOutcomePredictiveCandidate, ...]:
    if min_support < 2:
        raise ValueError("ACTION_OUTCOME_MIN_SUPPORT_MUST_EXCEED_ONE")
    if not (0.5 < float(min_consistency) <= 1.0):
        raise ValueError("ACTION_OUTCOME_INVALID_CONSISTENCY_GATE")
    rows = tuple(experiences)
    groups: dict[tuple[Any, ...], list[ActionOutcomeExperience]] = defaultdict(list)
    for r in rows:
        key = (
            r.start_state_id, r.capability_id, int(r.capability_epoch), r.frame_epochs,
            r.episode_schema_epochs, r.value_epoch, r.topology_epochs, r.coordination_epochs, r.evidence_premise_epochs,
        )
        groups[key].append(r)
    out: list[ActionOutcomePredictiveCandidate] = []
    for key, rs in groups.items():
        if len(rs) < min_support:
            continue
        buckets = Counter((r.actual_next_state_id, round(float(r.actual_value_effect), effect_round_digits)) for r in rs)
        (next_state, effect), count = sorted(buckets.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        consistency = count / len(rs)
        if consistency < min_consistency:
            continue
        payload = {
            "start_state_id": key[0], "capability_id": key[1], "next_state_id": next_state,
            "value_effect": float(effect), "capability_epoch": key[2], "frame_epochs": key[3],
            "episode_schema_epochs": key[4], "value_epoch": key[5], "topology_epochs": key[6],
            "coordination_epochs": key[7], "evidence_premise_epochs": key[8],
        }
        cid = "ACTION-LAW-CAND-" + _digest(payload)[:20]
        out.append(ActionOutcomePredictiveCandidate(
            candidate_id=cid, start_state_id=key[0], capability_id=key[1], next_state_id=next_state,
            value_effect=float(effect), support=len(rs), consistency=consistency,
            source_evidence_ids=tuple(sorted(r.evidence_id for r in rs)), capability_epoch=key[2],
            frame_epochs=key[3], episode_schema_epochs=key[4], value_epoch=key[5],
            topology_epochs=key[6], coordination_epochs=key[7], evidence_premise_epochs=key[8],
        ))
    return tuple(sorted(out, key=lambda c: (c.start_state_id, c.capability_id, -c.consistency, c.candidate_id)))


def _qualification_row(ledger: EvidenceLedger, ref: EvidenceRef) -> dict[str, Any] | None:
    row = ledger.get(ref.evidence_id)
    if row is None or row["sha256"] != ref.sha256:
        return None
    payload = row.get("payload")
    if not isinstance(payload, dict) or payload.get("kind") != "ACTION_OUTCOME_HOLDOUT":
        return None
    return payload


def evaluate_action_outcome_holdout(
    candidate: ActionOutcomePredictiveCandidate, refs: Iterable[EvidenceRef], ledger: EvidenceLedger,
) -> tuple[int, float]:
    usable = []
    for ref in refs:
        p = _qualification_row(ledger, ref)
        if p is None:
            continue
        if (
            str(p.get("start_state_id")) == candidate.start_state_id
            and str(p.get("capability_id")) == candidate.capability_id
            and int(p.get("capability_epoch", -1)) == candidate.capability_epoch
            and tuple((str(a), int(b)) for a, b in p.get("frame_epochs", ())) == candidate.frame_epochs
            and tuple((str(a), int(b)) for a, b in p.get("episode_schema_epochs", ())) == candidate.episode_schema_epochs
            and (str(p.get("value_epoch", ["", -1])[0]), int(p.get("value_epoch", ["", -1])[1])) == candidate.value_epoch
            and tuple((str(a), int(b)) for a, b in p.get("topology_epochs", ())) == candidate.topology_epochs
            and tuple((str(a), int(b)) for a, b in p.get("coordination_epochs", ())) == candidate.coordination_epochs
            and tuple((str(a), int(b)) for a, b in p.get("evidence_premise_epochs", ())) == candidate.evidence_premise_epochs
        ):
            usable.append(p)
    if not usable:
        return 0, 0.0
    matches = sum(
        str(p.get("actual_next_state_id")) == candidate.next_state_id
        and round(float(p.get("actual_value_effect")), 3) == round(float(candidate.value_effect), 3)
        for p in usable
    )
    return len(usable), matches / len(usable)


class ExternalActionOutcomeRelationQualifier:
    """Harness-side qualifier. It cannot be instantiated as Microseed authority."""
    def __init__(self, ledger: EvidenceLedger, *, qualifier_id: str = "HSP-EXTERNAL-ACTION-OUTCOME-QUALIFIER"):
        if not qualifier_id or qualifier_id.upper().startswith("MICROSEED"):
            raise ValueError("qualifier_id must identify an external qualification boundary")
        self.ledger = ledger
        self.qualifier_id = qualifier_id

    def qualify(
        self, candidate: ActionOutcomePredictiveCandidate, *, qualification_evidence: Iterable[EvidenceRef],
        min_support: int = 12, min_accuracy: float = 0.80,
    ) -> ActionOutcomeRelationQualificationTicket:
        refs = tuple(qualification_evidence)
        decision = FixedQualifier(self.ledger).decide(refs, Authority.REFERENCE_ONLY)
        support, accuracy = evaluate_action_outcome_holdout(candidate, refs, self.ledger)
        state = decision.state
        reason = decision.reason
        if set(candidate.source_evidence_ids) & {r.evidence_id for r in refs}:
            state, reason = QualificationState.REJECTED, "PROPOSAL_QUALIFICATION_EVIDENCE_OVERLAP"
        elif state in {QualificationState.SHADOW_QUALIFIED, QualificationState.QUALIFIED}:
            if support < int(min_support):
                state, reason = QualificationState.REJECTED, "INSUFFICIENT_INDEPENDENT_HOLDOUT"
            elif accuracy < float(min_accuracy):
                state, reason = QualificationState.REJECTED, f"HOLDOUT_ACCURACY_BELOW_BOUND:{accuracy:.6f}"
            else:
                reason = f"INDEPENDENT_HOLDOUT_QUALIFIED:{accuracy:.6f}"
        return ActionOutcomeRelationQualificationTicket(
            candidate_id=candidate.candidate_id, candidate_sha256=candidate.digest(), state=state,
            qualifier_id=self.qualifier_id, reason=reason, qualification_evidence=refs,
            holdout_support=support, holdout_accuracy=accuracy,
        )


def validate_external_action_outcome_ticket(
    candidate: ActionOutcomePredictiveCandidate, ticket: ActionOutcomeRelationQualificationTicket,
    ledger: EvidenceLedger, *, min_support: int = 12, min_accuracy: float = 0.80,
) -> tuple[bool, str]:
    if not ticket.qualifier_id or ticket.qualifier_id.upper().startswith("MICROSEED"):
        return False, "QUALIFIER_NOT_EXTERNAL"
    if ticket.candidate_id != candidate.candidate_id or ticket.candidate_sha256 != candidate.digest():
        return False, "CANDIDATE_BINDING_MISMATCH"
    if not ticket.qualification_evidence:
        return False, "NO_QUALIFICATION_EVIDENCE"
    if set(candidate.source_evidence_ids) & {r.evidence_id for r in ticket.qualification_evidence}:
        return False, "PROPOSAL_QUALIFICATION_EVIDENCE_OVERLAP"
    decision = FixedQualifier(ledger).decide(ticket.qualification_evidence, Authority.REFERENCE_ONLY)
    support, accuracy = evaluate_action_outcome_holdout(candidate, ticket.qualification_evidence, ledger)
    if support != ticket.holdout_support or abs(accuracy - ticket.holdout_accuracy) > 1e-12:
        return False, "HOLDOUT_METRICS_MISMATCH"
    if support < int(min_support):
        return False, "INSUFFICIENT_INDEPENDENT_HOLDOUT"
    if accuracy < float(min_accuracy):
        return False, "HOLDOUT_ACCURACY_BELOW_BOUND"
    if ticket.state not in {QualificationState.SHADOW_QUALIFIED, QualificationState.QUALIFIED}:
        return False, f"NOT_ADMISSIBLE:{ticket.state.value}"
    if decision.state not in {QualificationState.SHADOW_QUALIFIED, QualificationState.QUALIFIED}:
        return False, "QUALIFICATION_EVIDENCE_NOT_SUPPORTIVE"
    return True, "VALID_EXTERNAL_ACTION_OUTCOME_QUALIFICATION"


@dataclass(frozen=True)
class ProjectionConditionedRelationCandidate:
    """Proposal-only binding from one already-qualified opaque projection to learned relations.

    The projection is the selector substrate. This object does not discover a
    second state system and carries no semantic regime, truth, switch, or
    qualification authority. It only proposes which existing predictive relation
    should be used for an action inside one explicitly bounded task/channel/horizon
    scope, with sparse bucket-specific overrides over a default relation map.
    """

    candidate_id: str
    projection_id: str
    projection_epoch: int
    projection_signature_sha256: str
    task_id: str
    action_ids: tuple[str, ...]
    channel_ids: tuple[str, ...]
    horizon: int
    default_action_relations: tuple[tuple[str, str], ...]
    bucket_action_overrides: tuple[tuple[str, str, str], ...]
    source_evidence_ids: tuple[str, ...]
    authority: str = Authority.MODEL_OUTPUT_ONLY.value
    truth_authority: str = "NONE"
    semantic_regime_authority: str = "NONE"
    model_switch_authority: str = "NONE"
    qualification_authority: str = "NONE"

    def __post_init__(self) -> None:
        if not self.candidate_id or not self.projection_id or int(self.projection_epoch) < 0:
            raise ValueError("INVALID_PROJECTION_CONDITIONED_ROUTING_CANDIDATE")
        if len(self.projection_signature_sha256) != 64:
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_REQUIRES_PROJECTION_SIGNATURE")
        if not self.task_id or not self.action_ids or not self.channel_ids or int(self.horizon) < 1:
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_REQUIRES_BOUNDED_SCOPE")
        if len(set(self.action_ids)) != len(self.action_ids) or len(set(self.channel_ids)) != len(self.channel_ids):
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_SCOPE_DUPLICATE")
        defaults = dict(self.default_action_relations)
        if set(defaults) != set(self.action_ids):
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_REQUIRES_DEFAULT_FOR_EACH_ACTION")
        if len(defaults) != len(self.default_action_relations):
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_DUPLICATE_DEFAULT")
        seen: set[tuple[str, str]] = set()
        for bucket, action, relation_id in self.bucket_action_overrides:
            if not bucket or action not in self.action_ids or not relation_id:
                raise ValueError("INVALID_PROJECTION_CONDITIONED_ROUTING_OVERRIDE")
            key = (bucket, action)
            if key in seen:
                raise ValueError("PROJECTION_CONDITIONED_ROUTING_DUPLICATE_OVERRIDE")
            seen.add(key)
        if self.authority != Authority.MODEL_OUTPUT_ONLY.value or any(
            x != "NONE" for x in (
                self.truth_authority, self.semantic_regime_authority,
                self.model_switch_authority, self.qualification_authority,
            )
        ):
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_CANDIDATE_AUTHORITY_ESCALATION")
        object.__setattr__(self, "projection_epoch", int(self.projection_epoch))
        object.__setattr__(self, "horizon", int(self.horizon))
        object.__setattr__(self, "action_ids", tuple(str(x) for x in self.action_ids))
        object.__setattr__(self, "channel_ids", tuple(str(x) for x in self.channel_ids))
        object.__setattr__(self, "default_action_relations", tuple((str(a), str(r)) for a, r in self.default_action_relations))
        object.__setattr__(self, "bucket_action_overrides", tuple((str(b), str(a), str(r)) for b, a, r in self.bucket_action_overrides))
        object.__setattr__(self, "source_evidence_ids", tuple(str(x) for x in self.source_evidence_ids))

    def relation_id_for(self, bucket_id: str, action_id: str) -> str | None:
        for bucket, action, relation_id in self.bucket_action_overrides:
            if bucket == bucket_id and action == action_id:
                return relation_id
        return dict(self.default_action_relations).get(action_id)

    def relation_ids(self) -> tuple[str, ...]:
        return tuple(sorted(set(dict(self.default_action_relations).values()) | {r for _, _, r in self.bucket_action_overrides}))

    def signature_payload(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("candidate_id", None)
        d["source_evidence_ids"] = []
        return d

    def digest(self) -> str:
        return _digest(self.signature_payload())

    def serializable(self) -> dict[str, Any]:
        d = asdict(self)
        d["action_ids"] = list(self.action_ids)
        d["channel_ids"] = list(self.channel_ids)
        d["default_action_relations"] = [list(x) for x in self.default_action_relations]
        d["bucket_action_overrides"] = [list(x) for x in self.bucket_action_overrides]
        d["source_evidence_ids"] = list(self.source_evidence_ids)
        d["candidate_sha256"] = self.digest()
        return d

    @classmethod
    def from_serializable(cls, d: dict[str, Any]) -> "ProjectionConditionedRelationCandidate":
        x = dict(d)
        x.pop("candidate_sha256", None)
        x["action_ids"] = tuple(str(v) for v in x.get("action_ids", ()))
        x["channel_ids"] = tuple(str(v) for v in x.get("channel_ids", ()))
        x["default_action_relations"] = tuple((str(a), str(r)) for a, r in x.get("default_action_relations", ()))
        x["bucket_action_overrides"] = tuple((str(b), str(a), str(r)) for b, a, r in x.get("bucket_action_overrides", ()))
        x["source_evidence_ids"] = tuple(str(v) for v in x.get("source_evidence_ids", ()))
        return cls(**x)


@dataclass(frozen=True)
class ProjectionConditionedRelationQualificationTicket:
    candidate_id: str
    candidate_sha256: str
    state: QualificationState
    qualifier_id: str
    reason: str
    qualification_evidence: tuple[EvidenceRef, ...]
    holdout_support: int
    holdout_accuracy: float
    holdout_coverage: float
    qualified_bucket_ids: tuple[str, ...]


@dataclass(frozen=True)
class QualifiedProjectionConditionedRelationBinding:
    binding_id: str
    candidate_id: str
    candidate_sha256: str
    projection_id: str
    projection_epoch: int
    projection_signature_sha256: str
    task_id: str
    action_ids: tuple[str, ...]
    channel_ids: tuple[str, ...]
    horizon: int
    default_action_relations: tuple[tuple[str, str], ...]
    bucket_action_overrides: tuple[tuple[str, str, str], ...]
    source_evidence_ids: tuple[str, ...]
    qualification_evidence_ids: tuple[str, ...]
    holdout_support: int
    holdout_accuracy: float
    holdout_coverage: float
    qualified_bucket_ids: tuple[str, ...]
    authority: str = "EVIDENCE_BOUND_PROJECTION_CONDITIONED_RELATION_ROUTING_ONLY"
    truth_authority: str = "NONE"
    semantic_regime_authority: str = "NONE"
    model_switch_authority: str = "NONE"
    execution_authority: str = "NONE"
    self_qualification_authority: str = "NONE"

    def __post_init__(self) -> None:
        if any(x != "NONE" for x in (
            self.truth_authority, self.semantic_regime_authority, self.model_switch_authority,
            self.execution_authority, self.self_qualification_authority,
        )):
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_BINDING_AUTHORITY_ESCALATION")
        object.__setattr__(self, "projection_epoch", int(self.projection_epoch))
        object.__setattr__(self, "horizon", int(self.horizon))
        object.__setattr__(self, "action_ids", tuple(str(x) for x in self.action_ids))
        object.__setattr__(self, "channel_ids", tuple(str(x) for x in self.channel_ids))
        object.__setattr__(self, "default_action_relations", tuple((str(a), str(r)) for a, r in self.default_action_relations))
        object.__setattr__(self, "bucket_action_overrides", tuple((str(b), str(a), str(r)) for b, a, r in self.bucket_action_overrides))
        object.__setattr__(self, "source_evidence_ids", tuple(str(x) for x in self.source_evidence_ids))
        object.__setattr__(self, "qualification_evidence_ids", tuple(str(x) for x in self.qualification_evidence_ids))
        object.__setattr__(self, "qualified_bucket_ids", tuple(sorted(set(str(x) for x in self.qualified_bucket_ids))))
        if not self.qualified_bucket_ids:
            raise ValueError("PROJECTION_CONDITIONED_ROUTING_REQUIRES_QUALIFIED_BUCKET_SUPPORT")

    def relation_id_for(self, bucket_id: str, action_id: str) -> str | None:
        for bucket, action, relation_id in self.bucket_action_overrides:
            if bucket == bucket_id and action == action_id:
                return relation_id
        return dict(self.default_action_relations).get(action_id)

    def relation_ids(self) -> tuple[str, ...]:
        return tuple(sorted(set(dict(self.default_action_relations).values()) | {r for _, _, r in self.bucket_action_overrides}))

    def serializable(self) -> dict[str, Any]:
        d = asdict(self)
        d["action_ids"] = list(self.action_ids)
        d["channel_ids"] = list(self.channel_ids)
        d["default_action_relations"] = [list(x) for x in self.default_action_relations]
        d["bucket_action_overrides"] = [list(x) for x in self.bucket_action_overrides]
        d["source_evidence_ids"] = list(self.source_evidence_ids)
        d["qualification_evidence_ids"] = list(self.qualification_evidence_ids)
        d["qualified_bucket_ids"] = list(self.qualified_bucket_ids)
        return d

    @classmethod
    def from_serializable(cls, d: dict[str, Any]) -> "QualifiedProjectionConditionedRelationBinding":
        x = dict(d)
        x["action_ids"] = tuple(str(v) for v in x.get("action_ids", ()))
        x["channel_ids"] = tuple(str(v) for v in x.get("channel_ids", ()))
        x["default_action_relations"] = tuple((str(a), str(r)) for a, r in x.get("default_action_relations", ()))
        x["bucket_action_overrides"] = tuple((str(b), str(a), str(r)) for b, a, r in x.get("bucket_action_overrides", ()))
        x["source_evidence_ids"] = tuple(str(v) for v in x.get("source_evidence_ids", ()))
        x["qualification_evidence_ids"] = tuple(str(v) for v in x.get("qualification_evidence_ids", ()))
        x["qualified_bucket_ids"] = tuple(str(v) for v in x.get("qualified_bucket_ids", ()))
        return cls(**x)


def evaluate_projection_conditioned_relation_holdout(
    candidate: ProjectionConditionedRelationCandidate,
    refs: Iterable[EvidenceRef],
    ledger: EvidenceLedger,
    relations: Mapping[str, QualifiedActionOutcomePredictiveRelation],
) -> tuple[int, float, float]:
    refs = tuple(refs)
    relevant = []
    correct = 0
    covered = 0
    for ref in refs:
        row = ledger.get(ref.evidence_id)
        if row is None or row["sha256"] != ref.sha256:
            continue
        payload = row.get("payload", {})
        if payload.get("kind") != "PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT":
            continue
        if str(payload.get("projection_id", "")) != candidate.projection_id:
            continue
        if int(payload.get("projection_epoch", -1)) != candidate.projection_epoch:
            continue
        if str(payload.get("projection_signature_sha256", "")) != candidate.projection_signature_sha256:
            continue
        if str(payload.get("task_id", "")) != candidate.task_id:
            continue
        if int(payload.get("horizon", -1)) != candidate.horizon:
            continue
        action_id = str(payload.get("action_id", ""))
        channel_id = str(payload.get("channel_id", ""))
        bucket_id = str(payload.get("projection_bucket_id", ""))
        if action_id not in candidate.action_ids or channel_id not in candidate.channel_ids or not bucket_id:
            continue
        relevant.append(payload)
        relation_id = candidate.relation_id_for(bucket_id, action_id)
        relation = relations.get(relation_id or "")
        if relation is None:
            continue
        covered += 1
        observed = (
            str(payload.get("actual_next_state_id", "")),
            round(float(payload.get("actual_value_effect", 0.0)), 3),
        )
        predicted = (relation.next_state_id, round(float(relation.value_effect), 3))
        if observed == predicted:
            correct += 1
    support = len(relevant)
    accuracy = correct / support if support else 0.0
    coverage = covered / support if support else 0.0
    return support, accuracy, coverage


def projection_conditioned_holdout_bucket_ids(
    candidate: ProjectionConditionedRelationCandidate, refs: Iterable[EvidenceRef], ledger: EvidenceLedger
) -> tuple[str, ...]:
    buckets: set[str] = set()
    for ref in refs:
        row=ledger.get(ref.evidence_id)
        if row is None or row["sha256"] != ref.sha256:
            continue
        payload=row.get("payload",{})
        if payload.get("kind") != "PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT":
            continue
        if str(payload.get("projection_id","")) != candidate.projection_id or int(payload.get("projection_epoch",-1)) != candidate.projection_epoch:
            continue
        if str(payload.get("projection_signature_sha256","")) != candidate.projection_signature_sha256:
            continue
        if str(payload.get("task_id","")) != candidate.task_id or int(payload.get("horizon",-1)) != candidate.horizon:
            continue
        if str(payload.get("action_id","")) not in candidate.action_ids or str(payload.get("channel_id","")) not in candidate.channel_ids:
            continue
        bucket=str(payload.get("projection_bucket_id",""))
        if bucket:
            buckets.add(bucket)
    return tuple(sorted(buckets))


class ExternalProjectionConditionedRelationQualifier:
    """Harness-side qualifier for projection-conditioned relation routing.

    It does not qualify the projection or the relations themselves. Those are
    pre-existing independently qualified objects. This only qualifies the bounded
    routing/binding claim on disjoint holdout evidence.
    """

    def __init__(self, ledger: EvidenceLedger, *, qualifier_id: str = "HSP-EXTERNAL-PROJECTION-CONDITIONED-ROUTING-QUALIFIER"):
        if not qualifier_id or qualifier_id.upper().startswith("MICROSEED"):
            raise ValueError("qualifier_id must identify an external qualification boundary")
        self.ledger = ledger
        self.qualifier_id = qualifier_id

    def qualify(
        self,
        candidate: ProjectionConditionedRelationCandidate,
        *,
        qualification_evidence: Iterable[EvidenceRef],
        relations: Mapping[str, QualifiedActionOutcomePredictiveRelation],
        min_support: int = 12,
        min_accuracy: float = 0.90,
    ) -> ProjectionConditionedRelationQualificationTicket:
        refs = tuple(qualification_evidence)
        decision = FixedQualifier(self.ledger).decide(refs, Authority.REFERENCE_ONLY)
        support, accuracy, coverage = evaluate_projection_conditioned_relation_holdout(candidate, refs, self.ledger, relations)
        qualified_bucket_ids = projection_conditioned_holdout_bucket_ids(candidate, refs, self.ledger)
        state, reason = decision.state, decision.reason
        qids = {r.evidence_id for r in refs}
        relation_ancestry: set[str] = set()
        for relation_id in candidate.relation_ids():
            relation = relations.get(relation_id)
            if relation is not None:
                relation_ancestry.update(relation.source_evidence_ids)
                relation_ancestry.update(relation.qualification_evidence_ids)
        if set(candidate.source_evidence_ids) & qids:
            state, reason = QualificationState.REJECTED, "ROUTING_PROPOSAL_QUALIFICATION_EVIDENCE_OVERLAP"
        elif relation_ancestry & qids:
            state, reason = QualificationState.REJECTED, "ROUTING_QUALIFICATION_RELATION_EVIDENCE_OVERLAP"
        elif state in {QualificationState.SHADOW_QUALIFIED, QualificationState.QUALIFIED}:
            if support < int(min_support):
                state, reason = QualificationState.REJECTED, "INSUFFICIENT_INDEPENDENT_ROUTING_HOLDOUT"
            elif coverage < 1.0:
                state, reason = QualificationState.REJECTED, f"ROUTING_HOLDOUT_COVERAGE_INCOMPLETE:{coverage:.6f}"
            elif accuracy < float(min_accuracy):
                state, reason = QualificationState.REJECTED, f"ROUTING_HOLDOUT_ACCURACY_BELOW_BOUND:{accuracy:.6f}"
            else:
                reason = f"INDEPENDENT_PROJECTION_CONDITIONED_ROUTING_QUALIFIED:{accuracy:.6f}"
        return ProjectionConditionedRelationQualificationTicket(
            candidate_id=candidate.candidate_id,
            candidate_sha256=candidate.digest(),
            state=state,
            qualifier_id=self.qualifier_id,
            reason=reason,
            qualification_evidence=refs,
            holdout_support=support,
            holdout_accuracy=accuracy,
            holdout_coverage=coverage,
            qualified_bucket_ids=qualified_bucket_ids,
        )


def validate_external_projection_conditioned_relation_ticket(
    candidate: ProjectionConditionedRelationCandidate,
    ticket: ProjectionConditionedRelationQualificationTicket,
    ledger: EvidenceLedger,
    relations: Mapping[str, QualifiedActionOutcomePredictiveRelation],
    *,
    min_support: int = 12,
    min_accuracy: float = 0.90,
) -> tuple[bool, str]:
    if not ticket.qualifier_id or ticket.qualifier_id.upper().startswith("MICROSEED"):
        return False, "QUALIFIER_NOT_EXTERNAL"
    if ticket.candidate_id != candidate.candidate_id or ticket.candidate_sha256 != candidate.digest():
        return False, "CANDIDATE_BINDING_MISMATCH"
    if not ticket.qualification_evidence:
        return False, "NO_QUALIFICATION_EVIDENCE"
    qids = {r.evidence_id for r in ticket.qualification_evidence}
    if set(candidate.source_evidence_ids) & qids:
        return False, "ROUTING_PROPOSAL_QUALIFICATION_EVIDENCE_OVERLAP"
    relation_ancestry: set[str] = set()
    for relation_id in candidate.relation_ids():
        relation = relations.get(relation_id)
        if relation is None:
            return False, f"ROUTING_RELATION_NOT_FOUND:{relation_id}"
        relation_ancestry.update(relation.source_evidence_ids)
        relation_ancestry.update(relation.qualification_evidence_ids)
    if relation_ancestry & qids:
        return False, "ROUTING_QUALIFICATION_RELATION_EVIDENCE_OVERLAP"
    decision = FixedQualifier(ledger).decide(ticket.qualification_evidence, Authority.REFERENCE_ONLY)
    support, accuracy, coverage = evaluate_projection_conditioned_relation_holdout(candidate, ticket.qualification_evidence, ledger, relations)
    qualified_bucket_ids = projection_conditioned_holdout_bucket_ids(candidate, ticket.qualification_evidence, ledger)
    if tuple(sorted(ticket.qualified_bucket_ids)) != qualified_bucket_ids:
        return False, "ROUTING_QUALIFIED_BUCKET_SET_MISMATCH"
    if (support, accuracy, coverage) != (ticket.holdout_support, ticket.holdout_accuracy, ticket.holdout_coverage):
        return False, "ROUTING_HOLDOUT_METRICS_MISMATCH"
    if support < int(min_support):
        return False, "INSUFFICIENT_INDEPENDENT_ROUTING_HOLDOUT"
    if coverage < 1.0:
        return False, "ROUTING_HOLDOUT_COVERAGE_INCOMPLETE"
    if accuracy < float(min_accuracy):
        return False, "ROUTING_HOLDOUT_ACCURACY_BELOW_BOUND"
    if ticket.state not in {QualificationState.SHADOW_QUALIFIED, QualificationState.QUALIFIED}:
        return False, f"NOT_ADMISSIBLE:{ticket.state.value}"
    if decision.state not in {QualificationState.SHADOW_QUALIFIED, QualificationState.QUALIFIED}:
        return False, "QUALIFICATION_EVIDENCE_NOT_SUPPORTIVE"
    return True, "VALID_EXTERNAL_PROJECTION_CONDITIONED_RELATION_QUALIFICATION"
