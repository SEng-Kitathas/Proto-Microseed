from __future__ import annotations

from pathlib import Path
import tempfile

from microseed import (
    Authority,
    CapabilityContract,
    CounterfactualRehearsalConfig,
    EpisodeSchemaContract,
    FeasibilityState,
    Microseed,
    Observation,
    OperationalCoordinationContract,
    OperationalCounterpartyContract,
    OperationalFrameContract,
    QualificationState,
    RecruitmentOption,
    RecruitmentTopologyContract,
    RehearsalTransitionObservation,
    ValueVariableContract,
    derive_rehearsal_transition_relations,
    propose_counterfactual_rehearsal,
)
from microseed.development.rehearsal import CounterfactualRehearsalProposal


def _cap(cid: str) -> CapabilityContract:
    return CapabilityContract(
        cid,
        "opaque",
        {},
        {},
        (),
        (),
        Authority.DERIVED_READ_ONLY,
        ("MS1939",),
        "CURRENT",
        {},
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def _setup_world(ms: Microseed) -> None:
    ms.register_operational_frame(
        OperationalFrameContract(
            "F",
            "opaque-frame",
            "f" * 64,
            Authority.DERIVED_READ_ONLY,
            ("MS1939",),
            "CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
        )
    )
    ms.register_value_variable(
        ValueVariableContract(
            "V",
            "opaque-regulatory",
            2.0,
            3.0,
            "v" * 64,
            Authority.DERIVED_READ_ONLY,
            ("MS1939",),
            "CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            assistance_ancestry=(
                "SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE",
                "SUPPLIED_VIABILITY_INTERVAL",
            ),
        )
    )
    ms.observe_value_state("V", 0.0)

    cp = OperationalCounterpartyContract(
        "CP",
        "opaque-counterparty",
        "",
        Authority.DERIVED_READ_ONLY,
        ("MS1939",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    )
    cp.signature_sha256 = cp.computed_signature_sha256()
    ms.register_operational_counterparty(cp)

    coord = OperationalCoordinationContract(
        "R",
        "opaque-coordination",
        (("CP", 0),),
        "",
        Authority.DERIVED_READ_ONLY,
        ("MS1939",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    )
    coord.signature_sha256 = coord.computed_signature_sha256()
    ms.register_operational_coordination(coord)

    ms.register_capability(_cap("A"))
    ms.register_capability(_cap("B"))
    ms.register_capability(_cap("C"), coordination_dependencies=(("R", 0),))

    topo = RecruitmentTopologyContract(
        "T",
        "opaque-topology",
        (("A", "B"), ("B", "C")),
        (("A", 0), ("B", 0), ("C", 0)),
        "",
        Authority.DERIVED_READ_ONLY,
        ("MS1939",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    )
    topo.signature_sha256 = topo.computed_signature_sha256()
    ms.register_recruitment_topology(topo)

    ms.register_episode_schema(
        EpisodeSchemaContract(
            "E",
            "opaque-episode",
            "e" * 64,
            Authority.DERIVED_READ_ONLY,
            ("MS1939",),
            "CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            frame_epochs=(("F", 0),),
            value_epochs=(("V", 0),),
            coordination_epochs=(("R", 0),),
        )
    )


def _rows() -> tuple[RehearsalTransitionObservation, ...]:
    out: list[RehearsalTransitionObservation] = []
    k = 0
    for state, action, next_state, effect, coord in (
        ("S0", "A", "SA", 0.8, None),
        ("S0", "B", "S1", -0.4, None),
        ("S1", "C", "S2", 2.6, "R"),
        ("S1", "A", "SA", 0.8, None),
    ):
        for _ in range(12):
            k += 1
            out.append(
                RehearsalTransitionObservation(
                    f"EV{k}",
                    state,
                    action,
                    next_state,
                    effect,
                    0,
                    "F",
                    0,
                    "E",
                    0,
                    "T",
                    0,
                    coord,
                    0 if coord else None,
                )
            )
    return tuple(out)


def _opts() -> tuple[RecruitmentOption, ...]:
    return (
        RecruitmentOption("A", FeasibilityState.FEASIBLE, local_cost=0.1),
        RecruitmentOption("B", FeasibilityState.FEASIBLE, local_cost=0.1),
        RecruitmentOption("C", FeasibilityState.FEASIBLE, local_cost=0.1),
    )


def _set_control_state(ms: Microseed, state_id: str = "S0") -> None:
    ms.observe_opaque_control_state(
        Observation(
            f"CTRL-{state_id}",
            "EXT",
            "opaque-control",
            state_id,
            authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id=f"E-CTRL-{state_id}",
    )


def _close(ms: Microseed) -> None:
    ms.biography.close()
    ms.evidence.conn.close()
    ms.store.conn.close()


def test_zero_pressure_proposal_is_explicitly_not_action_indicated() -> None:
    with tempfile.TemporaryDirectory(prefix="ms1939-zero-pressure-") as td:
        ms = Microseed(Path(td))
        try:
            _setup_world(ms)
            ms.observe_value_state("V", 2.5)
            _set_control_state(ms)
            pressure = ms.value_pressure("V")
            assert pressure["pressure_magnitude"] == 0.0
            assert pressure["relation"] == "WITHIN_VIABLE_INTERVAL"

            proposal = ms.nominate_counterfactual_rehearsal(
                _rows(), _opts(), start_state_id="S0", value_id="V"
            )
            assert proposal is not None
            assert proposal.sequence == ("B",)
            assert proposal.predicted_value_effect < 0.0
            assert proposal.residual_pressure == 0.0
            assert proposal.action_indicated is False
            assert proposal.action_indication_authority == "NONE"

            packet = proposal.serializable()
            assert packet["action_indicated"] is False
            assert packet["action_indication_authority"] == "NONE"
            assert "PROPOSAL_RETURNED != ACTION_INDICATED" in packet["action_indication_rule"]

            status = ms.counterfactual_rehearsal_status(proposal.proposal_id)
            assert status["action_indicated"] is False
            assert status["action_indication_authority"] == "NONE"

            commitment = ms.derive_bounded_action_commitment(proposal.proposal_id)
            assert commitment.commitment.value == "NO"
            assert commitment.reason == "NO_CURRENT_REGULATORY_PRESSURE"
        finally:
            _close(ms)


def test_zero_pressure_pure_rehearsal_can_remain_epistemic_but_not_action_indicated() -> None:
    relations = derive_rehearsal_transition_relations(
        _rows(), CounterfactualRehearsalConfig()
    )
    proposal = propose_counterfactual_rehearsal(
        relations,
        start_state_id="S0",
        start_value=2.5,
        viable_low=2.0,
        viable_high=3.0,
        value_epoch=("V", 0),
        options=_opts(),
        cfg=CounterfactualRehearsalConfig(),
    )
    assert proposal is not None
    assert proposal.action_indicated is False
    assert proposal.action_indication_authority == "NONE"

    packet = proposal.serializable()
    restored = CounterfactualRehearsalProposal.from_serializable(packet)
    assert restored.digest() == proposal.digest()
    assert restored.action_indicated is False


def test_nonzero_pressure_multistep_rehearsal_and_separate_action_commitment_remain() -> None:
    with tempfile.TemporaryDirectory(prefix="ms1939-nonzero-pressure-") as td:
        ms = Microseed(Path(td))
        try:
            _setup_world(ms)
            _set_control_state(ms)
            proposal = ms.nominate_counterfactual_rehearsal(
                _rows(),
                _opts(),
                start_state_id="S0",
                value_id="V",
                config=CounterfactualRehearsalConfig(max_horizon=2),
            )
            assert proposal is not None
            assert proposal.sequence == ("B", "C")
            assert proposal.residual_pressure == 0.0
            assert proposal.authority == Authority.MODEL_OUTPUT_ONLY.value
            assert proposal.execution_authority == Authority.NONE.value
            assert proposal.action_indicated is False

            commitment = ms.derive_bounded_action_commitment(proposal.proposal_id)
            assert commitment.commitment.value == "YES"
            assert commitment.reason == "BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE"
        finally:
            _close(ms)
