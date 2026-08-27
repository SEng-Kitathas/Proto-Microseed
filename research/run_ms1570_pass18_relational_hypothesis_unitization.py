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

OUT = Path(__file__).with_name("MS1570_PASS18_RELATIONAL_HYPOTHESIS_UNITIZATION.json")


def digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Episode:
    episode_id: str
    probe_evidence_id: str
    target_evidence_id: str
    probe_result: str
    target_stance: str


@dataclass(frozen=True)
class RelationalAlternative:
    """Research-only proposal handle over recurrent observed relation pairs.

    The handle says only that one probe-result/target-stance conjunction recurred
    in actual evidence. It does not name a hidden regime, assign probability,
    grant truth, or authorize execution.
    """

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


def contract() -> ValueVariableContract:
    return ValueVariableContract(
        value_id="ENERGY",
        purpose="PASS18_BOUNDED_REGULATORY_COORDINATE",
        viable_low=0.4,
        viable_high=0.6,
        signature_sha256=digest("PASS18-ENERGY-CONTRACT"),
        authority=Authority.RESEARCH_ONLY,
        lineage=("MS1570_RESEARCH_FIXTURE",),
        currentness="CURRENT",
        qualification=QualificationState.QUALIFIED,
        assistance_ancestry=("SUPPLIED_VIABLE_INTERVAL",),
    )


def stance_for_effect(effect: float) -> str:
    c = contract()
    current_value = 0.65
    pressure = pressure_magnitude_for_value(c, current_value)
    row = {
        "effect": effect,
        "authority": Authority.MODEL_OUTPUT_ONLY.value,
        "episode_schema_epoch": ("PASS18-EPISODE", 0),
        "source_trace_ids": (digest(("effect", effect)),),
    }
    return project_regulatory_effect_license(
        "TARGET-ACTION",
        "ENERGY",
        current_value=current_value,
        current_pressure=pressure,
        value_epoch=0,
        contract=c,
        effect_row=row,
    ).commitment.value


def generate_episodes(seed: int, n: int, *, linked: bool) -> list[Episode]:
    rng = random.Random(seed)
    rows: list[Episode] = []
    for i in range(n):
        # Evaluator-only mode generates the data but is never exposed to the constructor.
        mode = rng.randrange(2)
        probe_result = "P-LEFT" if mode == 0 else "P-RIGHT"
        if rng.random() < 0.08:
            probe_result = "P-RIGHT" if probe_result == "P-LEFT" else "P-LEFT"

        if linked:
            effect = -0.10 if mode == 0 else +0.10
        else:
            effect = -0.10 if rng.randrange(2) == 0 else +0.10
        if rng.random() < 0.05:
            effect = -effect
        target_stance = stance_for_effect(effect)
        eid = f"E{seed}-{i:04d}"
        rows.append(Episode(
            episode_id=eid,
            probe_evidence_id=digest((eid, "probe", probe_result)),
            target_evidence_id=digest((eid, "target", effect)),
            probe_result=probe_result,
            target_stance=target_stance,
        ))
    return rows


def construct_alternatives(
    rows: Iterable[Episode],
    *,
    min_support: int = 8,
    min_conditional_consistency: float = 0.75,
) -> list[RelationalAlternative]:
    """Tiny fixed grammar: recurrent episode-bound conjunction only.

    For each actually observed probe result, preserve the recurrent target stance
    if it is supported and conditionally stable. No hidden-state token is created.
    """
    groups: dict[str, list[Episode]] = defaultdict(list)
    for row in rows:
        groups[row.probe_result].append(row)

    out: list[RelationalAlternative] = []
    for probe_result, group in sorted(groups.items()):
        counts = Counter(row.target_stance for row in group)
        target_stance, support = counts.most_common(1)[0]
        consistency = support / len(group)
        if support < min_support or consistency < min_conditional_consistency:
            continue
        source_ids = tuple(sorted(
            evidence_id
            for row in group
            if row.target_stance == target_stance
            for evidence_id in (row.probe_evidence_id, row.target_evidence_id)
        ))
        payload = {
            "probe_result": probe_result,
            "target_stance": target_stance,
            "support": support,
            "conditional_consistency": round(consistency, 12),
        }
        out.append(RelationalAlternative(
            candidate_id="REL-ALT-" + digest(payload)[:20],
            probe_result=probe_result,
            target_stance=target_stance,
            support=support,
            conditional_consistency=consistency,
            source_evidence_ids=source_ids,
        ))
    return out


def modal_baseline(train: list[Episode], holdout: list[Episode]) -> float:
    modal = Counter(row.target_stance for row in train).most_common(1)[0][0]
    return sum(row.target_stance == modal for row in holdout) / len(holdout)


def conditional_table_accuracy(train: list[Episode], holdout: list[Episode]) -> float:
    groups: dict[str, list[str]] = defaultdict(list)
    for row in train:
        groups[row.probe_result].append(row.target_stance)
    table = {
        key: Counter(values).most_common(1)[0][0]
        for key, values in groups.items()
    }
    fallback = Counter(row.target_stance for row in train).most_common(1)[0][0]
    return sum(row.target_stance == table.get(row.probe_result, fallback) for row in holdout) / len(holdout)


def alternative_accuracy(alts: list[RelationalAlternative], holdout: list[Episode]) -> float:
    table = {alt.probe_result: alt.target_stance for alt in alts}
    if not table:
        return 0.0
    eligible = [row for row in holdout if row.probe_result in table]
    if not eligible:
        return 0.0
    return sum(row.target_stance == table[row.probe_result] for row in eligible) / len(eligible)


def hypothesis_probe(alts: list[RelationalAlternative]) -> dict[str, object]:
    hypotheses = [
        Hypothesis(
            alt.candidate_id,
            lambda x, predicted=alt.probe_result: predicted if x == "DIAGNOSTIC-PROBE" else None,
        )
        for alt in alts
    ]
    hs = HypothesisSet(hypotheses)
    selected = hs.best_probe(["DIAGNOSTIC-PROBE"])
    if selected is not None and alts:
        observed = alts[0].probe_result
        hs.observe(selected, observed)
    else:
        observed = None
    surviving = [h.hypothesis_id for h in hs.live]
    return {
        "selected_probe": selected,
        "observed_probe_result": observed,
        "surviving_hypotheses": surviving,
        "disposition": hs.disposition(),
    }


def permuted_training(rows: list[Episode], seed: int) -> list[Episode]:
    rng = random.Random(seed)
    target_stances = [row.target_stance for row in rows]
    rng.shuffle(target_stances)
    return [
        Episode(
            episode_id=row.episode_id,
            probe_evidence_id=row.probe_evidence_id,
            target_evidence_id=row.target_evidence_id,
            probe_result=row.probe_result,
            target_stance=target_stances[i],
        )
        for i, row in enumerate(rows)
    ]


def main() -> None:
    train = generate_episodes(157018, 48, linked=True)
    holdout = generate_episodes(157019, 48, linked=True)
    no_link_train = generate_episodes(157020, 48, linked=False)
    no_link_holdout = generate_episodes(157021, 48, linked=False)

    alternatives = construct_alternatives(train)
    no_link_alternatives = construct_alternatives(no_link_train)
    permuted = construct_alternatives(permuted_training(train, 157022))

    modal_acc = modal_baseline(train, holdout)
    boring_conditional_acc = conditional_table_accuracy(train, holdout)
    alt_acc = alternative_accuracy(alternatives, holdout)
    no_link_modal = modal_baseline(no_link_train, no_link_holdout)
    no_link_alt = alternative_accuracy(no_link_alternatives, no_link_holdout)
    permuted_acc = alternative_accuracy(permuted, holdout)
    probe = hypothesis_probe(alternatives)

    train_ids = {
        eid
        for row in train
        for eid in (row.probe_evidence_id, row.target_evidence_id)
    }
    holdout_ids = {
        eid
        for row in holdout
        for eid in (row.probe_evidence_id, row.target_evidence_id)
    }

    checks = {
        "two_opaque_relational_alternatives_constructed": len(alternatives) == 2,
        "alternatives_preserve_distinct_probe_results": len({a.probe_result for a in alternatives}) == 2,
        "alternatives_preserve_distinct_target_stances": {a.target_stance for a in alternatives} == {"YES", "NO"},
        "candidate_authority_remains_model_output_only": all(a.authority == Authority.MODEL_OUTPUT_ONLY.value for a in alternatives),
        "candidate_truth_and_execution_authority_none": all(a.truth_authority == "NONE" and a.execution_authority == "NONE" for a in alternatives),
        "no_hidden_regime_identity_authority": all(a.regime_identity_authority == "NONE" for a in alternatives),
        "train_holdout_evidence_disjoint": train_ids.isdisjoint(holdout_ids),
        "relational_candidate_beats_action_modal_on_holdout": alt_acc >= modal_acc + 0.20,
        "relational_candidate_matches_boring_conditional_table": abs(alt_acc - boring_conditional_acc) < 1e-12,
        "existing_hypothesis_set_selects_the_diagnostic_probe": probe["selected_probe"] == "DIAGNOSTIC-PROBE",
        "one_actual_probe_result_reduces_to_one_live_alternative": probe["disposition"] == "IDENTIFIED_WITHIN_CANDIDATE_SET",
        "permuting_relation_destroys_useful_holdout_lift": permuted_acc <= modal_acc + 0.10,
        "unlinked_world_does_not_create_large_holdout_advantage": no_link_alt <= no_link_modal + 0.10,
    }

    result = {
        "milestone": "MS1570",
        "campaign_pass": 18,
        "phase": "BOUNDED_HYPOTHESIS_CONSTRUCTION_BASELINE",
        "discriminator": (
            "CAN_A_TINY_GENERAL_RELATIONAL_UNITIZATION_OPERATOR_CONSTRUCT_EVIDENCE_ANCHORED_"
            "ALTERNATIVES_FROM_ACTUAL_EPISODE_COOCCURRENCE_THAT_BEAT_AN_ACTION_ONLY_MODAL_"
            "BASELINE_ON_INDEPENDENT_HOLDOUT_AND_GIVE_EXISTING_ACTIVE_DISCRIMINATION_A_"
            "LAWFUL_DIAGNOSTIC_PROBE__WITHOUT_PREENUMERATED_HIDDEN_MODEL_FAMILIES_OR_"
            "GRANTING_TRUTH_REGIME_OR_EXECUTION_AUTHORITY"
        ),
        "fixed_research_assistance": {
            "episode_boundary": "SUPPLIED",
            "diagnostic_probe_handle": "SUPPLIED",
            "target_action_handle": "SUPPLIED",
            "constructor_grammar": "RECURRENT_PROBE_RESULT_X_TARGET_STANCE_CONJUNCTION_ONLY",
            "min_support": 8,
            "min_conditional_consistency": 0.75,
            "no_parameter_sweep": True,
        },
        "alternatives": [asdict(a) for a in alternatives],
        "metrics": {
            "action_only_modal_holdout_accuracy": modal_acc,
            "boring_probe_conditional_table_holdout_accuracy": boring_conditional_acc,
            "relational_alternative_holdout_accuracy": alt_acc,
            "permuted_relation_holdout_accuracy": permuted_acc,
            "unlinked_action_modal_holdout_accuracy": no_link_modal,
            "unlinked_relational_holdout_accuracy": no_link_alt,
        },
        "existing_hypothesis_set_composition": probe,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "A_MINIMAL_EPISODE_BOUND_RELATIONAL_UNITIZATION_IS_SUFFICIENT_TO_FORM_TWO_"
            "OPAQUE_EVIDENCE_ANCHORED_ALTERNATIVES_IN_THIS_BOUNDED_FIXTURE_AND_IS_BEHAVIORALLY_"
            "EQUIVALENT_TO_A_BORING_CONDITIONAL_FREQUENCY_TABLE__THE_VALUE_IS_NOT_A_SPECIAL_"
            "MODEL_FAMILY_BUT_THE_ABILITY_TO_REIFY_RECURRENT_RELATION_PAIRS_AS_PROPOSAL_ONLY_"
            "ALTERNATIVE_HANDLES_THAT_EXISTING_ACTIVE_DISCRIMINATION_CAN_CONSUME"
        ),
        "anti_flattery": (
            "PERMUTED_AND_UNLINKED_CONTROLS_PREVENT_CREDIT_FOR_MARGINAL_FREQUENCY__HELDOUT_"
            "EVIDENCE_IS_DISJOINT_FROM_PROPOSAL_ANCESTRY"
        ),
        "nonclaims": [
            "NO_GENERAL_WORLD_MODEL_GENERATOR",
            "NO_GRAMMAR_FREE_INDUCTION",
            "NO_LATENT_STATE_IDENTITY",
            "NO_ENDOGENOUS_EPISODE_BOUNDARY_DISCOVERY",
            "NO_R2_TRANSFER_CREDIT",
            "NO_MAINDEV_MUTATION",
        ],
        "new_primitive_earned": False,
        "main_dev_mutation": "NONE",
        "breadth_next": (
            "HOSTILE_THE_UNITIZATION_MECHANISM_AGAINST_ONE_OFF_ASSOCIATION_EVIDENCE_ANCESTRY_"
            "LEAKAGE_AND_A_SECOND_NOVEL_RELATIONAL_FIXTURE_BEFORE_ANY_RUNTIME_OWNER_IS_CONSIDERED"
        ),
    }
    if not result["all_checks_pass"]:
        OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise SystemExit("MS1570_PASS18_DISCRIMINATOR_NOT_EARNED")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
