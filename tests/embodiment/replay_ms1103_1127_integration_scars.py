from __future__ import annotations
import json,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from microseed.runtime.entity import Microseed
from microseed.runtime.types import OperationalCounterpartyContract,OperationalCoordinationContract,EpisodeSchemaContract,CapabilityContract,Authority,QualificationState

def cp():
 c=OperationalCounterpartyContract(counterparty_id='P',purpose='opaque',signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1053-1077',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED);c.signature_sha256=c.computed_signature_sha256();return c

def co(rid):
 c=OperationalCoordinationContract(coordination_id=rid,purpose='opaque',participant_counterparty_epochs=(('P',0),),signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1078-1102',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED);c.signature_sha256=c.computed_signature_sha256();return c

def ep(sid,rid):
 return EpisodeSchemaContract(schema_id=sid,purpose='opaque',signature_sha256=('a' if sid=='EA' else 'b')*64,authority=Authority.DERIVED_READ_ONLY,lineage=('MS1103-1127',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,coordination_epochs=((rid,0),))

def cap(cid):
 return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1)

def run():
 with tempfile.TemporaryDirectory(prefix='ms1103-1127-replay-') as td:
  m=Microseed(Path(td));m.register_operational_counterparty(cp(),evidence=());m.register_operational_coordination(co('RA'),evidence=());m.register_operational_coordination(co('RB'),evidence=())
  for sid,rid,cid in [('EA','RA','CA'),('EB','RB','CB')]:
   m.register_episode_schema(ep(sid,rid),evidence=());m.register_capability(cap(cid),evidence=(),extra_development_dependencies=(sid,));m.episodes.bind_capability(sid,cid)
  m.register_capability(CapabilityContract('CA2','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',{},dependencies=('CA',),qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1),evidence=())
  stale=m.change_operational_coordination('RA',reason='REPLAY_DRIFT')
  s=m.status()
  checks={
   'changed_relation_stale':not m.coordinations.is_current('RA',0),
   'bound_episode_stale':not m.episodes.is_current('EA',0),
   'unrelated_episode_current':m.episodes.is_current('EB',0),
   'bound_capability_stale':m.capabilities.contracts['CA'].qualification==QualificationState.STALE,
   'transitive_whole_stale':m.capabilities.contracts['CA2'].qualification==QualificationState.STALE,
   'unrelated_capability_current':m.capabilities.contracts['CB'].qualification in {QualificationState.QUALIFIED,QualificationState.SHADOW_QUALIFIED},
   'prelingual_hard_stop':s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE' and s['next_ms']>=1203 and s.get(f"ms{s['next_ms']}_started") is False,
   'selected_frontier':s['research_terminal_ms']>=1252 and s['frontier'].startswith('ATTN-MS'),
   'semantic_joint_goal_not_promoted':s['distributed_episode_semantic_joint_goal_authority']=='NONE',
  }
  return {'schema':'microseed.ms1103-1127.maindev-replay.v1.3','checks':checks,'all_pass':all(checks.values()),'stale':sorted(stale),'status':s}
if __name__=='__main__':
 out=run();print(json.dumps(out,indent=2,sort_keys=True));raise SystemExit(0 if out['all_pass'] else 1)
