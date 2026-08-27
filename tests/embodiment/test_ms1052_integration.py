from __future__ import annotations
from pathlib import Path
import tempfile

from microseed import Microseed
from microseed.persistence.biography import DevelopmentalBiography
from microseed.persistence.identity import continuity_witness_from_exports


def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1052-')
    return td,Microseed(Path(td.name))


def test_typed_continuity_witness_marks_same_graph_as_copy_ambiguous_not_identity():
    td,ms=make_ms()
    try:
        source=ms.biography_witness()
        w=ms.developmental_continuity_witness(source)
        assert w['relation']=='SAME_BIOGRAPHY_STATE'
        assert w['branch_semantics']=='GRAPH_STATE_EQUIVALENT__COPY_AMBIGUOUS'
        assert w['copy_ambiguity'] is True
        assert w['numerical_identity_authority']=='NONE'
        assert w['semantic_self_authority']=='NONE'
        assert w['exclusive_successor_authority']=='NOT_ESTABLISHED_BY_INTERNAL_BIOGRAPHY'
        assert w['selfhood_claim']=='NOT_QUALIFIED'
    finally: td.cleanup()


def test_structural_developmental_event_is_branch_relative_descendant_without_selfhood_gain():
    td,ms=make_ms()
    try:
        source=ms.biography_witness()
        ms.path.append('STRUCTURAL_REWRITE_CONTROL',{'opaque_delta':[1,0,1]})
        w=ms.developmental_continuity_witness(source)
        assert w['relation']=='DESCENDANT_CONTINUATION'
        assert w['branch_semantics']=='BRANCH_RELATIVE_DESCENDANT_CONTINUATION'
        assert w['copy_ambiguity'] is False
        assert w['numerical_identity_authority']=='NONE'
        assert w['selfhood_claim']=='NOT_QUALIFIED'
    finally: td.cleanup()


def test_common_parent_divergent_biographies_are_sibling_branches_not_same_self():
    with tempfile.TemporaryDirectory(prefix='ms1052-a-') as a_dir, tempfile.TemporaryDirectory(prefix='ms1052-b-') as b_dir:
        anchor={'shared':'anchor','historical_biography_before_v0_6':'UNKNOWN_INCOMPLETE'}
        a=DevelopmentalBiography(Path(a_dir)/'bio.sqlite3',legacy_anchor=anchor)
        b=DevelopmentalBiography(Path(b_dir)/'bio.sqlite3',legacy_anchor=anchor)
        a.append('LOCAL_EVENT',{'branch':'A'})
        b.append('LOCAL_EVENT',{'branch':'B'})
        ae,be=a.export(),b.export()
        rel=DevelopmentalBiography.relation(ae,be)
        w=continuity_witness_from_exports(ae,be,relation=rel).serializable()
        assert rel=='COMMON_ANCESTRY_DIVERGED'
        assert w['branch_semantics']=='SIBLING_OR_DIVERGED_BRANCHES'
        assert w['numerical_identity_authority']=='NONE'
        a.close();b.close()


def test_tampered_source_biography_forces_unknown_not_identity_guess():
    td,ms=make_ms()
    try:
        source=ms.biography_witness()
        source['events'][-1]['payload']['tampered']=True
        w=ms.developmental_continuity_witness(source)
        assert w['relation']=='UNKNOWN_INCOMPLETE'
        assert w['branch_semantics']=='UNKNOWN_INCOMPLETE'
        assert w['numerical_identity_authority']=='NONE'
    finally: td.cleanup()


def test_biography_witness_exposes_copy_ceiling_explicitly():
    td,ms=make_ms()
    try:
        w=ms.biography_witness()
        assert w['identity_claim']=='NOT_QUALIFIED'
        assert w['persistent_selfhood']=='NOT_QUALIFIED'
        assert w['numerical_identity_authority']=='NONE'
        assert w['execution_uniqueness_authority']=='NONE'
        assert 'COPY_AMBIGUOUS' in w['same_biography_state_semantics']
    finally: td.cleanup()


def test_no_internal_exclusive_successor_or_selfhood_api_is_promoted():
    td,ms=make_ms()
    try:
        for name in ('claim_unique_identity','claim_selfhood','select_original_copy','grant_exclusive_successor_authority','self_qualify_identity'):
            assert not hasattr(ms,name)
        assert ms.status()['exclusive_successor_authority']=='NOT_ESTABLISHED_BY_INTERNAL_BIOGRAPHY'
    finally: td.cleanup()


def test_ms1052_selected_frontier_and_ms1053_hard_stop():
    td,ms=make_ms()
    try:
        s=ms.status()
        assert s['research_terminal_ms']>=1152
        assert s['integration_evidence_through_ms']>=1152
        assert s['next_ms']>=1203
        assert s['next_ms'] >= 1278
        assert s['frontier'].startswith('ATTN-MS')
        assert s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
        assert s['identity_claim']=='NOT_QUALIFIED'
        assert 'BRANCH_RELATIVE_DEVELOPMENTAL_CONTINUITY' in s['persistent_identity']
    finally: td.cleanup()
