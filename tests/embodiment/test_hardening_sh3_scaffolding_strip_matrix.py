
from __future__ import annotations

import itertools
import random
import tempfile
from pathlib import Path

from microseed import (
    Authority, Microseed, Observation, OperationalFrameContract,
    ProjectionDiscoveryConfig, ProjectionSample, QualificationState,
)
from scratch.ms1996_endogenous_program_caller_choice_elimination import (
    fixture as program_fixture, _register_effect_and_feasibility, MAIN, FALLBACK, OBLIGATION, _close as close_program,
)
from scratch.ms2036_full_frame_bound_pareto_research import run_ms2036
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _build as language_build, derive_binding_candidate
from tests.embodiment.test_ms2055_n1a_constitutional_experimental_authority import _cap as n1a_cap, _obligation as n1a_obligation


def test_no_lived_program_history_does_not_get_replaced_by_capability_names_or_registry_order():
    td,m,calls,_,_,_=program_fixture()
    try:
        for cid in MAIN+(FALLBACK,):
            _register_effect_and_feasibility(m,calls,cid)
        m.observe_opaque_control_state(
            Observation('SH3-PROG','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-SH3-PROG',
        )
        before=(len(m.action_closure.intents),len(m.action_closure.executions))
        out=m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(obligation=OBLIGATION,max_nodes=64)
        after=(len(m.action_closure.intents),len(m.action_closure.executions))
        assert out['status']=='ABSTAIN'
        assert out['reason']=='NO_COHERENT_THREE_LOCUS_CHAIN_MODEL_SURFACE'
        assert out['truth_authority']==out['execution_authority']=='NONE'
        assert before==after and calls==[]
    finally: close_program(td,m)


def test_n1a_without_constitutional_value_frame_does_not_turn_unknownness_into_permission():
    td=tempfile.TemporaryDirectory(prefix='hardening-sh3-n1a-');ms=Microseed(Path(td.name));calls=[]
    try:
        ms.register_capability(n1a_cap('A',calls))
        ms.observe_opaque_control_state(Observation('CTRL','EXT','control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CTRL-SH3')
        out=ms.derive_n1a_experimental_warrant(n1a_obligation())
        assert out['status']=='ABSTAIN'
        assert out['reason']=='COMPLETE_CURRENT_VALUE_FRAME_REQUIRED'
        assert out['execution_authority']=='NONE'
        assert calls==[]
    finally:
        try:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
        finally:td.cleanup()


def test_ungrounded_readable_or_arbitrary_token_does_not_get_reference_from_surface_form():
    td=tempfile.TemporaryDirectory(prefix='hardening-sh3-lang-');ms,world=language_build(Path(td.name))
    try:
        readable=derive_binding_candidate(ms,(),(),signal_id='hello')
        assert readable['status']=='DEFER_UNKNOWN'
        assert readable['reason']=='SUFFICIENT_GROUNDED_USE_HISTORY_REQUIRED'
        for key in ('semantic_reference_authority','token_meaning_authority','truth_authority','execution_authority','language_authority'):
            assert readable[key]=='NONE'
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()


def test_incomplete_current_value_frame_does_not_get_completed_by_hidden_scalar_or_caller_subset():
    r=run_ms2036()
    missing=r['missing_observation']['surface']
    assert missing['status']=='DEFER_UNKNOWN'
    # The lawful API itself has no caller-selected value-frame parameter.
    assert r['api_scope']['caller_frame_parameter']=='ABSENT'
    assert r['runtime_selection_authorized']=='NO'


def _terrain_ms(td):
    ms=Microseed(Path(td.name))
    ms.register_operational_frame(OperationalFrameContract(
        'F','hardening-sh3-frame','f'*64,Authority.DERIVED_READ_ONLY,('MS_SUBSTRATE_HARDENING_V1:SH3',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    return ms


def _rows():
    out=[];idx=0
    for r in range(24):
        combos=list(itertools.product(('0','1'),repeat=3));random.Random(8810+r).shuffle(combos)
        for x,y,z in combos:
            out.append(ProjectionSample(f'SH3-{idx}',(x,z),'B','E1' if x!=y else 'E0','S','F',0));idx+=1
    return tuple(out)


def test_matched_but_noncausal_visibility_does_not_get_promoted_into_a_projection_because_a_causal_relation_exists_off_surface():
    td=tempfile.TemporaryDirectory(prefix='hardening-sh3-terrain-');ms=_terrain_ms(td)
    try:
        rows=_rows();train=rows[:128];validation=rows[128:]
        found=ms.discover_epistemic_projection_candidates(
            train,validation,ProjectionDiscoveryConfig(
                max_subset=2,min_train_support=96,min_key_action_support=8,
                min_validation_accuracy=.95,min_lift_over_action_baseline=.35,
                min_scope_accuracy=.95,max_candidates=4,
            )
        )
        assert found==[]
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()
