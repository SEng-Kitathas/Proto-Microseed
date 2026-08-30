from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Authority,CapabilityContract,EpistemicStatus,QueryObligation,QualificationState,RecruitmentOption,FeasibilityState,RehearsalTransitionObservation
from microseed.development.action_learning import projection_conditioned_hypothesis_surface_digest
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.runtime.entity import action_result_digest
from scratch.ms2005_bounded_referent_probe_reconstruction import UNIQUE_A
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _setup, _close

class PrefixWorld:
    def __init__(self):self.index=0;self.value=-1.0
    def apply(self,action):
        expected=('P0','P1')[self.index]
        assert action==expected,(action,expected);self.index+=1;self.value+=.5;return {'receipt':action}
    def observe(self):return {'next_state_id':'s0','value_id':'V','observed_value':self.value,'raw_tokens':[str(x) for x in UNIQUE_A[self.index]]}

def hob():return QueryObligation('MS2010-HIST','history effect',Authority.EFFECT,operational_scope_id='S')
def oob():return QueryObligation('MS2010-OBS','raw observe',Authority.OBSERVATION_ONLY,operational_scope_id='S')
def bob():return QueryObligation('MS2010-BASIS','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S')

def _attach_history(m,world):
    for cid in ('P0','P1'):
        m.register_capability(CapabilityContract(cid,'opaque prefix action',{}, {},(),(),Authority.EFFECT,('MS2010',),'CURRENT',{},query_obligation_id='MS2010-HIST',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S'))
        m.frames.bind_capability('F',cid)
    m.register_capability(CapabilityContract('OBS','raw observation',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS2010',),'CURRENT',{},query_obligation_id='MS2010-OBS',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','obs basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS2010',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='MS2010-BASIS',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    m.frames.bind_capability('F','OBS')

def _proposal(m,cid):
    rows=tuple(RehearsalTransitionObservation(f'MS2010-SEED-{cid}-{i}','s0',cid,'s0',.5,0,'F',0,'EP',0) for i in range(8))
    p=m.nominate_counterfactual_rehearsal(rows,(RecruitmentOption(cid,FeasibilityState.FEASIBLE,local_cost=.1),),start_state_id='s0',value_id='V');assert p is not None,p;return p

def _raw(m,tag):
    r=m.record_bounded_raw_observation_coordinates('OBS',oob(),evidence_id='MS2010-RAW-'+tag,capture_id='MS2010-CAP-RAW-'+tag,max_coordinates=8);assert r['status']=='BOUNDED_RAW_OBSERVATION_RECORDED',r

def _execute(m,cid,tag):
    p=_proposal(m,cid);n=m.nominate_bounded_action_intent(p.proposal_id,hob());assert n['status']=='ACTION_INTENT_NOMINATED',n
    x=m.execute_bounded_action(n['intent']['intent_id'],hob());assert x['status']=='ACTION_EXECUTED',x
    o=m.record_bounded_action_outcome_via_observation_basis(x['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=oob(),basis_capability_id='BASIS',basis_obligation=bob(),evidence_id='MS2010-OUT-'+tag,capture_id='MS2010-CAP-OUT-'+tag);assert o['status']=='ACTION_OUTCOME_OBSERVED',o

def run_ms2010():
    td,m,calls,bid,ba,bb=_setup(False);world=PrefixWorld()
    try:
        _attach_history(m,world);_raw(m,'0');_execute(m,'P0','0');_raw(m,'1');_execute(m,'P1','1');_raw(m,'2')
        # restore current regulatory pressure after the historical prefix; epoch remains exact.
        m.observe_value_state('V',-1.0)
        prefix=m.derive_current_owned_opaque_probe_prefix(max_steps=2);assert prefix['status']=='CURRENT_OWNED_OPAQUE_PROBE_PREFIX',prefix
        assert prefix['opaque_action_sequence']==('P0','P1') and prefix['raw_samples']==tuple(tuple(str(x) for x in row) for row in UNIQUE_A[:3]),prefix
        live=m.derive_current_partial_operational_referent_ambiguity(bid,max_probe_steps=2,max_records=1024);assert live['status']=='CURRENT_PARTIAL_OPERATIONAL_REFERENT_AMBIGUITY',live
        assert set(live['surviving_bucket_ids'])=={ba,bb} and live['informative_probe_status']=='CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE' and live['unique_probe_action_id']=='P2',live
        binding=m.action_outcome_learning.projection_conditioned_bindings[bid];hyp=projection_conditioned_hypothesis_surface_digest(binding,m.action_outcome_learning.relations)
        cand=next(x for x in live['informative_candidates'] if x['action_id']=='P2')
        disc=action_result_digest({'hypothesis':hyp,'survivors':list(live['surviving_bucket_ids']),'probe':'P2','partition':cand['predicted_response_partition']})
        ue=m.append_evidence('MS2010-E-U',{'kind':'OWNED_PARTIAL_REFERENT_DECISION_AMBIGUITY','binding_id':bid},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED-MS2010')
        d=m.record_action_limited_unknown(deficit_id='MS2010-D',question_key='ref-'+disc[:16],hypothesis_digest_sha256=hyp,unknown_evidence_id=ue.evidence_id,missing_discriminator_signature_sha256=disc,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),EpistemicCurrentnessAnchor('PROJECTION',binding.projection_id,binding.projection_epoch)),assistance_ancestry=('DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY','QUALIFIED_ROUTING_SURFACE','NO_CALLER_ALTERNATIVE_SET'))
        surface=m.derive_current_owned_referent_decision_surface(d.deficit_id,max_probe_steps=2,max_records=1024);assert surface['status']=='CURRENT_OWNED_REFERENT_DECISION_SURFACE',surface
        assert surface['unique_probe_action_id']=='P2' and len(surface['relation_sets'])==2 and len(surface['source_relation_digests'])==2,surface
        # Forged copied identity is not enough: exact current discriminator content is rederived.
        ue2=m.append_evidence('MS2010-E-U-BAD',{'kind':'FORGED_REFERENT_DEFICIT'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS2010-HOSTILE')
        bad=m.record_action_limited_unknown(deficit_id='MS2010-D-BAD',question_key='bad',hypothesis_digest_sha256=hyp,unknown_evidence_id=ue2.evidence_id,missing_discriminator_signature_sha256='f'*64,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),EpistemicCurrentnessAnchor('PROJECTION',binding.projection_id,binding.projection_epoch)),assistance_ancestry=('DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY','QUALIFIED_ROUTING_SURFACE'))
        rejected=m.derive_current_owned_referent_decision_surface(bad.deficit_id,max_probe_steps=2,max_records=1024);assert rejected['status']=='DEFER_UNKNOWN' and rejected['reason']=='CURRENT_REFERENT_DISCRIMINATOR_CONTENT_DRIFT',rejected
        return {'status':'PASS','prefix_actions':list(prefix['opaque_action_sequence']),'surviving_buckets':list(live['surviving_bucket_ids']),'unique_probe':'P2','source_relation_digest_count':len(surface['source_relation_digests']),'forged_discriminator':rejected['reason'],'handler_calls':calls,'execution_authority':'NONE','truth_authority':'NONE'}
    finally:_close(m);td.cleanup()

def main():print(json.dumps(run_ms2010(),indent=2,sort_keys=True))
if __name__=='__main__':main()
