from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus
from microseed.development.action_learning import projection_conditioned_hypothesis_surface_digest
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_action import EpistemicDecisionBearingContext,EpistemicStepExecutionContext
from microseed.development.epistemic_program import GeneratedEpistemicProgramCandidate,begin_generated_epistemic_program_trial
from microseed.runtime.entity import action_result_digest
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _setup,_close,act_ob
from scratch.ms2010_runtime_owned_referent_decision_surface import PrefixWorld,_attach_history,_raw,_execute,oob

def fixture(*,forged_sources=False):
    td,m,calls,bid,ba,bb=_setup(False);world=PrefixWorld();_attach_history(m,world);_raw(m,'0');_execute(m,'P0','0');_raw(m,'1');_execute(m,'P1','1');_raw(m,'2');m.observe_value_state('V',-1.0)
    live=m.derive_current_partial_operational_referent_ambiguity(bid,max_probe_steps=2,max_records=1024);assert live['status']=='CURRENT_PARTIAL_OPERATIONAL_REFERENT_AMBIGUITY',live
    binding=m.action_outcome_learning.projection_conditioned_bindings[bid];hyp=projection_conditioned_hypothesis_surface_digest(binding,m.action_outcome_learning.relations)
    cand=next(x for x in live['informative_candidates'] if x['action_id']=='P2')
    disc=action_result_digest({'hypothesis':hyp,'survivors':list(live['surviving_bucket_ids']),'probe':'P2','partition':cand['predicted_response_partition']})
    ue=m.append_evidence('MS2011-E-U',{'kind':'OWNED_PARTIAL_REFERENT_DECISION_AMBIGUITY','binding_id':bid},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED-MS2011')
    d=m.record_action_limited_unknown(deficit_id='MS2011-D',question_key='ref-'+disc[:16],hypothesis_digest_sha256=hyp,unknown_evidence_id=ue.evidence_id,missing_discriminator_signature_sha256=disc,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),EpistemicCurrentnessAnchor('PROJECTION',binding.projection_id,binding.projection_epoch)),assistance_ancestry=('DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY','QUALIFIED_ROUTING_SURFACE','NO_CALLER_ALTERNATIVE_SET'))
    surface=m.derive_current_owned_referent_decision_surface(d.deficit_id,max_probe_steps=2,max_records=1024);assert surface['status']=='CURRENT_OWNED_REFERENT_DECISION_SURFACE',surface
    sources=('f'*64,) if forged_sources else tuple(surface['source_relation_digests'])
    candidate=GeneratedEpistemicProgramCandidate('MS2011-P2-CAND'+('-BAD' if forged_sources else ''),('P2',),sources,(('F',0),),assistance_ancestry=('OWNED_REFERENT_DECISION_SURFACE','UNIQUE_INFORMATIVE_P2'))
    trial=begin_generated_epistemic_program_trial(candidate,deficit_id=d.deficit_id,discrimination_signature_sha256=disc,capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),start_state_id='s0',start_state_evidence_id=m.action_closure.current_state.evidence_id)
    dc=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())
    nomination=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial,dc,act_ob())
    if not forged_sources: assert nomination['status']=='ACTION_INTENT_NOMINATED',nomination
    return td,m,calls,world,trial,surface,nomination

def run_success():
    td,m,calls,world,trial,surface,n=fixture()
    try:
        # Caller supplies a context that says both worlds are the same. Runtime must ignore it for this owned referent deficit.
        forged=EpistemicDecisionBearingContext((surface['relation_sets'][0],surface['relation_sets'][0]),())
        r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=EpistemicStepExecutionContext(trial,decision_context=forged))
        assert r['status']=='ACTION_EXECUTED',r;assert calls==['P2'],calls
        return {'status':'PASS','execution_status':r['status'],'calls':list(calls),'forged_caller_context_ignored':'YES','execution_commitment_id':r['execution']['execution_commitment_id']}
    finally:_close(m);td.cleanup()

def run_duplicate_raw_block():
    td,m,calls,world,trial,surface,n=fixture()
    try:
        dup=m.record_bounded_raw_observation_coordinates('OBS',oob(),evidence_id='MS2011-RAW-DUP',capture_id='MS2011-RAW-DUP',max_coordinates=8);assert dup['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=EpistemicStepExecutionContext(trial,decision_context=EpistemicDecisionBearingContext((surface['relation_sets'][0],surface['relation_sets'][0]),())))
        assert r['status']=='NO_EXECUTION' and calls==[],(r,calls)
        assert r['reason']=='CURRENT_OWNED_REFERENT_DECISION_SURFACE_REQUIRED_AT_EXECUTION',r
        return {'status':'PASS','reason':r['reason'],'calls':calls}
    finally:_close(m);td.cleanup()

def run_pressure_drift_block():
    td,m,calls,world,trial,surface,n=fixture()
    try:
        m.observe_value_state('V',5.0)
        r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=EpistemicStepExecutionContext(trial,decision_context=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())))
        assert r['status']=='NO_EXECUTION' and calls==[],(r,calls)
        return {'status':'PASS','reason':r['reason'],'calls':calls,'commitment':r.get('commitment')}
    finally:_close(m);td.cleanup()

def run_source_forgery_block():
    td,m,calls,world,trial,surface,n=fixture(forged_sources=True)
    try:
        assert n['status']=='ABSTAIN' and n['reason']=='PROGRAM_RELATION_ANCESTRY_MISMATCH' and calls==[],(n,calls)
        return {'status':'PASS','reason':n['reason'],'stage':'NOMINATION','calls':calls}
    finally:_close(m);td.cleanup()

def run_ms2011():return {'status':'PASS','success':run_success(),'duplicate_raw':run_duplicate_raw_block(),'pressure_drift':run_pressure_drift_block(),'source_forgery':run_source_forgery_block(),'new_executor_required':'NO','execution_path':'ORDINARY_EXECUTE_BOUNDED_ACTION'}
def main():print(json.dumps(run_ms2011(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
