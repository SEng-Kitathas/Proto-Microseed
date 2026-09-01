
from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import (
    ACT, _build, _cap, _use_episode, derive_binding_candidate, binding_status,
)


def _ground_alt_signal(signal_id: str):
    td=tempfile.TemporaryDirectory(prefix='frontier-h-language-')
    ms,world=_build(Path(td.name))
    # Register a new opaque surface handle with the same physical signal effect.
    # The signal ID is arbitrary; the grounded world consequence remains the owner.
    ms.register_capability(
        _cap(signal_id, Authority.EFFECT, lambda **_: world.act('SIG-X')),
        coordination_dependencies=(('COORD-X',0),),
    )
    try:
        world.configure_alias(False)
        world.configure_signal_mode('P')
        world.configure_layout('A')
        train=tuple(_use_episode(ms,world,signal_id,i) for i in range(10))
        world.configure_layout('B')
        hold=tuple(_use_episode(ms,world,signal_id,100+i) for i in range(6))
        cand=derive_binding_candidate(ms,train,hold,signal_id=signal_id)
        assert cand['status']=='QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert binding_status(ms,cand)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert cand['semantic_reference_authority']=='NONE'
        assert cand['token_meaning_authority']=='NONE'
        assert cand['truth_authority']=='NONE'
        assert cand['execution_authority']=='NONE'
        assert cand['language_authority']=='NONE'
        return td,ms,world,cand,train,hold
    except Exception:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup();raise


def _close(td,ms):
    try:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
    finally:td.cleanup()


def test_independent_opaque_signal_handle_permutation_preserves_grounded_operational_referent_index_not_binding_identity():
    left=_ground_alt_signal('TOK-9F')
    right=_ground_alt_signal('TOK-2A')
    try:
        lc=left[3]; rc=right[3]
        # Different arbitrary token handles produce different content-bound binding
        # identities, but the grounded operational referent reached through actual
        # use is the same affordance-relative referent class.
        assert lc['binding']['signal_capability_id']=='TOK-9F'
        assert rc['binding']['signal_capability_id']=='TOK-2A'
        assert lc['binding_id'] != rc['binding_id']
        assert lc['binding']['signal_capability_signature_sha256'] != rc['binding']['signal_capability_signature_sha256']
        assert lc['binding']['operational_referent_signature_sha256'] == rc['binding']['operational_referent_signature_sha256']
        for c in (lc,rc):
            assert c['semantic_reference_authority']==c['token_meaning_authority']==c['truth_authority']==c['execution_authority']==c['language_authority']=='NONE'
    finally:
        _close(left[0],left[1]);_close(right[0],right[1])


def test_surface_readability_or_token_identity_without_grounded_history_cannot_create_reference_candidate():
    root=Path(tempfile.mkdtemp(prefix='frontier-h-language-unbound-'))
    ms,world=_build(root)
    # `_build` already registers human-readable `hello`; no grounded use history is supplied.
    try:
        readable=derive_binding_candidate(ms,(),(),signal_id='hello')
        assert readable['status']=='DEFER_UNKNOWN'
        assert readable['reason']=='SUFFICIENT_GROUNDED_USE_HISTORY_REQUIRED'
        assert readable['semantic_reference_authority']=='NONE'
        assert readable['token_meaning_authority']=='NONE'
        assert readable['execution_authority']=='NONE'
        # Arbitrary novel token is not even a current capability and therefore cannot
        # be smuggled into a qualified binding by naming it.
        novel=derive_binding_candidate(ms,(),(),signal_id='THE-WORD-CAT')
        assert novel['status']=='DEFER_UNKNOWN'
        assert novel['reason']=='SUFFICIENT_GROUNDED_USE_HISTORY_REQUIRED'
    finally:
        ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
        # tempfile created by mkdtemp is intentionally left to OS cleanup here because
        # the Microseed stores have been explicitly closed; no identity semantics depend on path.


def test_grounded_binding_stales_on_signal_or_coordination_currentness_and_does_not_execute():
    td,ms,world,cand,train,hold=_ground_alt_signal('TOK-CURRENT')
    try:
        before_intents=len(ms.action_closure.intents)
        before_exec=len(ms.action_closure.executions)
        assert binding_status(ms,cand)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        # Merely deriving/reading the binding never creates an intent or execution.
        assert len(ms.action_closure.intents)==before_intents
        assert len(ms.action_closure.executions)==before_exec
        ms.invalidate_capability('TOK-CURRENT',reason='FRONTIER-H-TOKEN-DRIFT')
        stale=binding_status(ms,cand)
        assert stale['status']=='STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert len(ms.action_closure.intents)==before_intents
        assert len(ms.action_closure.executions)==before_exec
    finally:
        _close(td,ms)
