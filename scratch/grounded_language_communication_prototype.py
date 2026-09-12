from __future__ import annotations

from typing import Any, Mapping

from scratch.grounded_language_readout_prototype import grounded_referent_control


def derive_grounded_communication_use(
    ms,
    candidate: dict[str, Any],
    *,
    surface_by_referent: Mapping[str, str],
    convention_surface_to_referent: Mapping[str, str],
    expected_referent_signature: str,
) -> dict[str, Any]:
    """Use a surface token to coordinate *after* grounded referent competence exists.

    The grounded candidate chooses the referent. The presentation map chooses a surface.
    The counterparty convention decodes the surface. No surface text can create the referent.
    """
    base={
        "language_authority":"NONE",
        "semantic_reference_authority":"NONE",
        "truth_authority":"NONE",
        "execution_authority":"NONE",
        "planner_authority":"NONE",
        "value_priority_authority":"NONE",
        "authority_gain":"NONE",
        "counterparty_autonomy":"PRESERVED",
    }
    control=grounded_referent_control(ms,candidate)
    if control.get("status")!="CURRENT_GROUNDED_REFERENT_CONTROL":
        return {**base,**control,"status":"DEFER_UNKNOWN","reason":str(control.get("reason","CURRENT_GROUNDED_BINDING_REQUIRED")),"communication_status":"NOT_EMITTED"}
    sig=str(control["operational_referent_signature_sha256"])
    if sig not in surface_by_referent:
        return {**base,**control,"status":"DEFER_UNKNOWN","reason":"CURRENT_SURFACE_PRESENTATION_MAPPING_REQUIRED","communication_status":"NOT_EMITTED"}
    surface=str(surface_by_referent[sig])
    decoded=convention_surface_to_referent.get(surface)
    acknowledged=(decoded==str(expected_referent_signature))
    return {
        **base,**control,
        "status":"GROUNDED_COMMUNICATION_USE_OBSERVED",
        "communication_status":"ACK" if acknowledged else "NO_ACK",
        "surface_token":surface,
        "decoded_referent_signature_sha256":None if decoded is None else str(decoded),
        "expected_referent_signature_sha256":str(expected_referent_signature),
        "grounded_sender_referent_signature_sha256":sig,
        "prediction_commitment":"YES" if acknowledged else "NO",
        "surface_can_select_sender_referent":"NO",
        "surface_can_create_binding":"NO",
        "convention_can_reinterpret_grounding":"NO",
    }


def attempt_text_override_of_grounded_communication(
    ms, candidate: dict[str, Any], *, operator_text: str, requested_referent_signature: str
) -> dict[str, Any]:
    """Explicitly refuse text/operator wording as a referent override."""
    control=grounded_referent_control(ms,candidate)
    if control.get("status")!="CURRENT_GROUNDED_REFERENT_CONTROL":
        return {**control,"status":"DEFER_UNKNOWN","reason":"CURRENT_GROUNDED_BINDING_REQUIRED"}
    actual=str(control["operational_referent_signature_sha256"])
    return {
        **control,
        "status":"TEXT_OVERRIDE_REFUSED",
        "operator_text":str(operator_text),
        "requested_referent_signature_sha256":str(requested_referent_signature),
        "grounded_referent_signature_sha256":actual,
        "override_applied":False,
        "language_authority":"NONE",
        "operator_status_authority":"NONE",
        "authority_gain":"NONE",
    }
