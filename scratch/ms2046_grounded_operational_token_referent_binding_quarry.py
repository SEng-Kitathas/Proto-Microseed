from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority,
    CapabilityContract,
    Microseed,
    OperationalCoordinationContract,
    OperationalCounterpartyContract,
    QualificationState,
    QueryObligation,
)
from microseed.cognition.referents import (
    derive_affordance_relative_referent_signature,
    nominate_by_boundary_coherence,
)
from scratch.ms1958_proto_referent_boundary_coherence import boundaries

ACT = QueryObligation("MS2046-ACT", "opaque effect", Authority.EFFECT, operational_scope_id="S")
OBS = QueryObligation("MS2046-OBS", "opaque raw observation", Authority.OBSERVATION_ONLY, operational_scope_id="S")
CAL_SCHEDULE = ("FX-P", "FX-Q", "FX-G", "FX-P", "FX-Q")


def _sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


class GroundedReferenceWorld:
    def __init__(self) -> None:
        self.layout = "A"
        self.alias = False
        self.signal_mode = "P"
        self.generations = [0, 0]
        self.reset_state()

    def reset_state(self) -> None:
        self.latent = [0, 0]

    def configure_layout(self, layout: str) -> None:
        if layout not in {"A", "B"}:
            raise ValueError(layout)
        self.layout = layout
        self.reset_state()

    def configure_signal_mode(self, mode: str) -> None:
        if mode not in {"P", "Q", "BOTH", "NONE"}:
            raise ValueError(mode)
        self.signal_mode = mode

    def configure_alias(self, alias: bool) -> None:
        self.alias = bool(alias)

    def replace_p_perfect_copy(self) -> None:
        self.generations[0] += 1

    def act(self, action_id: str) -> dict[str, object]:
        if action_id == "FX-P":
            if self.alias:
                self.latent[0] += 1; self.latent[1] += 1
            else:
                self.latent[0] += 1
        elif action_id == "FX-Q":
            if self.alias:
                self.latent[0] += 1; self.latent[1] += 1
            else:
                self.latent[1] += 1
        elif action_id == "FX-G":
            self.latent[0] += 1; self.latent[1] += 1
        elif action_id == "SIG-X":
            if self.signal_mode == "P":
                self.latent[0] += 1
            elif self.signal_mode == "Q":
                self.latent[1] += 1
            elif self.signal_mode == "BOTH":
                self.latent[0] += 1; self.latent[1] += 1
        elif action_id == "hello":
            # Human-readable surface intentionally has no grounded external convention.
            pass
        else:
            raise ValueError(action_id)
        return {"opaque_action_receipt": action_id}

    def observe(self) -> tuple[int, ...]:
        if self.layout == "A":
            mapping = (0, 0, 1, 1)
            scales = (1, 1, 1, 1)
            offsets = (7, 31, 79, 127)
        else:
            mapping = (1, 0, 1, 0)
            scales = (11, 13, 17, 19)
            offsets = (211, 307, 401, 503)
        counts = {0: 0, 1: 0}
        out: list[int] = []
        for i, source in enumerate(mapping):
            local = counts[source]; counts[source] += 1
            x = self.latent[source]
            raw = scales[i] * (x * x * (source + 5) + x * (source + 17) + 3 * local) + offsets[i]
            out.append(raw)
        return tuple(out)


def _counterparty() -> OperationalCounterpartyContract:
    c = OperationalCounterpartyContract(
        "CP-X", "opaque-independent-causal-source", "", Authority.DERIVED_READ_ONLY,
        ("MS2046",), "CURRENT", qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXTERNALLY_QUALIFIED_COUNTERPARTY_BOUNDARY",),
        invariants=("NO_SEMANTIC_IDENTITY_AUTHORITY",),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def _coordination() -> OperationalCoordinationContract:
    c = OperationalCoordinationContract(
        "COORD-X", "opaque-token-contingent-referent-localized-effect", (("CP-X", 0),), "",
        Authority.DERIVED_READ_ONLY, ("MS2046",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXTERNALLY_QUALIFIED_COORDINATION_BOUNDARY",),
        invariants=("SIGNAL != REFERENCE", "TOKEN_EMITTED != TOKEN_MEANS"),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def _cap(cid: str, authority: Authority, handler) -> CapabilityContract:
    return CapabilityContract(
        cid, "opaque", {}, {}, ("NO_SEMANTIC_REFERENCE_AUTHORITY",), (), authority,
        ("MS2046",), "CURRENT", {},
        query_obligation_id="MS2046-ACT" if authority == Authority.EFFECT else "MS2046-OBS",
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=handler, operational_scope_id="S",
    )


def _build(root: Path):
    ms = Microseed(root)
    world = GroundedReferenceWorld()
    ms.register_operational_counterparty(_counterparty())
    ms.register_operational_coordination(_coordination())
    for cid in ("FX-P", "FX-Q", "FX-G", "SIG-X", "hello"):
        ms.register_capability(
            _cap(cid, Authority.EFFECT, lambda _cid=cid, **_: world.act(_cid)),
            coordination_dependencies=(("COORD-X", 0),) if cid in {"SIG-X", "hello"} else (),
        )
    ms.register_capability(_cap("OBS-RAW", Authority.OBSERVATION_ONLY, lambda **_: {"channels": world.observe()}))
    return ms, world


def _observe(ms: Microseed) -> tuple[int, ...]:
    return tuple(ms.capabilities.invoke("OBS-RAW", OBS)["value"]["channels"])


def _calibrate(ms: Microseed, world: GroundedReferenceWorld) -> dict[str, object]:
    world.reset_state()
    samples = [_observe(ms)]
    for action in CAL_SCHEDULE:
        ms.capabilities.invoke(action, ACT)
        samples.append(_observe(ms))
    traces = tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b = boundaries(traces)
    nomination = nominate_by_boundary_coherence(b)
    rows = []
    for group in nomination.groups:
        sig = derive_affordance_relative_referent_signature(b, group, CAL_SCHEDULE)
        assert sig.status == "OPERATIONAL_REFERENT_SIGNATURE_DERIVED", sig
        rows.append({
            "group": tuple(group),
            "signature_sha256": str(sig.signature_sha256),
            "action_response_rows": tuple(sig.action_response_rows),
        })
    return {
        "status": nomination.status,
        "reason": nomination.reason,
        "rows": tuple(rows),
        "identity_authority": nomination.identity_authority,
    }


def _changed(before: tuple[int, ...], after: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(i for i, (a, b) in enumerate(zip(before, after)) if a != b)


def _use_episode(ms: Microseed, world: GroundedReferenceWorld, signal_id: str, index: int) -> dict[str, object]:
    calibration = _calibrate(ms, world)
    if calibration["status"] != "REFERENT_PARTITION_NOMINATED":
        return {"status": "DEFER_UNKNOWN", "reason": "CURRENT_OPERATIONAL_REFERENT_PARTITION_REQUIRED", "calibration": calibration}
    world.reset_state()
    before = _observe(ms)
    receipt = ms.capabilities.invoke(signal_id, ACT)
    after = _observe(ms)
    changed = _changed(before, after)
    matching = [row for row in calibration["rows"] if tuple(row["group"]) == changed]
    if len(matching) != 1:
        return {
            "status": "DEFER_UNKNOWN",
            "reason": "EXACT_SINGLE_CURRENT_OPERATIONAL_REFERENT_EFFECT_REQUIRED",
            "changed_channels": changed,
            "calibration": calibration,
        }
    row = matching[0]
    cap = ms.capabilities.contracts[signal_id]
    coord = ms.coordinations.contracts["COORD-X"]
    payload = {
        "episode_index": index,
        "signal_capability_id": signal_id,
        "signal_capability_epoch": ms.capabilities.epochs[signal_id],
        "signal_capability_signature_sha256": cap.computed_signature_sha256(),
        "coordination_id": "COORD-X",
        "coordination_epoch": ms.coordinations.epochs["COORD-X"],
        "coordination_signature_sha256": coord.computed_signature_sha256(),
        "target_operational_referent_signature_sha256": row["signature_sha256"],
        "target_group_current_channels": list(row["group"]),
        "before_raw": list(before),
        "after_raw": list(after),
        "effect_receipt": receipt["value"],
    }
    return {"status": "CURRENT_GROUNDED_SIGNAL_USE_EPISODE", "payload": payload, "episode_sha256": _sha(payload)}


def derive_binding_candidate(ms: Microseed, episodes: tuple[dict[str, object], ...], holdouts: tuple[dict[str, object], ...], signal_id: str = "SIG-X") -> dict[str, object]:
    base = {
        "semantic_reference_authority": "NONE",
        "token_meaning_authority": "NONE",
        "numerical_identity_authority": "NONE",
        "truth_authority": "NONE",
        "execution_authority": "NONE",
        "language_authority": "NONE",
    }
    if len(episodes) < 8:
        return {**base, "status": "DEFER_UNKNOWN", "reason": "SUFFICIENT_GROUNDED_USE_HISTORY_REQUIRED"}
    if len(holdouts) < 4:
        return {**base, "status": "DEFER_UNKNOWN", "reason": "INDEPENDENT_GROUNDED_HOLDOUT_REQUIRED"}
    rows = tuple(episodes) + tuple(holdouts)
    if any(row.get("status") != "CURRENT_GROUNDED_SIGNAL_USE_EPISODE" for row in rows):
        return {**base, "status": "DEFER_UNKNOWN", "reason": "EVERY_GROUNDED_USE_EPISODE_MUST_RESOLVE_EXACTLY"}
    train_sigs = {str(row["payload"]["target_operational_referent_signature_sha256"]) for row in episodes}  # type: ignore[index]
    hold_sigs = {str(row["payload"]["target_operational_referent_signature_sha256"]) for row in holdouts}  # type: ignore[index]
    if len(train_sigs) != 1:
        return {**base, "status": "DEFER_UNKNOWN", "reason": "TRAINING_REFERENT_BINDING_NOT_UNIQUE"}
    target = next(iter(train_sigs))
    if hold_sigs != {target}:
        return {**base, "status": "DEFER_UNKNOWN", "reason": "HOLDOUT_REFERENT_BINDING_DISAGREES"}
    if not ms.capabilities.is_current(signal_id):
        return {**base, "status": "DEFER_UNKNOWN", "reason": "SIGNAL_CAPABILITY_NOT_CURRENT"}
    if not ms.coordinations.is_current("COORD-X"):
        return {**base, "status": "DEFER_UNKNOWN", "reason": "COORDINATION_NOT_CURRENT"}
    cap = ms.capabilities.contracts[signal_id]
    coord = ms.coordinations.contracts["COORD-X"]
    first = episodes[0]["payload"]  # type: ignore[index]
    if int(first["signal_capability_epoch"]) != int(ms.capabilities.epochs[signal_id]) or str(first["signal_capability_signature_sha256"]) != cap.computed_signature_sha256():
        return {**base, "status": "DEFER_UNKNOWN", "reason": "SIGNAL_CAPABILITY_DESCRIPTOR_DRIFT"}
    if int(first["coordination_epoch"]) != int(ms.coordinations.epochs["COORD-X"]) or str(first["coordination_signature_sha256"]) != coord.computed_signature_sha256():
        return {**base, "status": "DEFER_UNKNOWN", "reason": "COORDINATION_DESCRIPTOR_DRIFT"}
    source_ids = tuple(str(row["episode_sha256"]) for row in rows)
    binding = {
        "signal_capability_id": signal_id,
        "signal_capability_epoch": ms.capabilities.epochs[signal_id],
        "signal_capability_signature_sha256": cap.computed_signature_sha256(),
        "coordination_id": "COORD-X",
        "coordination_epoch": ms.coordinations.epochs["COORD-X"],
        "coordination_signature_sha256": coord.computed_signature_sha256(),
        "operational_referent_signature_sha256": target,
        "training_episode_sha256": [str(row["episode_sha256"]) for row in episodes],
        "holdout_episode_sha256": [str(row["episode_sha256"]) for row in holdouts],
    }
    return {
        **base,
        "status": "QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE",
        "reason": "DISJOINT_GROUNDED_USE_HISTORY_AGREES_ON_ONE_CURRENT_OPERATIONAL_REFERENT_SIGNATURE",
        "binding_id": "OP-REF-BIND-" + _sha(binding)[:24],
        "binding": binding,
        "source_episode_sha256": source_ids,
        "authority_gain": "NONE",
    }


def binding_status(ms: Microseed, candidate: dict[str, object]) -> dict[str, object]:
    if candidate.get("status") != "QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE":
        return {"status": "UNKNOWN_INCOMPLETE", "reason": "QUALIFIED_BINDING_CANDIDATE_REQUIRED"}
    b = candidate["binding"]
    sid = str(b["signal_capability_id"])
    if not ms.capabilities.is_current(sid, int(b["signal_capability_epoch"])):
        return {"status": "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", "reason": "SIGNAL_CAPABILITY_NOT_CURRENT"}
    if ms.capabilities.contracts[sid].computed_signature_sha256() != str(b["signal_capability_signature_sha256"]):
        return {"status": "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", "reason": "SIGNAL_CAPABILITY_SIGNATURE_DRIFT"}
    if not ms.coordinations.is_current(str(b["coordination_id"]), int(b["coordination_epoch"])):
        return {"status": "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", "reason": "COORDINATION_NOT_CURRENT"}
    if ms.coordinations.contracts[str(b["coordination_id"])].computed_signature_sha256() != str(b["coordination_signature_sha256"]):
        return {"status": "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", "reason": "COORDINATION_SIGNATURE_DRIFT"}
    return {"status": "CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", "reason": "BOUND_CURRENTNESS_DESCRIPTORS_MATCH"}


def _history(ms: Microseed, world: GroundedReferenceWorld, *, train_mode: str = "P", hold_mode: str = "P", alias: bool = False):
    world.configure_alias(alias)
    world.configure_signal_mode(train_mode)
    world.configure_layout("A")
    train = tuple(_use_episode(ms, world, "SIG-X", i) for i in range(10))
    world.configure_signal_mode(hold_mode)
    world.configure_layout("B")
    hold = tuple(_use_episode(ms, world, "SIG-X", 100 + i) for i in range(6))
    return train, hold


def run_positive_and_permutation() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="ms2046-positive-") as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world)
            candidate = derive_binding_candidate(ms, train, hold)
            assert candidate["status"] == "QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", candidate
            assert binding_status(ms, candidate)["status"] == "CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE"
            train_groups = {tuple(row["payload"]["target_group_current_channels"]) for row in train}  # type: ignore[index]
            hold_groups = {tuple(row["payload"]["target_group_current_channels"]) for row in hold}  # type: ignore[index]
            assert train_groups != hold_groups
            return {"status": "PASS", "candidate": candidate, "train_groups": sorted(train_groups), "holdout_groups": sorted(hold_groups)}
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def run_ambiguous_and_alias_hostiles() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="ms2046-ambig-") as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world, train_mode="BOTH", hold_mode="BOTH")
            candidate = derive_binding_candidate(ms, train, hold)
            assert candidate["status"] == "DEFER_UNKNOWN", candidate
            assert candidate["reason"] == "EVERY_GROUNDED_USE_EPISODE_MUST_RESOLVE_EXACTLY"
            assert all(row["status"] == "DEFER_UNKNOWN" for row in train + hold)
            ambiguous = candidate
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    with tempfile.TemporaryDirectory(prefix="ms2046-alias-") as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world, alias=True)
            candidate = derive_binding_candidate(ms, train, hold)
            assert candidate["status"] == "DEFER_UNKNOWN", candidate
            assert candidate["reason"] == "EVERY_GROUNDED_USE_EPISODE_MUST_RESOLVE_EXACTLY"
            alias_result = candidate
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    return {"status": "PASS", "ambiguous_signal": ambiguous, "referent_alias": alias_result}


def run_currentness_hostiles() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="ms2046-current-") as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world)
            candidate = derive_binding_candidate(ms, train, hold)
            ms.invalidate_capability("SIG-X", reason="MS2046_SIGNAL_DRIFT")
            s = binding_status(ms, candidate)
            assert s == {"status": "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", "reason": "SIGNAL_CAPABILITY_NOT_CURRENT"}
            signal = s
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    with tempfile.TemporaryDirectory(prefix="ms2046-coord-") as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world)
            candidate = derive_binding_candidate(ms, train, hold)
            ms.change_operational_coordination("COORD-X", reason="MS2046_COORDINATION_DRIFT")
            s = binding_status(ms, candidate)
            assert s == {"status": "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", "reason": "SIGNAL_CAPABILITY_NOT_CURRENT"} or s == {"status": "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE", "reason": "COORDINATION_NOT_CURRENT"}
            coord = s
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    return {"status": "PASS", "signal_drift": signal, "coordination_drift": coord}


def run_perfect_copy_and_readable_token() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="ms2046-copy-") as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world)
            before = derive_binding_candidate(ms, train, hold)
            world.replace_p_perfect_copy()
            # New layout-B grounded uses remain operationally identical after evaluator-only replacement.
            world.configure_layout("B")
            hold2 = tuple(_use_episode(ms, world, "SIG-X", 200 + i) for i in range(6))
            after = derive_binding_candidate(ms, train, hold2)
            assert before["binding"]["operational_referent_signature_sha256"] == after["binding"]["operational_referent_signature_sha256"]
            assert before["numerical_identity_authority"] == after["numerical_identity_authority"] == "NONE"
            generation = world.generations[0]
            assert generation == 1
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    with tempfile.TemporaryDirectory(prefix="ms2046-readable-") as td:
        ms, world = _build(Path(td))
        try:
            candidate = derive_binding_candidate(ms, (), (), signal_id="hello")
            assert candidate["status"] == "DEFER_UNKNOWN"
            assert candidate["reason"] == "SUFFICIENT_GROUNDED_USE_HISTORY_REQUIRED"
            readable = candidate
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    return {"status": "PASS", "perfect_copy_generation_changed": generation, "operational_binding_survives": True, "numerical_identity_authority": "NONE", "readable_ungrounded_token": readable}


def run_convention_reversal_hostile() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="ms2046-reversal-") as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world, train_mode="P", hold_mode="Q")
            candidate = derive_binding_candidate(ms, train, hold)
            assert candidate["status"] == "DEFER_UNKNOWN", candidate
            assert candidate["reason"] == "HOLDOUT_REFERENT_BINDING_DISAGREES"
            return {"status": "PASS", "candidate": candidate, "automatic_new_meaning": "NO"}
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def run_ms2046() -> dict[str, object]:
    return {
        "status": "GROUNDED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE_EARNED",
        "positive": run_positive_and_permutation(),
        "ambiguity": run_ambiguous_and_alias_hostiles(),
        "currentness": run_currentness_hostiles(),
        "copy_and_fluency": run_perfect_copy_and_readable_token(),
        "convention_reversal": run_convention_reversal_hostile(),
        "earned": "REPEATED_CURRENT_SIGNAL_USE_PLUS_REFERENT_LOCALIZED_COUNTERPARTY_EFFECT_CAN_SUPPORT_A_QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE_WITHOUT_SEMANTIC_REFERENCE_AUTHORITY",
        "gate_law": "GROUNDING_CANDIDATE != LANGUAGE_GATE_ADMISSION",
        "semantic_reference_authority": "NONE",
        "language_authority": "NONE",
        "new_language_or_reference_manager_required": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2046(), indent=2, sort_keys=True, default=str))
