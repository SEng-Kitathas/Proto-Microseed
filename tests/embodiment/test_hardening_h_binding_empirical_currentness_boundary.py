
from __future__ import annotations

import tempfile
from pathlib import Path

from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _build,_history,_use_episode,derive_binding_candidate,binding_status


def test_old_grounded_token_binding_remains_structurally_current_after_external_convention_reversal_despite_new_contradictory_grounded_uses():
    with tempfile.TemporaryDirectory(prefix='hardening-h-currentness-') as td:
        ms,world=_build(Path(td))
        try:
            train,hold=_history(ms,world,train_mode='P',hold_mode='P')
            old=derive_binding_candidate(ms,train,hold)
            assert old['status']=='QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
            old_sig=old['binding']['operational_referent_signature_sha256']
            assert binding_status(ms,old)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'

            # External convention reverses with no signal-capability or coordination
            # descriptor drift. Fresh grounded uses now point to Q instead of P.
            world.configure_signal_mode('Q')
            world.configure_layout('A')
            fresh_train=tuple(_use_episode(ms,world,'SIG-X',300+i) for i in range(10))
            world.configure_layout('B')
            fresh_hold=tuple(_use_episode(ms,world,'SIG-X',400+i) for i in range(6))
            fresh=derive_binding_candidate(ms,fresh_train,fresh_hold)
            assert fresh['status']=='QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
            fresh_sig=fresh['binding']['operational_referent_signature_sha256']
            assert fresh_sig != old_sig

            # Hostile boundary: the old research candidate's currentness helper sees
            # only structural descriptor currentness and therefore cannot detect the
            # new contradictory grounded convention evidence.
            stale_leak=binding_status(ms,old)
            assert stale_leak['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
            assert ms.capabilities.epochs['SIG-X']==old['binding']['signal_capability_epoch']
            assert ms.coordinations.epochs['COORD-X']==old['binding']['coordination_epoch']
        finally:
            ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()


def test_mixed_pre_and_post_reversal_grounded_history_fails_closed_instead_of_declaring_one_reference():
    with tempfile.TemporaryDirectory(prefix='hardening-h-mixed-') as td:
        ms,world=_build(Path(td))
        try:
            train,hold=_history(ms,world,train_mode='P',hold_mode='P')
            world.configure_signal_mode('Q');world.configure_layout('B')
            reversed_hold=tuple(_use_episode(ms,world,'SIG-X',500+i) for i in range(6))
            mixed=derive_binding_candidate(ms,train,reversed_hold)
            assert mixed['status']=='DEFER_UNKNOWN'
            assert mixed['reason']=='HOLDOUT_REFERENT_BINDING_DISAGREES'
            assert mixed['semantic_reference_authority']=='NONE'
            assert mixed['token_meaning_authority']=='NONE'
            assert mixed['truth_authority']=='NONE'
            assert mixed['execution_authority']=='NONE'
            assert mixed['language_authority']=='NONE'
        finally:
            ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
