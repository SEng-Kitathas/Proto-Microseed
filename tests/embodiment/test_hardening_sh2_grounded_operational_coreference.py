
from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import (
    _build,_cap,_use_episode,derive_binding_candidate,binding_status,
)


def _register_token(ms,world,token_id:str):
    ms.register_capability(
        _cap(token_id,Authority.EFFECT,lambda **_: world.act('SIG-X')),
        coordination_dependencies=(('COORD-X',0),),
    )


def _ground(ms,world,token_id:str,*,mode:str,index_base:int):
    world.configure_alias(False);world.configure_signal_mode(mode);world.configure_layout('A')
    train=tuple(_use_episode(ms,world,token_id,index_base+i) for i in range(10))
    world.configure_layout('B')
    hold=tuple(_use_episode(ms,world,token_id,index_base+100+i) for i in range(6))
    c=derive_binding_candidate(ms,train,hold,signal_id=token_id)
    assert c['status']=='QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE',c
    assert binding_status(ms,c)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
    return c


def _coreference_surface(ms,left,right):
    base={'semantic_reference_authority':'NONE','truth_authority':'NONE','language_authority':'NONE','execution_authority':'NONE','identity_authority':'NONE','authority_gain':'NONE'}
    for side,c in [('LEFT',left),('RIGHT',right)]:
        if c.get('status')!='QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE':
            return {**base,'status':'DEFER_UNKNOWN','reason':f'{side}_QUALIFIED_BINDING_REQUIRED'}
        st=binding_status(ms,c)
        if st['status']!='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE':
            return {**base,'status':'DEFER_UNKNOWN','reason':f'{side}_BINDING_NOT_CURRENT','binding_status':st}
    lb=left['binding'];rb=right['binding']
    if lb['coordination_id']!=rb['coordination_id'] or lb['coordination_epoch']!=rb['coordination_epoch'] or lb['coordination_signature_sha256']!=rb['coordination_signature_sha256']:
        return {**base,'status':'DEFER_UNKNOWN','reason':'COMMON_CURRENT_COORDINATION_REQUIRED'}
    same=lb['operational_referent_signature_sha256']==rb['operational_referent_signature_sha256']
    return {
        **base,
        'status':'CURRENT_OPERATIONAL_COREFERENCE_RESEARCH_ONLY' if same else 'CURRENT_DISTINCT_OPERATIONAL_REFERENTS_RESEARCH_ONLY',
        'reason':'TWO_CURRENT_GROUNDED_BINDINGS_SHARE_ONE_OPERATIONAL_REFERENT_SIGNATURE' if same else 'CURRENT_GROUNDED_BINDINGS_RESOLVE_TO_DIFFERENT_OPERATIONAL_REFERENT_SIGNATURES',
        'left_binding_id':left['binding_id'],'right_binding_id':right['binding_id'],
        'left_signal_capability_id':lb['signal_capability_id'],'right_signal_capability_id':rb['signal_capability_id'],
        'operational_referent_signature_sha256':lb['operational_referent_signature_sha256'] if same else None,
    }


def _close(ms,td):
    try:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
    finally:td.cleanup()


def test_two_independently_grounded_arbitrary_tokens_can_be_operationally_coreferential_without_semantic_or_execution_authority():
    td=tempfile.TemporaryDirectory(prefix='hardening-sh2-coref-');ms,world=_build(Path(td.name))
    try:
        _register_token(ms,world,'TOK-A7');_register_token(ms,world,'TOK-Z2')
        a=_ground(ms,world,'TOK-A7',mode='P',index_base=1000);b=_ground(ms,world,'TOK-Z2',mode='P',index_base=3000)
        assert a['binding_id']!=b['binding_id']
        assert a['binding']['signal_capability_signature_sha256']!=b['binding']['signal_capability_signature_sha256']
        assert a['binding']['operational_referent_signature_sha256']==b['binding']['operational_referent_signature_sha256']
        before=(len(ms.action_closure.intents),len(ms.action_closure.executions))
        out=_coreference_surface(ms,a,b)
        after=(len(ms.action_closure.intents),len(ms.action_closure.executions))
        assert out['status']=='CURRENT_OPERATIONAL_COREFERENCE_RESEARCH_ONLY'
        assert out['left_signal_capability_id']=='TOK-A7' and out['right_signal_capability_id']=='TOK-Z2'
        assert out['semantic_reference_authority']==out['truth_authority']==out['language_authority']==out['execution_authority']==out['identity_authority']=='NONE'
        assert before==after
    finally:_close(ms,td)


def test_shared_coordination_and_token_shape_do_not_force_coreference_when_grounded_referents_differ():
    td=tempfile.TemporaryDirectory(prefix='hardening-sh2-distinct-');ms,world=_build(Path(td.name))
    try:
        _register_token(ms,world,'TOK-X1');_register_token(ms,world,'TOK-X2')
        p=_ground(ms,world,'TOK-X1',mode='P',index_base=5000);q=_ground(ms,world,'TOK-X2',mode='Q',index_base=7000)
        assert p['binding']['coordination_id']==q['binding']['coordination_id']=='COORD-X'
        assert p['binding']['operational_referent_signature_sha256']!=q['binding']['operational_referent_signature_sha256']
        out=_coreference_surface(ms,p,q)
        assert out['status']=='CURRENT_DISTINCT_OPERATIONAL_REFERENTS_RESEARCH_ONLY'
        assert out['semantic_reference_authority']==out['truth_authority']==out['execution_authority']=='NONE'
    finally:_close(ms,td)


def test_convention_reversal_or_mixed_grounding_history_cannot_be_promoted_to_contextual_meaning_by_coreference_logic():
    td=tempfile.TemporaryDirectory(prefix='hardening-sh2-reversal-');ms,world=_build(Path(td.name))
    try:
        _register_token(ms,world,'TOK-STABLE');_register_token(ms,world,'TOK-MIXED')
        stable=_ground(ms,world,'TOK-STABLE',mode='P',index_base=9000)
        world.configure_alias(False);world.configure_signal_mode('P');world.configure_layout('A')
        train=tuple(_use_episode(ms,world,'TOK-MIXED',11000+i) for i in range(10))
        world.configure_signal_mode('Q');world.configure_layout('B')
        hold=tuple(_use_episode(ms,world,'TOK-MIXED',11100+i) for i in range(6))
        mixed=derive_binding_candidate(ms,train,hold,signal_id='TOK-MIXED')
        assert mixed['status']=='DEFER_UNKNOWN'
        assert mixed['reason']=='HOLDOUT_REFERENT_BINDING_DISAGREES'
        out=_coreference_surface(ms,stable,mixed)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='RIGHT_QUALIFIED_BINDING_REQUIRED'
        assert out['language_authority']==out['truth_authority']==out['execution_authority']=='NONE'
    finally:_close(ms,td)


def test_coreference_fails_closed_when_one_grounded_binding_becomes_stale():
    td=tempfile.TemporaryDirectory(prefix='hardening-sh2-stale-');ms,world=_build(Path(td.name))
    try:
        _register_token(ms,world,'TOK-L');_register_token(ms,world,'TOK-R')
        l=_ground(ms,world,'TOK-L',mode='P',index_base=13000);r=_ground(ms,world,'TOK-R',mode='P',index_base=15000)
        assert _coreference_surface(ms,l,r)['status']=='CURRENT_OPERATIONAL_COREFERENCE_RESEARCH_ONLY'
        ms.invalidate_capability('TOK-R',reason='SH2-TOKEN-R-DRIFT')
        out=_coreference_surface(ms,l,r)
        assert out['status']=='DEFER_UNKNOWN';assert out['reason']=='RIGHT_BINDING_NOT_CURRENT'
        assert out['binding_status']['status']=='STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert out['execution_authority']=='NONE'
    finally:_close(ms,td)
