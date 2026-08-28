from __future__ import annotations

from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext,
    derive_program_observable_partition,
    derive_program_observable_trace_signature,
    program_partition_strictly_refines,
)
from microseed.development.epistemic_program import EpistemicProgramTrial, GeneratedEpistemicProgramCandidate
from microseed.development.rehearsal import RehearsalTransitionRelation


def _rel(s: str, a: str, n: str, evidence: str):
    return RehearsalTransitionRelation(
        state_id=s,capability_id=a,next_state_id=n,value_effect=0.0,
        support=2,consistency=1.0,source_evidence_ids=(evidence,),capability_epoch=0,
        frame_epoch=('F',0),episode_schema_epoch=('EP',0),value_epoch=('V',0),
    )


def _trial(candidate: GeneratedEpistemicProgramCandidate):
    return EpistemicProgramTrial(
        trial_id='T-'+candidate.candidate_id,deficit_id='D',discrimination_signature_sha256='d'*64,
        relation_candidate_id=candidate.candidate_id,relation_candidate_sha256=candidate.digest(),
        steps=candidate.steps,capability_epochs=tuple((s,0) for s in candidate.steps),
        capability_signatures=tuple((s,'c'*64) for s in candidate.steps),frame_epochs=(('F',0),),
        obligation_id='Q',operational_scope_id='S',start_state_id='S0',start_state_evidence_id='E0',
        source_relation_digests=candidate.source_relation_digests,
    )


def _fixture():
    # ABC and XYZ are physically different action words but have the exact same
    # represented visible-state trace under both alternatives.
    a0=(
        _rel('S0','A','S1','E-A0'),_rel('S1','B','S2','E-B0'),_rel('S2','C','P','E-C0'),
        _rel('S0','X','S1','E-X0'),_rel('S1','Y','S2','E-Y0'),_rel('S2','Z','P','E-Z0'),
    )
    a1=(
        _rel('S0','A','S1','E-A1'),_rel('S1','B','S2','E-B1'),_rel('S2','C','Q','E-C1'),
        _rel('S0','X','S1','E-X1'),_rel('S1','Y','S2','E-Y1'),_rel('S2','Z','Q','E-Z1'),
    )
    dc=EpistemicDecisionBearingContext((a0,a1),())
    all_digests=tuple(sorted({r.digest() for rows in dc.relation_sets for r in rows}))
    abc=GeneratedEpistemicProgramCandidate('G-ABC',('A','B','C'),all_digests,(('F',0),))
    xyz=GeneratedEpistemicProgramCandidate('G-XYZ',('X','Y','Z'),all_digests,(('F',0),))
    return dc,abc,xyz


def test_ranger1_different_program_words_can_have_identical_observable_trace_signature_and_partition():
    dc,abc,xyz=_fixture(); ta,tb=_trial(abc),_trial(xyz)
    sig_a=derive_program_observable_trace_signature(trial=ta,decision_context=dc)
    sig_b=derive_program_observable_trace_signature(trial=tb,decision_context=dc)
    part_a=derive_program_observable_partition(trial=ta,decision_context=dc)
    part_b=derive_program_observable_partition(trial=tb,decision_context=dc)
    assert abc.steps!=xyz.steps
    assert sig_a==sig_b==(('S1','S2','P'),('S1','S2','Q'))
    assert part_a==part_b==((0,),(1,))


def test_ranger2_equal_trace_and_partition_do_not_collapse_candidate_or_trial_identity():
    dc,abc,xyz=_fixture(); ta,tb=_trial(abc),_trial(xyz)
    assert derive_program_observable_trace_signature(trial=ta,decision_context=dc)==derive_program_observable_trace_signature(trial=tb,decision_context=dc)
    assert abc.digest()!=xyz.digest()
    assert abc.candidate_id!=xyz.candidate_id
    assert ta.digest()!=tb.digest()
    assert ta.steps!=tb.steps
    assert ta.relation_candidate_id!=tb.relation_candidate_id


def test_ranger3_equal_information_partitions_cannot_create_strict_refinement_selection_authority():
    dc,abc,xyz=_fixture(); ta,tb=_trial(abc),_trial(xyz)
    pa=derive_program_observable_partition(trial=ta,decision_context=dc)
    pb=derive_program_observable_partition(trial=tb,decision_context=dc)
    assert pa==pb
    assert not program_partition_strictly_refines(pa,pb)
    assert not program_partition_strictly_refines(pb,pa)


def test_ranger4_representation_equivalence_grants_no_program_authority():
    dc,abc,xyz=_fixture(); ta,tb=_trial(abc),_trial(xyz)
    assert derive_program_observable_trace_signature(trial=ta,decision_context=dc)==derive_program_observable_trace_signature(trial=tb,decision_context=dc)
    assert ta.truth_authority==ta.execution_authority==ta.qualification_authority=='NONE'
    assert tb.truth_authority==tb.execution_authority==tb.qualification_authority=='NONE'
