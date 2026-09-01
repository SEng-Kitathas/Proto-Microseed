
from __future__ import annotations

import tempfile
from pathlib import Path

from scratch.ms2046_grounded_operational_token_referent_binding_quarry import (
    _build,
    _history,
    _use_episode,
    binding_status,
    derive_binding_candidate,
    empirical_binding_currentness_status,
)


def _close(ms):
    ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def test_fresh_post_binding_grounded_use_reearns_same_referent_as_empirically_current_without_language_authority():
    with tempfile.TemporaryDirectory(prefix='hardening-h-empirical-current-') as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world, train_mode='P', hold_mode='P')
            old = derive_binding_candidate(ms, train, hold)
            assert old['status'] == 'QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
            world.configure_signal_mode('P')
            world.configure_layout('A')
            fresh_train = tuple(_use_episode(ms, world, 'SIG-X', 600 + i) for i in range(10))
            world.configure_layout('B')
            fresh_hold = tuple(_use_episode(ms, world, 'SIG-X', 700 + i) for i in range(6))
            status = empirical_binding_currentness_status(ms, old, fresh_train, fresh_hold)
            assert status['status'] == 'CURRENT_EMPIRICALLY_GROUNDED_TOKEN_REFERENT_BINDING_CANDIDATE', status
            assert status['structural_currentness']['status'] == 'CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
            assert status['operational_referent_signature_sha256'] == old['binding']['operational_referent_signature_sha256']
            assert status['language_authority'] == status['semantic_reference_authority'] == status['truth_authority'] == 'NONE'
            assert set(status['fresh_source_episode_sha256']).isdisjoint(set(old['source_episode_sha256']))
        finally:
            _close(ms)


def test_external_convention_reversal_becomes_empirically_stale_even_when_structural_descriptors_remain_current():
    with tempfile.TemporaryDirectory(prefix='hardening-h-empirical-stale-') as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world, train_mode='P', hold_mode='P')
            old = derive_binding_candidate(ms, train, hold)
            assert binding_status(ms, old)['status'] == 'CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
            world.configure_signal_mode('Q')
            world.configure_layout('A')
            fresh_train = tuple(_use_episode(ms, world, 'SIG-X', 800 + i) for i in range(10))
            world.configure_layout('B')
            fresh_hold = tuple(_use_episode(ms, world, 'SIG-X', 900 + i) for i in range(6))
            status = empirical_binding_currentness_status(ms, old, fresh_train, fresh_hold)
            assert status['status'] == 'STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE', status
            assert status['reason'] == 'EMPIRICAL_GROUNDED_REFERENT_SIGNATURE_DRIFT'
            assert status['structural_currentness']['status'] == 'CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
            assert status['old_operational_referent_signature_sha256'] != status['fresh_operational_referent_signature_sha256']
            assert status['language_authority'] == status['semantic_reference_authority'] == status['truth_authority'] == 'NONE'
        finally:
            _close(ms)


def test_original_training_evidence_cannot_be_reused_as_post_binding_empirical_currentness():
    with tempfile.TemporaryDirectory(prefix='hardening-h-empirical-reuse-') as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world, train_mode='P', hold_mode='P')
            old = derive_binding_candidate(ms, train, hold)
            status = empirical_binding_currentness_status(ms, old, train, hold)
            assert status['status'] == 'UNKNOWN_INCOMPLETE'
            assert status['reason'] == 'POST_BINDING_EMPIRICAL_EVIDENCE_MUST_BE_DISJOINT'
            assert status['structural_currentness']['status'] == 'CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        finally:
            _close(ms)


def test_mixed_fresh_currentness_evidence_fails_unknown_not_stale_or_current():
    with tempfile.TemporaryDirectory(prefix='hardening-h-empirical-mixed-') as td:
        ms, world = _build(Path(td))
        try:
            train, hold = _history(ms, world, train_mode='P', hold_mode='P')
            old = derive_binding_candidate(ms, train, hold)
            world.configure_signal_mode('P')
            world.configure_layout('A')
            fresh_train = tuple(_use_episode(ms, world, 'SIG-X', 1000 + i) for i in range(10))
            world.configure_signal_mode('Q')
            world.configure_layout('B')
            fresh_hold = tuple(_use_episode(ms, world, 'SIG-X', 1100 + i) for i in range(6))
            status = empirical_binding_currentness_status(ms, old, fresh_train, fresh_hold)
            assert status['status'] == 'UNKNOWN_INCOMPLETE', status
            assert status['reason'] == 'FRESH_GROUNDED_BINDING_CURRENTNESS_EVIDENCE_NOT_QUALIFIED'
            assert status['fresh_reason'] == 'HOLDOUT_REFERENT_BINDING_DISAGREES'
            assert status['language_authority'] == status['semantic_reference_authority'] == status['truth_authority'] == 'NONE'
        finally:
            _close(ms)
