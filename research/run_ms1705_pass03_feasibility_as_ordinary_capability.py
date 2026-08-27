from __future__ import annotations
import json, tempfile
from pathlib import Path
from microseed import Authority, CapabilityContract, FeasibilityState, Microseed, QualificationState, QueryObligation
from microseed.runtime.observation import currentness
from microseed.runtime.types import Observation


def effect_cap(cid: str):
    return CapabilityContract(cid,'opaque-effect',{}, {},(),(),Authority.EFFECT,('MS1705',),'CURRENT',{},
        query_obligation_id='Q-ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_: {'ok':True},operational_scope_id='S')


def raw_obs_cap(world: dict):
    return CapabilityContract('OBS-FEAS-A','bounded-feasibility-observation',{'target':'A'}, {'output':'opaque-feasibility-facts'},(),(),
        Authority.OBSERVATION_ONLY,('MS1705',),'CURRENT',{},query_obligation_id='Q-FEAS',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: dict(world),operational_scope_id='S')


def feasibility_cap(m: Microseed):
    def handler(*, now_iso: str):
        q=QueryObligation('Q-FEAS','current-feasibility:A',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='S')
        r=m.capabilities.invoke('OBS-FEAS-A',q)
        if r.get('status')!='CAPABILITY_RESULT' or r.get('authority')!=Authority.OBSERVATION_ONLY.value or not isinstance(r.get('value'),dict):
            return {'feasibility':FeasibilityState.UNKNOWN.value,'reason':'FEASIBILITY_OBSERVATION_UNAVAILABLE'}
        v=r['value']
        obs=Observation('INLINE','CAPABILITY:OBS-FEAS-A','feasibility:A',v,observed_at=v.get('observed_at'),authority=Authority.OBSERVATION_ONLY)
        if currentness(obs,now_iso,5)!='CURRENT':
            return {'feasibility':FeasibilityState.UNKNOWN.value,'reason':'FEASIBILITY_OBSERVATION_NOT_CURRENT'}
        if v.get('resource_ready') is None or v.get('hazard_clear') is None:
            return {'feasibility':FeasibilityState.UNKNOWN.value,'reason':'FEASIBILITY_FACT_INCOMPLETE'}
        state=FeasibilityState.FEASIBLE if v['resource_ready'] is True and v['hazard_clear'] is True else FeasibilityState.REFUSED
        return {'feasibility':state.value,'reason':'CURRENT_BOUNDED_FACTS','observed_at':v['observed_at']}
    return CapabilityContract('FEAS-A','bounded-execution-time-feasibility',{'target_capability_id':'A'},{'output':'FeasibilityState'},
        ('QUERY_RELATIVE','CURRENT_OBSERVATION_REQUIRED'),('NOT_GLOBAL_SAFETY_OR_TRUTH',),Authority.DERIVED_READ_ONLY,('MS1705',),'CURRENT',{},
        dependencies=('A','OBS-FEAS-A'),query_obligation_id='Q-FEAS',qualification=QualificationState.SHADOW_QUALIFIED,handler=handler,operational_scope_id='S')


def run():
    td=tempfile.TemporaryDirectory(prefix='ms1705-')
    try:
        m=Microseed(Path(td.name)); world={'resource_ready':True,'hazard_clear':True,'observed_at':'2026-08-25T11:10:00Z'}
        m.register_capability(effect_cap('A'));m.register_capability(raw_obs_cap(world));m.register_capability(feasibility_cap(m))
        q=QueryObligation('Q-FEAS','current-feasibility:A',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='S')
        r=m.capabilities.invoke('FEAS-A',q,now_iso='2026-08-25T11:10:02Z')
        assert r['status']=='CAPABILITY_RESULT' and r['authority']==Authority.DERIVED_READ_ONLY.value and r['value']['feasibility']=='FEASIBLE'
        c=m.capabilities.contracts['FEAS-A']; assert c.boundary['target_capability_id']=='A'
        sig=c.computed_signature_sha256(); epoch=m.capabilities.epochs['FEAS-A']

        # Action is still current while fresh world facts refuse use.
        world.update(resource_ready=False,observed_at='2026-08-25T11:10:03Z')
        rr=m.capabilities.invoke('FEAS-A',q,now_iso='2026-08-25T11:10:04Z')
        assert rr['value']['feasibility']=='REFUSED'
        assert m.capabilities.contracts['A'].currentness=='CURRENT'

        # Missing/stale facts preserve UNKNOWN.
        world.update(resource_ready=True,hazard_clear=None,observed_at='2026-08-25T11:10:05Z')
        ru=m.capabilities.invoke('FEAS-A',q,now_iso='2026-08-25T11:10:06Z'); assert ru['value']['feasibility']=='UNKNOWN'
        world.update(hazard_clear=True,observed_at='2026-08-25T11:00:00Z')
        rs=m.capabilities.invoke('FEAS-A',q,now_iso='2026-08-25T11:10:07Z'); assert rs['value']['feasibility']=='UNKNOWN'

        # Dependency invalidation transitively removes feasibility currentness.
        stale=m.invalidate_capability('OBS-FEAS-A',reason='OBS_PATH_LOST'); assert 'FEAS-A' in stale
        rb=m.capabilities.invoke('FEAS-A',q,now_iso='2026-08-25T11:10:08Z'); assert rb['status']=='UNKNOWN_INCOMPLETE'

        # Wrong scope is refused by ordinary capability routing.
        # Use fresh fixture because stale qualification already blocks first.
        td2=tempfile.TemporaryDirectory(prefix='ms1705b-')
        try:
            n=Microseed(Path(td2.name));w={'resource_ready':True,'hazard_clear':True,'observed_at':'2026-08-25T11:10:00Z'}
            n.register_capability(effect_cap('A'));n.register_capability(raw_obs_cap(w));n.register_capability(feasibility_cap(n))
            bad=n.capabilities.invoke('FEAS-A',QueryObligation('Q-FEAS','x',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='OTHER'),now_iso='2026-08-25T11:10:02Z')
            assert bad['status']=='UNKNOWN_INCOMPLETE' and bad['reason']=='OPERATIONAL_SCOPE_MISMATCH'
        finally:td2.cleanup()

        out={'pass':'MS1705_PASS03','feasibility_capability':{'id':'FEAS-A','epoch':epoch,'signature':sig,'authority':Authority.DERIVED_READ_ONLY.value,'dependencies':['A','OBS-FEAS-A']},
             'cases':{'safe':'FEASIBLE','fresh_block':'REFUSED','incomplete':'UNKNOWN','stale_observation':'UNKNOWN','dependency_loss':'UNKNOWN_INCOMPLETE','wrong_scope':'UNKNOWN_INCOMPLETE'},
             'disposition':'SURVIVED__ORDINARY_DERIVED_READ_ONLY_CAPABILITY_CAN_OWN_BOUNDED_FEASIBILITY_NOW_WITH_TRANSITIVE_CURRENTNESS__NO_FEASIBILITY_MANAGER',
             'boundary':'CURRENT_QUALIFIED_FEASIBILITY_CAPABILITY_CAN_STILL_BE_PHYSICALLY_WRONG_IF_ITS_GROUNDING_BASIS_IS_FALSELY_QUALIFIED'}
        Path(__file__).with_name('MS1705_PASS03_FEASIBILITY_AS_ORDINARY_CAPABILITY.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
    finally:td.cleanup()
if __name__=='__main__':run()
