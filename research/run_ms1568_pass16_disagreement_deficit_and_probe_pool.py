from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

from microseed import Microseed
from microseed.cognition.hypothesis import Hypothesis, HypothesisSet
from microseed.runtime.types import EpistemicStatus

OUT = Path(__file__).with_name("MS1568_PASS16_DISAGREEMENT_DEFICIT_AND_PROBE_POOL.json")


def sha(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def main() -> None:
    # Research adapter input represents the Pass-15 result: the same current use
    # has evidence-backed YES and NO consequence stances.
    stance_basis = {
        "query": "Q:ACT:VALUE:HIGH_CONSEQUENCE",
        "YES_evidence": ["E-Y-1", "E-Y-2", "E-Y-3"],
        "NO_evidence": ["E-N-1", "E-N-2"],
    }
    hypothesis_digest = sha(stance_basis)
    missing_disc = sha({"need": "PREDICTION_BEARING_LAWFUL_PROBE_THAT_SEPARATES_YES_NO_CONSEQUENCE_ALTERNATIVES"})

    with tempfile.TemporaryDirectory(prefix="microseed-ms1568-") as td:
        ms = Microseed(Path(td))
        unknown = ms.append_evidence(
            "MS1568-USE-ADEQUACY-UNKNOWN",
            {"stance_basis_sha256": hypothesis_digest, "reason": "QUERY_RELATIVE_CONSEQUENCE_STANCE_DISAGREEMENT"},
            EpistemicStatus.UNKNOWN_INCOMPLETE,
            source="MS1568-RESEARCH-ADAPTER",
        )
        deficit = ms.record_action_limited_unknown(
            deficit_id="MS1568-DEFICIT",
            question_key="Q:ACT:VALUE:HIGH_CONSEQUENCE",
            hypothesis_digest_sha256=hypothesis_digest,
            unknown_evidence_id=unknown.evidence_id,
            missing_discriminator_signature_sha256=missing_disc,
            assistance_ancestry=(
                "RESEARCH_ADAPTER_NOMINATED_DEFICIT_FROM_PASS15_STANCE_DISAGREEMENT",
                "NO_ADEQUACY_ANSWER_AUTHORITY",
            ),
        )

        # Two alternatives disagree only on repeating the uncertain consequential
        # action. The harmless candidate SAFE_CHECK is non-discriminating.
        h_yes = Hypothesis("H-YES", lambda probe: "YES" if probe == "ACT" else "SAME")
        h_no = Hypothesis("H-NO", lambda probe: "NO" if probe == "ACT" else "SAME")
        hs = HypothesisSet((h_yes, h_no))
        unfiltered = hs.best_probe(("ACT", "SAFE_CHECK"))
        lawful_pool_only = hs.best_probe(("SAFE_CHECK",))

        # When an independently lawful discriminating probe mapping is supplied,
        # the existing active-discrimination machinery uses it correctly.
        h_yes_p = Hypothesis("H-YES-P", lambda probe: "A" if probe == "P" else "SAME")
        h_no_p = Hypothesis("H-NO-P", lambda probe: "B" if probe == "P" else "SAME")
        hs2 = HypothesisSet((h_yes_p, h_no_p))
        lawful_discriminating = hs2.best_probe(("SAFE_CHECK", "P"))

        checks = {
            "stance_disagreement_can_be_carried_by_existing_action_limited_deficit": deficit.state.value == "ACTION_LIMITED",
            "deficit_nomination_grants_no_truth_or_semantic_question_authority": deficit.truth_authority == deficit.semantic_question_authority == "NONE",
            "active_discrimination_would_choose_uncertain_action_if_it_is_in_candidate_pool_and_only_discriminator": unfiltered == "ACT",
            "excluding_unlicensed_uncertain_action_from_probe_pool_yields_no_fake_probe": lawful_pool_only is None,
            "existing_active_discrimination_selects_lawful_discriminator_when_prediction_mapping_exists": lawful_discriminating == "P",
        }

    result = {
        "milestone": "MS1568",
        "campaign_pass": 16,
        "discriminator": (
            "CAN_QUERY_RELATIVE_STANCE_DISAGREEMENT_NOMINATE_THE_EXISTING_EPISTEMIC_DEFICIT_"
            "LIFECYCLE_WITHOUT_NEW_AUTHORITY_AND_CAN_EXISTING_ACTIVE_DISCRIMINATION_REFUSE_"
            "AN_UNCERTAIN_CONSEQUENTIAL_ACTION_WHEN_IT_IS_NOT_IN_THE_LAWFUL_PROBE_POOL"
        ),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "localization": (
            "QUERY_RELATIVE_STANCE_DISAGREEMENT_CAN_BE_ADAPTED_INTO_THE_EXISTING_ACTION_LIMITED_"
            "DEFICIT_LIFECYCLE_WITH_ZERO_NEW_AUTHORITY__HYPOTHESISSET_RESPECTS_THE_CALLER_"
            "SUPPLIED_PROBE_POOL_AND_DOES_NOT_INVENT_A_PROBE__THEREFORE_THE_REMAINING_SEAM_IS_"
            "NOT_DEFICIT_STATE_OR_SAFE_PROBE_GATING_BUT_ENDOGENOUS_FORMATION_OF_PREDICTION_"
            "BEARING_ALTERNATIVES_OVER_LAWFULLY_AVAILABLE_DIAGNOSTIC_INTERACTIONS"
        ),
        "assistance_debt": [
            "DEFICIT_NOMINATION_FROM_STANCE_DISAGREEMENT_IS_RESEARCH_ADAPTER_LOGIC",
            "LAWFUL_PROBE_POOL_IS_SUPPLIED_TO_HYPOTHESISSET",
            "PREDICTIONS_FOR_DIAGNOSTIC_PROBE_P_ARE_SUPPLIED",
        ],
        "critical_scar": (
            "ACTIVE_DISCRIMINATION_IS_NOT_A_SAFETY_AUTHORITY__IF_AN_UNCERTAIN_HIGH_CONSEQUENCE_"
            "ACTION_IS_OFFERED_AS_THE_ONLY_DISCRIMINATOR_IT_WILL_SELECT_IT__LAWFUL_PROBE_"
            "ELIGIBILITY_MUST_BE_ESTABLISHED_UPSTREAM"
        ),
        "breadth_rerank": (
            "TEST_WHETHER_EXISTING_REHEARSAL_ACTION_OUTCOME_RELATIONS_CAN_PREDICT_DIAGNOSTIC_"
            "PROBE_CONSEQUENCES_UNDER_EACH_LIVE_ALTERNATIVE__IF_NOT__THE_CAMPAIGN_HAS_LOCALIZED_"
            "BOUNDED_COUNTERFACTUAL_HYPOTHESIS_CONSTRUCTION_RATHER_THAN_GENERIC_UNCERTAINTY"
        ),
        "main_dev_mutation": "NONE",
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1568_PASS16_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
