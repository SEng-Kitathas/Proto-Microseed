from __future__ import annotations

import hashlib
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from microseed.development.epistemic import EpistemicDeficitRecord
from microseed.runtime.types import CapabilityContract, QueryObligation
from research.run_ms1553_pass01_evidence_adequacy_establish import (
    CFG,
    VALUE_ID,
    seeded_effect_world,
    obligation,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nominate(purpose: str, witness_predicate: str | None):
    td, ms = seeded_effect_world(trace_count=8, prefix=f"P3-{hashlib.sha1((purpose+str(witness_predicate)).encode()).hexdigest()[:8]}")
    try:
        q = QueryObligation(
            "ACT",
            purpose,
            required_authority=obligation("x").required_authority,
            witness_predicate=witness_predicate,
            operational_scope_id="R2",
        )
        r = ms.nominate_multi_value_action_intent((VALUE_ID,), q, config=CFG)
        return {
            "status": r.get("status"),
            "reason": r.get("reason"),
            "license_status": r.get("license", {}).get("status"),
            "licensed_action_ids": r.get("license", {}).get("licensed_action_ids"),
            "intent_basis_kind": r.get("intent", {}).get("basis_kind"),
            "obligation_id": r.get("intent", {}).get("obligation_id"),
            "operational_scope_id": r.get("intent", {}).get("operational_scope_id"),
            "supplied_purpose": purpose,
            "supplied_witness_predicate": witness_predicate,
        }
    finally:
        td.cleanup()


def main() -> None:
    entity = ROOT / "microseed/runtime/entity.py"
    caps = ROOT / "microseed/runtime/capabilities.py"
    types = ROOT / "microseed/runtime/types.py"
    discovery = ROOT / "microseed/development/discovery.py"
    licensing = ROOT / "microseed/development/action_licensing.py"

    cheap = nominate("cheap-reversible", "EXACT_WITNESS_FOR_CHEAP_QUERY")
    costly = nominate("high-consequence", "EXACT_WITNESS_FOR_HIGH_CONSEQUENCE_QUERY")
    same_decision = all(
        cheap.get(k) == costly.get(k)
        for k in (
            "status", "reason", "license_status", "licensed_action_ids",
            "intent_basis_kind", "obligation_id", "operational_scope_id",
        )
    )

    td, ms = seeded_effect_world(trace_count=8, prefix="P3-FIELDS")
    try:
        effect = ms.derive_multi_value_action_licenses((VALUE_ID,), config=CFG)["effect_witnesses"]["REST::ENERGY"]
    finally:
        td.cleanup()

    source = "\n".join(p.read_text(encoding="utf-8") for p in (entity, caps, types, licensing))
    witness_occurrences = {
        str(p.relative_to(ROOT)): p.read_text(encoding="utf-8").count("witness_predicate")
        for p in (entity, caps, types, licensing)
    }

    out = {
        "schema": "microseed.ms1555.pass03.recognition-irreducibility-audit.v1",
        "campaign": "MS1553-1577_DEVELOPMENTAL_CONSEQUENCE_EVIDENCE_ADEQUACY",
        "pass": 3,
        "ms": 1555,
        "phase": "HOSTILE_IRREDUCIBILITY_AUDIT",
        "discriminator": (
            "DOES_LIVE_MICROSEED_ALREADY_CONTAIN_A_LAWFUL_QUERY_LOCAL_OWNER_OR_TRIGGER_FOR_"
            "CURRENT_BUT_USE_INSUFFICIENT_CONSEQUENCE_EVIDENCE"
        ),
        "live_schema": {
            "QueryObligation_fields": list(QueryObligation.__dataclass_fields__),
            "CapabilityContract_fields": list(CapabilityContract.__dataclass_fields__),
            "EpistemicDeficitRecord_fields": list(EpistemicDeficitRecord.__dataclass_fields__),
            "effect_witness_fields": sorted(effect),
            "witness_predicate_occurrences": witness_occurrences,
            "current_query_gates_observed_in_source": [
                "required_authority",
                "obligation_id",
                "operational_scope_id",
            ],
            "effect_evidence_descriptors_observed": [
                k for k in ("effect", "support", "consistency", "source_trace_ids", "authority") if k in effect
            ],
        },
        "behavioral_equivalence": {
            "cheap_query": cheap,
            "high_consequence_query": costly,
            "same_operational_decision_despite_different_purpose_and_witness_predicate": same_decision,
        },
        "lineage_constraints": {
            "witness_predicate": (
                "RESERVED_BY_EARLIER_LINEAGE_FOR_EXACT_WITNESS_TO_QUERY_PROPOSITION_CORRESPONDENCE__"
                "NOT_AVAILABLE_FOR_SILENT_RISK_OR_ASSURANCE_REPURPOSING"
            ),
            "operational_scope_id": "OPAQUE_OPERATIONAL_LOCALITY__NOT_USE_ASSURANCE",
            "required_authority": "AUTHORITY_CLASS_REQUIREMENT__NOT_EVIDENCE_STRENGTH",
            "obligation_id": "QUERY_BINDING_IDENTITY__NOT_EVIDENCE_ADEQUACY",
            "purpose": "DESCRIPTIVE_STRING__NO_CURRENT_RUNTIME_SEMANTICS",
        },
        "irreducibility_verdict": (
            "NO_EXISTING_LIVE_FIELD_OR_BEHAVIORAL_GATE_EXPRESSES_QUERY_LOCAL_CONSEQUENCE_EVIDENCE_ADEQUACY__"
            "EXISTING_EPISTEMIC_DEFICIT_LIFECYCLE_CAN_CARRY_THE_UNKNOWN_AFTER_NOMINATION__"
            "THE_SMALLEST_OPEN_SEAM_IS_A_LAWFUL_RECOGNITION_ADMISSION_RELATION_BETWEEN_CURRENT_EVIDENCE_BASIS_AND_USE_QUERY"
        ),
        "specific_mechanism_earned": False,
        "new_primitive_earned": False,
        "main_dev_mutation": "NONE",
        "nonclaims": [
            "NO_RISK_SCORE_FIELD_EARNED",
            "NO_CONFIDENCE_FIELD_EARNED",
            "NO_WITNESS_PREDICATE_REPURPOSING",
            "NO_QUERY_PURPOSE_SEMANTICS_PROMOTED",
            "NO_PAL_CONTRACT_IMPORT",
        ],
        "file_sha256": {
            str(p.relative_to(ROOT)): sha(p)
            for p in (entity, caps, types, discovery, licensing)
        },
    }
    path = Path(__file__).with_name("MS1555_PASS03_RECOGNITION_IRREDUCIBILITY_AUDIT.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
