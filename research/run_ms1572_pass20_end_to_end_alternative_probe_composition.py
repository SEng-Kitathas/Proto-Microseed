from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from microseed import (
    Authority,
    CapabilityContract,
    EpistemicContrastBinding,
    EpistemicContrastRow,
    EpistemicStatus,
    Microseed,
    QualificationState,
    QueryObligation,
)
from microseed.cognition.hypothesis import Hypothesis, HypothesisSet
from research.run_ms1571_pass19_relational_unitization_hostiles import (
    construct_alternatives,
    generate_three_way,
)

OUT = Path(__file__).with_name("MS1572_PASS20_END_TO_END_ALTERNATIVE_PROBE_COMPOSITION.json")


def h(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def probe_contract(result: str) -> CapabilityContract:
    return CapabilityContract(
        "DIAGNOSTIC-PROBE",
        "bounded-diagnostic-observation",
        {},
        {},
        (),
        (),
        Authority.DERIVED_READ_ONLY,
        ("MS1572-PASS20",),
        "CURRENT",
        {},
        query_obligation_id="Q-DIAGNOSTIC-PROBE",
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: {"probe_outcome": result},
        operational_scope_id="PASS20-BOUNDED-DIAGNOSTIC",
    )


def as_hypotheses(alternatives):
    return [
        Hypothesis(
            a.candidate_id,
            lambda x, predicted=a.probe_result: predicted if x == "DIAGNOSTIC-PROBE" else None,
        )
        for a in alternatives
    ]


def main() -> None:
    train = generate_three_way(157220, 72, linked=True)
    alternatives = construct_alternatives(train)
    hypothesis_digest = h(tuple(sorted(a.candidate_id for a in alternatives)))
    hypotheses = as_hypotheses(alternatives)

    # Choose one actually generated candidate result for the bounded world.
    actual_probe_result = "P-CENTER"
    expected_candidate = next(a for a in alternatives if a.probe_result == actual_probe_result)

    with tempfile.TemporaryDirectory(prefix="microseed-ms1572-") as td:
        ms = Microseed(Path(td))
        unknown = ms.append_evidence(
            "E-P20-USE-UNKNOWN",
            {
                "query": "TARGET-ACTION::ENERGY::HIGH-CONSEQUENCE",
                "candidate_ids": [a.candidate_id for a in alternatives],
                "reason": "CURRENT_CONSEQUENCE_EVIDENCE_SUPPORTS_MULTIPLE_QUERY_RELEVANT_RELATIONAL_ALTERNATIVES",
            },
            EpistemicStatus.UNKNOWN_INCOMPLETE,
            source="MS1572-RESEARCH-ADAPTER",
        )
        deficit = ms.record_action_limited_unknown(
            deficit_id="D-P20",
            question_key="use-adequacy:TARGET-ACTION:ENERGY:Q-HIGH",
            hypothesis_digest_sha256=hypothesis_digest,
            unknown_evidence_id=unknown.evidence_id,
            missing_discriminator_signature_sha256=h("DIAGNOSTIC-PROBE"),
            assistance_ancestry=(
                "PASS20_RESEARCH_ADAPTER_NOMINATED_DEFICIT_FROM_PASS19_RELATIONAL_ALTERNATIVES",
            ),
        )

        discrimination = ms.active_discrimination(
            hypotheses,
            ["DIAGNOSTIC-PROBE"],
            [],
        )

        ms.register_capability(probe_contract(actual_probe_result))
        bound = ms.bind_probe_capability(deficit.deficit_id, "DIAGNOSTIC-PROBE")
        query = QueryObligation(
            "Q-DIAGNOSTIC-PROBE",
            "bounded-diagnostic-probe",
            required_authority=Authority.DERIVED_READ_ONLY,
            operational_scope_id="PASS20-BOUNDED-DIAGNOSTIC",
        )
        invoked = ms.capabilities.invoke("DIAGNOSTIC-PROBE", query)
        observed_probe_result = invoked["value"]["probe_outcome"]

        # Existing contrast machinery needs a current opaque projection handle.
        # Formation of the projection remains explicit assistance; the candidate
        # prediction partition itself is generated from Pass-19 alternatives.
        ms.register_epistemic_projection(
            "PASS20-PROBE-PROJECTION",
            h("PASS20-PROBE-PROJECTION"),
            assistance_ancestry=(
                "PASS20_EXISTING_CONTRAST_API_REQUIRES_CURRENT_PROJECTION_HANDLE",
            ),
        )
        generated_partition = tuple(
            (a.candidate_id, h(a.probe_result))
            for a in alternatives
        )
        binding = EpistemicContrastBinding(
            binding_id="B-P20",
            deficit_id=deficit.deficit_id,
            hypothesis_digest_sha256=hypothesis_digest,
            rows=(EpistemicContrastRow(
                "PASS20-PROBE-PROJECTION",
                0,
                generated_partition,
                None,
            ),),
            assistance_ancestry=(
                "PASS20_BINDING_ADAPTER_FROM_RESEARCH_CANDIDATE_PREDICTIONS_TO_EXISTING_CONTRAST_API",
            ),
        )
        ms.register_epistemic_contrast(binding)

        actual_evidence = ms.append_evidence(
            "E-P20-PROBE-ACTUAL",
            {
                "actual_probe_capability_id": "DIAGNOSTIC-PROBE",
                "actual_probe_result": observed_probe_result,
                "epistemic_projection": {
                    "projection_id": "PASS20-PROBE-PROJECTION",
                    "projection_epoch": 0,
                    "outcome_digest_sha256": h(observed_probe_result),
                },
            },
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="EXT-PASS20-DIAGNOSTIC",
        )
        ms.record_epistemic_probe_evidence(deficit.deficit_id, actual_evidence.evidence_id)
        bearing = ms.assess_epistemic_evidence_bearing(
            deficit.deficit_id,
            "B-P20",
            actual_evidence.evidence_id,
        )
        final_deficit = ms.epistemic_deficit_status(deficit.deficit_id)

        # Existing hypothesis maintenance can now narrow the candidate set, but
        # the surviving target stance remains proposal content only. This pass
        # intentionally does not invoke TARGET-ACTION.
        hs = HypothesisSet(hypotheses)
        hs.observe("DIAGNOSTIC-PROBE", observed_probe_result)
        surviving_ids = [x.hypothesis_id for x in hs.live]
        surviving = [a for a in alternatives if a.candidate_id in surviving_ids]

        # Hostile controls.
        no_lawful_probe = ms.active_discrimination(hypotheses, [], [])
        unexpected = HypothesisSet(hypotheses)
        unexpected.observe("DIAGNOSTIC-PROBE", "P-UNSEEN")

        checks = {
            "research_candidates_form_more_than_one_live_alternative": len(alternatives) == 3,
            "existing_active_discrimination_selects_generated_disagreement_probe": discrimination["next_probe"] == "DIAGNOSTIC-PROBE",
            "probe_binding_is_not_resolution": bound["state"] == "PROBE_AVAILABLE",
            "probe_executes_only_through_current_qualified_capability": invoked["status"] == "CAPABILITY_RESULT" and invoked["authority"] == Authority.DERIVED_READ_ONLY.value,
            "contrast_partition_is_generated_from_candidate_predictions": set(generated_partition) == {(a.candidate_id, h(a.probe_result)) for a in alternatives},
            "actual_evidence_is_discriminating": bearing["bearing_kind"] == "DISCRIMINATES_LIVE_SET",
            "actual_evidence_requests_revisit_not_resolution": final_deficit["state"] == "REVISIT_REQUIRED",
            "actual_probe_reduces_candidate_set_to_one": hs.disposition() == "IDENTIFIED_WITHIN_CANDIDATE_SET" and len(surviving) == 1,
            "surviving_candidate_matches_actual_probe_result": surviving[0].candidate_id == expected_candidate.candidate_id,
            "surviving_target_stance_remains_model_output_not_execution_authority": surviving[0].execution_authority == "NONE" and surviving[0].truth_authority == "NONE",
            "no_lawful_probe_pool_means_no_probe": no_lawful_probe["next_probe"] is None,
            "unexpected_probe_result_challenges_model_space_instead_of_forcing_candidate": unexpected.disposition() == "MODEL_SPACE_MISSPECIFIED_OR_CONTRADICTED",
            "bearing_has_zero_answer_authority": bearing["truth_authority"] == "NONE" and bearing["answer_authority"] == "NONE",
        }

        result = {
            "milestone": "MS1572",
            "campaign_pass": 20,
            "phase": "END_TO_END_EXISTING_LIFECYCLE_COMPOSITION",
            "discriminator": (
                "CAN_RECURRENT_RELATIONAL_ALTERNATIVE_HANDLES_FROM_ACTUAL_EVIDENCE_FEED_THE_"
                "EXISTING_EPISTEMIC_DEFICIT_ACTIVE_DISCRIMINATION_CAPABILITY_INVOCATION_"
                "EVIDENCE_BEARING_AND_REVISIT_LIFECYCLE_WITHOUT_A_NEW_RUNTIME_OWNER_OR_"
                "WITHOUT_TURNING_THE_SURVIVING_ALTERNATIVE_INTO_TRUTH_OR_EXECUTION_AUTHORITY"
            ),
            "candidate_ids": [a.candidate_id for a in alternatives],
            "generated_partition": [list(x) for x in generated_partition],
            "discrimination": discrimination,
            "probe_invocation": invoked,
            "bearing": bearing,
            "final_deficit": final_deficit,
            "surviving_candidate": {
                "candidate_id": surviving[0].candidate_id,
                "probe_result": surviving[0].probe_result,
                "target_stance": surviving[0].target_stance,
                "truth_authority": surviving[0].truth_authority,
                "execution_authority": surviving[0].execution_authority,
            } if surviving else None,
            "checks": checks,
            "all_checks_pass": all(checks.values()),
            "assistance_debt": [
                "EPISODE_BOUNDARY_PROBE_HANDLE_AND_TARGET_ACTION_HANDLE_REMAIN_SUPPLIED",
                "RESEARCH_ADAPTER_NOMINATES_THE_EXISTING_EPISTEMIC_DEFICIT_FROM_RELATIONAL_ALTERNATIVES",
                "CURRENT_EPISTEMIC_PROJECTION_HANDLE_REMAINS_SUPPLIED_AS_REQUIRED_BY_EXISTING_CONTRAST_API",
                "RUNTIME_HAS_NO_ADMISSION_PATH_FOR_RESEARCH_GENERATED_CONTRAST_BINDINGS",
                "NO_CREDIT_FOR_TARGET_ACTION_EXECUTION_AFTER_REVISIT",
            ],
            "localization": (
                "THE_MINIMAL_RELATIONAL_ALTERNATIVES_COMPOSE_THROUGH_THE_EXISTING_DEFICIT_PROBE_"
                "AND_BEARING_LIFECYCLE_WITHOUT_NEW_RUNTIME_CONTROL_MACHINERY__THE_REMAINING_"
                "INTEGRATION_SEAM_IS_PROPOSAL_ADMISSION_QUESTION_PRESSURE_AND_CONTRAST_BINDING_"
                "FROM_EVIDENCE_NOT_ACTIVE_DISCRIMINATION_OR_EXECUTION"
            ),
            "new_primitive_earned": False,
            "main_dev_mutation": "NONE",
            "breadth_next": (
                "RETURN_TO_REAL_R2_EVIDENCE_AND_TEST_WHETHER_QUERY_RELATIVE_STANCE_DISAGREEMENT_"
                "PLUS_EXISTING_EPISODE_ANCESTRY_CAN_NOMINATE_USEFUL_RELATIONAL_ALTERNATIVES_"
                "WITHOUT_SUPPLYING_A_DIAGNOSTIC_MAPPING__IF_NOT_STOP_BEFORE_RUNTIME_INTEGRATION"
            ),
        }
        OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if not result["all_checks_pass"]:
            raise SystemExit("MS1572_PASS20_END_TO_END_COMPOSITION_FAILED")
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
