from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, Microseed,
    Observation, OperationalFrameContract, QualificationState,
    ValueVariableContract,
)
from scratch.lang_c08c_native_owned_affordance_relation import _execute,_raw,_external_control_state
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_c08i_native_pair_harvest import _qualification_mapping,_registration_records


class OpaqueFourLocusWorld:
    def __init__(self):
        self.a=self.b=self.c=self.d=0
        self.value=-1.0
        self.sensor_transform=lambda row:tuple(row)
    def raw(self):
        return tuple(self.sensor_transform((self.a,self.a,self.b,self.b,self.c,self.c,self.d,self.d)))
    def observe(self):
        return {'next_state_id':'s0','value_id':'V','observed_value':self.value,'raw_tokens':[str(x) for x in self.raw()]}
    def apply(self,action:str):
        if action=='QA': self.a+=1
        elif action=='QB': self.b+=1
        elif action=='QC': self.c+=1
        elif action=='QD': self.d+=1
        else: raise AssertionError(action)
        self.value+=0.25
        return {'receipt':action}
    def set_passive_baseline(self,a:int,b:int,c:int,d:int):
        self.a=a;self.b=b;self.c=c;self.d=d
    def bump(self,locus:str):
        if locus=='A': self.a+=1
        elif locus=='B': self.b+=1
        elif locus=='C': self.c+=1
        elif locus=='D': self.d+=1
        else: raise ValueError(locus)


def _close(ms:Microseed):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()


def _observe_s0(ms:Microseed,tag:str):
    out=ms.observe_opaque_control_state(
        Observation(f'CAP-ARITY4-S0-{tag}','EXTERNAL-WORLD','opaque-control-state','s0',authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-ARITY4-S0-{tag}',
    )
    assert out['status']=='CURRENT_OPAQUE_CONTROL_STATE',out
    return out


def attach_four_runtime_surface(ms:Microseed,world:OpaqueFourLocusWorld,tag:str):
    ms.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('ARITY4-SUPPLIED-BODY',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    ms.register_value_variable(ValueVariableContract('V','reg',0,10,'v'*64,Authority.REFERENCE_ONLY,('ARITY4-SUPPLIED-BODY',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    ms.observe_value_state('V',-1.0)
    ms.register_episode_schema(EpisodeSchemaContract('EP','opaque-episode','e'*64,Authority.DERIVED_READ_ONLY,('ARITY4-SUPPLIED-BODY',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    for cid in ('QA','QB','QC','QD'):
        ms.register_capability(CapabilityContract(
            cid,'opaque low-level body action',{}, {},(),(),Authority.EFFECT,('ARITY4',),'CURRENT',{},
            query_obligation_id='C08C-ACT',qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S'))
        ms.frames.bind_capability('F',cid)
    ms.register_capability(CapabilityContract(
        'C08C-OBS-RAW','opaque raw observation',{}, {},(),(),Authority.OBSERVATION_ONLY,('ARITY4',),'CURRENT',{},
        query_obligation_id='C08C-OBS',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:world.observe(),operational_scope_id='S'))
    ms.register_capability(CapabilityContract(
        'C08C-OBS-BASIS','opaque observation basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('ARITY4',),'CURRENT',{},
        dependencies=('C08C-OBS-RAW',),query_obligation_id='C08C-BASIS',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    ms.frames.bind_capability('F','C08C-OBS-RAW')
    _observe_s0(ms,f'{tag}-ATTACH')
    return {'status':'SUPPLIED_FOUR_LOCUS_BODY_ATTACHED','body_capabilities':sorted(ms.capabilities.contracts)}


def fresh_four_owned_profiles(ms:Microseed,world:OpaqueFourLocusWorld,*,tag:str,serial_base:int=0):
    world.set_passive_baseline(0,0,0,0)
    _observe_s0(ms,f'{tag}-START')
    _raw(ms,f'{tag}-P0')
    seq=(('QA','A0'),('QA','A1'),('QB','B0'),('QB','B1'),('QC','C0'),('QC','C1'),('QD','D0'),('QD','D1'))
    for offset,(cid,step) in enumerate(seq):
        _execute(ms,cid,f'{tag}-{step}',serial_base+offset)
        _raw(ms,f'{tag}-P{offset+1}')
    profiles=ms.record_current_owned_affordance_effect_profiles(
        evidence_id_prefix=f'E-ARITY4-{tag}-PROFILE',max_probe_steps=8,
    )
    assert profiles['status']=='CURRENT_OWNED_AFFORDANCE_EFFECT_PROFILES_RECORDED',profiles
    assert profiles['profile_count']==4,profiles
    by_action={str(row['exclusive_action_id']):row for row in profiles['profiles']}
    assert set(by_action)=={'QA','QB','QC','QD'},by_action
    assert len({str(row['operational_referent_signature_sha256']) for row in by_action.values()})==4
    return by_action


def passive_referent_exposure_four(ms:Microseed,world:OpaqueFourLocusWorld,*,locus:str,token:str,index:int,tag:str):
    world.set_passive_baseline(0,0,0,0)
    _external_control_state(ms,f'{tag}-PRE')
    _raw(ms,f'{tag}-PRE')
    world.bump(locus)
    _external_control_state(ms,f'{tag}-POST')
    _raw(ms,f'{tag}-POST')
    localized=ms.derive_and_record_current_owned_passive_operational_referent_localization(max_events=65536,max_records=65536)
    assert localized['status']=='CURRENT_OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZED',localized
    observed=observe_opaque_token(ms,token,index,phase='ARITY4-FOUR-REFERENT')
    assert observed['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',observed
    return {'localization':localized,'token':observed}


def seed_four_current_native_referent_associations(ms:Microseed,world:OpaqueFourLocusWorld,*,tokens=('R4','T9','W3','K7')):
    profiles=fresh_four_owned_profiles(ms,world,tag='SEED',serial_base=0)
    locus_for={'QA':'A','QB':'B','QC':'C','QD':'D'}
    action_for={'A':'QA','B':'QB','C':'QC','D':'QD'}
    token_for={'A':tokens[0],'B':tokens[1],'C':tokens[2],'D':tokens[3]}
    seq=('A','B','C','D')*3
    for i,locus in enumerate(seq):
        passive_referent_exposure_four(ms,world,locus=locus,token=token_for[locus],index=100+i,tag=f'PAIR-{i}-{locus}')
    lifecycle=ms.harvest_qualify_and_register_current_opaque_evidence_associations(max_records=65536)
    assert lifecycle['status']=='HARVESTED_NATIVE_OPAQUE_ASSOCIATIONS_EPISTEMICALLY_QUALIFIED_AND_REGISTERED',lifecycle
    assert tuple(lifecycle['qualifications']['scopes'])==('NATIVE_TOKEN_REFERENT',),lifecycle
    mapping=_qualification_mapping(lifecycle,'NATIVE_TOKEN_REFERENT')
    expected={token_for[locus]:str(profiles[action_for[locus]]['operational_referent_signature_sha256']) for locus in ('A','B','C','D')}
    assert mapping==expected,(mapping,expected)
    records=_registration_records(lifecycle,'NATIVE_TOKEN_REFERENT')
    assert set(records)==set(tokens),records
    for locus in ('A','B','C','D'):
        token=token_for[locus];action=action_for[locus]
        live=ms.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[action]['evidence_id']))
        assert live['status']=='CURRENTNESS_CONFIRMED',live
    # Fixture hygiene: qualification/evidence output is grouping-neutral. End seeding with an
    # actual observation-owned control-state boundary so downstream experiments start cleanly.
    _observe_s0(ms,'SEED-END-CLEAN-WINDOW')
    return {'profiles':profiles,'mapping':mapping,'records':records,'lifecycle':lifecycle}


def fixture(sensor_transform=None,tokens=('R4','T9','W3','K7')):
    td=TemporaryDirectory(prefix='arity-four-grounded-');world=OpaqueFourLocusWorld()
    if sensor_transform is not None:world.sensor_transform=sensor_transform
    ms=Microseed(Path(td.name));attach_four_runtime_surface(ms,world,'ARITY4')
    seeded=seed_four_current_native_referent_associations(ms,world,tokens=tokens)
    return td,ms,world,seeded
