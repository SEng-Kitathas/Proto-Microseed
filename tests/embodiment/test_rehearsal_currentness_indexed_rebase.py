from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import inspect
import time
import statistics

from microseed import Authority, Microseed
from microseed.development.action_learning import (
    ActionOutcomeLearningRegistry,
    QualifiedActionOutcomePredictiveRelation,
)


def _relation(relation_id: str, *, next_state: str = "S1", source: str = "E1") -> QualifiedActionOutcomePredictiveRelation:
    return QualifiedActionOutcomePredictiveRelation(
        relation_id=relation_id,
        candidate_id=f"C-{relation_id}",
        candidate_sha256=(relation_id.encode().hex()+"0"*64)[:64],
        start_state_id="S0",
        capability_id="A",
        next_state_id=next_state,
        value_effect=1.0,
        support=4,
        consistency=1.0,
        source_evidence_ids=(source,),
        qualification_evidence_ids=(f"Q-{source}",),
        holdout_support=2,
        holdout_accuracy=1.0,
        capability_epoch=0,
        frame_epochs=(("F",0),),
        episode_schema_epochs=(("EP",0),),
        value_epoch=("V",0),
        authority="EVIDENCE_BOUND_PREDICTIVE_RELATION_ONLY",
        truth_authority="NONE",
        causal_theorem_authority="NONE",
        execution_authority="NONE",
        semantic_goal_authority="NONE",
    )


def _minimal_proposal(digest: str):
    return SimpleNamespace(
        capability_epochs=(), frame_epochs=(), episode_schema_epochs=(), value_epoch=("V",0),
        topology_epochs=(), coordination_epochs=(), evidence_premise_epochs=(), evidence_premise_signatures=(),
        transition_relation_digests=(digest,), sequence=("A",),
        authority=Authority.MODEL_OUTPUT_ONLY.value, truth_authority="NONE", execution_authority="NONE",
        qualification_authority="NONE", semantic_goal_authority="NONE", action_indicated=False,
        action_indication_authority="NONE",
    )


def test_relation_digest_index_rebuild_and_replacement_cleanup_are_exact():
    reg=ActionOutcomeLearningRegistry()
    r1=_relation("R1")
    r2=_relation("R2")
    digest=r1.as_rehearsal_relation().digest()
    assert r2.as_rehearsal_relation().digest()==digest
    reg.add_relation(r1); reg.add_relation(r2)
    assert reg.learned_relation_ids_for_rehearsal_digest(digest)==("R1","R2")

    # Replacing R1 with different rehearsal content removes only its old digest binding.
    r1b=_relation("R1",next_state="S2",source="E2")
    new_digest=r1b.as_rehearsal_relation().digest()
    assert new_digest!=digest
    reg.add_relation(r1b)
    assert reg.learned_relation_ids_for_rehearsal_digest(digest)==("R2",)
    assert reg.learned_relation_ids_for_rehearsal_digest(new_digest)==("R1",)

    # Durable-style replay through the same authoritative add path rebuilds the same index.
    replay=ActionOutcomeLearningRegistry()
    for row in reg.relations.values():
        replay.add_relation(QualifiedActionOutcomePredictiveRelation.from_serializable(row.serializable()))
    assert replay._rehearsal_relation_ids_by_digest==reg._rehearsal_relation_ids_by_digest


def test_proposal_stays_current_when_any_matching_learned_owner_is_current_and_blocks_only_when_all_stale():
    with TemporaryDirectory(prefix="rehearsal-index-currentness-") as td:
        m=Microseed(Path(td))
        try:
            r1=_relation("R1"); r2=_relation("R2")
            digest=r1.as_rehearsal_relation().digest(); assert r2.as_rehearsal_relation().digest()==digest
            m.action_outcome_learning.add_relation(r1); m.action_outcome_learning.add_relation(r2)
            proposal=_minimal_proposal(digest)
            m.counterfactual_rehearsals.proposals["P"]=proposal
            m.values.is_current=lambda vid,epoch: True

            current={"R1":False,"R2":True}
            m._action_outcome_relation_current=lambda r: current[r.relation_id]
            status=m.counterfactual_rehearsal_status("P")
            assert status["status"]=="CURRENT_REHEARSAL_PROPOSAL",status

            current["R2"]=False
            status=m.counterfactual_rehearsal_status("P")
            assert status["status"]=="UNKNOWN_INCOMPLETE",status
            assert status["reason"]=="REHEARSAL_LEARNED_RELATION_NOT_CURRENT:R1,R2"
            assert status["authority"]==Authority.NONE.value
        finally:
            m.biography.close(); m.evidence.conn.close(); m.store.conn.close()


def test_unrelated_stale_learned_relations_do_not_invalidate_proposal_and_status_does_not_scan_all_relations():
    with TemporaryDirectory(prefix="rehearsal-index-selective-") as td:
        m=Microseed(Path(td))
        try:
            target=_relation("TARGET")
            target_digest=target.as_rehearsal_relation().digest()
            m.action_outcome_learning.add_relation(target)
            for i in range(2500):
                m.action_outcome_learning.add_relation(_relation(f"U{i}",next_state=f"U-S{i}",source=f"U-E{i}"))
            m.counterfactual_rehearsals.proposals["P"]=_minimal_proposal(target_digest)
            m.values.is_current=lambda vid,epoch: True
            m._action_outcome_relation_current=lambda r: r.relation_id=="TARGET"

            class NoValuesScanDict(dict):
                def values(self):
                    raise AssertionError("FULL_LEARNED_RELATION_SCAN_FORBIDDEN")
            m.action_outcome_learning.relations=NoValuesScanDict(m.action_outcome_learning.relations)
            status=m.counterfactual_rehearsal_status("P")
            assert status["status"]=="CURRENT_REHEARSAL_PROPOSAL",status
            src=inspect.getsource(Microseed.counterfactual_rehearsal_status)
            assert "action_outcome_learning.relations.values()" not in src
            assert "learned_relation_ids_for_rehearsal_digest" in src
        finally:
            m.biography.close(); m.evidence.conn.close(); m.store.conn.close()


def test_supplied_row_transition_digest_with_no_learned_registry_owner_remains_current():
    with TemporaryDirectory(prefix="rehearsal-index-supplied-") as td:
        m=Microseed(Path(td))
        try:
            m.counterfactual_rehearsals.proposals["P"]=_minimal_proposal("f"*64)
            m.values.is_current=lambda vid,epoch: True
            status=m.counterfactual_rehearsal_status("P")
            assert status["status"]=="CURRENT_REHEARSAL_PROPOSAL",status
        finally:
            m.biography.close(); m.evidence.conn.close(); m.store.conn.close()


def test_digest_lookup_cost_is_history_flat_with_thousands_of_unrelated_relations():
    measurements=[]
    for n in (195,1108,5000,20000):
        reg=ActionOutcomeLearningRegistry()
        target=_relation("TARGET")
        target_digest=target.as_rehearsal_relation().digest()
        reg.add_relation(target)
        for i in range(n):
            reg.add_relation(_relation(f"U{i}",next_state=f"U-S{i}",source=f"U-E{i}"))
        samples=[]
        for _ in range(5000):
            t=time.perf_counter_ns(); ids=reg.learned_relation_ids_for_rehearsal_digest(target_digest); samples.append((time.perf_counter_ns()-t)/1e6)
        assert ids==("TARGET",)
        measurements.append(statistics.median(samples))
    # Ratio threshold, not absolute timing. Lookup must not resemble an O(n) registry scan.
    assert max(measurements) <= max(0.01, min(measurements)*5), measurements


def test_microseed_restart_rebuilds_rehearsal_digest_index_from_qualified_relation_store_event():
    with TemporaryDirectory(prefix="rehearsal-index-restart-") as td:
        root=Path(td)
        m1=Microseed(root)
        try:
            relation=_relation("R-RESTART")
            digest=relation.as_rehearsal_relation().digest()
            m1.action_outcome_learning.add_relation(relation)
            m1.store.append("ACTION_OUTCOME_PREDICTIVE_RELATION_QUALIFIED",relation.serializable())
            assert m1.action_outcome_learning.learned_relation_ids_for_rehearsal_digest(digest)==("R-RESTART",)
        finally:
            m1.biography.close(); m1.evidence.conn.close(); m1.store.conn.close()
        m2=Microseed(root)
        try:
            assert "R-RESTART" in m2.action_outcome_learning.relations
            assert m2.action_outcome_learning.learned_relation_ids_for_rehearsal_digest(digest)==("R-RESTART",)
        finally:
            m2.biography.close(); m2.evidence.conn.close(); m2.store.conn.close()


def test_actual_counterfactual_rehearsal_status_cost_is_flat_vs_unrelated_learned_relation_count():
    medians=[]
    for n in (195,1108,5000):
        with TemporaryDirectory(prefix=f"rehearsal-status-scale-{n}-") as td:
            m=Microseed(Path(td))
            try:
                target=_relation("TARGET")
                digest=target.as_rehearsal_relation().digest()
                m.action_outcome_learning.add_relation(target)
                for i in range(n):
                    m.action_outcome_learning.add_relation(_relation(f"U{i}",next_state=f"S-U-{i}",source=f"E-U-{i}"))
                m.counterfactual_rehearsals.proposals["P"]=_minimal_proposal(digest)
                m.values.is_current=lambda vid,epoch: True
                m._action_outcome_relation_current=lambda r: True
                samples=[]
                for _ in range(1500):
                    t=time.perf_counter_ns(); status=m.counterfactual_rehearsal_status("P"); samples.append((time.perf_counter_ns()-t)/1e6)
                assert status["status"]=="CURRENT_REHEARSAL_PROPOSAL"
                medians.append(statistics.median(samples))
            finally:
                m.biography.close(); m.evidence.conn.close(); m.store.conn.close()
    assert max(medians) <= max(0.05,min(medians)*3), medians
