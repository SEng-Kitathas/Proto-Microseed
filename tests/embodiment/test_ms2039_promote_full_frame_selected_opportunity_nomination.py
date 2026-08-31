from microseed import EpistemicStatus
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2035_organism_owned_current_value_frame_completeness import _contract
from scratch.ms2036_full_frame_bound_pareto_research import _fixture, _p2_dominates_effects, _tradeoff_effects


def test_ms2039_tradeoff_abstains_without_durable_state():
    td, ms, calls, *_ = _fixture(_tradeoff_effects())
    try:
        before = (len(ms.epistemic_deficits.records), len(ms.action_closure.intents), len(ms.action_closure.executions))
        r = ms.nominate_current_strict_full_frame_referent_epistemic_opportunity(act_ob())
        after = (len(ms.epistemic_deficits.records), len(ms.action_closure.intents), len(ms.action_closure.executions))
        assert r["status"] == "ABSTAIN", r
        assert r["reason"] == "NO_UNIQUE_STRICT_PARETO_DOMINATOR", r
        assert before == after
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def test_ms2039_dominance_materializes_one_unknown_deficit_and_intent_without_execution():
    td, ms, calls, *_ = _fixture(_p2_dominates_effects())
    try:
        r = ms.nominate_current_strict_full_frame_referent_epistemic_opportunity(act_ob())
        assert r["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", r
        assert r["selected_probe_action_id"] == "P2"
        assert r["deficit_delta"] == 1 and r["intent_delta"] == 1 and r["execution_delta"] == 0
        ev = ms.evidence.get(r["unknown_evidence_id"])
        assert ev is not None
        assert ev["disposition"] == EpistemicStatus.UNKNOWN_INCOMPLETE.value
        assert ev["source"] == "MICROSEED_ENDOGENOUS_SELECTED_FULL_FRAME_EPISTEMIC_OPPORTUNITY"
        payload = ev["payload"]
        assert payload["kind"] == "SELECTED_OWNED_REFERENT_FULL_FRAME_EPISTEMIC_UNKNOWN"
        assert payload["cross_deficit_selection_authority"] == "STRICT_FULL_FRAME_PARETO_REGULATORY_DOMINANCE_ONLY"
        assert payload["complete_value_frame_digest_sha256"] == r["selection_surface"]["complete_value_frame"]["frame_digest_sha256"]
        deficit = ms.epistemic_deficits.records[r["selected_deficit_id"]]
        assert "ENDOGENOUS_UNKNOWN_MATERIALIZED_AFTER_STRICT_FULL_FRAME_PARETO_SELECTION" in deficit.assistance_ancestry
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def test_ms2039_idempotent_second_nomination_and_incomplete_frame_abstain():
    td, ms, calls, *_ = _fixture(_p2_dominates_effects())
    try:
        first = ms.nominate_current_strict_full_frame_referent_epistemic_opportunity(act_ob())
        second = ms.nominate_current_strict_full_frame_referent_epistemic_opportunity(act_ob())
        assert first["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED"
        assert second["status"] == "ABSTAIN"
        assert second["reason"] == "SELECTED_EPISTEMIC_DEFICIT_ALREADY_PERSISTED"
        assert second["deficit_delta"] == second["intent_delta"] == second["execution_delta"] == 0
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()

    td, ms, calls, *_ = _fixture(_p2_dominates_effects())
    try:
        ms.register_value_variable(_contract("X"))
        r = ms.nominate_current_strict_full_frame_referent_epistemic_opportunity(act_ob())
        assert r["status"] == "ABSTAIN", r
        assert r["reason"] == "CURRENT_VALUE_FRAME_OBSERVATION_MISSING:X"
        assert r["deficit_delta"] == r["intent_delta"] == r["execution_delta"] == 0
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def test_ms2039_historical_same_value_nomination_path_remains_available():
    td, ms, calls, *_ = _fixture(_tradeoff_effects())
    try:
        old = ms.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
        assert old["status"] in {"ABSTAIN", "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", "SELECTED_OPPORTUNITY_PERSISTED_BUT_NOT_NOMINATED"}
        assert old["execution_authority"] == "NONE"
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()
