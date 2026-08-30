from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from microseed import Microseed, RehearsalTransitionObservation
from microseed.development.rehearsal import CounterfactualRehearsalConfig
from research.substrate_shadow.environment_adapter import AdapterConfig, ShadowEnvironmentAdapter
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


MAIN = ("K-17", "M-23", "R-41")


class LivedThreeLocusWorld:
    """External opaque world used only as the reality owner for MS1997.

    The hidden mode is evaluator/world state. It is never written into Microseed evidence.
    Both modes expose the same opaque control-state sequence through the first two loci;
    only the terminal control state and regulatory effect history differ.
    """

    name = "MS1997-LIVED-THREE-LOCUS-WORLD"
    action_ids = MAIN
    compatibility_sha256 = hashlib.sha256(
        b"MS1997-LIVED-THREE-LOCUS-WORLD:v1:K17-M23-R41:two-hidden-modes"
    ).hexdigest()

    def __init__(self) -> None:
        self.mode = "P"
        self.phase = 0
        self.value = -3.0

    def configure_mode(self, mode: str) -> None:
        if mode not in {"P", "N"}:
            raise ValueError("INVALID_WORLD_MODE")
        self.mode = mode

    @property
    def sign(self) -> float:
        return 1.0 if self.mode == "P" else -1.0

    def is_available(self) -> bool:
        return True

    def reset(self) -> None:
        self.phase = 0
        self.value = -3.0 if self.mode == "P" else 3.0

    def _state(self) -> str:
        if self.phase == 0:
            return "s0"
        if self.phase == 1:
            return "s1"
        if self.phase == 2:
            return "s2"
        return "u" if self.mode == "P" else "v"

    def apply(self, action_id: str) -> dict:
        expected = MAIN[self.phase] if self.phase < 3 else None
        if action_id != expected:
            raise RuntimeError("WORLD_REJECTED_OUT_OF_SEQUENCE_ACTION")
        self.value += self.sign
        self.phase += 1
        return {
            "receipt": "opaque-effect-applied",
            "action_id": action_id,
            "phase": self.phase,
        }

    def observe(self) -> dict:
        return {"next_state_id": self._state(), "observed_value": self.value}

    def observe_outcome(self) -> dict:
        return self.observe()

    def fork(self) -> "LivedThreeLocusWorld":
        return deepcopy(self)


def equipped_rows(adapter: ShadowEnvironmentAdapter, mode: str, tag: str) -> tuple[RehearsalTransitionObservation, ...]:
    """Explicit EQUIPPED training model; not organism-owned history and not truth.

    It supplies only the bounded one-step rehearsal structure needed to make the
    training effects lawful. The MS1997 claim is specifically that the *later*
    endogenous three-locus surface is derived from authenticated executed outcomes,
    not from these supplied rehearsal rows.
    """
    sign = 1.0 if mode == "P" else -1.0
    terminal = "u" if mode == "P" else "v"
    specs = (
        ("s0", MAIN[0], "s1"),
        ("s1", MAIN[1], "s2"),
        ("s2", MAIN[2], terminal),
    )
    c = adapter.config
    rows = []
    for state, action, nxt in specs:
        for i in range(8):
            rows.append(RehearsalTransitionObservation(
                f"ASSIST-MS1997-{tag}-{state}-{action}-{i}",
                state, action, nxt, sign,
                0, c.frame_id, 0, c.episode_id, 0,
            ))
    return tuple(rows)


def run_episode(ms: Microseed, adapter: ShadowEnvironmentAdapter, world: LivedThreeLocusWorld, *, mode: str, index: int) -> dict:
    world.configure_mode(mode)
    world.reset()
    adapter.observe_control(ms, f"EP-{index}-START")
    rows = equipped_rows(adapter, mode, f"{index}")
    options = tuple(adapter.option(aid) for aid in MAIN)
    selected = []
    evidence_chain = []

    for step in range(3):
        current = ms.action_closure.current_state
        assert current is not None
        before_evidence = current.evidence_id
        proposal = ms.nominate_counterfactual_rehearsal(
            rows,
            options,
            start_state_id=current.state_id,
            value_id=adapter.config.value_id,
            config=CounterfactualRehearsalConfig(max_horizon=1, max_nodes=16),
        )
        assert proposal is not None, (mode, index, step, current.state_id)
        # All three opaque options were supplied; current represented state determines
        # which one-step relation is applicable. The caller does not pass a preferred action.
        assert len(proposal.sequence) == 1
        intent = ms.nominate_bounded_action_intent(proposal.proposal_id, adapter.act_obligation())
        assert intent["status"] == "ACTION_INTENT_NOMINATED", intent
        assert intent["intent"]["control_state_evidence_id"] == before_evidence
        execution = adapter.execute_intent(ms, intent["intent"]["intent_id"])
        assert execution["status"] == "ACTION_EXECUTED", execution
        evidence_id = f"E-MS1997-LIVED-{index}-{step}"
        outcome = adapter.record_execution_outcome(
            ms,
            execution["execution"]["execution_id"],
            evidence_id=evidence_id,
            capture_id=f"CAP-MS1997-LIVED-{index}-{step}",
        )
        assert outcome["status"] == "ACTION_OUTCOME_OBSERVED", outcome
        assert ms.action_closure.current_state is not None
        assert ms.action_closure.current_state.evidence_id == evidence_id
        selected.append(intent["intent"]["capability_id"])
        evidence_chain.append((before_evidence, evidence_id))

    final = world.observe()
    assert tuple(selected) == MAIN
    assert final["next_state_id"] == ("u" if mode == "P" else "v")
    assert final["observed_value"] == 0.0
    return {
        "mode_evaluator_only": mode,
        "selected_actions": selected,
        "evidence_chain": evidence_chain,
        "final_state": final["next_state_id"],
        "final_value": final["observed_value"],
    }


def run_ms1997() -> dict[str, object]:
    td = tempfile.TemporaryDirectory(prefix="ms1997-lived-history-")
    root = Path(td.name)
    world = LivedThreeLocusWorld()
    adapter = ShadowEnvironmentAdapter(
        world,
        AdapterConfig(
            adapter_instance_id="MS1997-LIVED",
            viable_low=-0.25,
            viable_high=0.25,
        ),
    )
    ms = Microseed(root)
    try:
        adapter.attach(ms)
        episodes = []
        for index, mode in enumerate(("P", "P", "N", "N")):
            episodes.append(run_episode(ms, adapter, world, mode=mode, index=index))

        experiences = ms._action_outcome_experiences()
        assert len(experiences) == 12
        # The endogenous discovery surface must be fed by the actual execution IDs and
        # outcome evidence just recorded through ordinary action closure.
        lived_execution_ids = {x.execution_id for x in experiences}
        assert lived_execution_ids == set(ms.action_closure.executions)

        surface = ms.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        assert surface["status"] == "THREE_LOCUS_CHAIN_MODEL_SURFACE", surface
        assert surface["hypothesis_count"] == 6
        assert surface["chain_count"] == 2
        assert len(surface["relation_sets"]) == 2
        assert all(len(model) == 3 for model in surface["relation_sets"])

        # Return to the common represented root without fabricating an action outcome.
        world.configure_mode("P")
        world.reset()
        adapter.observe_control(ms, "GENERATOR-ROOT")
        generated = ms.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=adapter.act_obligation(),
            max_nodes=64,
        )
        assert generated["status"] == "REPRESENTED_INFORMATIVE_PROGRAMS_FOUND", generated
        candidates = tuple(generated["candidates"])
        main = next((c for c in candidates if c.steps == MAIN), None)
        assert main is not None, generated
        assert main.execution_authority == main.truth_authority == main.qualification_authority == main.closure_authority == "NONE"

        # Prove successor discovery is using the ordinary evidence chain rather than
        # harness-supplied execution links.
        couplings = ms.derive_action_outcome_successor_couplings()
        assert len(couplings) == 4
        for coupling in couplings:
            assert coupling.support == 2
            for first_x, second_x in coupling.source_execution_pairs:
                second = ms.action_closure.executions[second_x]
                second_intent = ms.action_closure.intents[second.intent_id]
                first_outcome = next(o for o in ms.action_closure.outcomes.values() if o.execution_id == first_x)
                assert second_intent.control_state_evidence_id == first_outcome.evidence_id

        # The evaluator's causal mode label is not persisted as an organism fact.
        # Operational consequences are of course observed; the remaining assistance
        # limitation is that the supplied rehearsal rows are mode-conditioned.
        durable_evidence_payloads = [
            row.get("payload", {}) for row in ms.store.events()
            if row.get("kind") in {"EVIDENCE_APPENDED", "BOUNDED_ACTION_OUTCOME"}
        ]
        assert all(not (isinstance(payload, dict) and "mode" in payload) for payload in durable_evidence_payloads)

        return {
            "status": "BOUNDARY_CONFIRMED",
            "episodes": episodes,
            "ordinary_execution_count": len(ms.action_closure.executions),
            "ordinary_outcome_count": len(ms.action_closure.outcomes),
            "experience_count": len(experiences),
            "alternative_hypothesis_count": surface["hypothesis_count"],
            "successor_coupling_count": len(couplings),
            "three_locus_chain_count": surface["chain_count"],
            "alternative_model_count": len(surface["relation_sets"]),
            "generated_program": list(main.steps),
            "generated_candidate_id": main.candidate_id,
            "generated_candidate_sha256": main.digest(),
            "caller_supplied_preferred_action": "NO__ALL_CURRENT_OPAQUE_OPTIONS_PRESENT_DURING_TRAINING_REHEARSAL",
            "caller_supplied_endogenous_program": "NO",
            "history_source": "AUTHENTICATED_ORDINARY_EFFECT_EXECUTION_PLUS_BOUNDED_OBSERVATION_INGRESS",
            "training_assistance": "EQUIPPED_ONE_STEP_REHEARSAL_ROWS_PER_EXTERNAL_WORLD_MODE",
            "training_assistance_authority": "MODEL_ASSISTANCE_ONLY_NOT_ORGANISM_HISTORY_TRUTH_OR_EXECUTION_AUTHORITY",
            "evaluator_hidden_mode_label_in_durable_organism_evidence": "NO",
            "mode_conditioned_training_assistance": "YES__EXPLICIT_REMAINING_LIMITATION",
            "candidate_execution_authority": main.execution_authority,
            "candidate_truth_authority": main.truth_authority,
            "new_core_mechanism_required": "NO",
            "earned": "AUTHENTICATED_LIVED_ACTION_OUTCOME_HISTORY_CAN_DIRECTLY_FORM_THE_EXISTING_THREE_LOCUS_ALTERNATIVE_SURFACE_AND_ENDOGENOUSLY_GENERATE_THE_DISCRIMINATING_OPAQUE_PROGRAM_WITHOUT_SYNTHETIC_ACTION_CLOSURE_RECORDS",
            "remaining_boundary": "REMOVE_MODE_CONDITIONED_TRAINING_ASSISTANCE_AND_COMPOSE_DELAY_DRIFT_LIVENESS_RESTART_REFERENT_PRESSURE_IN_ONE_SUSTAINED_WORLD",
        }
    finally:
        _close(ms)
        td.cleanup()


def main() -> None:
    print(json.dumps(run_ms1997(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
