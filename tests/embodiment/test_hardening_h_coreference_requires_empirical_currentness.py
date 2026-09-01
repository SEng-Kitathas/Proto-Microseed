
from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import (
    _build,
    _cap,
    _use_episode,
    bounded_operational_coreference_status,
    derive_binding_candidate,
    empirical_binding_currentness_status,
)


def _register_token(ms, world, token_id: str, physical_action: str):
    ms.register_capability(
        _cap(token_id, Authority.EFFECT, lambda _action=physical_action, **_: world.act(_action)),
        coordination_dependencies=(('COORD-X', 0),),
    )


def _ground(ms, world, token_id: str, base: int, *, mode: str = 'P'):
    world.configure_alias(False); world.configure_signal_mode(mode); world.configure_layout('A')
    train = tuple(_use_episode(ms, world, token_id, base + i) for i in range(10))
    world.configure_layout('B')
    hold = tuple(_use_episode(ms, world, token_id, base + 100 + i) for i in range(6))
    c = derive_binding_candidate(ms, train, hold, signal_id=token_id)
    assert c['status'] == 'QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE', c
    return c, train, hold


def _fresh(ms, world, token_id: str, base: int, *, mode: str = 'P'):
    world.configure_alias(False); world.configure_signal_mode(mode); world.configure_layout('A')
    train = tuple(_use_episode(ms, world, token_id, base + i) for i in range(10))
    world.configure_layout('B')
    hold = tuple(_use_episode(ms, world, token_id, base + 100 + i) for i in range(6))
    return train, hold


def _close(ms, td):
    try:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    finally:
        td.cleanup()


def test_query_local_coreference_passes_only_when_both_bindings_are_empirically_current():
    td = tempfile.TemporaryDirectory(prefix='hardening-h-emp-coref-'); ms, world = _build(Path(td.name))
    try:
        _register_token(ms, world, 'TOK-A', 'SIG-X'); _register_token(ms, world, 'TOK-B', 'SIG-X')
        a, _, _ = _ground(ms, world, 'TOK-A', 1000, mode='P')
        b, _, _ = _ground(ms, world, 'TOK-B', 2000, mode='P')
        af = _fresh(ms, world, 'TOK-A', 3000, mode='P')
        bf = _fresh(ms, world, 'TOK-B', 4000, mode='P')
        out = bounded_operational_coreference_status(ms, a, b, af[0], af[1], bf[0], bf[1])
        assert out['status'] == 'CURRENT_BOUNDED_OPERATIONAL_COREFERENCE_CANDIDATE', out
        assert out['left_status']['status'] == out['right_status']['status'] == 'CURRENT_EMPIRICALLY_GROUNDED_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert out['durable_coreference_registry_warranted'] is False
        assert out['semantic_reference_authority'] == out['numerical_identity_authority'] == out['truth_authority'] == out['execution_authority'] == out['language_authority'] == 'NONE'
    finally:
        _close(ms, td)


def test_external_reversal_blocks_old_query_local_coreference_even_when_structural_binding_descriptors_remain_current():
    td = tempfile.TemporaryDirectory(prefix='hardening-h-emp-coref-reversal-'); ms, world = _build(Path(td.name))
    try:
        _register_token(ms, world, 'TOK-A', 'SIG-X'); _register_token(ms, world, 'TOK-B', 'SIG-X')
        a, _, _ = _ground(ms, world, 'TOK-A', 5000, mode='P')
        b, _, _ = _ground(ms, world, 'TOK-B', 6000, mode='P')
        af = _fresh(ms, world, 'TOK-A', 7000, mode='Q')
        bf = _fresh(ms, world, 'TOK-B', 8000, mode='P')
        out = bounded_operational_coreference_status(ms, a, b, af[0], af[1], bf[0], bf[1])
        assert out['status'] == 'DEFER_UNKNOWN', out
        assert out['reason'] == 'BOTH_GROUNDED_BINDINGS_MUST_BE_EMPIRICALLY_CURRENT'
        assert out['left_status']['status'] == 'STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert out['left_status']['reason'] == 'EMPIRICAL_GROUNDED_REFERENT_SIGNATURE_DRIFT'
        assert out['right_status']['status'] == 'CURRENT_EMPIRICALLY_GROUNDED_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert out['language_authority'] == out['semantic_reference_authority'] == out['truth_authority'] == 'NONE'
    finally:
        _close(ms, td)


def test_query_local_distinction_requires_empirical_currentness_and_preserves_distinct_referents():
    td = tempfile.TemporaryDirectory(prefix='hardening-h-emp-coref-distinct-'); ms, world = _build(Path(td.name))
    try:
        _register_token(ms, world, 'TOK-P', 'SIG-X'); _register_token(ms, world, 'TOK-Q', 'FX-Q')
        p, _, _ = _ground(ms, world, 'TOK-P', 9000, mode='P')
        q, _, _ = _ground(ms, world, 'TOK-Q', 10000, mode='P')
        pf = _fresh(ms, world, 'TOK-P', 11000, mode='P')
        qf = _fresh(ms, world, 'TOK-Q', 12000, mode='P')
        assert empirical_binding_currentness_status(ms, p, pf[0], pf[1])['status'] == 'CURRENT_EMPIRICALLY_GROUNDED_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert empirical_binding_currentness_status(ms, q, qf[0], qf[1])['status'] == 'CURRENT_EMPIRICALLY_GROUNDED_TOKEN_REFERENT_BINDING_CANDIDATE'
        out = bounded_operational_coreference_status(ms, p, q, pf[0], pf[1], qf[0], qf[1])
        assert out['status'] == 'CURRENT_BOUNDED_OPERATIONAL_DISTINCTION', out
        assert out['left_operational_referent_signature_sha256'] != out['right_operational_referent_signature_sha256']
        assert out['semantic_reference_authority'] == out['truth_authority'] == out['execution_authority'] == 'NONE'
    finally:
        _close(ms, td)


def test_original_qualifying_evidence_cannot_make_coreference_empirically_current():
    td = tempfile.TemporaryDirectory(prefix='hardening-h-emp-coref-reuse-'); ms, world = _build(Path(td.name))
    try:
        _register_token(ms, world, 'TOK-A', 'SIG-X'); _register_token(ms, world, 'TOK-B', 'SIG-X')
        a, at, ah = _ground(ms, world, 'TOK-A', 13000, mode='P')
        b, bt, bh = _ground(ms, world, 'TOK-B', 14000, mode='P')
        out = bounded_operational_coreference_status(ms, a, b, at, ah, bt, bh)
        assert out['status'] == 'DEFER_UNKNOWN', out
        assert out['reason'] == 'BOTH_GROUNDED_BINDINGS_MUST_BE_EMPIRICALLY_CURRENT'
        assert out['left_status']['reason'] == 'POST_BINDING_EMPIRICAL_EVIDENCE_MUST_BE_DISJOINT'
        assert out['right_status']['reason'] == 'POST_BINDING_EMPIRICAL_EVIDENCE_MUST_BE_DISJOINT'
    finally:
        _close(ms, td)
