from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Authority,EpistemicStatus,Observation
from microseed.development.action_learning import projection_conditioned_hypothesis_surface_digest
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_action import EpistemicDecisionBearingContext,EpistemicStepExecutionContext
from microseed.development.epistemic_program import GeneratedEpistemicProgramCandidate,begin_generated_epistemic_program_trial,advance_epistemic_program_trial
from microseed.runtime.entity import action_result_digest
from scratch.ms2005_bounded_referent_probe_reconstruction import UNIQUE_A
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _setup,_close,act_ob
from scratch.ms2010_runtime_owned_referent_decision_surface import _attach_history,_raw,_execute,oob,bob

class ProbeObservationWorld:
    def __init__(self,calls): self.calls=calls;self.index=0;self.value=-1.0
    def apply(self,action):
        expected=('P0','P1')[self.index];assert action==expected,(action,expected,self.index)
        self.index+=1;self.value+=.5;return {'receipt':action}
    def observe(self):
        if self.calls and self.calls[-1]=='P2':
            return {'next_state_id':'probe-a','raw_tokens':[str(x) for x in UNIQUE_A[3]]}
        return {'next_state_id':'s0','value_id':'V','observed_value':self.value,'raw_tokens':[str(x) for x in UNIQUE_A[self.index]]}

def _epistemic_fixture():
    td,m,calls,bid,ba,bb=_setup(False);world=ProbeObservationWorld(calls);_attach_history(m,world);m.frames.bind_capability('F','P2')
    _raw(m,'0');_execute(m,'P0','0');_raw(m,'1');_execute(m,'P1','1');_raw(m,'2');m.observe_value_state('V',-1.0)
    live=m.derive_current_partial_operational_referent_ambiguity(bid,max_probe_steps=2,max_records=1024);assert live['status']=='CURRENT_PARTIAL_OPERATIONAL_REFERENT_AMBIGUITY',live
    binding=m.action_outcome_learning.projection_conditioned_bindings[bid];hyp=projection_conditioned_hypothesis_surface_digest(binding,m.action_outcome_learning.relations)
    cand=next(x for x in live['informative_candidates'] if x['action_id']=='P2')
    disc=action_result_digest({'hypothesis':hyp,'survivors':list(live['surviving_bucket_ids']),'probe':'P2','partition':cand['predicted_response_partition']})
    ue=m.append_evidence('MS2012-E-U',{'kind':'OWNED_PARTIAL_REFERENT_DECISION_AMBIGUITY','binding_id':bid},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED-MS2012')
    d=m.record_action_limited_unknown(deficit_id='MS2012-D',question_key='ref-'+disc[:16],hypothesis_digest_sha256=hyp,unknown_evidence_id=ue.evidence_id,missing_discriminator_signature_sha256=disc,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),EpistemicCurrentnessAnchor('PROJECTION',binding.projection_id,binding.projection_epoch)),assistance_ancestry=('DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY','QUALIFIED_ROUTING_SURFACE','NO_CALLER_ALTERNATIVE_SET'))
    surface=m.derive_current_owned_referent_decision_surface(d.deficit_id,max_probe_steps=2,max_records=1024);assert surface['status']=='CURRENT_OWNED_REFERENT_DECISION_SURFACE',surface
    candidate=GeneratedEpistemicProgramCandidate('MS2012-P2-CAND',('P2',),tuple(surface['source_relation_digests']),(('F',0),),assistance_ancestry=('OWNED_REFERENT_DECISION_SURFACE','UNIQUE_INFORMATIVE_P2'))
    trial=begin_generated_epistemic_program_trial(candidate,deficit_id=d.deficit_id,discrimination_signature_sha256=disc,capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),start_state_id='s0',start_state_evidence_id=m.action_closure.current_state.evidence_id)
    dc=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())
    n=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial,dc,act_ob());assert n['status']=='ACTION_INTENT_NOMINATED',n
    x=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=EpistemicStepExecutionContext(trial,decision_context=EpistemicDecisionBearingContext((surface['relation_sets'][0],surface['relation_sets'][0]),())))
    assert x['status']=='ACTION_EXECUTED',x;assert calls==['P2'],calls
    return td,m,calls,world,bid,ba,bb,trial,dc,n,x

def _advance(m,trial,n,x):
    eid=x['execution']['execution_id'];intent=m.action_closure.intents[n['intent']['intent_id']];execution=m.action_closure.executions[eid];outcome=next(o for o in m.action_closure.outcomes.values() if o.execution_id==eid)
    advanced=advance_epistemic_program_trial(trial,intent=intent,execution=execution,outcome=outcome,capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs));assert advanced.status=='COMPLETE',advanced
    return advanced,outcome

def positive_authenticated():
    td,m,calls,world,bid,ba,bb,trial,dc,n,x=_epistemic_fixture()
    try:
        eid=x['execution']['execution_id']
        out=m.record_bounded_action_outcome_via_observation_basis(eid,observation_capability_id='OBS',observation_obligation=oob(),basis_capability_id='BASIS',basis_obligation=bob(),evidence_id='MS2012-E-P2-AUTH',capture_id='MS2012-C-P2-AUTH')
        assert out['status']=='ACTION_OUTCOME_OBSERVED',out;assert out['outcome']['actual_next_state_id']=='probe-a';assert out['outcome']['prediction_commitment']['commitment']=='UNKNOWN'
        admitted=m.derive_admitted_opaque_transition_sample(eid);assert admitted['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE',admitted
        raw=m.record_bounded_raw_observation_coordinates('OBS',oob(),evidence_id='MS2012-RAW-3',capture_id='MS2012-RAW-3',max_coordinates=8);assert raw['status']=='BOUNDED_RAW_OBSERVATION_RECORDED',raw
        prefix=m.derive_current_owned_opaque_probe_prefix(max_steps=3);assert prefix['status']=='CURRENT_OWNED_OPAQUE_PROBE_PREFIX',prefix;assert prefix['opaque_action_sequence']==('P0','P1','P2'),prefix
        resolved=m.derive_current_partial_operational_referent_ambiguity(bid,max_probe_steps=3,max_records=2048);assert resolved['status']=='CURRENT_PARTIAL_OPERATIONAL_REFERENT_RESOLVED',resolved;assert resolved['resolved_bucket_id']==ba,(resolved,ba)
        advanced,_=_advance(m,trial,n,x)
        complete=m.record_completed_epistemic_program_evidence(advanced,evidence_id='MS2012-E-COMPLETE-AUTH')
        return {'status':'PASS','admitted_status':admitted['status'],'prefix_actions':list(prefix['opaque_action_sequence']),'resolved_bucket_id':resolved['resolved_bucket_id'],'expected_bucket_id':ba,'program_evidence':complete,'truth_authority':complete.get('truth_authority'),'answer_authority':complete.get('answer_authority'),'execution_authority':complete.get('execution_authority')}
    finally:_close(m);td.cleanup()

def forged_unadmitted():
    td,m,calls,world,bid,ba,bb,trial,dc,n,x=_epistemic_fixture()
    try:
        eid=x['execution']['execution_id']
        forged=Observation('MS2012-C-FORGED','CAPABILITY:FAKE-OBS',f'action-execution:{eid}',{'next_state_id':'probe-a'},currentness_basis='QUALIFIED_OBSERVATION_CAPABILITY_AND_BOUNDED_USE_BASIS',authority=Authority.OBSERVATION_ONLY,lineage=('OBSERVATION_CAPABILITY:FAKE@0','OBSERVATION_USE_BASIS:FAKE@0'))
        raw=m.record_bounded_action_outcome(eid,forged,evidence_id='MS2012-E-P2-FORGED');assert raw['status']=='ACTION_OUTCOME_OBSERVED',raw
        admitted=m.derive_admitted_opaque_transition_sample(eid);assert admitted['status']=='ABSTAIN' and admitted['reason']=='AUTHENTICATED_OBSERVATION_INGRESS_REQUIRED',admitted
        advanced,_=_advance(m,trial,n,x)
        complete=m.record_completed_epistemic_program_evidence(advanced,evidence_id='MS2012-E-COMPLETE-FORGED')
        return {'status':'OBSERVED','admitted':admitted,'program_evidence':complete,'deficit_state':m.epistemic_deficits.records['MS2012-D'].state.value,'forged_program_evidence_accepted':complete.get('status')=='PROGRAM_EVIDENCE_RECORDED'}
    finally:_close(m);td.cleanup()

def run_ms2012_pre_repair():return {'authenticated':positive_authenticated(),'forged':forged_unadmitted()}
def main():print(json.dumps(run_ms2012_pre_repair(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
