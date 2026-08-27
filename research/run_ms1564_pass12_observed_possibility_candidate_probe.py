from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

from microseed.development.action_learning import ActionOutcomeExperience
from microseed.development.value import residual_pressure_after_effect
from microseed.runtime.types import Authority, ValueVariableContract

OUT = Path(__file__).with_name("MS1564_PASS12_OBSERVED_POSSIBILITY_CANDIDATE_PROBE.json")


def digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class ObservedOutcomePossibilityCandidate:
    candidate_id: str
    start_state_id: str
    capability_id: str
    value_epoch: tuple[str, int]
    actual_next_state_id: str
    actual_value_effect: float
    support: int
    source_evidence_ids: tuple[str, ...]
    authority: str = Authority.MODEL_OUTPUT_ONLY.value
    truth_authority: str = "NONE"
    probability_authority: str = "NONE"
    execution_authority: str = "NONE"

    def __post_init__(self) -> None:
        if self.support < 1 or self.support != len(self.source_evidence_ids):
            raise ValueError("POSSIBILITY_SUPPORT_ANCESTRY_MISMATCH")
        if not math.isfinite(self.actual_value_effect):
            raise ValueError("POSSIBILITY_NONFINITE_EFFECT")
        if len(set(self.source_evidence_ids)) != len(self.source_evidence_ids):
            raise ValueError("POSSIBILITY_DUPLICATE_EVIDENCE_ID")
        if any(x != "NONE" for x in (self.truth_authority, self.probability_authority, self.execution_authority)):
            raise ValueError("POSSIBILITY_AUTHORITY_ESCALATION")

    def serializable(self) -> dict[str, object]:
        return asdict(self)


def nominate_observed_possibilities(
    rows: Iterable[ActionOutcomeExperience], *, effect_round_digits: int = 3
) -> tuple[ObservedOutcomePossibilityCandidate, ...]:
    rows = tuple(rows)
    grouped: dict[tuple[object, ...], list[ActionOutcomeExperience]] = {}
    for row in rows:
        key = (
            row.start_state_id,
            row.capability_id,
            row.value_epoch,
            row.actual_next_state_id,
            round(float(row.actual_value_effect), effect_round_digits),
        )
        grouped.setdefault(key, []).append(row)
    out = []
    for key, members in sorted(grouped.items(), key=lambda kv: str(kv[0])):
        payload = {
            "start_state_id": key[0],
            "capability_id": key[1],
            "value_epoch": key[2],
            "actual_next_state_id": key[3],
            "actual_value_effect": key[4],
        }
        out.append(ObservedOutcomePossibilityCandidate(
            candidate_id="OBS-POSS-" + digest(payload)[:20],
            start_state_id=str(key[0]),
            capability_id=str(key[1]),
            value_epoch=(str(key[2][0]), int(key[2][1])),
            actual_next_state_id=str(key[3]),
            actual_value_effect=float(key[4]),
            support=len(members),
            source_evidence_ids=tuple(sorted(row.evidence_id for row in members)),
        ))
    return tuple(out)


def classify_for_current_value(
    candidate: ObservedOutcomePossibilityCandidate,
    contract: ValueVariableContract,
    current_value: float,
) -> str:
    before = residual_pressure_after_effect(contract, current_value, 0.0)
    after = residual_pressure_after_effect(contract, current_value, candidate.actual_value_effect)
    if before > 0.0:
        if after < before:
            return "LOWERS_PRESSURE"
        if after > before:
            return "WORSENS_PRESSURE"
        return "NO_DISCRIMINATING_ADVANTAGE"
    return "PRESERVES_VIABLE_INTERVAL" if after == 0.0 else "CREATES_PRESSURE"


def row(i: int, effect: float) -> ActionOutcomeExperience:
    return ActionOutcomeExperience(
        evidence_id=f"E-{i:03d}",
        execution_id=f"X-{i:03d}",
        start_state_id="S",
        capability_id="ACT",
        actual_next_state_id="N",
        actual_value_effect=effect,
        capability_epoch=1,
        frame_epochs=(("F", 1),),
        episode_schema_epochs=(("EP", 1),),
        value_epoch=("V", 1),
    )


def main() -> None:
    rows = tuple([row(i, -0.25) for i in range(16)] + [row(16 + i, +0.25) for i in range(4)])
    reversed_rows = tuple(reversed(rows))
    candidates = nominate_observed_possibilities(rows)
    reversed_candidates = nominate_observed_possibilities(reversed_rows)

    contract = ValueVariableContract(
        value_id="V",
        purpose="bounded-regulatory-value",
        viable_low=0.4,
        viable_high=0.6,
        signature_sha256="f" * 64,
        authority=Authority.REFERENCE_ONLY,
        lineage=("MS1564-RESEARCH-FIXTURE",),
        currentness="CURRENT",
    )
    classifications = {
        c.candidate_id: classify_for_current_value(c, contract, current_value=0.65)
        for c in candidates
    }

    checks = {
        "two_observed_consequence_alternatives_are_preserved": len(candidates) == 2,
        "candidate_identity_is_input_order_invariant": [c.candidate_id for c in candidates] == [c.candidate_id for c in reversed_candidates],
        "candidate_ancestry_is_cluster_local_not_all_rows": sorted(c.support for c in candidates) == [4, 16],
        "possibility_candidates_carry_no_truth_probability_or_execution_authority": all(
            c.truth_authority == c.probability_authority == c.execution_authority == "NONE" for c in candidates
        ),
        "same_candidates_can_receive_different_current_use_relations_without_semantic_labels_in_candidate": (
            set(classifications.values()) == {"LOWERS_PRESSURE", "WORSENS_PRESSURE"}
        ),
    }

    result = {
        "milestone": "MS1564",
        "campaign_pass": 12,
        "discriminator": (
            "DOES_THE_SMALLEST_NONPREDICTIVE_OPERATION__PRESERVE_DISTINCT_ACTUALLY_OBSERVED_"
            "CONSEQUENCES_AS_OPAQUE_EVIDENCE_BOUND_POSSIBILITY_CANDIDATES__SUPPLY_THE_MISSING_"
            "SAFE_VS_HARMFUL_USE_CONTRAST_WITHOUT_HIDDEN_STATE_PROBABILITY_OR_NEW_AUTHORITY"
        ),
        "research_only_mechanism": (
            "GROUP_ACTUAL_ACTION_OUTCOME_EXPERIENCES_BY_EXISTING_STRUCTURAL_ANCESTRY_PLUS_"
            "ACTUAL_NEXT_STATE_AND_ROUNDED_ACTUAL_EFFECT__ONE_OPAQUE_PROPOSAL_HANDLE_PER_"
            "OBSERVED_OUTCOME_CLUSTER__CLASSIFY_RELATIVE_TO_CURRENT_VALUE_ONLY_AT_QUERY_TIME"
        ),
        "candidates": [c.serializable() for c in candidates],
        "query_time_classifications": classifications,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "assistance_debt": [
            "FIXED_EFFECT_ROUND_DIGITS_3",
            "DISCRETE_FIXTURE_DOES_NOT_ESTABLISH_GENERAL_NOISY_CLUSTERING",
            "CANDIDATE_TYPE_EXISTS_ONLY_IN_RESEARCH_SCRIPT",
            "NO_ENDOGENOUS_PROBE_MAPPING_EARNED",
        ],
        "localization": (
            "A_TINY_NONPREDICTIVE_POSSIBILITY_NOMINATION_OPERATION_IS_SUFFICIENT_TO_PRESERVE_"
            "THE_BIMODAL_EVIDENCE_THAT_CURRENT_PREDICTIVE_NOMINATION_LOSES__IT_CAN_REUSE_"
            "EXISTING_VALUE_GEOMETRY_FOR_QUERY_TIME_RELATION__BUT_THIS_PASS_DOES_NOT_SHOW_"
            "THAT_THE_OPERATION_GENERALIZES_TO_NOISY_CONTINUOUS_OUTCOMES_OR_CAN_FORM_A_"
            "LAWFUL_DISCRIMINATING_PROBE"
        ),
        "next_discriminator": (
            "ANTI_FLATTERY__TEST_THE_OPERATION_ON_NOISY_CONTINUOUS_R2_EXPERIENCE_WITHOUT_"
            "TUNING_CLUSTER_WIDTH__IF_FIXED_ROUNDING_EXPLODES_INTO_UNUSABLE_POSSIBILITIES_"
            "DO_NOT_PROMOTE_IT__QUARRY_EXISTING_QUANTIZATION_TOLERANCE_BEFORE_NEW_CLUSTERING"
        ),
        "main_dev_mutation": "NONE",
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1564_PASS12_PROBE_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
