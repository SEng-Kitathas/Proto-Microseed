
from __future__ import annotations

import importlib.util
from pathlib import Path

from microseed import Authority, CapabilityContract, Microseed, Observation, QualificationState, QueryObligation
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import (
    GroundedReferenceWorld, _counterparty, _coordination, _cap as lang_cap,
    _use_episode, derive_binding_candidate, binding_status, OBS as LANG_OBS,
)


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_sh4_ms2063',path);assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def _register_language_surface(ms):
    world=GroundedReferenceWorld()
    ms.register_operational_counterparty(_counterparty())
    ms.register_operational_coordination(_coordination())
    for cid in ('FX-P','FX-Q','FX-G','SIG-X','hello'):
        ms.register_capability(
            lang_cap(cid,Authority.EFFECT,lambda _cid=cid,**_: world.act(_cid)),
            coordination_dependencies=(('COORD-X',0),) if cid in {'SIG-X','hello'} else (),
        )
    ms.register_capability(lang_cap('OBS-RAW',Authority.OBSERVATION_ONLY,lambda **_:{'channels':world.observe()}))
    return world


def _ground_signal(ms,world,base=20000):
    world.configure_alias(False);world.configure_signal_mode('P');world.configure_layout('A')
    train=tuple(_use_episode(ms,world,'SIG-X',base+i) for i in range(10))
    world.configure_layout('B')
    hold=tuple(_use_episode(ms,world,'SIG-X',base+100+i) for i in range(6))
    c=derive_binding_candidate(ms,train,hold,signal_id='SIG-X')
    assert c['status']=='QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
    assert binding_status(ms,c)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
    return c


def _n1a_ob():
    return QueryObligation('SH4-N1A','TOKEN=SIG-X;INFORMATION_GAIN=999;PREFER=EXP-X',required_authority=Authority.EFFECT,operational_scope_id='SH4-S')


def _register_n1a(ms,calls):
    ms.register_capability(CapabilityContract(
        'EXP-X','opaque-hardening-experiment',{}, {},(),(),Authority.EFFECT,('MS_SUBSTRATE_HARDENING_V1:SH4',),'CURRENT',{},
        query_obligation_id='SH4-N1A',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:calls.append('EXP-X') or {'receipt':'EXP-X'},operational_scope_id='SH4-S',
    ))


def _close(ms):
    for obj in (getattr(ms,'biography',None),getattr(ms,'evidence',None),getattr(ms,'store',None)):
        try:
            if hasattr(obj,'conn'): obj.conn.close()
            elif hasattr(obj,'close'): obj.close()
        except Exception: pass


def test_hierarchy_grounded_token_and_n1a_share_one_durable_microseed_without_authority_accumulation_across_restart_and_drift():
    m=_m();fx=m.build_integrated();ms=fx['ms'];root=Path(fx['td'].name);n1a_calls=[]
    ms2=None
    try:
        # Existing hierarchy is current before auxiliary developmental history is added.
        hierarchy_id=fx['routing_id'];tokens=tuple(fx['target_tokens']);bound_ids=tuple(x.capability_id for x in fx['bound']);bound_sigs=tuple(x.computed_signature_sha256() for x in fx['bound'])
        assert ms.projection_conditioned_relation_routing_status(hierarchy_id)['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'

        lang_world=_register_language_surface(ms)
        binding=_ground_signal(ms,lang_world)
        assert binding['semantic_reference_authority']==binding['truth_authority']==binding['language_authority']==binding['execution_authority']=='NONE'

        _register_n1a(ms,n1a_calls)
        warrant=ms.derive_n1a_experimental_warrant(_n1a_ob())
        assert warrant['status']=='N1A_EXPERIMENTAL_WARRANT_ISSUED'
        assert warrant['eligible_capability_ids']==['EXP-X']
        assert warrant['information_value_authority']=='NONE'
        assert all(cid in warrant['rejected'] for cid in ('REQ-BASE',)+bound_ids)
        intent=ms.nominate_n1a_experimental_action_intent(_n1a_ob());assert intent['status']=='N1A_ACTION_INTENT_NOMINATED'
        ex=ms.execute_bounded_action(intent['intent']['intent_id'],_n1a_ob());assert ex['status']=='ACTION_EXECUTED';assert n1a_calls==['EXP-X']
        outcome=ms.record_bounded_action_outcome(
            ex['execution']['execution_id'],
            Observation('SH4-N1A-OUT','EXT',f"action-execution:{ex['execution']['execution_id']}",{'next_state_id':'SH4-AFTER','observed_values':{'V':2.0}},authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-SH4-N1A-OUT',
        )
        assert outcome['status']=='N1A_ACTION_OUTCOME_OBSERVED'
        again=ms.derive_n1a_experimental_warrant(_n1a_ob())
        assert again['status']=='ABSTAIN' and again['reason']=='NO_CURRENT_ELIGIBLE_UNMODELED_ACTION'
        assert again['execution_authority']=='NONE'

        # Additional language/N1A history must not corrupt the already-qualified hierarchy.
        assert ms.projection_conditioned_relation_routing_status(hierarchy_id)['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        hp=m.current_proposal(fx,('SH4-HIER','H0','C0','SH4-HIER-M'),'SH4-HIER-BEFORE-RST');assert hp is not None
        assert hp.sequence==(fx['bound'][0].capability_id,)
        hi=ms.nominate_bounded_action_intent(hp.proposal_id,m.act_ob());assert hi['status']=='ACTION_INTENT_NOMINATED'
        hx=ms.execute_bounded_action(hi['intent']['intent_id'],m.act_ob());assert hx['status']=='ACTION_EXECUTED';assert hx['handler_value']['target']==tokens[0]
        assert binding_status(ms,binding)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'

        # Restart: learned hierarchy lineage and N1A consumption persist, executable runtime structure does not.
        ms2=Microseed(root)
        assert hierarchy_id in ms2.action_outcome_learning.projection_conditioned_bindings
        assert ms2.projection_conditioned_relation_routing_status(hierarchy_id)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert 'REQ-BASE' not in ms2.capabilities.contracts and 'SIG-X' not in ms2.capabilities.contracts and 'EXP-X' not in ms2.capabilities.contracts

        world2=m.TwoLevelWorld();world2.bind_targets(tokens)
        m.register_runtime(ms2,world2,register_frame_state=True)
        target_rec=ms2.epistemic_projections.records['TARGET-P'];rebound=m.derive_bound_requests(ms2,world2,target_rec,tokens)
        assert tuple(x.capability_id for x in rebound)==bound_ids and tuple(x.computed_signature_sha256() for x in rebound)==bound_sigs
        lang_world2=_register_language_surface(ms2)
        _register_n1a(ms2,n1a_calls)
        assert ms2.projection_conditioned_relation_routing_status(hierarchy_id)['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        # Exact descriptor re-registration restores the old grounding currentness; it does not grant any authority.
        assert binding_status(ms2,binding)['status']=='CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        for key in ('semantic_reference_authority','truth_authority','language_authority','execution_authority'):
            assert binding[key]=='NONE'
        persisted=ms2.derive_n1a_experimental_warrant(_n1a_ob())
        assert persisted['status']=='ABSTAIN' and persisted['reason']=='NO_CURRENT_ELIGIBLE_UNMODELED_ACTION'
        assert persisted['rejected']['EXP-X'] in {'N1A_FIRST_EXPOSURE_ALREADY_CONSUMED','CONSEQUENCE_ALREADY_MODELED:CAPABILITY_ALREADY_EXECUTED_THIS_EPOCH','CURRENT_PREDICTIVE_RELATION_EXISTS:R-HARM'} or 'ALREADY' in persisted['rejected']['EXP-X'] or 'MODELED' in persisted['rejected']['EXP-X']
        assert n1a_calls==['EXP-X']

        # Hierarchy still works after restart plus re-registration of unrelated language/N1A surfaces.
        fx2={**fx,'ms':ms2,'world':world2,'bound':rebound}
        hp2=m.current_proposal(fx2,('SH4-RST','H0','C1','SH4-RST-M'),'SH4-HIER-AFTER-RST');assert hp2 is not None
        assert hp2.sequence==(rebound[1].capability_id,)
        hi2=ms2.nominate_bounded_action_intent(hp2.proposal_id,m.act_ob());assert hi2['status']=='ACTION_INTENT_NOMINATED'
        hx2=ms2.execute_bounded_action(hi2['intent']['intent_id'],m.act_ob());assert hx2['status']=='ACTION_EXECUTED';assert hx2['handler_value']['target']==tokens[1]

        # Drift only the language token surface. Grounding stales, but hierarchy and N1A history do not cross-contaminate.
        ms2.invalidate_capability('SIG-X',reason='SH4-LANGUAGE-SIGNAL-DRIFT')
        stale=binding_status(ms2,binding);assert stale['status']=='STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE'
        assert ms2.projection_conditioned_relation_routing_status(hierarchy_id)['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        persisted2=ms2.derive_n1a_experimental_warrant(_n1a_ob())
        assert persisted2['status']=='ABSTAIN';assert n1a_calls==['EXP-X']
        assert not hasattr(ms2,'language_manager') and not hasattr(ms2,'hierarchy_manager') and not hasattr(ms2,'curiosity_manager')
    finally:
        if ms2 is not None:_close(ms2)
        _close(ms)
        fx['td'].cleanup()
