from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import CounterfactualRehearsalConfig
from microseed.runtime.types import FeasibilityState
from scratch.ms1977_raw_coordinate_projection_boundary import World, obs_ob
from scratch.ms1983_owned_raw_projection_routing import prepare_current_raw, train_projection_and_routing
from scratch.ms1977_raw_coordinate_projection_boundary import build
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _proposal(ms, binding_id: str):
    return ms.nominate_current_raw_projection_conditioned_rehearsal(
        (),
        (RecruitmentOption("B", FeasibilityState.FEASIBLE),),
        start_state_id="ALIAS",
        value_id="V",
        projection_routing_id=binding_id,
        routing_task_id="MS1983",
        routing_channel_id="opaque-control",
        config=CounterfactualRehearsalConfig(max_horizon=1),
    )


def run_ms1998() -> dict[str, object]:
    td = tempfile.TemporaryDirectory(prefix="ms1998-owned-context-rehearsal-")
    world = World()
    ms = build(Path(td.name), world)
    try:
        candidate, binding_id, bucket_even, bucket_odd = train_projection_and_routing(ms, world)

        # Current context 1: owned raw evidence projects to the EVEN bucket.
        prepare_current_raw(ms, world, ("0", "0"), 0)
        even = _proposal(ms, binding_id)
        assert even is not None
        assert even.sequence == ("B",)
        assert even.predicted_state_path == ("ALIAS", "EVEN")
        assert even.predicted_value_effect == 2.2

        # Current context 2: same organism, same action vocabulary, different owned
        # raw evidence. No caller bucket changes; the routed rehearsal must change.
        prepare_current_raw(ms, world, ("0", "1"), 1)
        odd = _proposal(ms, binding_id)
        assert odd is not None
        assert odd.sequence == ("B",)
        assert odd.predicted_state_path == ("ALIAS", "ODD")
        assert odd.predicted_value_effect == 2.2
        assert even.transition_relation_digests != odd.transition_relation_digests

        # Duplicate current raw receipts are intentionally not arbitrated. The
        # existing owned resolver returns DEFER_UNKNOWN, so the bridge returns no
        # rehearsal rather than falling back to a default or first bucket.
        duplicate = ms.record_bounded_raw_observation_coordinates(
            "OBS",
            obs_ob(),
            evidence_id="E-MS1998-DUP-RAW",
            capture_id="MS1998-DUP-RAW",
            max_coordinates=4,
        )
        assert duplicate["status"] == "BOUNDED_RAW_OBSERVATION_RECORDED"
        ambiguous_relation = ms.resolve_current_raw_projection_conditioned_relation(
            binding_id,
            action_id="B",
            task_id="MS1983",
            channel_id="opaque-control",
            horizon=1,
        )
        assert ambiguous_relation["status"] == "DEFER_UNKNOWN"
        assert ambiguous_relation["reason"] == "EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_CURRENT_STATE_REQUIRED"
        assert ambiguous_relation["matching_receipt_count"] == 2
        ambiguous = _proposal(ms, binding_id)
        assert ambiguous is None

        return {
            "status": "BOUNDARY_CONFIRMED",
            "projection_candidate_sha256": candidate.digest(),
            "binding_id": binding_id,
            "even_bucket": bucket_even,
            "odd_bucket": bucket_odd,
            "even_path": list(even.predicted_state_path),
            "odd_path": list(odd.predicted_state_path),
            "caller_supplied_projection_bucket": "NO",
            "caller_supplied_routed_relation": "NO",
            "current_context_basis": "CURRENT_BOUNDED_RAW_OBSERVATION_PLUS_EXACT_ADMITTED_PROJECTION",
            "duplicate_current_receipts": "DEFER_UNKNOWN_NO_REHEARSAL",
            "new_persistent_state_owner": "NO",
            "selection_authority": "NONE",
            "truth_authority": "NONE",
            "execution_authority": "NONE",
            "semantic_projection_authority": "NONE",
            "new_core_mechanism_required": "YES__NARROW_COMPOSITION_BRIDGE_ONLY",
            "earned": "CURRENT_OWNED_RAW_PROJECTION_CAN_REENTER_EXISTING_QUALIFIED_RELATION_ROUTING_AND_COUNTERFACTUAL_REHEARSAL_WITHOUT_CALLER_SUPPLIED_BUCKET_OR_NEW_SELECTION_AUTHORITY",
            "remaining_boundary": "USE_THE_BRIDGE_WITH_ORGANISM_VISIBLE_VALUE_CONTEXT_TO_REMOVE_EVALUATOR_MODE_CONDITIONED_TRAINING_ASSISTANCE",
        }
    finally:
        _close(ms)
        world.close()
        td.cleanup()


def main() -> None:
    print(json.dumps(run_ms1998(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
