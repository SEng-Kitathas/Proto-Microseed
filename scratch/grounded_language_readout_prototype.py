from __future__ import annotations

from typing import Any, Mapping

from scratch.ms2046_grounded_operational_token_referent_binding_quarry import binding_status


def grounded_referent_control(ms, candidate: dict[str, Any]) -> dict[str, Any]:
    """Return the non-language grounded control state for a qualified binding candidate."""
    current=binding_status(ms,candidate)
    base={
        "language_authority":"NONE",
        "semantic_reference_authority":"NONE",
        "truth_authority":"NONE",
        "execution_authority":"NONE",
        "planner_authority":"NONE",
        "value_priority_authority":"NONE",
    }
    if current.get("status")!="CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE":
        return {**base,"status":"DEFER_UNKNOWN","reason":str(current.get("reason","CURRENT_GROUNDED_BINDING_REQUIRED"))}
    b=candidate["binding"]
    return {
        **base,
        "status":"CURRENT_GROUNDED_REFERENT_CONTROL",
        "operational_referent_signature_sha256":str(b["operational_referent_signature_sha256"]),
        "binding_id":str(candidate["binding_id"]),
        "grounded_source_episode_sha256":tuple(str(x) for x in candidate["source_episode_sha256"]),
    }


def derive_grounded_language_readout(ms, candidate: dict[str, Any], surface_labels: Mapping[str,str] | None = None) -> dict[str, Any]:
    """Expose a readable/opaque label *after* grounded referent competence is established.

    The surface cannot select or alter the referent. It is derived from the grounded referent signature.
    """
    control=grounded_referent_control(ms,candidate)
    if control.get("status")!="CURRENT_GROUNDED_REFERENT_CONTROL":
        return {**control,"readout_status":"NO_LANGUAGE_READOUT"}
    sig=str(control["operational_referent_signature_sha256"])
    labels=dict(surface_labels or {})
    label=labels.get(sig,"REF-"+sig[:12])
    return {
        **control,
        "status":"CURRENT_GROUNDED_LANGUAGE_READOUT",
        "readout_status":"SURFACE_ONLY",
        "surface_label":str(label),
        "surface_label_source":"POST_GROUNDING_PRESENTATION_MAP",
        "surface_can_select_referent":"NO",
        "surface_can_create_binding":"NO",
        "opaque_equivalent_supported":"YES",
        "authority_gain":"NONE",
    }


def attempt_surface_selected_referent(*, surface_text: str, available_referents: tuple[str,...]) -> dict[str, Any]:
    """Explicitly refuse the smuggling path: readable text cannot choose a referent."""
    return {
        "status":"DEFER_UNKNOWN",
        "reason":"GROUNDED_BINDING_REQUIRED_BEFORE_LANGUAGE_READOUT",
        "surface_text":str(surface_text),
        "available_referent_count":len(available_referents),
        "language_authority":"NONE",
        "semantic_reference_authority":"NONE",
        "execution_authority":"NONE",
        "authority_gain":"NONE",
    }
