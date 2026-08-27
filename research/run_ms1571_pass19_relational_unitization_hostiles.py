from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import hashlib
import json
import random
from pathlib import Path
from typing import Iterable

from microseed.cognition.hypothesis import Hypothesis, HypothesisSet
from microseed.development.action_licensing import project_regulatory_effect_license
from microseed.development.value import pressure_magnitude_for_value
from microseed.runtime.types import Authority, QualificationState, ValueVariableContract
from research.run_ms1570_pass18_relational_hypothesis_unitization import (
    Episode as Pass18Episode,
    construct_alternatives as pass18_construct_alternatives,
)

OUT = Path(__file__).with_name("MS1571_PASS19_RELATIONAL_UNITIZATION_HOSTILES.json")


def digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Episode:
    episode_id: str
    probe_evidence_id: str
    target_evidence_id: str
    probe_result: str
    target_stance: str


@dataclass(frozen=True)
class RelationalAlternative:
    candidate_id: str
    probe_result: str
    target_stance: str
    support: int
    conditional_consistency: float
    source_evidence_ids: tuple[str, ...]
    authority: str = Authority.MODEL_OUTPUT_ONLY.value
    truth_authority: str = "NONE"
    execution_authority: str = "NONE"
    regime_identity_authority: str = "NONE"


def value_contract() -> ValueVariableContract:
    return ValueVariableContract(
        value_id="ENERGY",
        purpose="PASS19_THREE_STANCE_FIXTURE",
        viable_low=0.4,
        viable_high=0.6,
        signature_sha256=digest("PASS19-ENERGY-CONTRACT"),
        authority=Authority.RESEARCH_ONLY,
        lineage=("MS1571_RESEARCH_FIXTURE",),
        currentness="CURRENT",
        qualification=QualificationState.QUALIFIED,
        assistance_ancestry=("SUPPLIED_VIABLE_INTERVAL",),
    )


def stance_for_effect(effect: float) -> str:
    c = value_contract()
    current_value = 0.65
    pressure = pressure_magnitude_for_value(c, current_value)
    relation = project_regulatory_effect_license(
        "TARGET-ACTION",
        "ENERGY",
        current_value=current_value,
        current_pressure=pressure,
        value_epoch=0,
        contract=c,
        effect_row={
            "effect": effect,
            "authority": Authority.MODEL_OUTPUT_ONLY.value,
            "episode_schema_epoch": ("PASS19-EPISODE", 0),
            "source_trace_ids": (digest(("effect", effect)),),
        },
    )
    return relation.commitment.value


def unique_semantic_rows(rows: Iterable[Episode]) -> list[Episode]:
    """Deduplicate exact evidence ancestry; reject identity/content conflicts."""
    by_identity: dict[tuple[str, str], Episode] = {}
    for row in rows:
        identity = (row.probe_evidence_id, row.target_evidence_id)
        prior = by_identity.get(identity)
        if prior is not None and (
            prior.probe_result != row.probe_result
            or prior.target_stance != row.target_stance
        ):
            raise ValueError("EVIDENCE_IDENTITY_CONTENT_CONFLICT")
        by_identity[identity] = row
    return list(by_identity.values())


def construct_alternatives(
    rows: Iterable[Episode],
    *,
    min_support: int = 8,
    min_conditional_consistency: float = 0.75,
) -> list[RelationalAlternative]:
    groups: dict[str, list[Episode]] = defaultdict(list)
    for row in unique_semantic_rows(rows):
        groups[row.probe_result].append(row)

    out: list[RelationalAlternative] = []
    for probe_result, group in sorted(groups.items()):
        counts = Counter(row.target_stance for row in group)
        target_stance, support = counts.most_common(1)[0]
        consistency = support / len(group)
        if support < min_support or consistency < min_conditional_consistency:
            continue
        supporting = [row for row in group if row.target_stance == target_stance]
        source_ids = tuple(sorted({
            evidence_id
            for row in supporting
            for evidence_id in (row.probe_evidence_id, row.target_evidence_id)
        }))
        semantic_payload = {
            "probe_result": probe_result,
            "target_stance": target_stance,
            "operator": "EPISODE_BOUND_RELATIONAL_UNITIZATION",
        }
        out.append(RelationalAlternative(
            candidate_id="REL-ALT-" + digest(semantic_payload)[:20],
            probe_result=probe_result,
            target_stance=target_stance,
            support=support,
            conditional_consistency=consistency,
            source_evidence_ids=source_ids,
        ))
    return out


def generate_three_way(seed: int, n: int, *, linked: bool) -> list[Episode]:
    rng = random.Random(seed)
    probe_for_mode = ("P-LEFT", "P-CENTER", "P-RIGHT")
    effect_for_mode = (-0.10, 0.0, +0.10)
    rows: list[Episode] = []
    for i in range(n):
        mode = rng.randrange(3)
        probe_result = probe_for_mode[mode]
        if rng.random() < 0.05:
            probe_result = probe_for_mode[rng.randrange(3)]

        effect_mode = mode if linked else rng.randrange(3)
        effect = effect_for_mode[effect_mode]
        if rng.random() < 0.03:
            effect = effect_for_mode[rng.randrange(3)]
        stance = stance_for_effect(effect)
        eid = f"P19-{seed}-{i:04d}"
        rows.append(Episode(
            episode_id=eid,
            probe_evidence_id=digest((eid, "probe", probe_result)),
            target_evidence_id=digest((eid, "target", effect)),
            probe_result=probe_result,
            target_stance=stance,
        ))
    return rows


def modal_accuracy(train: list[Episode], holdout: list[Episode]) -> float:
    modal = Counter(r.target_stance for r in train).most_common(1)[0][0]
    return sum(r.target_stance == modal for r in holdout) / len(holdout)


def table_accuracy(train: list[Episode], holdout: list[Episode]) -> float:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in train:
        grouped[row.probe_result].append(row.target_stance)
    table = {k: Counter(v).most_common(1)[0][0] for k, v in grouped.items()}
    fallback = Counter(r.target_stance for r in train).most_common(1)[0][0]
    return sum(r.target_stance == table.get(r.probe_result, fallback) for r in holdout) / len(holdout)


def alt_accuracy(alts: list[RelationalAlternative], holdout: list[Episode]) -> float:
    table = {a.probe_result: a.target_stance for a in alts}
    if not table:
        return 0.0
    eligible = [r for r in holdout if r.probe_result in table]
    return sum(r.target_stance == table[r.probe_result] for r in eligible) / len(eligible) if eligible else 0.0


def probe_reduction(alts: list[RelationalAlternative]) -> dict[str, object]:
    hypotheses = [
        Hypothesis(
            a.candidate_id,
            lambda x, prediction=a.probe_result: prediction if x == "DIAGNOSTIC-PROBE" else None,
        )
        for a in alts
    ]
    outcomes: dict[str, dict[str, object]] = {}
    for alt in alts:
        hs = HypothesisSet(hypotheses)
        selected = hs.best_probe(["DIAGNOSTIC-PROBE"])
        hs.observe("DIAGNOSTIC-PROBE", alt.probe_result)
        outcomes[alt.probe_result] = {
            "selected": selected,
            "disposition": hs.disposition(),
            "survivors": [h.hypothesis_id for h in hs.live],
        }
    return outcomes


def main() -> None:
    # Hostile 1: demonstrate the exact Pass-18 proposal was vulnerable to repeated
    # copies of the same evidence identity inflating support.
    one = Pass18Episode(
        episode_id="DUP-ONE",
        probe_evidence_id=digest(("DUP-ONE", "probe")),
        target_evidence_id=digest(("DUP-ONE", "target")),
        probe_result="P-LEFT",
        target_stance="YES",
    )
    pass18_duplicate_inflation = pass18_construct_alternatives([one] * 20)

    hardened_one = Episode(**asdict(one))
    hardened_duplicate = construct_alternatives([hardened_one] * 20)
    one_off = construct_alternatives([
        Episode(
            episode_id=f"ONEOFF-{i}",
            probe_evidence_id=digest(("ONEOFF", i, "probe")),
            target_evidence_id=digest(("ONEOFF", i, "target")),
            probe_result=f"P-{i}",
            target_stance=("YES", "NO", "UNKNOWN")[i % 3],
        )
        for i in range(7)
    ])

    train = generate_three_way(157119, 72, linked=True)
    holdout = generate_three_way(157120, 72, linked=True)
    unlinked_train = generate_three_way(157121, 72, linked=False)
    unlinked_holdout = generate_three_way(157122, 72, linked=False)
    alts = construct_alternatives(train)
    alts_reversed = construct_alternatives(reversed(train))
    unlinked_alts = construct_alternatives(unlinked_train)

    modal = modal_accuracy(train, holdout)
    boring = table_accuracy(train, holdout)
    relational = alt_accuracy(alts, holdout)
    unlinked_modal = modal_accuracy(unlinked_train, unlinked_holdout)
    unlinked_relational = alt_accuracy(unlinked_alts, unlinked_holdout)
    probe = probe_reduction(alts)

    train_ids = {eid for r in train for eid in (r.probe_evidence_id, r.target_evidence_id)}
    holdout_ids = {eid for r in holdout for eid in (r.probe_evidence_id, r.target_evidence_id)}

    expected_stances = {"YES", "NO", "UNKNOWN"}
    checks = {
        "pass18_duplicate_inflation_hostile_detected": len(pass18_duplicate_inflation) == 1 and pass18_duplicate_inflation[0].support == 20,
        "hardened_constructor_deduplicates_same_evidence_identity": hardened_duplicate == [],
        "one_off_associations_do_not_qualify": one_off == [],
        "three_way_fixture_forms_three_opaque_alternatives": len(alts) == 3,
        "three_way_fixture_preserves_full_existing_ternary_stance_set": {a.target_stance for a in alts} == expected_stances,
        "candidate_semantic_identity_is_input_order_invariant": [a.candidate_id for a in alts] == [a.candidate_id for a in alts_reversed],
        "source_evidence_ids_are_unique_inside_each_candidate": all(len(a.source_evidence_ids) == len(set(a.source_evidence_ids)) for a in alts),
        "train_holdout_ancestry_is_disjoint": train_ids.isdisjoint(holdout_ids),
        "three_way_relational_model_beats_global_modal": relational >= modal + 0.25,
        "relational_model_matches_boring_conditional_table": abs(relational - boring) < 1e-12,
        "unlinked_control_has_no_material_relational_gain": unlinked_relational <= unlinked_modal + 0.10,
        "existing_hypothesis_set_can_reduce_each_three_way_alternative_with_one_probe": all(
            row["selected"] == "DIAGNOSTIC-PROBE"
            and row["disposition"] == "IDENTIFIED_WITHIN_CANDIDATE_SET"
            and len(row["survivors"]) == 1
            for row in probe.values()
        ),
        "all_alternatives_have_zero_truth_execution_regime_authority": all(
            a.authority == Authority.MODEL_OUTPUT_ONLY.value
            and a.truth_authority == "NONE"
            and a.execution_authority == "NONE"
            and a.regime_identity_authority == "NONE"
            for a in alts
        ),
    }

    result = {
        "milestone": "MS1571",
        "campaign_pass": 19,
        "phase": "HOSTILE_RELATIONAL_UNITIZATION_CONTROLS",
        "discriminator": (
            "DOES_THE_PASS18_MINIMAL_RELATIONAL_UNITIZATION_SURVIVE_DUPLICATE_EVIDENCE_"
            "ONE_OFF_ASSOCIATION_AND_A_NOVEL_THREE_ALTERNATIVE_FIXTURE_WITH_INDEPENDENT_"
            "HOLDOUT__WITHOUT_GAINING_TRUTH_EXECUTION_OR_REGIME_IDENTITY_AUTHORITY"
        ),
        "pass18_hostile_finding": {
            "duplicate_evidence_copies": 20,
            "unhardened_candidate_count": len(pass18_duplicate_inflation),
            "unhardened_inflated_support": pass18_duplicate_inflation[0].support if pass18_duplicate_inflation else 0,
            "scar": "REPEATED_COPY_OF_ONE_EVIDENCE_IDENTITY_MUST_NOT_INFLATE_RELATIONAL_SUPPORT",
        },
        "hardened_rule": (
            "COUNT_UNIQUE_PROBE_EVIDENCE_ID_X_TARGET_EVIDENCE_ID_PAIRS__REJECT_IDENTITY_CONTENT_CONFLICT__"
            "THEN_APPLY_THE_SAME_FIXED_SUPPORT_AND_CONSISTENCY_GATES"
        ),
        "three_way_alternatives": [asdict(a) for a in alts],
        "metrics": {
            "global_modal_holdout_accuracy": modal,
            "boring_conditional_table_holdout_accuracy": boring,
            "relational_alternative_holdout_accuracy": relational,
            "unlinked_modal_holdout_accuracy": unlinked_modal,
            "unlinked_relational_holdout_accuracy": unlinked_relational,
        },
        "probe_reduction": probe,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "THE_MINIMAL_MECHANISM_SURVIVES_AFTER_EVIDENCE_IDENTITY_DEDUPLICATION_AND_GENERALIZES_"
            "FROM_BINARY_TO_THREE_WAY_EXISTING_TERNARY_STANCES__IT_REMAINS_EQUIVALENT_TO_A_"
            "BORING_CONDITIONAL_RECURRENCE_TABLE_NOT_A_SPECIAL_MODEL_ARCHITECTURE"
        ),
        "nonclaims": [
            "NO_STRUCTURAL_SHARED_ROOT_INDEPENDENCE_CLAIM",
            "NO_GENERAL_LATENT_MODEL",
            "NO_ENDOGENOUS_PROBE_DISCOVERY",
            "NO_R2_TRANSFER_CREDIT",
            "NO_MAINDEV_MUTATION",
        ],
        "new_primitive_earned": False,
        "main_dev_mutation": "NONE",
        "breadth_next": (
            "COMPOSE_THE_HARDENED_PROPOSAL_ONLY_ALTERNATIVES_WITH_EXISTING_EPISTEMIC_DEFICIT_"
            "HYPOTHESISSET_PROBE_AND_ACTUAL_EVIDENCE_REVISIT_IN_ONE_END_TO_END_BOUNDED_EPISODE_"
            "WITHOUT_ADDING_A_NEW_RUNTIME_OWNER"
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not result["all_checks_pass"]:
        raise SystemExit("MS1571_PASS19_HOSTILE_CONTROLS_FAILED")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
