from __future__ import annotations

import hashlib

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


def _same_caller_deficits(ms):
    unknown = ms.append_evidence(
        "E-MS1946-UNKNOWN-T1-EFFECT",
        {"represented_capability_id": "SIG-T1", "effect_model": "UNKNOWN"},
        EpistemicStatus.UNKNOWN_INCOMPLETE,
        source="MS1946-REGRESSION",
    )
    hypothesis = _sha("caller-hypothesis:T1-effect-unknown")
    discriminator = _sha("caller-discriminator:T1-effect-observation")
    for did in ("D-MS1946-T1", "D-MS1946-T0"):
        ms.record_action_limited_unknown(
            deficit_id=did,
            question_key="OPAQUE-UNMODELED-SIGNAL-EFFECT",
            hypothesis_digest_sha256=hypothesis,
            unknown_evidence_id=unknown.evidence_id,
            missing_discriminator_signature_sha256=discriminator,
            assistance_ancestry=("CALLER_SUPPLIED_HYPOTHESIS", "CALLER_SUPPLIED_DISCRIMINATOR"),
        )
    return hypothesis, discriminator


def test_represented_t1_has_no_predictive_candidate_before_actual_history():
    td, ms, _, _, _ = _prepare_ms1944_plus_represented_t1()
    try:
        assert ms.capabilities.contracts["SIG-T1"].currentness == "CURRENT"
        assert not any(
            r.capability_id == "SIG-T1" and ms._action_outcome_relation_current(r)
            for r in ms.action_outcome_learning.relations.values()
        )
        assert [c for c in ms.nominate_action_outcome_predictive_candidates() if c.capability_id == "SIG-T1"] == []
    finally:
        _finish(td, ms)


def test_legacy_probe_binding_is_caller_selection_not_content_derived_relevance():
    td, ms, _, _, _ = _prepare_ms1944_plus_represented_t1()
    try:
        _, discriminator = _same_caller_deficits(ms)
        t1 = ms.bind_probe_capability("D-MS1946-T1", "SIG-T1")
        t0 = ms.bind_probe_capability("D-MS1946-T0", "SIG-T0")
        assert t1["state"] == t0["state"] == "PROBE_AVAILABLE"
        assert t1["missing_discriminator_signature_sha256"] == discriminator
        assert t0["missing_discriminator_signature_sha256"] == discriminator
        assert t1["probe_capability_id"] == "SIG-T1"
        assert t0["probe_capability_id"] == "SIG-T0"
    finally:
        _finish(td, ms)


def test_modern_program_gate_refuses_caller_bound_unmodeled_t1_without_registered_discriminator():
    td, ms, _, _, _ = _prepare_ms1944_plus_represented_t1()
    try:
        _, discriminator = _same_caller_deficits(ms)
        ms.bind_probe_capability("D-MS1946-T1", "SIG-T1")
        trial = _trial(ms, deficit_id="D-MS1946-T1", capability_id="SIG-T1", discriminator=discriminator)
        satisfaction = ms.derive_current_program_discriminator_satisfaction(trial)
        assert satisfaction.commitment.value == "UNKNOWN"
        assert satisfaction.reason == "UNIQUE_CURRENT_REGISTERED_DISCRIMINATOR_REQUIRED"
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
        assert local.reason == "EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_REFUSED"
    finally:
        _finish(td, ms)


def test_revised_surface_direct_probe_owner_cannot_originate_unmodeled_t1_case():
    td, ms, _, _, _ = _prepare_ms1944_plus_represented_t1()
    try:
        _same_caller_deficits(ms)
        result = ms.current_revised_surface_direct_probe_availability(
            old_deficit_id="D-MS1946-T1",
            successor_deficit_id="D-MS1946-T1",
        )
        assert result["status"] == "ABSTAIN"
    finally:
        _finish(td, ms)
