from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, Microseed,
    Observation, OperationalFrameContract, QualificationState,
    ValueVariableContract,
)
from scratch.lang_c08c_native_owned_affordance_relation import ACT,OBS,BASIS,_execute,_raw,_external_control_state
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_c08i_native_pair_harvest import _qualification_mapping,_registration_records


class OpaqueThreeLocusWorld:
    def __init__(self):
        self.x=self.y=self.z=0
        self.value=-1.0
        self.sensor_transform=lambda row:tuple(row)
    def raw(self):
        return tuple(self.sensor_transform((self.x,self.x,self.y,self.y,self.z,self.z)))
    def observe(self):
        return {'next_state_id':'s0','value_id':'V','observed_value':self.value,'raw_tokens':[str(x) for x in self.raw()]}
    def apply(self,action:str):
        if action=='QX': self.x+=1
        elif action=='QY': self.y+=1
        elif action=='QZ': self.z+=1
        else: raise AssertionError(action)
        self.value+=0.25
        return {'receipt':action}
    def set_passive_baseline(self,x:int,y:int,z:int):
        self.x=x;self.y=y;self.z=z
    def bump(self,locus:str):
        if locus=='X': self.x+=1
        elif locus=='Y': self.y+=1
        elif locus=='Z': self.z+=1
        else: raise ValueError(locus)


def _close(ms:Microseed):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()


def _observe_s0(ms:Microseed,tag:str):
    out=ms.observe_opaque_control_state(
        Observation(f'CAP-B3-S0-{tag}','EXTERNAL-WORLD','opaque-control-state','s0',authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-B3-S0-{tag}',
    )
    assert out['status']=='CURRENT_OPAQUE_CONTROL_STATE',out
    return out


def attach_three_runtime_surface(ms:Microseed,world:OpaqueThreeLocusWorld,tag:str):
    ms.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('B3-SUPPLIED-BODY',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    ms.register_value_variable(ValueVariableContract('V','reg',0,10,'v'*64,Authority.REFERENCE_ONLY,('B3-SUPPLIED-BODY',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    ms.observe_value_state('V',-1.0)
    ms.register_episode_schema(EpisodeSchemaContract('EP','opaque-episode','e'*64,Authority.DERIVED_READ_ONLY,('B3-SUPPLIED-BODY',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    for cid in ('QX','QY','QZ'):
        ms.register_capability(CapabilityContract(
            cid,'opaque low-level body action',{}, {},(),(),Authority.EFFECT,('B3',),'CURRENT',{},
            query_obligation_id='C08C-ACT',qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S'))
        ms.frames.bind_capability('F',cid)
    ms.register_capability(CapabilityContract(
        'C08C-OBS-RAW','opaque raw observation',{}, {},(),(),Authority.OBSERVATION_ONLY,('B3',),'CURRENT',{},
        query_obligation_id='C08C-OBS',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:world.observe(),operational_scope_id='S'))
    ms.register_capability(CapabilityContract(
        'C08C-OBS-BASIS','opaque observation basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('B3',),'CURRENT',{},
        dependencies=('C08C-OBS-RAW',),query_obligation_id='C08C-BASIS',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    ms.frames.bind_capability('F','C08C-OBS-RAW')
    _observe_s0(ms,f'{tag}-ATTACH')
    return {'status':'SUPPLIED_THREE_LOCUS_BODY_ATTACHED','body_capabilities':sorted(ms.capabilities.contracts)}


def fresh_three_owned_profiles(ms:Microseed,world:OpaqueThreeLocusWorld,*,tag:str,serial_base:int=0):
    world.set_passive_baseline(0,0,0)
    _observe_s0(ms,f'{tag}-START')
    _raw(ms,f'{tag}-P0')
    seq=(('QX','X0'),('QX','X1'),('QY','Y0'),('QY','Y1'),('QZ','Z0'),('QZ','Z1'))
    for offset,(cid,step) in enumerate(seq):
        _execute(ms,cid,f'{tag}-{step}',serial_base+offset)
        _raw(ms,f'{tag}-P{offset+1}')
    profiles=ms.record_current_owned_affordance_effect_profiles(
        evidence_id_prefix=f'E-B3-{tag}-PROFILE',max_probe_steps=6,
    )
    assert profiles['status']=='CURRENT_OWNED_AFFORDANCE_EFFECT_PROFILES_RECORDED',profiles
    assert profiles['profile_count']==3,profiles
    by_action={str(row['exclusive_action_id']):row for row in profiles['profiles']}
    assert set(by_action)=={'QX','QY','QZ'},by_action
    assert len({str(row['operational_referent_signature_sha256']) for row in by_action.values()})==3
    return by_action


def passive_referent_exposure_three(ms:Microseed,world:OpaqueThreeLocusWorld,*,locus:str,token:str,index:int,tag:str):
    world.set_passive_baseline(0,0,0)
    _external_control_state(ms,f'{tag}-PRE')
    _raw(ms,f'{tag}-PRE')
    world.bump(locus)
    _external_control_state(ms,f'{tag}-POST')
    _raw(ms,f'{tag}-POST')
    localized=ms.derive_and_record_current_owned_passive_operational_referent_localization(max_events=32768,max_records=32768)
    assert localized['status']=='CURRENT_OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZED',localized
    observed=observe_opaque_token(ms,token,index,phase='B3-THREE-REFERENT')
    assert observed['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',observed
    return {'localization':localized,'token':observed}


def seed_three_current_native_referent_associations(ms:Microseed,world:OpaqueThreeLocusWorld,*,tokens=('R4','T9','W3')):
    profiles=fresh_three_owned_profiles(ms,world,tag='SEED',serial_base=0)
    locus_for={'QX':'X','QY':'Y','QZ':'Z'}
    action_for={'X':'QX','Y':'QY','Z':'QZ'}
    token_for={'X':tokens[0],'Y':tokens[1],'Z':tokens[2]}
    for i,locus in enumerate(('X','Y','Z','X','Y','Z','X','Y','Z')):
        passive_referent_exposure_three(ms,world,locus=locus,token=token_for[locus],index=100+i,tag=f'PAIR-{i}-{locus}')
    lifecycle=ms.harvest_qualify_and_register_current_opaque_evidence_associations(max_records=32768)
    assert lifecycle['status']=='HARVESTED_NATIVE_OPAQUE_ASSOCIATIONS_EPISTEMICALLY_QUALIFIED_AND_REGISTERED',lifecycle
    assert tuple(lifecycle['qualifications']['scopes'])==('NATIVE_TOKEN_REFERENT',),lifecycle
    mapping=_qualification_mapping(lifecycle,'NATIVE_TOKEN_REFERENT')
    expected={token_for[locus]:str(profiles[action_for[locus]]['operational_referent_signature_sha256']) for locus in ('X','Y','Z')}
    assert mapping==expected,(mapping,expected)
    records=_registration_records(lifecycle,'NATIVE_TOKEN_REFERENT')
    assert set(records)==set(tokens),records
    for locus in ('X','Y','Z'):
        token=token_for[locus]; action=action_for[locus]
        live=ms.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[action]['evidence_id']))
        assert live['status']=='CURRENTNESS_CONFIRMED',live
    return {'profiles':profiles,'mapping':mapping,'records':records,'lifecycle':lifecycle}


def fixture(sensor_transform=None,tokens=('R4','T9','W3')):
    td=TemporaryDirectory(prefix='b3-three-grounded-'); world=OpaqueThreeLocusWorld()
    if sensor_transform is not None: world.sensor_transform=sensor_transform
    ms=Microseed(Path(td.name));attach_three_runtime_surface(ms,world,'B3')
    seeded=seed_three_current_native_referent_associations(ms,world,tokens=tokens)
    return td,ms,world,seeded
