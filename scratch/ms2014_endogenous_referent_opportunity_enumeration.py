from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path
from typing import Any
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Authority,CapabilityContract,EpistemicStatus,QualificationState
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier,projection_conditioned_hypothesis_surface_digest
from microseed.development.epistemic import EpistemicCurrentnessAnchor,EpistemicDeficitRecord
from microseed.development.epistemic_action import EpistemicDecisionBearingContext,derive_current_grounded_feasibility_surface,derive_current_decision_bearing_commitment_from_grounded_surface,derive_current_program_discrimination_commitment,derive_epistemic_program_step_commitment
from microseed.development.epistemic_program import GeneratedEpistemicProgramCandidate,begin_generated_epistemic_program_trial
from microseed.runtime.entity import action_result_digest
from scratch.ms2005_bounded_referent_probe_reconstruction import ACTIONS,UNIQUE_A,_samples_from_boundaries,_persist_context
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _setup,_close,_relation,act_ob
from scratch.ms2010_runtime_owned_referent_decision_surface import PrefixWorld,_attach_history,_raw,_execute

P4_D=_samples_from_boundaries(((1,),(1,),(2,5),(2,5)),len(ACTIONS))

def _opportunity_for_binding(m,binding,obligation,max_probe_steps=2,max_records=2048):
    live=m.derive_current_partial_operational_referent_ambiguity(binding.binding_id,max_probe_steps=max_probe_steps,max_records=max_records)
    if live.get('status')!='CURRENT_PARTIAL_OPERATIONAL_REFERENT_AMBIGUITY' or live.get('informative_probe_status')!='CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE': return None
    probe=str(live['unique_probe_action_id']);hyp=projection_conditioned_hypothesis_surface_digest(binding,m.action_outcome_learning.relations)
    cand=next(x for x in live['informative_candidates'] if x['action_id']==probe)
    disc=action_result_digest({'hypothesis':hyp,'survivors':list(live['surviving_bucket_ids']),'probe':probe,'partition':cand['predicted_response_partition']})
    sets=[];probe_digests=[];value_epochs=set();frame_epochs=set()
    for bucket in live['surviving_bucket_ids']:
        rows=[]
        for action in binding.action_ids:
            rid=binding.relation_id_for(str(bucket),str(action));rel=m.action_outcome_learning.relations.get(str(rid)) if rid else None
            if rel is None or not m._action_outcome_relation_current(rel): return None
            edge=rel.as_epistemic_alternative_relation()
            if edge is None:return None
            rows.append(edge)
            if edge.value_epoch is not None:value_epochs.add(tuple(edge.value_epoch))
            frame_epochs.add(tuple(edge.frame_epoch))
            if str(action)==probe:probe_digests.append(edge.digest())
        sets.append(tuple(rows))
    if len(value_epochs)!=1:return None
    value_id,value_epoch=next(iter(value_epochs))
    if not m.values.is_current(value_id,value_epoch):return None
    raw_ids=tuple(live['probe_prefix']['raw_observation_evidence_ids']); unknown_eid=raw_ids[-1] if raw_ids else ''
    content={'hypothesis':hyp,'discriminator':disc,'value_epoch':[value_id,value_epoch],'probe':probe,'probe_sources':sorted(set(probe_digests)),'survivors':list(live['surviving_bucket_ids'])}
    oid='owned-referent-opportunity-'+action_result_digest(content)[:24]
    deficit=EpistemicDeficitRecord(deficit_id=oid,question_key='opaque-referent-'+disc[:24],hypothesis_digest_sha256=hyp,unknown_evidence_id=unknown_eid,missing_discriminator_signature_sha256=disc,premise_anchors=(EpistemicCurrentnessAnchor('VALUE',value_id,value_epoch),EpistemicCurrentnessAnchor('PROJECTION',binding.projection_id,binding.projection_epoch)),assistance_ancestry=('DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY','QUALIFIED_ROUTING_SURFACE','NO_CALLER_BINDING_OR_DEFICIT'))
    candidate=GeneratedEpistemicProgramCandidate('owned-referent-program-'+action_result_digest({'opportunity':oid,'probe':probe})[:24],(probe,),tuple(sorted(set(probe_digests))),tuple(sorted(frame_epochs)),assistance_ancestry=('OWNED_REFERENT_DECISION_SURFACE','UNIQUE_INFORMATIVE_PROBE'))
    try:trial=begin_generated_epistemic_program_trial(candidate,deficit_id=deficit.deficit_id,discrimination_signature_sha256=disc,capabilities=m.capabilities,obligation=obligation,current_frame_epochs=dict(m.frames.epochs),start_state_id=m.action_closure.current_state.state_id,start_state_evidence_id=m.action_closure.current_state.evidence_id)
    except ValueError:return None
    dc=EpistemicDecisionBearingContext(tuple(sets),())
    opts,basis=derive_current_grounded_feasibility_surface(capabilities=m.capabilities,operational_scope_id=obligation.operational_scope_id)
    first=trial.steps[0]; option=next((x for x in opts if x.capability_id==first),None)
    if option is None:return None
    priority=derive_current_decision_bearing_commitment_from_grounded_surface(trial=trial,deficit=deficit,decision_context=dc,feasibility_options=opts,capabilities=m.capabilities,values=m.values,current_frame_epochs=dict(m.frames.epochs),current_episode_epochs=dict(m.episodes.epochs),current_topology_epochs=dict(m.topologies.epochs),current_coordination_epochs=dict(m.coordinations.epochs))
    if not priority.licenses_yes():return None
    info=derive_current_program_discrimination_commitment(trial=trial,decision_context=dc,decision_bearing_commitment=priority)
    if not info.licenses_yes():return None
    cmt=derive_epistemic_program_step_commitment(trial=trial,deficit=deficit,feasibility=option,capabilities=m.capabilities,obligation=obligation,current_frame_epochs=dict(m.frames.epochs),current_state=m.action_closure.current_state,priority_commitment=priority,information_commitment=info)
    if not cmt.licenses_yes():return None
    return {'opportunity_id':oid,'content_signature_sha256':action_result_digest(content),'binding_id':binding.binding_id,'probe_action_id':probe,'value_epoch':(value_id,value_epoch),'surviving_bucket_ids':tuple(live['surviving_bucket_ids']),'deficit':deficit,'candidate':candidate,'trial':trial,'decision_context':dc,'priority':priority,'information':info,'commitment':cmt,'selection_authority':'NONE','execution_authority':'NONE'}

def enumerate_current_owned_referent_opportunities(m,obligation):
    coord=m.operational_referent_class_set_projection_signature_sha256();rows=[]
    for binding in sorted(m.action_outcome_learning.projection_conditioned_bindings.values(),key=lambda b:b.binding_id):
        rec=m.epistemic_projections.records.get(binding.projection_id)
        if rec is None or rec.signature_sha256!=coord or not m._projection_conditioned_binding_current(binding):continue
        op=_opportunity_for_binding(m,binding,obligation)
        if op is not None:rows.append(op)
    # content-equivalent duplicate bindings are witnesses of one opportunity, not two opportunities.
    by_content={}
    for op in rows:by_content.setdefault(op['content_signature_sha256'],[]).append(op)
    collapsed=[]
    for sig,group in sorted(by_content.items()):
        rep=sorted(group,key=lambda x:x['binding_id'])[0];collapsed.append({**rep,'equivalent_binding_ids':tuple(sorted(x['binding_id'] for x in group))})
    if not collapsed:return {'status':'NO_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY','opportunities':(), 'selection_authority':'NONE'}
    probes=tuple(sorted(set(x['probe_action_id'] for x in collapsed)))
    if len(collapsed)==1:return {'status':'CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY','opportunities':tuple(collapsed),'probe_action_ids':probes,'selection_authority':'CONTENT_UNIQUENESS_ONLY','execution_authority':'NONE'}
    if len(probes)==1:return {'status':'MULTIPLE_REFERENT_PRESSURES_SHARED_PROBE','opportunities':tuple(collapsed),'probe_action_ids':probes,'selection_authority':'SHARED_ACTION_COMPOSITION_ONLY','execution_authority':'NONE'}
    return {'status':'MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES','reason':'NO_CROSS_DEFICIT_SELECTION_AUTHORITY','opportunities':tuple(collapsed),'probe_action_ids':probes,'selection_authority':'NONE','execution_authority':'NONE'}

def _generic_holdouts(m,projection,task,bucket,rels,tag):
    refs=[]
    for action,rel in rels.items():
        for i in range(12):
            refs.append(m.append_evidence(f'MS2014-H-{tag}-{action}-{i}',{'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':projection.projection_id,'projection_epoch':projection.epoch,'projection_signature_sha256':projection.signature_sha256,'task_id':task,'horizon':1,'action_id':action,'channel_id':'opaque-control','projection_bucket_id':bucket,'actual_next_state_id':rel.next_state_id,'actual_value_effect':rel.value_effect},EpistemicStatus.PRESSURE_SUPPORTED,source='MS2014-HOLDOUT'))
    return refs

def _second_binding(m,projection,ba,bd):
    # Independent downstream decision pair C/D, unique referent probe P4.
    for cid in ('C','D','P4'):
        if cid not in m.capabilities.contracts:
            m.register_capability(CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS2014',),'CURRENT',{},query_obligation_id='MS2008-ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:{'receipt':_cid},operational_scope_id='S'))
            m.register_capability(CapabilityContract('FEAS-'+cid,'feas',{'target_capability_id':cid},{},(),(),Authority.DERIVED_READ_ONLY,('MS2014',),'CURRENT',{},dependencies=(cid,),query_obligation_id='MS2008-FEAS-'+cid,qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'feasibility':'FEASIBLE','reason':'CURRENT'},operational_scope_id='S'))
    rel_a={'C':_relation(m,'R2-A-C','C','c-next',2.0,'2AC'),'D':_relation(m,'R2-A-D','D','d-next',0.0,'2AD'),'P4':_relation(m,'R2-A-P4','P4','p4-a',0.0,'2AP')}
    rel_d={'C':_relation(m,'R2-D-C','C','c-next-d',0.0,'2DC'),'D':_relation(m,'R2-D-D','D','d-next-d',2.0,'2DD'),'P4':_relation(m,'R2-D-P4','P4','p4-d',0.0,'2DP')}
    prop=m.append_evidence('MS2014-ROUTE2-PROP',{'kind':'ROUTING_PROPOSAL','basis':'SECOND_OWNED_REFERENT_DECISION_SURFACE'},EpistemicStatus.PRESSURE_SUPPORTED,source='MS2014')
    route=m.nominate_projection_conditioned_relation_routing(projection_id=projection.projection_id,task_id='MS2014-DECISION-2',action_ids=('C','D','P4'),channel_ids=('opaque-control',),horizon=1,default_action_relations=tuple((a,rel_a[a].relation_id) for a in ('C','D','P4')),bucket_action_overrides=tuple((bd,a,rel_d[a].relation_id) for a in ('C','D','P4')),source_evidence_ids=(prop.evidence_id,))
    refs=_generic_holdouts(m,projection,'MS2014-DECISION-2',ba,rel_a,'A')+_generic_holdouts(m,projection,'MS2014-DECISION-2',bd,rel_d,'D')
    ticket=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='EXTERNAL-MS2014-ROUTE2').qualify(route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations,min_support=12,min_accuracy=.95)
    admitted=m.qualify_projection_conditioned_relation_routing(ticket);assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',admitted
    return str(admitted['binding']['binding_id'])

def _base_fixture():
    td,m,calls,bid,ba,bb=_setup(False);world=PrefixWorld();_attach_history(m,world);_raw(m,'0');_execute(m,'P0','0');_raw(m,'1');_execute(m,'P1','1');_raw(m,'2');m.observe_value_state('V',-1.0);return td,m,bid,ba,bb

def run_unique():
    td,m,bid,ba,bb=_base_fixture()
    try:
        r=enumerate_current_owned_referent_opportunities(m,act_ob());assert r['status']=='CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY',r
        op=r['opportunities'][0];assert op['probe_action_id']=='P2' and op['binding_id']==bid,op
        return {'status':'PASS','enumeration_status':r['status'],'probe_action_ids':list(r['probe_action_ids']),'opportunity_count':len(r['opportunities']),'caller_supplied_binding_id':'NO','caller_supplied_deficit_id':'NO'}
    finally:_close(m);td.cleanup()

def run_multiple():
    td,m,bid,ba,bb=_base_fixture()
    try:
        cd=_persist_context(m,'MS2014-D',P4_D);bd=str(cd['projection_bucket_id']);projection=m.epistemic_projections.records[m.action_outcome_learning.projection_conditioned_bindings[bid].projection_id]
        bid2=_second_binding(m,projection,ba,bd)
        r=enumerate_current_owned_referent_opportunities(m,act_ob());assert r['status']=='MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES',r
        assert set(r['probe_action_ids'])=={'P2','P4'},r
        return {'status':'BLOCKED_AS_DESIGNED','enumeration_status':r['status'],'reason':r['reason'],'probe_action_ids':list(r['probe_action_ids']),'opportunity_count':len(r['opportunities']),'binding_ids':[x['binding_id'] for x in r['opportunities']],'selection_authority':r['selection_authority'],'existing_candidate_arbitration_scope':'SINGLE_DEFICIT_ONLY'}
    finally:_close(m);td.cleanup()

def main():print(json.dumps({'unique':run_unique(),'multiple':run_multiple()},indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
