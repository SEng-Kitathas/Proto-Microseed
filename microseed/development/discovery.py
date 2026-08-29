from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class OperationalTrace:
    """Prelingual operational trace supplied to the bounded discovery bridge.

    The trace boundary and effect coordinates are observations supplied by the
    current sensor/action frame. Recording them here does NOT claim Microseed
    constructed that frame. Dependency epochs are captured by the entity when
    the trace is recorded so a proposal cannot silently outlive its premises.
    """

    trace_id: str
    steps: tuple[str, ...]
    step_effects: tuple[tuple[float, ...], ...]
    operational_scope_id: str | None = None
    obligation_id: str | None = None
    dependency_epochs: tuple[tuple[str, int], ...] = ()
    frame_id: str | None = None
    frame_epoch: int | None = None
    episode_schema_id: str | None = None
    episode_schema_epoch: int | None = None
    topology_ids: tuple[str, ...] = ()
    topology_epochs: tuple[tuple[str, int], ...] = ()
    counterparty_ids: tuple[str, ...] = ()
    counterparty_epochs: tuple[tuple[str, int], ...] = ()
    coordination_ids: tuple[str, ...] = ()
    coordination_epochs: tuple[tuple[str, int], ...] = ()

    def serializable(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "steps": list(self.steps),
            "step_effects": [list(x) for x in self.step_effects],
            "operational_scope_id": self.operational_scope_id,
            "obligation_id": self.obligation_id,
            "dependency_epochs": [list(x) for x in self.dependency_epochs],
            "frame_id": self.frame_id,
            "frame_epoch": self.frame_epoch,
            "episode_schema_id": self.episode_schema_id,
            "episode_schema_epoch": self.episode_schema_epoch,
            "topology_ids": list(self.topology_ids),
            "topology_epochs": [list(x) for x in self.topology_epochs],
            "counterparty_ids": list(self.counterparty_ids),
            "counterparty_epochs": [list(x) for x in self.counterparty_epochs],
            "coordination_ids": list(self.coordination_ids),
            "coordination_epochs": [list(x) for x in self.coordination_epochs],
        }

    @classmethod
    def from_serializable(cls, value: dict[str, Any]) -> "OperationalTrace":
        return cls(
            trace_id=value["trace_id"],
            steps=tuple(value["steps"]),
            step_effects=tuple(tuple(float(y) for y in x) for x in value["step_effects"]),
            operational_scope_id=value.get("operational_scope_id"),
            obligation_id=value.get("obligation_id"),
            dependency_epochs=tuple((str(x[0]), int(x[1])) for x in value.get("dependency_epochs", ())),
            frame_id=value.get("frame_id"),
            frame_epoch=(None if value.get("frame_epoch") is None else int(value.get("frame_epoch"))),
            episode_schema_id=value.get("episode_schema_id"),
            episode_schema_epoch=(None if value.get("episode_schema_epoch") is None else int(value.get("episode_schema_epoch"))),
            topology_ids=tuple(str(x) for x in value.get("topology_ids", ())),
            topology_epochs=tuple((str(x[0]), int(x[1])) for x in value.get("topology_epochs", ())),
            counterparty_ids=tuple(str(x) for x in value.get("counterparty_ids", ())),
            counterparty_epochs=tuple((str(x[0]), int(x[1])) for x in value.get("counterparty_epochs", ())),
            coordination_ids=tuple(str(x) for x in value.get("coordination_ids", ())),
            coordination_epochs=tuple((str(x[0]), int(x[1])) for x in value.get("coordination_epochs", ())),
        )


@dataclass(frozen=True)
class DiscoveryConfig:
    """Constitutional prior for the bounded MS853-877 proposal generator.

    These numbers/language are supplied assistance and MUST remain visible in a
    candidate's ancestry. This is deliberately not presented as a general
    program-discovery mechanism.
    """

    min_len: int = 2
    max_len: int = 3
    min_singleton_samples: int = 5
    min_support: int = 8
    min_global_scopes: int = 2
    min_consistency: float = 0.78
    residual_tolerance_l1: float = 1.1
    min_residual_l1: float = 0.75
    quantization_step: float = 0.5
    max_candidates: int = 8

    def assistance_ancestry(self) -> tuple[str, ...]:
        return (
            "SUPPLIED_TRACE_BOUNDARIES",
            "SUPPLIED_EFFECT_COORDINATES",
            "STABLE_CAPABILITY_HANDLE_IDENTITY",
            f"FIXED_CONTIGUOUS_MOTIF_LANGUAGE_LEN_{self.min_len}_{self.max_len}",
            "FIXED_DISCOVERY_THRESHOLDS",
            "SINGLETON_BASELINE_ESTIMATOR",
            "CROSS_SCOPE_RESIDUAL_HOMOGENEITY_RULE",
        )


@dataclass(frozen=True)
class CandidateFinding:
    motif: tuple[str, ...]
    operational_scope_id: str | None
    support: int
    distinct_scopes: int
    residual: tuple[float, ...]
    consistency: float
    score: float
    source_trace_ids: tuple[str, ...]
    dependency_epochs: tuple[tuple[str, int], ...]
    frame_epochs: tuple[tuple[str, int], ...] = ()
    episode_schema_epochs: tuple[tuple[str, int], ...] = ()
    topology_epochs: tuple[tuple[str, int], ...] = ()
    counterparty_epochs: tuple[tuple[str, int], ...] = ()
    coordination_epochs: tuple[tuple[str, int], ...] = ()

    def structural_payload(self) -> dict[str, Any]:
        return {
            "motif": list(self.motif),
            "operational_scope_id": self.operational_scope_id,
            "support": self.support,
            "distinct_scopes": self.distinct_scopes,
            "residual": list(self.residual),
            "consistency": self.consistency,
            "dependency_epochs": [list(x) for x in self.dependency_epochs],
            "frame_epochs": [list(x) for x in self.frame_epochs],
            "episode_schema_epochs": [list(x) for x in self.episode_schema_epochs],
            "topology_epochs": [list(x) for x in self.topology_epochs],
            "counterparty_epochs": [list(x) for x in self.counterparty_epochs],
            "coordination_epochs": [list(x) for x in self.coordination_epochs],
        }

    def candidate_key(self) -> str:
        raw = json.dumps(
            {
                "motif": self.motif,
                "scope": self.operational_scope_id,
                "residual": self.residual,
                "epochs": self.dependency_epochs,
                "frame_epochs": self.frame_epochs,
                "episode_schema_epochs": self.episode_schema_epochs,
                "topology_epochs": self.topology_epochs,
                "counterparty_epochs": self.counterparty_epochs,
                "coordination_epochs": self.coordination_epochs,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


def _add(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(x + y for x, y in zip(a, b))


def _sub(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(x - y for x, y in zip(a, b))


def _sum(vs: Iterable[tuple[float, ...]], dim: int) -> tuple[float, ...]:
    out = (0.0,) * dim
    for v in vs:
        out = _add(out, v)
    return out


def _l1(v: tuple[float, ...]) -> float:
    return sum(abs(x) for x in v)


def _dist(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return _l1(_sub(a, b))


def _median(vs: list[tuple[float, ...]]) -> tuple[float, ...]:
    return tuple(float(statistics.median([v[i] for v in vs])) for i in range(len(vs[0])))


def _quantize(v: tuple[float, ...], step: float) -> tuple[float, ...]:
    return tuple(round(x / step) * step for x in v)


def _current_trace(
    trace: OperationalTrace,
    current_epochs: dict[str, int],
    current_frame_epochs: dict[str, int] | None = None,
    current_episode_schema_epochs: dict[str, int] | None = None,
    current_topology_epochs: dict[str, int] | None = None,
    current_counterparty_epochs: dict[str, int] | None = None,
    current_coordination_epochs: dict[str, int] | None = None,
) -> bool:
    seen = dict(trace.dependency_epochs)
    if not all(seen.get(step) == current_epochs.get(step) for step in set(trace.steps)):
        return False
    if trace.frame_id is not None:
        if trace.frame_epoch is None or current_frame_epochs is None:
            return False
        if current_frame_epochs.get(trace.frame_id) != trace.frame_epoch:
            return False
    elif trace.frame_epoch is not None:
        return False
    if trace.episode_schema_id is not None:
        if trace.episode_schema_epoch is None or current_episode_schema_epochs is None:
            return False
        if current_episode_schema_epochs.get(trace.episode_schema_id) != trace.episode_schema_epoch:
            return False
    elif trace.episode_schema_epoch is not None:
        return False
    families = (
        (trace.topology_ids, trace.topology_epochs, current_topology_epochs),
        (trace.counterparty_ids, trace.counterparty_epochs, current_counterparty_epochs),
        (trace.coordination_ids, trace.coordination_epochs, current_coordination_epochs),
    )
    for ids, epochs, current in families:
        if tuple(x for x, _ in epochs) != ids:
            return False
        if epochs and current is None:
            return False
        if any(current.get(obj_id) != epoch for obj_id, epoch in epochs):
            return False
    return True


def _singleton_baselines(
    traces: list[OperationalTrace], cfg: DiscoveryConfig
) -> dict[str, tuple[float, ...]]:
    rows: dict[str, list[tuple[float, ...]]] = defaultdict(list)
    for t in traces:
        if len(t.steps) == 1:
            rows[t.steps[0]].append(t.step_effects[0])
    return {
        cap: _median(effects)
        for cap, effects in rows.items()
        if len(effects) >= cfg.min_singleton_samples
    }



def derive_value_bound_singleton_effects(
    traces: Iterable[OperationalTrace],
    current_epochs: dict[str, int],
    episode_value_bindings: dict[tuple[str, int], tuple[str, int]],
    current_value_epochs: dict[str, int],
    cfg: DiscoveryConfig | None = None,
    *,
    current_capability_ids: set[str] | None = None,
    current_frame_epochs: dict[str, int] | None = None,
    current_episode_schema_epochs: dict[str, int] | None = None,
    current_topology_epochs: dict[str, int] | None = None,
    current_counterparty_epochs: dict[str, int] | None = None,
    current_coordination_epochs: dict[str, int] | None = None,
) -> dict[tuple[str, str], dict[str, Any]]:
    """Derive current scalar action/value effects from existing robust trace machinery.

    The scalar coordinate is usable only when a current episode schema binds that
    trace ancestry to exactly one current value variable. Distinct supported
    ancestry shapes are deliberately not averaged into one law. This is a
    read-only projection: no proposal, qualification, persistence, or semantic
    effect identity is created.
    """
    config = cfg or DiscoveryConfig()
    grouped: dict[tuple[Any, ...], list[OperationalTrace]] = defaultdict(list)

    for trace in traces:
        if len(trace.steps) != 1 or len(trace.step_effects) != 1:
            continue
        if len(trace.step_effects[0]) != 1:
            continue
        if trace.episode_schema_id is None or trace.episode_schema_epoch is None:
            continue
        if trace.frame_id is None or trace.frame_epoch is None:
            continue
        if not _current_trace(
            trace,
            current_epochs,
            current_frame_epochs,
            current_episode_schema_epochs,
            current_topology_epochs,
            current_counterparty_epochs,
            current_coordination_epochs,
        ):
            continue

        binding = episode_value_bindings.get(
            (trace.episode_schema_id, int(trace.episode_schema_epoch))
        )
        if binding is None:
            continue
        value_id, value_epoch = binding
        if current_value_epochs.get(value_id) != int(value_epoch):
            continue

        capability_id = trace.steps[0]
        if current_capability_ids is not None and capability_id not in current_capability_ids:
            continue
        shape = (
            capability_id,
            value_id,
            trace.frame_id,
            int(trace.frame_epoch),
            trace.episode_schema_id,
            int(trace.episode_schema_epoch),
            tuple(trace.topology_epochs),
            tuple(trace.counterparty_epochs),
            tuple(trace.coordination_epochs),
        )
        grouped[shape].append(trace)

    supported: dict[tuple[Any, ...], dict[str, Any]] = {}
    for shape, rows in sorted(grouped.items(), key=lambda item: repr(item[0])):
        if len(rows) < config.min_singleton_samples:
            continue
        effects = [row.step_effects[0] for row in rows]
        center = _quantize(_median(effects), config.quantization_step)
        consistency = sum(
            _dist(effect, center) <= config.residual_tolerance_l1
            for effect in effects
        ) / len(effects)
        if consistency < config.min_consistency:
            continue
        capability_epochs = {
            dict(row.dependency_epochs).get(shape[0])
            for row in rows
        }
        if len(capability_epochs) != 1 or None in capability_epochs:
            continue

        supported[shape] = {
            "status": "CURRENT_EFFECT",
            "capability_id": str(shape[0]),
            "value_id": str(shape[1]),
            "capability_epoch": int(next(iter(capability_epochs))),
            "value_epoch": int(episode_value_bindings[(shape[4], shape[5])][1]),
            "effect": float(center[0]),
            "support": len(rows),
            "consistency": float(consistency),
            "frame_epoch": (str(shape[2]), int(shape[3])),
            "episode_schema_epoch": (str(shape[4]), int(shape[5])),
            "source_trace_ids": tuple(sorted(row.trace_id for row in rows)),
            "authority": "MODEL_OUTPUT_ONLY",
            "truth_authority": "NONE",
            "semantic_effect_coordinate_authority": "NONE",
            "assistance_ancestry": config.assistance_ancestry(),
        }

    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for shape, row in supported.items():
        by_pair[(str(shape[0]), str(shape[1]))].append(row)

    result: dict[tuple[str, str], dict[str, Any]] = {}
    for pair, rows in sorted(by_pair.items()):
        if len(rows) == 1:
            result[pair] = rows[0]
            continue
        result[pair] = {
            "status": "UNKNOWN_MULTIPLE_CURRENT_ANCESTRY_SHAPES",
            "capability_id": pair[0],
            "value_id": pair[1],
            "candidate_effects": tuple(sorted(float(row["effect"]) for row in rows)),
            "ancestry_shapes": tuple(
                sorted(
                    (row["frame_epoch"], row["episode_schema_epoch"])
                    for row in rows
                )
            ),
            "authority": "NONE",
            "truth_authority": "NONE",
            "semantic_effect_coordinate_authority": "NONE",
        }
    return result


def derive_value_bound_candidate_motif_effect(
    candidate_id: str,
    motif: tuple[str, ...],
    source_trace_ids: Iterable[str],
    traces: dict[str, OperationalTrace],
    current_epochs: dict[str, int],
    requested_value_id: str,
    episode_value_epochs: dict[tuple[str, int], tuple[tuple[str, int], ...]],
    current_value_epochs: dict[str, int],
    cfg: DiscoveryConfig | None = None,
    *,
    candidate_operational_signature: dict[str, Any] | None = None,
    current_frame_epochs: dict[str, int] | None = None,
    current_episode_schema_epochs: dict[str, int] | None = None,
    current_topology_epochs: dict[str, int] | None = None,
    current_counterparty_epochs: dict[str, int] | None = None,
    current_coordination_epochs: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Project one discovered motif's exact current trace ancestry onto one value.

    This is a read-only bridge from an already-nominated operational motif to the
    same scalar effect shape used by current regulatory action licensing. It does
    not qualify/admit the candidate, select a policy, assign token meaning, claim
    reference, or grant execution/truth authority.

    The candidate's source trace IDs are part of the subject binding. Every source
    trace must still be current and must contain the nominated contiguous motif.
    The exact contributing occurrence count must still match the candidate's
    recorded support when that support is available. Value interpretation is
    allowed only through one exact current episode -> one current value binding.
    """
    config = cfg or DiscoveryConfig()
    motif = tuple(str(x) for x in motif)
    source_ids = tuple(str(x) for x in source_trace_ids)
    sig = candidate_operational_signature or {}

    def unknown(reason: str) -> dict[str, Any]:
        return {
            "status": "UNKNOWN_INCOMPLETE",
            "candidate_id": str(candidate_id),
            "value_id": str(requested_value_id),
            "reason": reason,
            "authority": "NONE",
            "truth_authority": "NONE",
            "semantic_effect_coordinate_authority": "NONE",
            "semantic_signal_authority": "NONE",
            "reference_authority": "NONE",
        }

    if not motif:
        return unknown("CANDIDATE_MOTIF_REQUIRED")
    if not source_ids:
        return unknown("SOURCE_TRACE_IDS_REQUIRED")

    occurrences: list[tuple[OperationalTrace, tuple[float, ...]]] = []
    source_rows: list[OperationalTrace] = []
    for trace_id in source_ids:
        trace = traces.get(trace_id)
        if trace is None:
            return unknown(f"SOURCE_TRACE_MISSING:{trace_id}")
        if not _current_trace(
            trace,
            current_epochs,
            current_frame_epochs,
            current_episode_schema_epochs,
            current_topology_epochs,
            current_counterparty_epochs,
            current_coordination_epochs,
        ):
            return unknown(f"SOURCE_TRACE_NOT_CURRENT:{trace_id}")
        if not trace.step_effects or any(len(v) != 1 for v in trace.step_effects):
            return unknown("SCALAR_VALUE_EFFECT_COORDINATE_REQUIRED")
        found = False
        length = len(motif)
        for start in range(len(trace.steps) - length + 1):
            if tuple(trace.steps[start : start + length]) != motif:
                continue
            found = True
            effect = _sum(trace.step_effects[start : start + length], 1)
            occurrences.append((trace, effect))
        if not found:
            return unknown(f"SOURCE_TRACE_MOTIF_MISMATCH:{trace_id}")
        source_rows.append(trace)

    expected_support = sig.get("support")
    if expected_support is not None and len(occurrences) != int(expected_support):
        return unknown("CANDIDATE_SUPPORT_SUBJECT_MISMATCH")
    if len(occurrences) < config.min_support:
        return unknown("MOTIF_EFFECT_SUPPORT_INSUFFICIENT")

    frame_keys = {(t.frame_id, t.frame_epoch) for t in source_rows}
    episode_keys = {(t.episode_schema_id, t.episode_schema_epoch) for t in source_rows}
    if len(frame_keys) != 1 or next(iter(frame_keys))[0] is None or next(iter(frame_keys))[1] is None:
        return unknown("EXACT_SINGLE_CURRENT_FRAME_ANCESTRY_REQUIRED")
    if len(episode_keys) != 1 or next(iter(episode_keys))[0] is None or next(iter(episode_keys))[1] is None:
        return unknown("EXACT_SINGLE_CURRENT_EPISODE_ANCESTRY_REQUIRED")
    frame_id, frame_epoch = next(iter(frame_keys))
    schema_id, schema_epoch = next(iter(episode_keys))

    # Re-resolve the candidate subject from *all* exact source traces, not just
    # one representative row. Discovery originally requires these ancestry
    # families to be uniform, but a later trace replacement must not silently
    # change the subject while remaining individually current.
    uniform_families: dict[str, tuple[tuple[str, int], ...]] = {}
    for key in ("topology_epochs", "counterparty_epochs", "coordination_epochs"):
        values = {tuple(getattr(trace, key)) for trace in source_rows}
        if len(values) != 1:
            return unknown(f"SOURCE_TRACE_{key.upper()}_SUBJECT_MISMATCH")
        uniform_families[key] = next(iter(values))

    expected_families = (
        ("frame_epochs", ((str(frame_id), int(frame_epoch)),)),
        ("episode_schema_epochs", ((str(schema_id), int(schema_epoch)),)),
        ("topology_epochs", uniform_families["topology_epochs"]),
        ("counterparty_epochs", uniform_families["counterparty_epochs"]),
        ("coordination_epochs", uniform_families["coordination_epochs"]),
    )
    for key, actual in expected_families:
        if key in sig:
            expected = tuple((str(x[0]), int(x[1])) for x in sig.get(key, ()))
            normalized_actual = tuple((str(x[0]), int(x[1])) for x in actual)
            if expected != normalized_actual:
                return unknown(f"CANDIDATE_{key.upper()}_SUBJECT_MISMATCH")

    value_bindings = episode_value_epochs.get((str(schema_id), int(schema_epoch)))
    if value_bindings is None:
        return unknown("CURRENT_EPISODE_VALUE_BINDING_REQUIRED")
    if len(value_bindings) != 1:
        return unknown("EXACT_SINGLE_VALUE_BINDING_REQUIRED")
    bound_value_id, bound_value_epoch = value_bindings[0]
    if str(bound_value_id) != str(requested_value_id):
        return unknown("REQUESTED_VALUE_NOT_EPISODE_BOUND")
    if current_value_epochs.get(str(requested_value_id)) != int(bound_value_epoch):
        return unknown("BOUND_VALUE_NOT_CURRENT")

    effects = [float(effect[0]) for _, effect in occurrences]
    center = _quantize((float(statistics.median(effects)),), config.quantization_step)[0]
    consistency = sum(
        abs(effect - center) <= config.residual_tolerance_l1
        for effect in effects
    ) / len(effects)
    if consistency < config.min_consistency:
        return unknown("MOTIF_EFFECT_CONSISTENCY_INSUFFICIENT")

    return {
        "status": "CURRENT_EFFECT",
        "candidate_id": str(candidate_id),
        "capability_id": str(candidate_id),
        "value_id": str(requested_value_id),
        "value_epoch": int(bound_value_epoch),
        "effect": float(center),
        "support": len(occurrences),
        "consistency": float(consistency),
        "frame_epoch": (str(frame_id), int(frame_epoch)),
        "episode_schema_epoch": (str(schema_id), int(schema_epoch)),
        "topology_epochs": tuple(source_rows[0].topology_epochs),
        "counterparty_epochs": tuple(source_rows[0].counterparty_epochs),
        "coordination_epochs": tuple(source_rows[0].coordination_epochs),
        "source_trace_ids": source_ids,
        "authority": "MODEL_OUTPUT_ONLY",
        "truth_authority": "NONE",
        "semantic_effect_coordinate_authority": "NONE",
        "semantic_signal_authority": "NONE",
        "reference_authority": "NONE",
        "assistance_ancestry": (
            "CURRENT_SINGLE_VALUE_EPISODE_BINDING",
            "EXACT_DISCOVERED_MOTIF_SOURCE_TRACES",
            "SUPPLIED_SCALAR_VALUE_EFFECT_COORDINATE",
        ),
    }

def _occurrences(
    traces: list[OperationalTrace], cfg: DiscoveryConfig
) -> dict[tuple[str, ...], list[tuple[OperationalTrace, tuple[float, ...]]]]:
    out: dict[tuple[str, ...], list[tuple[OperationalTrace, tuple[float, ...]]]] = defaultdict(list)
    for t in traces:
        dim = len(t.step_effects[0])
        for length in range(cfg.min_len, min(cfg.max_len, len(t.steps)) + 1):
            for start in range(len(t.steps) - length + 1):
                motif = t.steps[start : start + length]
                effect = _sum(t.step_effects[start : start + length], dim)
                out[motif].append((t, effect))
    return out


def _uniform_epoch_family(
    rows: list[tuple[OperationalTrace, tuple[float, ...]]],
    attr: str,
) -> tuple[tuple[str, int], ...] | None:
    values = {tuple(getattr(trace, attr)) for trace, _ in rows}
    if len(values) != 1:
        return None
    return next(iter(values))


def _finding_for_rows(
    motif: tuple[str, ...],
    rows: list[tuple[OperationalTrace, tuple[float, ...]]],
    baselines: dict[str, tuple[float, ...]],
    cfg: DiscoveryConfig,
    *,
    scope: str | None,
) -> CandidateFinding | None:
    if len(rows) < cfg.min_support or any(x not in baselines for x in motif):
        return None
    dim = len(next(iter(baselines.values())))
    predicted = _sum([baselines[x] for x in motif], dim)
    residuals = [_sub(effect, predicted) for _, effect in rows]
    center = _quantize(_median(residuals), cfg.quantization_step)
    novelty = _l1(center)
    consistency = sum(_dist(r, center) <= cfg.residual_tolerance_l1 for r in residuals) / len(residuals)
    if novelty < cfg.min_residual_l1 or consistency < cfg.min_consistency:
        return None
    scopes = {t.operational_scope_id for t, _ in rows}
    epoch_rows = [dict(t.dependency_epochs) for t, _ in rows]
    dep_epochs: list[tuple[str, int]] = []
    for dep in dict.fromkeys(motif):
        vals = {row.get(dep) for row in epoch_rows}
        if len(vals) != 1 or None in vals:
            return None
        dep_epochs.append((dep, int(next(iter(vals)))))
    frame_values: dict[str, set[int | None]] = defaultdict(set)
    any_frame = False
    any_legacy = False
    for trace, _ in rows:
        if trace.frame_id is None:
            any_legacy = True
            continue
        any_frame = True
        frame_values[trace.frame_id].add(trace.frame_epoch)
    # Do not mix learned-frame and legacy/supplied-frame evidence into one finding:
    # their assistance/currentness ancestry is materially different.
    if any_frame and any_legacy:
        return None
    frame_epochs: list[tuple[str, int]] = []
    for frame_id, vals in sorted(frame_values.items()):
        if len(vals) != 1 or None in vals:
            return None
        frame_epochs.append((frame_id, int(next(iter(vals)))))
    episode_values: dict[str, set[int | None]] = defaultdict(set)
    any_episode_schema = False
    any_ungrouped_schema = False
    for trace, _ in rows:
        if trace.episode_schema_id is None:
            any_ungrouped_schema = True
            continue
        any_episode_schema = True
        episode_values[trace.episode_schema_id].add(trace.episode_schema_epoch)
    # Do not mix explicitly schema-bound grouping evidence with legacy/supplied
    # grouping in one candidate: the assistance/currentness ancestry differs.
    if any_episode_schema and any_ungrouped_schema:
        return None
    episode_schema_epochs: list[tuple[str, int]] = []
    for schema_id, vals in sorted(episode_values.items()):
        if len(vals) != 1 or None in vals:
            return None
        episode_schema_epochs.append((schema_id, int(next(iter(vals)))))
    topology_epochs = _uniform_epoch_family(rows, "topology_epochs")
    counterparty_epochs = _uniform_epoch_family(rows, "counterparty_epochs")
    coordination_epochs = _uniform_epoch_family(rows, "coordination_epochs")
    if topology_epochs is None or counterparty_epochs is None or coordination_epochs is None:
        return None
    return CandidateFinding(
        motif=motif,
        operational_scope_id=scope,
        support=len(rows),
        distinct_scopes=len(scopes),
        residual=center,
        consistency=consistency,
        score=len(rows) * consistency * novelty,
        source_trace_ids=tuple(sorted({t.trace_id for t, _ in rows})),
        dependency_epochs=tuple(dep_epochs),
        frame_epochs=tuple(frame_epochs),
        episode_schema_epochs=tuple(episode_schema_epochs),
        topology_epochs=topology_epochs,
        counterparty_epochs=counterparty_epochs,
        coordination_epochs=coordination_epochs,
    )


def discover_candidates(
    traces: Iterable[OperationalTrace],
    current_epochs: dict[str, int],
    cfg: DiscoveryConfig | None = None,
    *,
    current_frame_epochs: dict[str, int] | None = None,
    current_episode_schema_epochs: dict[str, int] | None = None,
    current_topology_epochs: dict[str, int] | None = None,
    current_counterparty_epochs: dict[str, int] | None = None,
    current_coordination_epochs: dict[str, int] | None = None,
) -> list[CandidateFinding]:
    """Return bounded high-recall proposal candidates, never qualification.

    Global findings require the same residual to recur independently in at least
    `min_global_scopes` opaque operational scopes. Relations that only survive in
    one scope may still be proposed as scope-local candidates. The caller must
    use external qualification before admission.
    """

    cfg = cfg or DiscoveryConfig()
    live = [t for t in traces if t.steps and t.step_effects and len(t.steps) == len(t.step_effects)]
    live = [t for t in live if _current_trace(
        t, current_epochs, current_frame_epochs, current_episode_schema_epochs,
        current_topology_epochs, current_counterparty_epochs, current_coordination_epochs,
    )]
    if not live:
        return []
    dims = {len(v) for t in live for v in t.step_effects}
    if len(dims) != 1 or 0 in dims:
        return []
    baselines = _singleton_baselines(live, cfg)
    if not baselines:
        return []
    occurrences = _occurrences(live, cfg)
    findings: list[CandidateFinding] = []
    for motif, rows in occurrences.items():
        by_scope: dict[str | None, list[tuple[OperationalTrace, tuple[float, ...]]]] = defaultdict(list)
        for row in rows:
            by_scope[row[0].operational_scope_id].append(row)
        local_findings = [
            x
            for scope, scope_rows in by_scope.items()
            if (x := _finding_for_rows(motif, scope_rows, baselines, cfg, scope=scope)) is not None
        ]
        # A global proposal requires independently recurring compatible residuals.
        if len(local_findings) >= cfg.min_global_scopes:
            best_group: list[CandidateFinding] = []
            for seed in local_findings:
                group = [x for x in local_findings if _dist(x.residual, seed.residual) <= cfg.quantization_step]
                if len(group) > len(best_group):
                    best_group = group
            if len({x.operational_scope_id for x in best_group}) >= cfg.min_global_scopes:
                global_rows = [
                    row for row in rows if row[0].operational_scope_id in {x.operational_scope_id for x in best_group}
                ]
                g = _finding_for_rows(motif, global_rows, baselines, cfg, scope=None)
                if g is not None:
                    findings.append(g)
        # Preserve incompatible or one-scope relations as explicitly local proposals.
        if not any(f.motif == motif and f.operational_scope_id is None for f in findings):
            findings.extend(local_findings)
    findings.sort(key=lambda x: (-x.score, x.motif, str(x.operational_scope_id)))
    return findings[: cfg.max_candidates]
