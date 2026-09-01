
from __future__ import annotations

import copy

from microseed.development.discovery import DiscoveryConfig
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2034_pareto_value_frame_completeness_authority_blocker import derive_strict_pareto_selection_from_vector_rows
from scratch.ms2036_full_frame_bound_pareto_research import (
    _fixture, _tradeoff_effects, _p2_dominates_effects,
    derive_full_frame_bound_cross_value_vectors,
)

CFG=DiscoveryConfig(min_singleton_samples=5,quantization_step=0.5,min_consistency=0.99)


def _surface(effects):
    td,ms,calls,by_probe,witnesses=_fixture(effects)
    return td,ms,calls,derive_full_frame_bound_cross_value_vectors(ms,(by_probe['P2'],by_probe['P4']),witnesses)


def _scale_and_rename(vectors, *, v_scale: float, w_scale: float, rename: dict[str,str]):
    out=copy.deepcopy(vectors)
    for row in out:
        old=row['probe_action_id']
        row['probe_action_id']=rename.get(old,old)
        row['deficit_id']='DEF-'+rename.get(old,old)
        row['worst_residual_by_value']['V']*=v_scale
        row['worst_residual_by_value']['W']*=w_scale
        for branch in row['branches']:
            branch['residual_by_value']['V']*=v_scale
            branch['residual_by_value']['W']*=w_scale
    return tuple(out)


def test_incomparable_full_frame_tradeoff_remains_unselected_under_extreme_positive_coordinate_rescaling_order_reversal_and_label_permutation():
    td,ms,calls,surface=_surface(_tradeoff_effects())
    try:
        assert surface['status']=='CURRENT_FULL_FRAME_BOUND_CROSS_VALUE_VECTORS'
        base=derive_strict_pareto_selection_from_vector_rows(tuple(surface['vectors']))
        assert base['status']=='NO_STRICT_PARETO_SELECTION'
        scaled=_scale_and_rename(surface['vectors'],v_scale=1000.0,w_scale=0.001,rename={'P2':'OPAQUE-Z9','P4':'OPAQUE-A1'})
        hostile=derive_strict_pareto_selection_from_vector_rows(tuple(reversed(scaled)))
        assert hostile['status']=='NO_STRICT_PARETO_SELECTION'
        assert hostile['reason']=='NO_UNIQUE_STRICT_PARETO_DOMINATOR'
        assert hostile['research_selection_authority']=='NONE'
        assert hostile['execution_authority']=='NONE'
        assert calls==[]
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()


def test_strict_full_frame_dominator_survives_extreme_positive_rescaling_order_reversal_and_opaque_renaming_without_execution_authority():
    td,ms,calls,surface=_surface(_p2_dominates_effects())
    try:
        base=derive_strict_pareto_selection_from_vector_rows(tuple(surface['vectors']))
        assert base['status']=='CURRENT_STRICT_PARETO_SELECTION_RESEARCH_ONLY'
        assert base['selected_probe_action_id']=='P2'
        scaled=_scale_and_rename(surface['vectors'],v_scale=0.0001,w_scale=10000.0,rename={'P2':'OPAQUE-Q7','P4':'OPAQUE-X3'})
        hostile=derive_strict_pareto_selection_from_vector_rows(tuple(reversed(scaled)))
        assert hostile['status']=='CURRENT_STRICT_PARETO_SELECTION_RESEARCH_ONLY'
        assert hostile['selected_probe_action_id']=='OPAQUE-Q7'
        assert hostile['research_selection_authority']=='STRICT_PARETO_REGULATORY_DOMINANCE_ONLY'
        assert hostile['execution_authority']=='NONE'
        assert hostile['semantic_value_priority_authority']=='NONE'
        assert calls==[]
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()


def test_runtime_full_frame_owner_abstains_on_tradeoff_and_selects_only_pareto_dominator_read_only():
    td,ms,calls,_,_=_fixture(_tradeoff_effects())
    try:
        before=(len(ms.store.events()),len(ms.action_closure.intents),len(ms.action_closure.executions))
        trade=ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob(),config=CFG)
        after=(len(ms.store.events()),len(ms.action_closure.intents),len(ms.action_closure.executions))
        assert trade['status']=='NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION'
        assert trade['selection_authority']=='NONE' and trade['execution_authority']=='NONE'
        assert before==after and calls==[]
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()
    td,ms,calls,_,_=_fixture(_p2_dominates_effects())
    try:
        dom=ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob(),config=CFG)
        assert dom['status']=='CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION'
        assert dom['selected_probe_action_id']=='P2'
        assert dom['selection_authority']=='STRICT_FULL_FRAME_PARETO_REGULATORY_DOMINANCE_ONLY'
        assert dom['execution_authority']=='NONE'
        assert calls==[]
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()
