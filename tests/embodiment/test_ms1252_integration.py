from pathlib import Path
import hashlib
import itertools
import tempfile
import pytest

from microseed import (
    Microseed, Authority, EpistemicStatus, QualificationState,
    OperationalFrameContract, EpisodeSchemaContract,
    ConstructorProjectionSample, ConstructorGrowthConfig,
    ExternalConstructorQualifier, EpistemicContrastBinding, EpistemicContrastRow,
)


def H(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def new(*, episode=False):
    td = tempfile.TemporaryDirectory(prefix="microseed-ms1252-")
    m = Microseed(Path(td.name))
    m.register_operational_frame(OperationalFrameContract(
        frame_id="F", purpose="opaque-raw-action-effect-boundary", signature_sha256=H("frame-v0"),
        authority=Authority.DERIVED_READ_ONLY, lineage=("MS1228-1252",), currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXTERNAL_FRAME_QUALIFICATION",),
        invariants=("NO_SEMANTIC_FEATURE_AUTHORITY",),
    ))
    if episode:
        m.register_episode_schema(EpisodeSchemaContract(
            schema_id="EPS", purpose="opaque-history-window", signature_sha256=H("episode-v0"),
            authority=Authority.DERIVED_READ_ONLY, lineage=("MS1228-1252",), currentness="CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            assistance_ancestry=("EXTERNAL_EPISODE_SCHEMA_QUALIFICATION",),
            frame_epochs=(("F", 0),),
            invariants=("NO_SEMANTIC_TIME_AUTHORITY",),
        ))
    return td, m


def triple_rows(prefix: str, *, dim=8, true=(1, 4, 6)):
    out = []
    i = 0
    for bits in itertools.product("01", repeat=dim):
        for action in ("a0", "a1"):
            p = 0
            for j in true:
                p ^= int(bits[j])
            y = p ^ (action == "a1")
            out.append(ConstructorProjectionSample(
                f"{prefix}-{i}", (tuple(bits),), action, f"e{int(y)}", f"r{i % 3}", "F", 0,
            ))
            i += 1
    return out


def temporal_rows(prefix: str, *, dim=4, cur=2, prev=1):
    out = []
    i = 0
    for now in itertools.product("01", repeat=dim):
        for old in itertools.product("01", repeat=dim):
            for action in ("a0", "a1"):
                y = int(now[cur]) ^ int(old[prev]) ^ (action == "a1")
                out.append(ConstructorProjectionSample(
                    f"{prefix}-{i}", (tuple(now), tuple(old)), action, f"e{int(y)}", f"r{i % 2}",
                    "F", 0, "EPS", 0,
                ))
                i += 1
    return out


def triple_discover(m, *, ceiling=4, budget=20000):
    cfg = ConstructorGrowthConfig(
        max_support_ceiling=ceiling, max_lag_ceiling=0, min_train_support=100,
        min_validation_accuracy=.99, min_lift_over_action_baseline=.40, min_scope_accuracy=.99,
        node_budget=budget,
    )
    return m.discover_epistemic_constructor_candidates(
        triple_rows("tr"), triple_rows("pr"), triple_rows("va"), cfg
    )


def temporal_discover(m, *, max_lag=1):
    cfg = ConstructorGrowthConfig(
        max_support_ceiling=3, max_lag_ceiling=max_lag, min_train_support=100,
        min_validation_accuracy=.99, min_lift_over_action_baseline=.40, min_scope_accuracy=.99,
    )
    return m.discover_epistemic_constructor_candidates(
        temporal_rows("tr"), temporal_rows("pr"), temporal_rows("va"), cfg
    )


def ticket(m, cid, eid="Q"):
    ev = m.append_evidence(
        eid, {"heldout_accuracy": 1.0, "independent_scope": True},
        EpistemicStatus.PRESSURE_SUPPORTED, source="HSP_EXTERNAL_MS1252",
    )
    return ExternalConstructorQualifier(m.evidence, qualifier_id="HSP-MS1252").qualify(
        m.epistemic_constructor_candidates[cid], qualification_evidence=(ev,)
    )


def test_conflict_directed_growth_recovers_triple_without_exact_degree_selection():
    td, m = new()
    try:
        found = triple_discover(m)
        assert found
        c = m.epistemic_constructor_candidates[found[0]["candidate_id"]]
        assert tuple((a.lag, a.position) for a in c.atoms) == ((0, 1), (0, 4), (0, 6))
        assert c.validation_accuracy == 1.0
        assert c.lag_depth_used == 0
        assert "SUPPLIED_SUPPORT_CEILING_4" in c.assistance_ancestry
        assert c.proposal_authority == c.qualification_authority == "NONE"
        assert c.semantic_projection_authority == c.truth_authority == "NONE"
    finally:
        td.cleanup()


def test_support_ceiling_below_required_order_abstains_instead_of_faking_proxy():
    td, m = new()
    try:
        assert triple_discover(m, ceiling=2) == []
    finally:
        td.cleanup()


def test_temporal_coordinate_is_reached_only_after_present_state_failure():
    td, m = new(episode=True)
    try:
        assert temporal_discover(m, max_lag=0) == []
        found = temporal_discover(m, max_lag=1)
        assert found
        c = m.epistemic_constructor_candidates[found[0]["candidate_id"]]
        assert tuple((a.lag, a.position) for a in c.atoms) == ((0, 2), (1, 1))
        assert c.episode_schema_epochs == (("EPS", 0),)
        assert c.frame_epochs == (("F", 0),)
        assert c.validation_accuracy == 1.0
        assert "SUPPLIED_HISTORY_WINDOW_MAX_LAG_1" in c.assistance_ancestry
    finally:
        td.cleanup()


def test_temporal_samples_require_explicit_episode_schema_ancestry():
    with pytest.raises(ValueError, match="TEMPORAL_CONSTRUCTOR_SAMPLE_REQUIRES_EPISODE_SCHEMA_CURRENTNESS"):
        ConstructorProjectionSample(
            "s", (("0", "1"), ("1", "0")), "a0", "e0", None, "F", 0,
        )


def test_stale_episode_schema_blocks_temporal_search_before_candidate_nomination():
    td, m = new(episode=True)
    try:
        rows = temporal_rows("x")
        m.change_episode_schema("EPS", reason="GROUPING_DRIFT")
        with pytest.raises(ValueError, match="STALE_OR_UNKNOWN_CONSTRUCTOR_SAMPLE_EPISODE_SCHEMA"):
            m.discover_epistemic_constructor_candidates(rows, rows, rows, ConstructorGrowthConfig(max_lag_ceiling=1))
    finally:
        td.cleanup()


def test_external_qualification_required_and_admission_preserves_constructor_ancestry():
    td, m = new()
    try:
        found = triple_discover(m); cid = found[0]["candidate_id"]
        c = m.epistemic_constructor_candidates[cid]
        bad = ExternalConstructorQualifier(m.evidence, qualifier_id="HSP-MS1252").qualify(c, qualification_evidence=())
        with pytest.raises(ValueError, match="NOT_ADMISSIBLE|NO_QUALIFICATION_EVIDENCE"):
            m.admit_epistemic_constructor_candidate(bad, projection_id="P")
        rec = m.admit_epistemic_constructor_candidate(ticket(m, cid), projection_id="P")
        assert rec.projection_origin == "ENDOGENOUS_CONSTRUCTOR_GROWTH_EXTERNALLY_QUALIFIED"
        assert rec.proposal_candidate_sha256 == c.digest()
        assert rec.qualification_evidence_ids == ("Q",)
        assert rec.frame_epochs == (("F", 0),)
        assert rec.episode_schema_epochs == ()
        assert rec.discovery_authority == rec.semantic_projection_authority == "NONE"
    finally:
        td.cleanup()


def test_candidate_nomination_restarts_without_qualification_gain():
    td, m = new()
    try:
        found = triple_discover(m); cid = found[0]["candidate_id"]
        sig = m.epistemic_constructor_candidates[cid].digest()
        root = Path(td.name); del m
        m2 = Microseed(root)
        assert cid in m2.epistemic_constructor_candidates
        c = m2.epistemic_constructor_candidates[cid]
        assert c.digest() == sig
        assert c.qualification_authority == "NONE"
        assert cid not in m2.epistemic_projections.records
    finally:
        td.cleanup()


def test_post_admission_frame_drift_invalidates_projection_and_bound_contrast():
    td, m = new()
    try:
        found = triple_discover(m); cid = found[0]["candidate_id"]
        rec = m.admit_epistemic_constructor_candidate(ticket(m, cid), projection_id="P")
        u = m.append_evidence("U", {"opaque": True}, EpistemicStatus.UNKNOWN_INCOMPLETE, source="MS1252")
        d = m.record_action_limited_unknown(
            deficit_id="D", question_key="opaque", hypothesis_digest_sha256=H("hyp"),
            unknown_evidence_id=u.evidence_id, missing_discriminator_signature_sha256=H("missing"),
        )
        b = EpistemicContrastBinding(
            "B", "D", d.hypothesis_digest_sha256,
            (EpistemicContrastRow("P", rec.epoch, (("h0", H("e0")), ("h1", H("e1")))),),
            assistance_ancestry=("BOUND_TO_CONSTRUCTOR_PROJECTION",),
        )
        m.register_epistemic_contrast(b)
        m.change_operational_frame("F", reason="RAW_BOUNDARY_CHANGED")
        rec2 = m.epistemic_projections.records["P"]
        assert rec2.current is False and rec2.epoch == 1
        assert m.epistemic_contrasts.bindings["B"].state == "STALE"
        assert "PROJECTION_DRIFT:P@1" in m.epistemic_contrasts.bindings["B"].stale_reason
    finally:
        td.cleanup()


def test_post_admission_episode_drift_invalidates_temporal_projection():
    td, m = new(episode=True)
    try:
        found = temporal_discover(m); cid = found[0]["candidate_id"]
        rec = m.admit_epistemic_constructor_candidate(ticket(m, cid), projection_id="TP")
        assert rec.episode_schema_epochs == (("EPS", 0),) and rec.current
        m.change_episode_schema("EPS", reason="TEMPORAL_GROUPING_CHANGED")
        rec2 = m.epistemic_projections.records["TP"]
        assert rec2.current is False and rec2.epoch == 1
    finally:
        td.cleanup()


def test_admitted_constructor_projection_feeds_existing_bearing_without_truth_or_answer_authority():
    td, m = new()
    try:
        found = triple_discover(m); cid = found[0]["candidate_id"]
        m.admit_epistemic_constructor_candidate(ticket(m, cid), projection_id="P")
        u = m.append_evidence("U", {"opaque": True}, EpistemicStatus.UNKNOWN_INCOMPLETE, source="MS1252")
        d = m.record_action_limited_unknown(
            deficit_id="D", question_key="opaque", hypothesis_digest_sha256=H("hyp"),
            unknown_evidence_id=u.evidence_id, missing_discriminator_signature_sha256=H("missing"),
        )
        m.register_epistemic_contrast(EpistemicContrastBinding(
            "B", "D", d.hypothesis_digest_sha256,
            (EpistemicContrastRow("P", 0, (("h0", H("e0")), ("h1", H("e1")))),),
            assistance_ancestry=("BOUND_AFTER_EXTERNAL_QUALIFICATION",),
        ))
        e = m.append_evidence(
            "E", {"epistemic_projection": {"projection_id": "P", "projection_epoch": 0, "outcome_digest_sha256": H("e1")}},
            EpistemicStatus.PRESSURE_SUPPORTED, source="MS1252",
        )
        r = m.assess_epistemic_evidence_bearing("D", "B", e.evidence_id)
        assert r["bearing_kind"] == "DISCRIMINATES_LIVE_SET"
        assert r["state"] == "REVISIT_REQUIRED"
        assert r["truth_authority"] == r["answer_authority"] == "NONE"
    finally:
        td.cleanup()


def test_bounded_budget_exhaustion_abstains():
    td, m = new()
    try:
        assert triple_discover(m, budget=2) == []
    finally:
        td.cleanup()


def test_ms1252_status_and_ms1253_hard_stop_and_nonpromotions():
    td, m = new()
    try:
        s = m.status()
        assert s["embodiment"].startswith("PROTO_MICROSEED_MAINDEV_INTEGRATION_V")
        assert s["research_terminal_ms"] >= 1252 and s["integration_evidence_through_ms"] >= 1252
        assert s["next_ms"] >= 1278
        assert s["frontier"].startswith("ATTN-MS")
        assert "EXACT_HYPERGRAPH_PATH" in s["projection_constructor_growth"]
        assert "NO_EFFECT_METRIC_OR_NOISE_RATE_MODEL" in s["projection_constructor_growth"]
        assert not hasattr(m, "qualify_epistemic_constructor_candidate")
        assert not hasattr(m, "discover_general_projection_constructor")
        assert not hasattr(m, "discover_noise_tolerant_projection_constructor")
        assert s["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally:
        td.cleanup()
