from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment, conjoin_required_commitments


def c(cid: str, stance: TernaryCommitment, reason: str, premise_ids=()):
    return RelationalCommitment(
        cid,
        "capability:REST:query:ACT",
        stance,
        reason=reason,
        qualifiers=(("authority_gain", "NONE"),),
        premise_ids=tuple(premise_ids),
    )


def combine(effect: TernaryCommitment, adequacy: TernaryCommitment):
    effect_c = c("EFFECT", effect, f"EFFECT_{effect.value}", ("TRACE-1",))
    adequacy_c = c("ADEQUACY", adequacy, f"ADEQUACY_{adequacy.value}", ("EVIDENCE-BASIS-1", "QUERY-ACT"))
    out = conjoin_required_commitments(
        (effect_c, adequacy_c),
        commitment_id=f"COMPOSITE-{effect.value}-{adequacy.value}",
        target_id="capability:REST:query:ACT:use",
        reason_prefix="REQUIRED_USE_PREMISE",
    )
    return out.serializable()


def main() -> None:
    matrix = {
        "effect_yes__adequacy_yes": combine(TernaryCommitment.YES, TernaryCommitment.YES),
        "effect_yes__adequacy_unknown": combine(TernaryCommitment.YES, TernaryCommitment.UNKNOWN),
        "effect_yes__adequacy_no": combine(TernaryCommitment.YES, TernaryCommitment.NO),
        "effect_no__adequacy_yes": combine(TernaryCommitment.NO, TernaryCommitment.YES),
        "effect_unknown__adequacy_yes": combine(TernaryCommitment.UNKNOWN, TernaryCommitment.YES),
    }
    checks = {
        "yes_requires_both_yes": matrix["effect_yes__adequacy_yes"]["commitment"] == "YES",
        "unknown_adequacy_blocks_yes": matrix["effect_yes__adequacy_unknown"]["commitment"] == "UNKNOWN",
        "no_adequacy_refuses_use": matrix["effect_yes__adequacy_no"]["commitment"] == "NO",
        "effect_no_still_refuses": matrix["effect_no__adequacy_yes"]["commitment"] == "NO",
        "effect_unknown_stays_unknown": matrix["effect_unknown__adequacy_yes"]["commitment"] == "UNKNOWN",
        "no_execution_authority_created": all(
            all(q != ["execution_authority", "EFFECT"] for q in row.get("qualifiers", []))
            for row in matrix.values()
        ),
        "ancestry_preserved": set(matrix["effect_yes__adequacy_yes"]["premise_ids"]) == {"EFFECT", "ADEQUACY"},
    }
    out = {
        "schema": "microseed.ms1557.pass05.commitment-composition.v1",
        "campaign": "MS1553-1577_DEVELOPMENTAL_CONSEQUENCE_EVIDENCE_ADEQUACY",
        "pass": 5,
        "ms": 1557,
        "phase": "COMPOSITION_FIRST_BEHAVIORAL_GATE",
        "discriminator": (
            "IF_A_QUERY_LOCAL_EVIDENCE_ADEQUACY_STANCE_EXISTS_CAN_EXISTING_RELATIONAL_COMMITMENT_COMPOSITION_"
            "CONSUME_IT_WITH_CURRENT_EFFECT_LICENSING_WITHOUT_A_NEW_EXECUTIVE_OR_ACTION_GATE"
        ),
        "matrix": matrix,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "surviving_localization": (
            "EXISTING_CONJUNCTIVE_COMMITMENT_ALGEBRA_ALREADY_EXPRESSES_EFFECT_USE_REQUIRES_EFFECT_PREMISE_AND_EVIDENCE_ADEQUACY_PREMISE__"
            "UNKNOWN_ADEQUACY_NATURALLY_ABSTAINS_AND_NO_NEW_AUTHORITY_IS_CREATED__MISSING_SEAM_REDUCES_TO_LAWFUL_ADEQUACY_STANCE_PRODUCTION"
        ),
        "specific_mechanism_earned": False,
        "new_primitive_earned": False,
        "main_dev_mutation": "NONE",
        "nonclaims": [
            "NO_ADEQUACY_STANCE_DERIVATION_EARNED",
            "NO_NEW_COMMITMENT_VALUE",
            "NO_EXECUTIVE",
            "NO_ACTION_MANAGER",
            "NO_PAL_IMPORT",
        ],
    }
    path = Path(__file__).with_name("MS1557_PASS05_COMMITMENT_COMPOSITION.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
