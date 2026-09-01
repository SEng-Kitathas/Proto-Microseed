
from __future__ import annotations

from pathlib import Path
import tempfile

from microseed import Authority, CapabilityContract, Microseed, QualificationState, QueryObligation


def _obl():
    return QueryObligation('ACT-SH7', 'opaque action', required_authority=Authority.EFFECT, operational_scope_id='SH7-S')


def _cap(calls):
    return CapabilityContract(
        'SH7-PING', 'opaque current action', {}, {}, (), (), Authority.EFFECT,
        ('MS_SUBSTRATE_HARDENING_V1:SH7',), 'CURRENT', {},
        query_obligation_id='ACT-SH7', qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: calls.append('SH7-PING') or {'receipt':'same-current-action'},
        operational_scope_id='SH7-S',
    )


def _make(branch_events=()):
    td = tempfile.TemporaryDirectory(prefix='hardening-sh7-history-')
    calls = []
    ms = Microseed(Path(td.name))
    ms.register_capability(_cap(calls))
    for label in branch_events:
        ms.path.append('SH7_HISTORY_ONLY_EVENT', {'branch_label': label, 'current_operational_delta': 'NONE'})
    return td, ms, calls


def _close(td, ms):
    try:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    finally:
        td.cleanup()


def _operational_fingerprint(ms):
    return {
        'capability_ids': tuple(sorted(ms.capabilities.contracts)),
        'capability_epochs': tuple(sorted(ms.capabilities.epochs.items())),
        'capability_signatures': tuple(sorted((cid, c.computed_signature_sha256()) for cid, c in ms.capabilities.contracts.items())),
        'capability_current': tuple(sorted((cid, ms.capabilities.is_current(cid)) for cid in ms.capabilities.contracts)),
    }


def test_matched_current_operational_state_can_have_descendant_history_without_identity_or_action_preference():
    td_a, a, calls_a = _make(())
    td_b, b, calls_b = _make(('extra-history',))
    try:
        assert _operational_fingerprint(a) == _operational_fingerprint(b)
        ra = a.capabilities.invoke('SH7-PING', _obl())
        rb = b.capabilities.invoke('SH7-PING', _obl())
        assert ra['status'] == rb['status'] == 'CAPABILITY_RESULT'
        assert ra.get('value') == rb.get('value')
        assert calls_a == calls_b == ['SH7-PING']
        w = b.developmental_continuity_witness(a.biography_witness())
        assert w['relation'] == 'DESCENDANT_CONTINUATION', w
        assert w['branch_semantics'] == 'BRANCH_RELATIVE_DESCENDANT_CONTINUATION'
        assert w['numerical_identity_authority'] == 'NONE'
        assert w['semantic_self_authority'] == 'NONE'
        assert w['exclusive_successor_authority'] == 'NOT_ESTABLISHED_BY_INTERNAL_BIOGRAPHY'
        assert w['selfhood_claim'] == 'NOT_QUALIFIED'
    finally:
        _close(td_a, a); _close(td_b, b)


def test_matched_current_operational_state_with_sibling_histories_stays_copy_ambiguous_not_self_selection():
    td_a, a, calls_a = _make(('left-only',))
    td_b, b, calls_b = _make(('right-only',))
    try:
        assert _operational_fingerprint(a) == _operational_fingerprint(b)
        wa = a.biography_witness(); wb = b.biography_witness()
        assert wa['graph_digest'] != wb['graph_digest']
        w = b.developmental_continuity_witness(wa)
        assert w['relation'] == 'COMMON_ANCESTRY_DIVERGED', w
        assert w['branch_semantics'] == 'SIBLING_OR_DIVERGED_BRANCHES'
        assert w['numerical_identity_authority'] == 'NONE'
        assert w['semantic_self_authority'] == 'NONE'
        assert w['exclusive_successor_authority'] == 'NOT_ESTABLISHED_BY_INTERNAL_BIOGRAPHY'
        assert not hasattr(b, 'select_original_copy')
        assert not hasattr(b, 'claim_selfhood')
        assert not hasattr(b, 'rank_successor_by_biography')
        assert a.capabilities.invoke('SH7-PING', _obl())['status'] == b.capabilities.invoke('SH7-PING', _obl())['status'] == 'CAPABILITY_RESULT'
    finally:
        _close(td_a, a); _close(td_b, b)


def test_identical_biography_graph_is_explicit_copy_ambiguity_even_with_matched_current_operational_surface():
    td_a, a, calls_a = _make(())
    td_b, b, calls_b = _make(())
    try:
        assert _operational_fingerprint(a) == _operational_fingerprint(b)
        w = b.developmental_continuity_witness(a.biography_witness())
        assert w['relation'] == 'SAME_BIOGRAPHY_STATE', w
        assert w['branch_semantics'] == 'GRAPH_STATE_EQUIVALENT__COPY_AMBIGUOUS'
        assert w['copy_ambiguity'] is True
        assert w['numerical_identity_authority'] == 'NONE'
        assert w['selfhood_claim'] == 'NOT_QUALIFIED'
        assert a.biography_witness()['same_biography_state_semantics'] == 'GRAPH_STATE_EQUIVALENCE__COPY_AMBIGUOUS_NOT_NUMERICAL_IDENTITY'
    finally:
        _close(td_a, a); _close(td_b, b)
