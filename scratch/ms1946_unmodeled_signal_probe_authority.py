from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus, FeasibilityState, RecruitmentOption
from microseed.development.epistemic_action import derive_epistemic_program_step_local_precheck
from microseed.development.epistemic_program import EpistemicProgramTrial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1945_represented_signal_alternative_selection import (
    _finish,
    _prepare_ms1944_plus_represented_t1,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _trial(ms, *, deficit_id: str, capability_id: str, discriminator: str) -> EpistemicProgramTrial:
    cap = ms.capabilities.contracts[capability_id]
    current = ms.action_closure.current_state
    assert current is not None
    return EpistemicProgramTrial(
        trial_id=f"MS1946-TRIAL-{deficit_id}-{capability_id}",
        deficit_id=deficit_id,
        discrimination_signature_sha256=discriminator,
        relation_candidate_id=f"MS1946-NO-RELATION-{capability_id}",
        relation_candidate_sha256=_sha(f"no-relation:{capability_id}"),
        steps=(capability_id,),
        capability_epochs=((capability_id, ms.capabilities.epochs[capability_id]),),
        capability_signatures=((capability_id, cap.computed_signature_sha256()),),
        frame_epochs=(),
        obligation_id="ACT",
        operational_scope_id="S",
        start_state_id=current.state_id,
        start_state_evidence_id=current.evidence_id,
        source_relation_digests=(),
    )


def main() -> None:
    td, ms, world, t0_relation_id, _coord_before = _prepare_ms1944_plus_represented_t1()
    try:
        checks = {}
        # T1 is represented/current as an EFFECT capability but has no learned predictive relation.
        assert "SIG-T1" in ms.capabilities.contracts
        assert ms.capabilities.contracts["SIG-T1"].currentness == "CURRENT"
        assert not any(
            r.capability_id == "SIG-T1" and ms._action_outcome_relation_current(r)
            for r in ms.action_outcome_learning.relations.values()
        )
        checks["t1_represented_current_effect_but_unmodeled"] = True

        # There is no admitted T1 action/outcome candidate before T1 has actual history.
        t1_candidates = [
            c for c in ms.nominate_action_outcome_predictive_candidates()
            if c.capability_id == "SIG-T1"
        ]
        assert t1_candidates == []
        checks["no_t1_predictive_candidate_before_actual_history"] = True

        # Create one actual UNKNOWN evidence record. The deficit API itself still requires
        # caller-supplied hypothesis/discriminator identities.
        unknown = ms.append_evidence(
            "E-MS1946-UNKNOWN-T1-EFFECT",
            {"represented_capability_id": "SIG-T1", "effect_model": "UNKNOWN"},
            EpistemicStatus.UNKNOWN_INCOMPLETE,
            source="MS1946-COMPOSITION-PROBE",
        )
        hypothesis = _sha("caller-hypothesis:T1-effect-unknown")
        discriminator = _sha("caller-discriminator:T1-effect-observation")

        # Two deficits with identical UNKNOWN/hypothesis/discriminator can be bound to
        # different current qualified EFFECT capabilities solely by caller choice.
        d_t1 = ms.record_action_limited_unknown(
            deficit_id="D-MS1946-T1",
            question_key="OPAQUE-UNMODELED-SIGNAL-EFFECT",
            hypothesis_digest_sha256=hypothesis,
            unknown_evidence_id=unknown.evidence_id,
            missing_discriminator_signature_sha256=discriminator,
            assistance_ancestry=("CALLER_SUPPLIED_HYPOTHESIS", "CALLER_SUPPLIED_DISCRIMINATOR"),
        )
        d_t0 = ms.record_action_limited_unknown(
            deficit_id="D-MS1946-T0",
            question_key="OPAQUE-UNMODELED-SIGNAL-EFFECT",
            hypothesis_digest_sha256=hypothesis,
            unknown_evidence_id=unknown.evidence_id,
            missing_discriminator_signature_sha256=discriminator,
            assistance_ancestry=("CALLER_SUPPLIED_HYPOTHESIS", "CALLER_SUPPLIED_DISCRIMINATOR"),
        )
        assert d_t1.missing_discriminator_signature_sha256 == d_t0.missing_discriminator_signature_sha256
        assert d_t1.state.value == d_t0.state.value == "ACTION_LIMITED"

        b_t1 = ms.bind_probe_capability("D-MS1946-T1", "SIG-T1")
        b_t0 = ms.bind_probe_capability("D-MS1946-T0", "SIG-T0")
        assert b_t1["state"] == b_t0["state"] == "PROBE_AVAILABLE"
        assert b_t1["probe_capability_id"] == "SIG-T1"
        assert b_t0["probe_capability_id"] == "SIG-T0"
        checks["legacy_probe_binding_accepts_caller_selected_t0_or_t1_for_same_deficit_content"] = True

        # The modern program gate does not trust that caller-selected PROBE_AVAILABLE binding.
        # With no independently registered contrast and no relation ancestry, satisfaction is UNKNOWN.
        trial = _trial(ms, deficit_id="D-MS1946-T1", capability_id="SIG-T1", discriminator=discriminator)
        satisfaction = ms.derive_current_program_discriminator_satisfaction(trial)
        assert satisfaction.commitment.value == "UNKNOWN"
        assert satisfaction.reason == "UNIQUE_CURRENT_REGISTERED_DISCRIMINATOR_REQUIRED"
        checks["modern_program_gate_rejects_probe_without_registered_discriminator"] = True

        local = derive_epistemic_program_step_local_precheck(
            trial=trial,
            deficit=ms.epistemic_deficits.records["D-MS1946-T1"],
            feasibility=RecruitmentOption("SIG-T1", FeasibilityState.FEASIBLE),
            capabilities=ms.capabilities,
            obligation=act_ob(),
            current_frame_epochs=dict(ms.frames.epochs),
            current_state=ms.action_closure.current_state,
            program_discriminator_satisfaction=satisfaction,
        )
        assert not local.licenses_yes()
        checks["no_lawful_epistemic_step_intent_from_caller_bound_unmodeled_probe"] = True

        # Existing revised-surface direct-probe derivation cannot help: it is explicitly
        # downstream of a current represented revised contrast built from qualified relations.
        direct = ms.current_revised_surface_direct_probe_availability(
            old_deficit_id="D-MS1946-T1",
            successor_deficit_id="D-MS1946-T1",
        )
        assert direct["status"] == "ABSTAIN"
        checks["modern_direct_probe_derivation_requires_prior_represented_contrast"] = True

        # The bounded conclusion is a missing binding/representation, not permission to add curiosity.
        result = {
            "status": "BOUNDARY_CONFIRMED",
            "checks": checks,
            "t0_current_relation_id": t0_relation_id,
            "t1_current_predictive_relation_count": 0,
            "caller_hypothesis_digest_sha256": hypothesis,
            "caller_discriminator_signature_sha256": discriminator,
            "t1_probe_binding_state": b_t1["state"],
            "t0_probe_binding_state": b_t0["state"],
            "program_satisfaction": satisfaction.serializable(),
            "local_precheck": local.serializable(),
            "direct_probe_surface": direct,
            "earned_boundary": "CURRENT_OWNERS_CANNOT_ENDOGENOUSLY_BIND_UNMODELED_REPRESENTED_SIGNAL_TO_EXACT_DISCRIMINATOR_WITHOUT_SUPPLIED_CONTRAST_OR_PREDICTED_OUTCOME_STRUCTURE",
            "authority": "NONE",
            "execution_authority": "NONE",
            "semantic_signal_authority": "NONE",
            "curiosity_authority": "NONE",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        _finish(td, ms)


if __name__ == "__main__":
    main()
