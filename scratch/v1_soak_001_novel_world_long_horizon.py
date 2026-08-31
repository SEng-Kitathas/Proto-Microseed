from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
import time
import zipfile
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from microseed import Authority, Microseed
from microseed.cognition.referents import OperationalReferentSignature
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier
from microseed.development.predictive_adaptation import PredictiveCurrentnessConfig
from microseed.development.rehearsal import CounterfactualRehearsalConfig
from research.substrate_shadow.environment_adapter import AdapterConfig, ShadowEnvironmentAdapter
from scratch.ms1997_lived_history_to_endogenous_program import MAIN
from scratch.ms1998_observable_context_assistance_removal import (
    ObservableContextWorld,
    _candidate_by_action,
    qualify_relations_from_later_history,
    relation_holdout_refs,
    run_assisted_episode,
)

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None

CANONICAL_V1 = "0fa41f1ed4cf2fbd341b5f0b63adbc0034d4ac39"
PROBES = ("Q0", "Q1", "Q2", "Q3")
ENTITY_PATTERNS = (0b0001, 0b0010, 0b0011, 0b0100, 0b0101, 0b0110, 0b0111, 0b1000)
VISUAL_MAPPINGS = {
    "FULL_A": tuple(x for e in range(8) for x in (e, e)),
    "CROSS": (0, 4, 1, 5, 2, 6, 3, 7, 7, 3, 6, 2, 5, 1, 4, 0),
    "OCCLUDE_25": (0, 0, 1, 1, 3, 3, 4, 4, 6, 6, 7, 7),
    "POST": (7, 2, 5, 0, 3, 6, 1, 4, 4, 1, 6, 3, 0, 5, 2, 7),
    "ALIAS_67": (2, 6, 0, 7, 4, 1, 5, 3, 3, 5, 1, 4, 7, 0, 6, 2),
    "POST_2": (5, 0, 6, 1, 7, 2, 4, 3, 3, 4, 2, 7, 1, 6, 0, 5),
}


class NovelDevelopmentalWorld(ObservableContextWorld):
    """V1 control lane plus evaluator-only high-dimensional referent diagnostics.

    The live control lane retains the already-earned MS1998 four-coordinate raw bound.
    The causal regime changes only R-41's terminal consequence: P ends at ``u`` and
    D ends at ``w``.  Regulatory effects stay +1 throughout, so current-value
    reprojection cannot mask stale transition-model reuse.
    """

    name = "V1-SOAK-001-NOVEL-DEVELOPMENTAL-WORLD"
    compatibility_sha256 = hashlib.sha256(
        b"V1-SOAK-001:v2:K17-M23-R41:terminal-only-R-drift:8-referents:forked-diagnostics"
    ).hexdigest()

    def __init__(self, seed: int = 2053001) -> None:
        super().__init__()
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.episode_index = 0
        self.total_episodes = 1
        self.visual_phase = "FULL_A"
        self.entity_latent = [0] * 8
        self.entity_generations = [0] * 8
        self.referent_probe_step = 0
        self.spurious = 0

    def configure_mode(self, mode: str) -> None:
        if mode not in {"P", "D"}:
            raise ValueError("INVALID_WORLD_MODE")
        self.mode = mode

    @property
    def sign(self) -> float:
        return 1.0

    def reset(self) -> None:
        self.phase = 0
        self.value = -3.0

    def _state(self) -> str:
        if self.phase == 0:
            return "s0"
        if self.phase == 1:
            return "s1"
        if self.phase == 2:
            return "s2"
        return "u" if self.mode == "P" else "w"

    def fork(self) -> "NovelDevelopmentalWorld":
        return deepcopy(self)

    def configure_episode(self, episode_index: int, total_episodes: int, shift_episode: int) -> None:
        self.episode_index = int(episode_index)
        self.total_episodes = max(1, int(total_episodes))
        self.configure_mode("P" if episode_index < shift_episode else "D")
        q = episode_index / max(1, total_episodes - 1)
        if q < 0.20:
            self.visual_phase = "FULL_A"
        elif q < 0.35:
            self.visual_phase = "CROSS"
        elif q < 0.45:
            self.visual_phase = "OCCLUDE_25"
        elif q < 0.62:
            self.visual_phase = "POST"
        elif q < 0.76:
            self.visual_phase = "ALIAS_67"
        else:
            self.visual_phase = "POST_2"
        self.spurious = ((episode_index // 7) ^ (episode_index // 19) ^ self.seed) & 1
        if episode_index in {shift_episode, int(total_episodes * 0.82)}:
            self.entity_generations[(episode_index // max(1, shift_episode)) % 8] += 1

    def _effective_pattern(self, entity: int) -> int:
        if self.visual_phase == "ALIAS_67" and entity == 7:
            return ENTITY_PATTERNS[6]
        return ENTITY_PATTERNS[entity]

    def _touch_entities(self, probe_index: int) -> None:
        bit = 1 << probe_index
        for entity in range(8):
            if self._effective_pattern(entity) & bit:
                self.entity_latent[entity] += 1

    def apply(self, action_id: str) -> dict:
        receipt = super().apply(action_id)
        self._touch_entities(MAIN.index(action_id))
        return receipt

    def reset_referent_probe(self) -> None:
        self.referent_probe_step = 0
        self.entity_latent = [0] * 8

    def probe(self, probe_id: str) -> dict[str, object]:
        if self.referent_probe_step >= len(PROBES) or PROBES[self.referent_probe_step] != probe_id:
            raise RuntimeError("WORLD_REJECTED_OUT_OF_SEQUENCE_REFERENT_PROBE")
        self._touch_entities(self.referent_probe_step)
        self.referent_probe_step += 1
        return {"receipt": "opaque-referent-probe-applied", "probe_id": probe_id, "step": self.referent_probe_step}

    def _render_entity_channel(self, entity: int, local: int, channel_index: int) -> int:
        phase_index = list(VISUAL_MAPPINGS).index(self.visual_phase) + 1
        generation = self.entity_generations[entity]
        state = self.entity_latent[entity]
        scale = 2 + ((phase_index * 11 + entity * 7 + local * 5 + generation * 3) % 23)
        offset = 1009 + phase_index * 10007 + entity * 997 + local * 271 + channel_index * 13 + generation * 1231
        return scale * (state * state * (entity + 3) + state * (local + 5) + 17 * local) + offset

    def observe_entities(self) -> tuple[int, ...]:
        mapping = VISUAL_MAPPINGS[self.visual_phase]
        counts = Counter()
        out: list[int] = []
        for channel_index, entity in enumerate(mapping):
            local = counts[entity]
            counts[entity] += 1
            out.append(self._render_entity_channel(entity, local, channel_index))
        return tuple(out)

    def observe(self) -> dict:
        row = super().observe()
        base = list(row["raw_tokens"])
        # Preserve the inherited max-4 live raw-ingress contract.
        row["raw_tokens"] = base + [f"n{self.spurious}", f"r{sum(self.entity_latent) & 1}"]
        row["visual_phase"] = self.visual_phase
        return row


@dataclass(frozen=True)
class SoakConfig:
    episodes: int = 1200
    shift_episode: int = 600
    snapshot_every: int = 300
    referent_every: int = 100
    seed: int = 2053001
    max_rss_mb: int = 1536
    max_disk_mb: int = 1024
    max_action_seconds: float = 10.0


class Telemetry:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.fp = path.open("a", encoding="utf-8", newline="\n")
        self.count = 0

    def emit(self, kind: str, **payload: object) -> None:
        row = {"seq": self.count, "kind": kind, "wall_time": time.time(), **payload}
        self.fp.write(json.dumps(row, sort_keys=True, default=str, separators=(",", ":")) + "\n")
        self.fp.flush()
        self.count += 1

    def close(self) -> None:
        self.fp.close()


def close_ms(ms: Microseed) -> None:
    ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def tree_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.exists() else 0


def rss_mb() -> float | None:
    if psutil is None:
        return None
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def watchdog(cfg: SoakConfig, runtime_root: Path, telemetry: Telemetry, *, episode: int, phase: str) -> None:
    rss = rss_mb(); disk = tree_bytes(runtime_root) / (1024 * 1024)
    telemetry.emit("WATCHDOG", episode=episode, phase=phase, rss_mb=rss, runtime_disk_mb=disk)
    if rss is not None and rss > cfg.max_rss_mb:
        raise RuntimeError(f"WATCHDOG_RSS_LIMIT:{rss:.2f}>{cfg.max_rss_mb}")
    if disk > cfg.max_disk_mb:
        raise RuntimeError(f"WATCHDOG_DISK_LIMIT:{disk:.2f}>{cfg.max_disk_mb}")


def attach(root: Path, world: NovelDevelopmentalWorld, session: int) -> tuple[Microseed, ShadowEnvironmentAdapter]:
    ms = Microseed(root)
    adapter = ShadowEnvironmentAdapter(world, AdapterConfig(adapter_instance_id=f"V1-SOAK-001-S{session}", viable_low=-.25, viable_high=.25))
    adapter.attach(ms)
    for cid in MAIN + (adapter.config.observation_capability_id,):
        ms.frames.bind_capability(adapter.config.frame_id, cid)
    effect_ids = sorted(cid for cid, c in ms.capabilities.contracts.items() if c.authority == Authority.EFFECT)
    if effect_ids != sorted(MAIN):
        raise RuntimeError(f"UNEXPECTED_EFFECT_CAPABILITY_SURFACE:{effect_ids}")
    return ms, adapter


def bootstrap_p(ms: Microseed, adapter: ShadowEnvironmentAdapter, world: NovelDevelopmentalWorld, telemetry: Telemetry) -> dict[str, str]:
    telemetry.emit("BOOTSTRAP_BEGIN", assistance="EXTERNALLY_EQUIPPED_ONE_STEP_REHEARSAL_ROWS")
    train: list[dict[str, object]] = []
    for i in range(12):
        train.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="SOAK-BOOT-P-TRAIN"))
    candidates = _candidate_by_action(ms)
    hold: list[dict[str, object]] = []
    for i in range(12):
        hold.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="P", index=i, phase="SOAK-BOOT-P-HOLD"))
    relations = qualify_relations_from_later_history(ms, candidates, hold, prefix="SOAK-P-QUAL")
    telemetry.emit("BOOTSTRAP_END", relation_ids=relations, training_episode_count=12, holdout_episode_count=12, assistance_authority="EXTERNAL_QUALIFICATION_REMAINS_EXTERNAL")
    return relations


def execute_proposal_step(ms: Microseed, adapter: ShadowEnvironmentAdapter, world: NovelDevelopmentalWorld, telemetry: Telemetry, cfg: SoakConfig, *, episode: int, phase: str, step: int, proposal_id: str) -> dict[str, object]:
    state = ms.action_closure.current_state; assert state is not None
    before = world.observe()
    status = ms.counterfactual_rehearsal_status(proposal_id)
    intent = ms.nominate_bounded_action_intent(proposal_id, adapter.act_obligation())
    if intent.get("status") != "ACTION_INTENT_NOMINATED":
        telemetry.emit("INTENT_BLOCKED", episode=episode, phase=phase, step=step, state=state.state_id, proposal_id=proposal_id, proposal_status=status, intent=intent, before=before)
        return {"status": "INTENT_BLOCKED", "intent": intent, "proposal_status": status, "state": state.state_id}
    action = str(intent["intent"]["capability_id"])
    t0 = time.monotonic(); execution = adapter.execute_intent(ms, intent["intent"]["intent_id"]); dt = time.monotonic() - t0
    if dt > cfg.max_action_seconds:
        raise RuntimeError(f"WATCHDOG_ACTION_DURATION:{dt:.6f}>{cfg.max_action_seconds}")
    if execution.get("status") != "ACTION_EXECUTED":
        raise RuntimeError(f"EXECUTION_BLOCKED_AFTER_INTENT:{execution}")
    eid = f"E-V1-SOAK-001-{phase}-{episode}-{step}"
    outcome = adapter.record_execution_outcome(ms, execution["execution"]["execution_id"], evidence_id=eid, capture_id=f"CAP-V1-SOAK-001-{phase}-{episode}-{step}")
    if outcome.get("status") != "ACTION_OUTCOME_OBSERVED":
        raise RuntimeError(f"OUTCOME_NOT_OBSERVED:{outcome}")
    after = world.observe()
    telemetry.emit("ACTION_EFFECT", episode=episode, phase=phase, step=step, state=state.state_id, proposal_id=proposal_id, proposal_status=status, action=action, intent_id=intent["intent"]["intent_id"], execution_id=execution["execution"]["execution_id"], outcome_evidence_id=eid, action_seconds=dt, before=before, after=after, outcome=outcome["outcome"])
    return {"status": "PASS", "action": action, "before": before, "after": after}


def prime_zero_row_proposals(ms: Microseed, adapter: ShadowEnvironmentAdapter, world: NovelDevelopmentalWorld, telemetry: Telemetry, cfg: SoakConfig) -> dict[str, str]:
    world.configure_mode("P"); world.reset(); adapter.observe_control(ms, "SOAK-PRIME-START")
    options = tuple(adapter.option(a) for a in MAIN)
    proposals: dict[str, str] = {}
    for step, expected in enumerate(MAIN):
        state = ms.action_closure.current_state; assert state is not None
        proposal = ms.nominate_counterfactual_rehearsal((), options, start_state_id=state.state_id, value_id=adapter.config.value_id, config=CounterfactualRehearsalConfig(max_horizon=1, max_nodes=16))
        if proposal is None or proposal.sequence != (expected,):
            raise RuntimeError(f"ZERO_ROW_PRIME_FAILED:{state.state_id}:{proposal}")
        proposals[state.state_id] = proposal.proposal_id
        result = execute_proposal_step(ms, adapter, world, telemetry, cfg, episode=-1, phase="PRIME", step=step, proposal_id=proposal.proposal_id)
        if result["status"] != "PASS":
            raise RuntimeError(f"ZERO_ROW_PRIME_EXECUTION_FAILED:{result}")
    telemetry.emit("ZERO_ROW_PROPOSALS_PRIMED", proposal_by_state=proposals)
    return proposals


def run_reused_episode(ms: Microseed, adapter: ShadowEnvironmentAdapter, world: NovelDevelopmentalWorld, telemetry: Telemetry, cfg: SoakConfig, proposal_by_state: dict[str, str], *, episode: int, phase: str) -> dict[str, object]:
    world.configure_episode(episode, cfg.episodes, cfg.shift_episode); world.reset(); adapter.observe_control(ms, f"SOAK-{phase}-{episode}-START")
    selected: list[str] = []
    for step, expected in enumerate(MAIN):
        state = ms.action_closure.current_state; assert state is not None
        pid = proposal_by_state[state.state_id]
        result = execute_proposal_step(ms, adapter, world, telemetry, cfg, episode=episode, phase=phase, step=step, proposal_id=pid)
        if result["status"] != "PASS":
            return {"status": result["status"], "step": step, "selected": selected, "detail": result}
        selected.append(str(result["action"]))
        if selected[-1] != expected:
            raise RuntimeError(f"UNEXPECTED_CONTROL_ACTION:{episode}:{step}:{selected[-1]}")
    return {"status": "PASS", "selected": selected, "final": world.observe()}


def _sig(row: dict[str, object]) -> OperationalReferentSignature:
    return OperationalReferentSignature("OPERATIONAL_REFERENT_SIGNATURE_DERIVED", str(row["signature_sha256"]), tuple((str(a), tuple(bool(x) for x in bits)) for a, bits in row["action_response_rows"]), "AFFORDANCE_RELATIVE_BOUNDARY_RESPONSE_ONLY")


def referent_diagnostic(ms: Microseed, world: NovelDevelopmentalWorld, telemetry: Telemetry, *, episode: int, diagnostic_index: int) -> dict[str, object]:
    diag = world.fork(); diag.reset_referent_probe(); samples = [diag.observe_entities()]
    for probe_id in PROBES:
        diag.probe(probe_id); samples.append(diag.observe_entities())
    derived = ms.derive_operational_referent_signatures_from_raw_trace(tuple(samples), PROBES)
    row: dict[str, object] = {"episode": episode, "visual_phase": world.visual_phase, "derived_status": derived.get("status"), "sample_width": len(samples[0]), "probe_count": len(PROBES), "numerical_identity_authority": "NONE", "semantic_reference_authority": "NONE", "language_authority": "NONE"}
    if derived.get("status") == "OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE":
        classes = list(derived["signature_classes"]); row["class_count"] = len(classes); row["signature_sha256"] = sorted(str(x["signature_sha256"]) for x in classes)
        for i, item in enumerate(classes):
            ms.record_operational_referent_signature(f"V1-SOAK-001-REF-{diagnostic_index}-{i}", _sig(item))
        context = ms.derive_current_operational_referent_class_set_context(tuple(samples), PROBES, max_records=4096)
        row["current_context_status"] = context.get("status"); row["projection_bucket_id"] = context.get("projection_bucket_id")
    telemetry.emit("REFERENT_DIAGNOSTIC", **row)
    return row


def program_diagnostic(ms: Microseed, adapter: ShadowEnvironmentAdapter, telemetry: Telemetry, *, episode: int) -> dict[str, object]:
    try:
        surface = ms.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        generated = ms.derive_current_generated_epistemic_program_candidates_from_three_locus_history(obligation=adapter.act_obligation(), max_nodes=64)
        row = {"episode": episode, "surface_status": surface.get("status"), "hypothesis_count": surface.get("hypothesis_count"), "chain_count": surface.get("chain_count"), "generated_status": generated.get("status"), "generated_steps": [list(c.steps) for c in generated.get("candidates", ())]}
    except Exception as exc:
        row = {"episode": episode, "status": "DIAGNOSTIC_EXCEPTION", "error": f"{type(exc).__name__}:{exc}"}
    telemetry.emit("PROGRAM_DIAGNOSTIC", **row); return row


def relation_statuses(ms: Microseed, relation_ids: dict[str, str]) -> dict[str, str]:
    return {a: str(ms.action_outcome_predictive_relation_status(rid).get("status")) for a, rid in relation_ids.items()}


def proposal_statuses(ms: Microseed, proposal_by_state: dict[str, str]) -> dict[str, str]:
    return {s: str(ms.counterfactual_rehearsal_status(pid).get("status")) for s, pid in proposal_by_state.items()}


def snapshot_and_restart(ms: Microseed, world: NovelDevelopmentalWorld, runtime_root: Path, snapshots: Path, telemetry: Telemetry, *, session: int, episode: int, active_relations: dict[str, str], proposal_by_state: dict[str, str]) -> tuple[Microseed, ShadowEnvironmentAdapter, int, dict[str, object]]:
    pre_rel = relation_statuses(ms, active_relations); pre_prop = proposal_statuses(ms, proposal_by_state); close_ms(ms)
    snapshots.mkdir(parents=True, exist_ok=True); archive = snapshots / f"snapshot-e{episode:05d}-s{session:02d}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in sorted(runtime_root.rglob("*")):
            if p.is_file(): zf.write(p, p.relative_to(runtime_root).as_posix())
    archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest(); session += 1
    reopened = Microseed(runtime_root); pre_attach_rel = relation_statuses(reopened, active_relations); pre_attach_prop = proposal_statuses(reopened, proposal_by_state); close_ms(reopened)
    ms2, adapter2 = attach(runtime_root, world, session)
    post_rel = relation_statuses(ms2, active_relations); post_prop = proposal_statuses(ms2, proposal_by_state)
    receipt = {"episode": episode, "session": session, "archive": str(archive), "archive_bytes": archive.stat().st_size, "archive_sha256": archive_sha, "pre_close_relation_status": pre_rel, "pre_close_proposal_status": pre_prop, "pre_attach_relation_status": pre_attach_rel, "pre_attach_proposal_status": pre_attach_prop, "post_attach_relation_status": post_rel, "post_attach_proposal_status": post_prop, "automatic_authority_gain": "NONE"}
    telemetry.emit("SNAPSHOT_RESTART", **receipt)
    return ms2, adapter2, session, receipt


def assess_localized_shift_and_qualify_r(ms: Microseed, adapter: ShadowEnvironmentAdapter, world: NovelDevelopmentalWorld, p_relations: dict[str, str], proposal_by_state: dict[str, str], telemetry: Telemetry, cfg: SoakConfig) -> tuple[str, str]:
    assessments = {a: ms.assess_action_outcome_predictive_currentness(p_relations[a], config=PredictiveCurrentnessConfig(window_size=8, min_accuracy=.75, consecutive_failure_windows=2)) for a in MAIN}
    for action, assessed in assessments.items(): telemetry.emit("DRIFT_ASSESSMENT", action=action, assessed=assessed)
    if assessments["K-17"].get("status") != "CURRENT_WITHIN_BOUNDS" or assessments["M-23"].get("status") != "CURRENT_WITHIN_BOUNDS" or assessments["R-41"].get("status") != "DRIFT_WITNESS":
        raise RuntimeError(f"LOCALIZED_DRIFT_SHAPE_WRONG:{assessments}")
    old_status = relation_statuses(ms, p_relations); prop_status = proposal_statuses(ms, proposal_by_state)
    if old_status["R-41"] != "STALE_PREDICTIVE_RELATION" or old_status["K-17"] != "CURRENT_PREDICTIVE_RELATION" or old_status["M-23"] != "CURRENT_PREDICTIVE_RELATION":
        raise RuntimeError(f"LOCALIZED_RELATION_CURRENTNESS_WRONG:{old_status}")
    if prop_status["s2"] != "UNKNOWN_INCOMPLETE" or prop_status["s0"] != "CURRENT_REHEARSAL_PROPOSAL" or prop_status["s1"] != "CURRENT_REHEARSAL_PROPOSAL":
        raise RuntimeError(f"LOCALIZED_PROPOSAL_CURRENTNESS_WRONG:{prop_status}")

    # Explicitly prove K/M remain executable while old R is blocked at s2.
    world.configure_mode("D"); world.reset(); adapter.observe_control(ms, "SOAK-SHIFT-BLOCK-CHECK")
    for step, state_id in enumerate(("s0", "s1")):
        result = execute_proposal_step(ms, adapter, world, telemetry, cfg, episode=cfg.shift_episode + 16, phase="SHIFT-BLOCK-CHECK", step=step, proposal_id=proposal_by_state[state_id])
        if result["status"] != "PASS": raise RuntimeError(f"UNCHANGED_RELATION_BLOCKED:{state_id}:{result}")
    blocked = execute_proposal_step(ms, adapter, world, telemetry, cfg, episode=cfg.shift_episode + 16, phase="SHIFT-BLOCK-CHECK", step=2, proposal_id=proposal_by_state["s2"])
    if blocked["status"] != "INTENT_BLOCKED": raise RuntimeError(f"STALE_R_PROPOSAL_NOT_BLOCKED:{blocked}")
    telemetry.emit("LOCALIZED_FAIL_CLOSED_CONFIRMED", old_relation_status=old_status, proposal_status=prop_status, blocked_r=blocked)

    witness_id = str(assessments["R-41"]["witness"]["witness_id"])
    replacements = ms.nominate_action_outcome_replacement_candidates(p_relations["R-41"], witness_id, min_support=8, min_consistency=.78)
    if len(replacements) != 1:
        raise RuntimeError(f"EXPECTED_ONE_R_REPLACEMENT:{len(replacements)}")
    candidate = replacements[0]
    if candidate.capability_id != "R-41" or candidate.next_state_id != "w" or candidate.value_effect != 1.0:
        raise RuntimeError(f"R_REPLACEMENT_SHAPE_WRONG:{candidate}")

    # External/federated qualification only after the stale-model execution path is blocked.
    hold: list[dict[str, object]] = []
    for i in range(12): hold.extend(run_assisted_episode(ms, adapter, world, evaluator_mode="D", index=i, phase="SOAK-SHIFT-D-HOLDOUT"))
    refs = relation_holdout_refs(ms, candidate, hold, prefix="SOAK-D-R-REPL-QUAL")
    ticket = ExternalActionOutcomeRelationQualifier(ms.evidence, qualifier_id="EXTERNAL-V1-SOAK-001-R-REPLACEMENT").qualify(candidate, qualification_evidence=refs)
    admitted = ms.qualify_action_outcome_predictive_relation(ticket)
    if admitted.get("status") != "CURRENT_PREDICTIVE_RELATION": raise RuntimeError(f"R_REPLACEMENT_NOT_QUALIFIED:{admitted}")
    new_r = str(admitted["relation"]["relation_id"])

    # Walk to s2 using unchanged durable proposals, then nominate a new zero-row R proposal.
    world.configure_mode("D"); world.reset(); adapter.observe_control(ms, "SOAK-NEW-R-PRIME")
    for step, state_id in enumerate(("s0", "s1")):
        result = execute_proposal_step(ms, adapter, world, telemetry, cfg, episode=cfg.shift_episode + 17, phase="NEW-R-PRIME", step=step, proposal_id=proposal_by_state[state_id])
        if result["status"] != "PASS": raise RuntimeError(f"NEW_R_PRIME_PREFIX_FAILED:{result}")
    current = ms.action_closure.current_state; assert current is not None and current.state_id == "s2"
    proposal = ms.nominate_counterfactual_rehearsal((), tuple(adapter.option(a) for a in MAIN), start_state_id="s2", value_id=adapter.config.value_id, config=CounterfactualRehearsalConfig(max_horizon=1, max_nodes=16))
    if proposal is None or proposal.sequence != ("R-41",) or proposal.predicted_state_path[-1] != "w":
        raise RuntimeError(f"NEW_R_ZERO_ROW_NOT_NOMINATED:{proposal}")
    result = execute_proposal_step(ms, adapter, world, telemetry, cfg, episode=cfg.shift_episode + 17, phase="NEW-R-PRIME", step=2, proposal_id=proposal.proposal_id)
    if result["status"] != "PASS": raise RuntimeError(f"NEW_R_ZERO_ROW_NOT_EXECUTABLE:{result}")
    telemetry.emit("R_REPLACEMENT_QUALIFIED_AND_REENTERED", old_r_relation=p_relations["R-41"], new_r_relation=new_r, old_r_proposal=proposal_by_state["s2"], new_r_proposal=proposal.proposal_id, assistance="EXTERNAL_DISJOINT_HOLDOUT_QUALIFICATION")
    return new_r, proposal.proposal_id


def event_kind_counts(ms: Microseed) -> dict[str, int]:
    return dict(Counter(str(e.get("kind")) for e in ms.store.events()))


def run_soak(cfg: SoakConfig, output_root: Path) -> dict[str, object]:
    if not (40 <= cfg.shift_episode < cfg.episodes - 40): raise ValueError("SHIFT_EPISODE_MUST_LEAVE_PRE_AND_POST_WINDOWS")
    output_root.mkdir(parents=True, exist_ok=True); runtime_root = output_root / "runtime"; snapshots = output_root / "snapshots"; telemetry = Telemetry(output_root / "telemetry.jsonl")
    config_payload = {**cfg.__dict__, "canonical_v1": CANONICAL_V1, "run_subject": "V1_REPAIR_DESCENDANT_AFTER_STALE_REHEARSAL_VIOLATION"}
    (output_root / "config.json").write_text(json.dumps(config_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    telemetry.emit("RUN_BEGIN", config=config_payload, pid=os.getpid())
    world = NovelDevelopmentalWorld(cfg.seed); session = 0; ms, adapter = attach(runtime_root, world, session)
    p_relations: dict[str, str] = {}; proposal_by_state: dict[str, str] = {}; referent_rows=[]; restart_rows=[]; program_rows=[]; long_pass=0; drift_pass=0; started=time.monotonic(); new_r_relation=None; new_r_proposal=None
    try:
        p_relations = bootstrap_p(ms, adapter, world, telemetry)
        if relation_statuses(ms, p_relations) != {a: "CURRENT_PREDICTIVE_RELATION" for a in MAIN}: raise RuntimeError("BOOTSTRAP_RELATIONS_NOT_CURRENT")
        proposal_by_state = prime_zero_row_proposals(ms, adapter, world, telemetry, cfg)
        program_rows.append(program_diagnostic(ms, adapter, telemetry, episode=-1)); referent_rows.append(referent_diagnostic(ms, world, telemetry, episode=0, diagnostic_index=0)); watchdog(cfg, runtime_root, telemetry, episode=0, phase="POST_BOOTSTRAP")
        diag_index=1
        for episode in range(cfg.episodes):
            phase = "PRE_SHIFT" if episode < cfg.shift_episode else ("SHIFT_DRIFT" if episode < cfg.shift_episode + 16 else "POST_SHIFT")
            result = run_reused_episode(ms, adapter, world, telemetry, cfg, proposal_by_state, episode=episode, phase=phase)
            if result["status"] != "PASS": raise RuntimeError(f"UNEXPECTED_LONG_PHASE_BLOCK:{episode}:{result}")
            long_pass += 1
            if phase == "SHIFT_DRIFT": drift_pass += 1

            if episode == cfg.shift_episode + 15:
                new_r_relation, new_r_proposal = assess_localized_shift_and_qualify_r(ms, adapter, world, p_relations, proposal_by_state, telemetry, cfg)
                proposal_by_state["s2"] = new_r_proposal
                # The helper performs one complete D prime episode; do not count it as ordinary long phase.

            if cfg.referent_every > 0 and episode > 0 and episode % cfg.referent_every == 0:
                referent_rows.append(referent_diagnostic(ms, world, telemetry, episode=episode, diagnostic_index=diag_index)); diag_index += 1
            if episode in {max(1, cfg.shift_episode // 2), min(cfg.episodes - 1, cfg.shift_episode + 100), cfg.episodes - 1}:
                program_rows.append(program_diagnostic(ms, adapter, telemetry, episode=episode))
            if cfg.snapshot_every > 0 and episode > 0 and episode % cfg.snapshot_every == 0:
                active_rel = {"K-17": p_relations["K-17"], "M-23": p_relations["M-23"], "R-41": new_r_relation or p_relations["R-41"]}
                ms, adapter, session, receipt = snapshot_and_restart(ms, world, runtime_root, snapshots, telemetry, session=session, episode=episode, active_relations=active_rel, proposal_by_state=proposal_by_state); restart_rows.append(receipt)
            if episode % max(20, cfg.referent_every or 20) == 0: watchdog(cfg, runtime_root, telemetry, episode=episode, phase=phase)

        if new_r_relation is None or new_r_proposal is None: raise RuntimeError("SHIFT_REPLACEMENT_NEVER_COMPLETED")
        final_old = relation_statuses(ms, p_relations)
        final_active = {"K-17": ms.action_outcome_predictive_relation_status(p_relations["K-17"])["status"], "M-23": ms.action_outcome_predictive_relation_status(p_relations["M-23"])["status"], "R-41": ms.action_outcome_predictive_relation_status(new_r_relation)["status"]}
        if final_old != {"K-17":"CURRENT_PREDICTIVE_RELATION","M-23":"CURRENT_PREDICTIVE_RELATION","R-41":"STALE_PREDICTIVE_RELATION"}: raise RuntimeError(f"FINAL_LOCALIZED_OLD_STATUS_WRONG:{final_old}")
        if final_active != {a:"CURRENT_PREDICTIVE_RELATION" for a in MAIN}: raise RuntimeError(f"FINAL_ACTIVE_STATUS_WRONG:{final_active}")
        final_prop = proposal_statuses(ms, proposal_by_state)
        if final_prop != {"s0":"CURRENT_REHEARSAL_PROPOSAL","s1":"CURRENT_REHEARSAL_PROPOSAL","s2":"CURRENT_REHEARSAL_PROPOSAL"}: raise RuntimeError(f"FINAL_PROPOSAL_STATUS_WRONG:{final_prop}")
        effect_ids = sorted(cid for cid,c in ms.capabilities.contracts.items() if c.authority == Authority.EFFECT)
        if effect_ids != sorted(MAIN): raise RuntimeError(f"FINAL_EFFECT_SURFACE_DRIFT:{effect_ids}")
        counts=event_kind_counts(ms)
        summary={
            "status":"PASS","canonical_v1":CANONICAL_V1,"run_subject":"V1_REPAIR_DESCENDANT_AFTER_STALE_REHEARSAL_VIOLATION","episodes_requested":cfg.episodes,"ordinary_long_phase_episode_pass_count":long_pass,"shift_drift_episode_pass_count":drift_pass,"shift_episode":cfg.shift_episode,
            "bootstrap_relation_ids":p_relations,"replacement_r_relation_id":new_r_relation,"active_proposal_ids":proposal_by_state,"final_old_relation_status":final_old,"final_active_relation_status":final_active,"final_active_proposal_status":final_prop,
            "restart_count":len(restart_rows),"restart_receipts":restart_rows,"referent_diagnostics":referent_rows,"program_diagnostics":program_rows,"ordinary_execution_count":len(ms.action_closure.executions),"ordinary_outcome_count":len(ms.action_closure.outcomes),"predictive_relation_count":len(ms.action_outcome_learning.relations),"store_event_count":sum(counts.values()),"store_event_kind_counts":counts,"effect_capability_ids":effect_ids,
            "network_capability_exposed":"NO","shell_capability_exposed":"NO","source_mutation_capability_exposed":"NO","language_branch_mechanism_present":"NO","naked_branch_mechanism_present":"NO","semantic_reference_authority":"NONE","numerical_identity_authority":"NONE","language_authority":"NONE","new_core_manager":"NO",
            "midrun_external_qualification_assistance":"YES__R_REPLACEMENT_ONLY__EXPLICIT_EQUIPPED_FEDERATED_BOUNDARY","referent_probe_schedule_assistance":"YES__FORKED_WORLD_DIAGNOSTIC_ONLY","elapsed_seconds":time.monotonic()-started,"telemetry_event_count":telemetry.count,"runtime_bytes":tree_bytes(runtime_root),"snapshot_bytes":tree_bytes(snapshots),
            "earned":"REPAIRED_V1_DESCENDANT_MAINTAINED_LONG_HORIZON_DURABLE_ZERO_ROW_OPERATION_ACROSS_RESTARTS_AND_REFERENT_GEOMETRY_PRESSURE_THEN_LOCALIZED_TERMINAL_CAUSAL_DRIFT_STALed_ONLY_R41_BLOCKED_ITS_DURABLE_REHEARSAL_AND_RESUMED_AFTER_EXPLICIT_REPLACEMENT_QUALIFICATION_WITHOUT_GLOBAL_RESET",
            "not_earned":"CANONICAL_V1_PROMOTION_OR_OPEN_ENDED_DEVELOPMENT_OR_SELF_QUALIFICATION_OR_NAKED_AUTONOMY_OR_AGI",
        }
        telemetry.emit("RUN_END",summary=summary); (output_root/"result_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8"); return summary
    except Exception as exc:
        failure={"status":"FAIL","error":f"{type(exc).__name__}:{exc}","elapsed_seconds":time.monotonic()-started,"telemetry_event_count":telemetry.count}; telemetry.emit("RUN_FAILURE",**failure); (output_root/"result_summary.json").write_text(json.dumps(failure,indent=2,sort_keys=True)+"\n",encoding="utf-8"); raise
    finally:
        try: close_ms(ms)
        except Exception: pass
        telemetry.close()


def parse_args() -> argparse.Namespace:
    ap=argparse.ArgumentParser(); ap.add_argument("--episodes",type=int,default=1200); ap.add_argument("--shift-episode",type=int,default=600); ap.add_argument("--snapshot-every",type=int,default=300); ap.add_argument("--referent-every",type=int,default=100); ap.add_argument("--seed",type=int,default=2053001); ap.add_argument("--output-root",type=Path,required=True); return ap.parse_args()


def main() -> None:
    args=parse_args(); cfg=SoakConfig(episodes=args.episodes,shift_episode=args.shift_episode,snapshot_every=args.snapshot_every,referent_every=args.referent_every,seed=args.seed); print(json.dumps(run_soak(cfg,args.output_root),indent=2,sort_keys=True,default=str))


if __name__=="__main__": main()
