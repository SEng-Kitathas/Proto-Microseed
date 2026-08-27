from __future__ import annotations
import hashlib, json, tempfile
from dataclasses import asdict
from pathlib import Path

from microseed import (
    Authority, CapabilityContract, EpistemicStatus, FeasibilityState, Microseed,
    Observation, QualificationState, QueryObligation,
)
from microseed.development.commitment_adapters import project_feasibility
from microseed.development.recruitment import RecruitmentOption


def _sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def obs_cap(cid: str, world: dict):
    def handler(**_):
        return {
            "resource_ready": world.get("resource_ready"),
            "hazard_clear": world.get("hazard_clear"),
            "observed_at": world.get("observed_at"),
        }
    return CapabilityContract(
        cid, "bounded-feasibility-observation",
        {"referent": "feasibility:A"}, {"output": "opaque-current-resource-hazard-witness"},
        ("OBSERVATION_ONLY",), ("MAY_BE_STALE_OR_INCOMPLETE",),
        Authority.OBSERVATION_ONLY, ("MS1704",), "CURRENT", {},
        query_obligation_id="Q-FEAS-A", qualification=QualificationState.SHADOW_QUALIFIED,
        handler=handler, operational_scope_id="S-FEAS",
    )


def grounded_feasibility(m: Microseed, *, now_iso: str, max_age_seconds: int = 5):
    cid = "OBS-FEAS-A"
    obligation = QueryObligation(
        "Q-FEAS-A", "current-bounded-feasibility:A",
        required_authority=Authority.OBSERVATION_ONLY, operational_scope_id="S-FEAS",
    )
    result = m.capabilities.invoke(cid, obligation)
    cap = m.capabilities.contracts.get(cid)
    target = "capability:A:feasibility-now"
    if (
        result.get("status") != "CAPABILITY_RESULT"
        or result.get("authority") != Authority.OBSERVATION_ONLY.value
        or cap is None
        or cap.qualification not in {QualificationState.QUALIFIED, QualificationState.SHADOW_QUALIFIED}
        or cap.currentness != "CURRENT"
    ):
        commitment = project_feasibility(
            FeasibilityState.UNKNOWN,
            commitment_id="FEAS-" + _sha({"result": result, "now": now_iso})[:20],
            target_id=target,
            premise_ids=(),
        )
        return RecruitmentOption("A", FeasibilityState.UNKNOWN), commitment, None

    value = result.get("value")
    if not isinstance(value, dict):
        commitment = project_feasibility(
            FeasibilityState.UNKNOWN,
            commitment_id="FEAS-" + _sha({"value": repr(value), "now": now_iso})[:20],
            target_id=target,
            premise_ids=(),
        )
        return RecruitmentOption("A", FeasibilityState.UNKNOWN), commitment, None

    payload = {
        "capability_id": cid,
        "capability_epoch": m.capabilities.epochs[cid],
        "capability_signature": cap.computed_signature_sha256(),
        "obligation_id": obligation.obligation_id,
        "operational_scope_id": obligation.operational_scope_id,
        "value": value,
    }
    capture = "FEAS-CAP-" + _sha(payload)[:20]
    obs = Observation(
        capture_id=capture,
        origin=f"CAPABILITY:{cid}",
        referent="feasibility:A",
        value=value,
        observed_at=value.get("observed_at"),
        currentness_basis="QUALIFIED_OBSERVATION_CAPABILITY_PLUS_TIME_BOUNDED_ACQUISITION",
        authority=Authority.OBSERVATION_ONLY,
        lineage=(
            f"OBSERVATION_CAPABILITY:{cid}@{m.capabilities.epochs[cid]}",
            f"OBSERVATION_CAPABILITY_SIGNATURE:{cap.computed_signature_sha256()}",
        ),
    )
    current = m.observe(obs, now_iso=now_iso, max_age_seconds=max_age_seconds)
    evidence_payload = {
        "observation": {
            "capture_id": obs.capture_id, "origin": obs.origin, "referent": obs.referent,
            "value": obs.value, "observed_at": obs.observed_at,
            "currentness_basis": obs.currentness_basis, "lineage": list(obs.lineage),
            "authority": obs.authority.value,
        },
        "currentness": current["currentness"],
        "observed_under": payload,
    }
    evidence_id = "E-FEAS-" + _sha(evidence_payload)[:20]
    ref = m.append_evidence(
        evidence_id, evidence_payload,
        EpistemicStatus.PRESSURE_SUPPORTED if current["currentness"] == "CURRENT" else EpistemicStatus.UNKNOWN_INCOMPLETE,
        source=f"CAPABILITY:{cid}",
    )

    if current["currentness"] != "CURRENT":
        state = FeasibilityState.UNKNOWN
    elif value.get("resource_ready") is None or value.get("hazard_clear") is None:
        state = FeasibilityState.UNKNOWN
    elif value.get("resource_ready") is True and value.get("hazard_clear") is True:
        state = FeasibilityState.FEASIBLE
    else:
        state = FeasibilityState.REFUSED

    option = RecruitmentOption(
        "A", state, local_cost=0.1,
        resource_tags=("R-A",), model_evidence_ids=(ref.evidence_id,),
    )
    commitment = project_feasibility(
        state,
        commitment_id="FEAS-" + _sha({"evidence": ref.sha256, "state": state.value})[:20],
        target_id=target,
        premise_ids=(ref.evidence_id, cid),
    )
    return option, commitment, evidence_payload


def run():
    td = tempfile.TemporaryDirectory(prefix="ms1704-")
    try:
        m = Microseed(Path(td.name))
        world = {"resource_ready": True, "hazard_clear": True, "observed_at": "2026-08-25T11:00:00Z"}
        m.register_capability(obs_cap("OBS-FEAS-A", world))

        safe, c_safe, p_safe = grounded_feasibility(m, now_iso="2026-08-25T11:00:02Z")
        assert safe.feasibility == FeasibilityState.FEASIBLE and c_safe.licenses_yes()
        assert p_safe["currentness"] == "CURRENT"
        assert p_safe["observation"]["origin"] == "CAPABILITY:OBS-FEAS-A"
        assert any(x.startswith("OBSERVATION_CAPABILITY_SIGNATURE:") for x in p_safe["observation"]["lineage"])

        # Current capability != feasible now.
        world.update(resource_ready=False, hazard_clear=True, observed_at="2026-08-25T11:00:03Z")
        refused, c_refused, _ = grounded_feasibility(m, now_iso="2026-08-25T11:00:04Z")
        assert refused.feasibility == FeasibilityState.REFUSED and c_refused.licenses_no()
        assert m.capabilities.contracts["OBS-FEAS-A"].currentness == "CURRENT"

        # Historical success cannot dominate fresh current refusal.
        assert safe.feasibility == FeasibilityState.FEASIBLE and refused.feasibility == FeasibilityState.REFUSED

        # Missing current fact preserves UNKNOWN.
        world.update(resource_ready=True, hazard_clear=None, observed_at="2026-08-25T11:00:05Z")
        unknown, c_unknown, _ = grounded_feasibility(m, now_iso="2026-08-25T11:00:06Z")
        assert unknown.feasibility == FeasibilityState.UNKNOWN and not c_unknown.licenses_yes() and not c_unknown.licenses_no()

        # Stale physical observation preserves UNKNOWN even while observation capability metadata is current.
        world.update(resource_ready=True, hazard_clear=True, observed_at="2026-08-25T10:59:00Z")
        stale, c_stale, p_stale = grounded_feasibility(m, now_iso="2026-08-25T11:00:10Z", max_age_seconds=5)
        assert stale.feasibility == FeasibilityState.UNKNOWN and p_stale["currentness"] == "STALE"
        assert m.capabilities.contracts["OBS-FEAS-A"].currentness == "CURRENT"

        # Observation path loss blocks grounding regardless of last good observation.
        m.invalidate_capability("OBS-FEAS-A", reason="SENSOR_ACCESS_LOST")
        blocked, c_blocked, p_blocked = grounded_feasibility(m, now_iso="2026-08-25T11:00:11Z")
        assert blocked.feasibility == FeasibilityState.UNKNOWN and p_blocked is None

        out = {
            "pass": "MS1704_PASS02",
            "safe_current": {"state": safe.feasibility.value, "commitment": c_safe.serializable(), "evidence": p_safe},
            "fresh_refusal": {"state": refused.feasibility.value, "commitment": c_refused.serializable()},
            "missing_fact": {"state": unknown.feasibility.value, "commitment": c_unknown.serializable()},
            "stale_observation": {"state": stale.feasibility.value, "commitment": c_stale.serializable(), "currentness": p_stale["currentness"]},
            "observation_path_loss": {"state": blocked.feasibility.value, "commitment": c_blocked.serializable()},
            "disposition": "SURVIVED__FRESH_QUALIFIED_OBSERVATION_PLUS_EXISTING_CURRENTNESS_AND_TERNARY_FEASIBILITY_COMPOSE_INTO_BOUNDED_FEASIBILITY_NOW__NO_FEASIBILITY_REGISTRY",
            "scars": [
                "CAPABILITY_CURRENTNESS != PHYSICAL_FEASIBILITY_NOW",
                "HISTORICAL_SUCCESS != CURRENT_FEASIBILITY",
                "STALE_OR_INCOMPLETE_FEASIBILITY_OBSERVATION => UNKNOWN",
                "FEASIBILITY_CURRENTNESS_CAN_BE_INHERITED_FROM_EXACT_SUPPORTING_OBSERVATION",
                "GROUNDED_BOUNDED_FEASIBILITY != GLOBAL_SAFETY_OR_PHYSICAL_TRUTH",
            ],
        }
        here = Path(__file__).with_name("MS1704_PASS02_EMBODIED_FEASIBILITY_GROUNDING.json")
        here.write_text(json.dumps(out, indent=2, sort_keys=True))
        print(json.dumps({"disposition": out["disposition"], "states": [safe.feasibility.value, refused.feasibility.value, unknown.feasibility.value, stale.feasibility.value, blocked.feasibility.value]}, indent=2))
    finally:
        td.cleanup()


if __name__ == "__main__":
    run()
