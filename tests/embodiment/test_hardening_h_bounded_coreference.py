
from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import (
    _build,_cap,_use_episode,derive_binding_candidate,binding_status,
)


def _register_token(ms,world,token_id:str,physical_action:str):
    ms.register_capability(
        _cap(token_id,Authority.EFFECT,lambda _action=physical_action,**_:world.act(_action)),
        coordination_dependencies=(('COORD-X',0),),
    )


def _ground(ms,world,token_id:str,base:int):
    world.configure_alias(False);world.configure_signal_mode('P');world.configure_layout('A')
    train=tuple(_use_episode(ms,world,token_id,base+i) for i in range(10))
    world.configure_layout('B')
    hold=tuple(_use_episode(ms,world,token_id,base+100+i) for i in range(6))
    c=derive_binding_candidate(ms,train,hold,signal_id=token_id)
    assert c['status']=='QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
    assert binding_status(ms,c)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
    return c


def _bounded_coreference(ms,a,b):
    base={
        'semantic_reference_authority':'NONE','token_meaning_authority':'NONE',
        'numerical_identity_authority':'NONE','truth_authority':'NONE',
        'execution_authority':'NONE','language_authority':'NONE',
    }
    sa=binding_status(ms,a);sb=binding_status(ms,b)
    if sa['status']!='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE' or sb['status']!='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE':
        return {**base,'status':'DEFER_UNKNOWN','reason':'BOTH_GROUNDED_BINDINGS_MUST_BE_CURRENT','left_status':sa,'right_status':sb}
    la=a['binding']['operational_referent_signature_sha256'];lb=b['binding']['operational_referent_signature_sha256']
    if la==lb:
        return {**base,'status':'CURRENT_BOUNDED_OPERATIONAL_COREFERENCE_CANDIDATE','reason':'TWO_CURRENT_GROUNDED_BINDINGS_SHARE_ONE_OPERATIONAL_REFERENT_SIGNATURE','operational_referent_signature_sha256':la,'binding_ids':[a['binding_id'],b['binding_id']]}
    return {**base,'status':'CURRENT_BOUNDED_OPERATIONAL_DISTINCTION','reason':'CURRENT_GROUNDED_BINDINGS_RESOLVE_TO_DIFFERENT_OPERATIONAL_REFERENT_SIGNATURES','binding_ids':[a['binding_id'],b['binding_id']]}


def _close(ms,td):
    try:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
    finally:td.cleanup()


def test_two_surface_distinct_tokens_can_corefer_operationally_without_semantic_or_identity_authority():
    td=tempfile.TemporaryDirectory(prefix='hardening-h-coref-');ms,world=_build(Path(td.name))
    try:
        _register_token(ms,world,'TOK-A','SIG-X');_register_token(ms,world,'TOK-B','SIG-X')
        a=_ground(ms,world,'TOK-A',1000);b=_ground(ms,world,'TOK-B',2000)
        assert a['binding_id']!=b['binding_id']
        assert a['binding']['signal_capability_signature_sha256']!=b['binding']['signal_capability_signature_sha256']
        q=_bounded_coreference(ms,a,b)
        assert q['status']=='CURRENT_BOUNDED_OPERATIONAL_COREFERENCE_CANDIDATE'
        assert q['semantic_reference_authority']==q['numerical_identity_authority']==q['truth_authority']==q['execution_authority']==q['language_authority']=='NONE'
        # Hidden perfect-copy replacement of the P source leaves the operational
        # signature unchanged. Therefore the bounded co-reference result is *not*
        # numerical identity evidence.
        world.replace_p_perfect_copy()
        q2=_bounded_coreference(ms,a,b)
        assert q2['status']==q['status']
        assert q2['numerical_identity_authority']=='NONE'
    finally:_close(ms,td)


def test_current_grounded_tokens_to_different_operational_referents_do_not_corefer_even_under_same_coordination_contract():
    td=tempfile.TemporaryDirectory(prefix='hardening-h-distinct-');ms,world=_build(Path(td.name))
    try:
        _register_token(ms,world,'TOK-P','SIG-X');_register_token(ms,world,'TOK-Q','FX-Q')
        p=_ground(ms,world,'TOK-P',3000);q=_ground(ms,world,'TOK-Q',4000)
        assert p['binding']['operational_referent_signature_sha256']!=q['binding']['operational_referent_signature_sha256']
        out=_bounded_coreference(ms,p,q)
        assert out['status']=='CURRENT_BOUNDED_OPERATIONAL_DISTINCTION'
        assert out['semantic_reference_authority']==out['truth_authority']==out['execution_authority']=='NONE'
    finally:_close(ms,td)


def test_one_sided_token_currentness_drift_blocks_coreference_instead_of_inheriting_from_the_still_current_alias():
    td=tempfile.TemporaryDirectory(prefix='hardening-h-stale-');ms,world=_build(Path(td.name))
    try:
        _register_token(ms,world,'TOK-A','SIG-X');_register_token(ms,world,'TOK-B','SIG-X')
        a=_ground(ms,world,'TOK-A',5000);b=_ground(ms,world,'TOK-B',6000)
        assert _bounded_coreference(ms,a,b)['status']=='CURRENT_BOUNDED_OPERATIONAL_COREFERENCE_CANDIDATE'
        ms.invalidate_capability('TOK-A',reason='HARDENING-H-ONE-SIDED-TOKEN-DRIFT')
        assert binding_status(ms,a)['status']=='STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert binding_status(ms,b)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        out=_bounded_coreference(ms,a,b)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['reason']=='BOTH_GROUNDED_BINDINGS_MUST_BE_CURRENT'
        assert out['semantic_reference_authority']==out['numerical_identity_authority']==out['execution_authority']=='NONE'
    finally:_close(ms,td)


def test_coordination_drift_blocks_both_coreference_bindings_without_rebinding_token_meaning():
    td=tempfile.TemporaryDirectory(prefix='hardening-h-coord-');ms,world=_build(Path(td.name))
    try:
        _register_token(ms,world,'TOK-A','SIG-X');_register_token(ms,world,'TOK-B','SIG-X')
        a=_ground(ms,world,'TOK-A',7000);b=_ground(ms,world,'TOK-B',8000)
        ms.change_operational_coordination('COORD-X',reason='HARDENING-H-COORDINATION-DRIFT')
        out=_bounded_coreference(ms,a,b)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['token_meaning_authority']==out['semantic_reference_authority']==out['language_authority']=='NONE'
    finally:_close(ms,td)
