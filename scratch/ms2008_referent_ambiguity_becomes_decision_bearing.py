from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path
from typing import Any
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus, Microseed, Observation,
    OperationalFrameContract, QualificationState, QueryObligation, ValueVariableContract,
)
from microseed.development.action_learning import (
    ExternalProjectionConditionedRelationQualifier, QualifiedActionOutcomePredictiveRelation,
    projection_conditioned_hypothesis_surface_digest,
)
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext, derive_current_decision_bearing_commitment_from_grounded_surface,
    derive_current_grounded_feasibility_surface, derive_current_program_discrimination_commitment,
)
from microseed.development.epistemic_program import GeneratedEpistemicProgramCandidate, begin_generated_epistemic_program_trial
from microseed.runtime.entity import action_result_digest
from scratch.ms2005_bounded_referent_probe_reconstruction import ACTIONS, UNIQUE_A, UNIQUE_B, _persist_context, _close
from scratch.ms2007_partial_referent_ambiguity_from_owned_history import derive_current_partial_referent_ambiguity

ACTS=('A','B','P2')

def act_ob(): return QueryObligation('MS2008-ACT','opaque action',Authority.EFFECT,operational_scope_id='S')
def fob(cid): return QueryObligation('MS2008-FEAS-'+cid,'feas:'+cid,Authority.DERIVED_READ_ONLY,operational_scope_id='S')

def _relation(ms,rid,cid,next_state,effect,tag):
    for eid in (f'SRC-{rid}',f'QUAL-{rid}'):
        if ms.evidence.get(eid) is None: ms.append_evidence(eid,{'kind':'MS2008_RELATION_ANCESTRY','id':eid},EpistemicStatus.PRESSURE_SUPPORTED,source='MS2008')
    r=QualifiedActionOutcomePredictiveRelation(
        relation_id=rid,candidate_id='C-'+rid,candidate_sha256=hashlib.sha256(('cand:'+rid).encode()).hexdigest(),
        start_state_id='s0',capability_id=cid,next_state_id=next_state,value_effect=float(effect),support=24,consistency=1.0,
        source_evidence_ids=(f'SRC-{rid}',),qualification_evidence_ids=(f'QUAL-{rid}',),holdout_support=12,holdout_accuracy=1.0,
        capability_epoch=ms.capabilities.epochs[cid],frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
    );ms.action_outcome_learning.add_relation(r);return r

def _holdout(ms,projection,bucket,action,relation,tag):
    refs=[]
    for i in range(12):
        refs.append(ms.append_evidence(f'H-{tag}-{i}',{
            'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':projection.projection_id,'projection_epoch':projection.epoch,
            'projection_signature_sha256':projection.signature_sha256,'task_id':'MS2008-DECISION','horizon':1,'action_id':action,'channel_id':'opaque-control',
            'projection_bucket_id':bucket,'actual_next_state_id':relation.next_state_id,'actual_value_effect':relation.value_effect,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='MS2008-HOLDOUT'))
    return refs

def _qualify(ms,projection,ba,bb,rels_a,rels_b):
    prop=ms.append_evidence('MS2008-ROUTE-PROP',{'kind':'ROUTING_PROPOSAL','basis':'OWNED_REFERENT_DECISION_SURFACE'},EpistemicStatus.PRESSURE_SUPPORTED,source='MS2008')
    route=ms.nominate_projection_conditioned_relation_routing(
        projection_id=projection.projection_id,task_id='MS2008-DECISION',action_ids=ACTS,channel_ids=('opaque-control',),horizon=1,
        default_action_relations=tuple((a,rels_a[a].relation_id) for a in ACTS),
        bucket_action_overrides=tuple((bb,a,rels_b[a].relation_id) for a in ACTS),source_evidence_ids=(prop.evidence_id,),
    )
    refs=[]
    for bucket,tag,rels in ((ba,'A',rels_a),(bb,'B',rels_b)):
        for a in ACTS: refs.extend(_holdout(ms,projection,bucket,a,rels[a],tag+'-'+a))
    ticket=ExternalProjectionConditionedRelationQualifier(ms.evidence,qualifier_id='EXTERNAL-MS2008').qualify(
        route,qualification_evidence=tuple(refs),relations=ms.action_outcome_learning.relations,min_support=12,min_accuracy=.95)
    admitted=ms.qualify_projection_conditioned_relation_routing(ticket);assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',admitted
    return str(admitted['binding']['binding_id'])

def _setup(same_downstream=False):
    td=tempfile.TemporaryDirectory(prefix='ms2008-decision-');m=Microseed(Path(td.name));calls=[]
    m.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS2008',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','reg',0,10,'v'*64,Authority.REFERENCE_ONLY,('MS2008',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED));m.observe_value_state('V',-1.0)
    m.register_episode_schema(EpisodeSchemaContract('EP','opaque-episode','e'*64,Authority.DERIVED_READ_ONLY,('MS2008',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    for cid in ACTS:
        m.register_capability(CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS2008',),'CURRENT',{},query_obligation_id='MS2008-ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:calls.append(_cid) or {'receipt':_cid},operational_scope_id='S'))
        m.register_capability(CapabilityContract('FEAS-'+cid,'feas',{'target_capability_id':cid},{},(),(),Authority.DERIVED_READ_ONLY,('MS2008',),'CURRENT',{},dependencies=(cid,),query_obligation_id='MS2008-FEAS-'+cid,qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'feasibility':'FEASIBLE','reason':'CURRENT'},operational_scope_id='S'))
    ca=_persist_context(m,'MS2008-A',UNIQUE_A);cb=_persist_context(m,'MS2008-B',UNIQUE_B);ba=str(ca['projection_bucket_id']);bb=str(cb['projection_bucket_id'])
    projection=m.register_epistemic_projection('MS2008-REFSET',m.operational_referent_class_set_projection_signature_sha256(),assistance_ancestry=('SUPPLIED_OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_COORDINATE','NO_SEMANTIC_REFERENT_AUTHORITY'))
    aeff=(2.0,0.0);beff=(2.0,0.0) if same_downstream else (0.0,2.0)
    rels_a={'A':_relation(m,'R-A-A','A','a-next',aeff[0],'AA'),'B':_relation(m,'R-A-B','B','b-next',aeff[1],'AB'),'P2':_relation(m,'R-A-P2','P2','probe-a',0,'AP')}
    rels_b={'A':_relation(m,'R-B-A','A','a-next-b',beff[0],'BA'),'B':_relation(m,'R-B-B','B','b-next-b',beff[1],'BB'),'P2':_relation(m,'R-B-P2','P2','probe-b',0,'BP')}
    bid=_qualify(m,projection,ba,bb,rels_a,rels_b)
    m.observe_opaque_control_state(Observation('MS2008-CS','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='MS2008-E-CS')
    return td,m,calls,bid,ba,bb

def derive_owned_referent_decision_context(m,binding_id,partial_samples,observed_actions):
    live=derive_current_partial_referent_ambiguity(m,binding_id,partial_samples,observed_actions,max_records=512)
    if live.get('status')!='CURRENT_PARTIAL_REFERENT_CLASS_SET_AMBIGUITY': return {'status':'ABSTAIN','reason':live.get('status'),'live':live}
    binding=m.action_outcome_learning.projection_conditioned_bindings[str(binding_id)]
    sets=[];digests=[]
    for bucket in live['surviving_bucket_ids']:
        rows=[]
        for action in binding.action_ids:
            rid=binding.relation_id_for(str(bucket),str(action));rel=m.action_outcome_learning.relations.get(str(rid)) if rid else None
            if rel is None or not m._action_outcome_relation_current(rel): return {'status':'ABSTAIN','reason':'ROUTED_RELATION_NOT_CURRENT','bucket':bucket,'action':action}
            edge=rel.as_epistemic_alternative_relation()
            if edge is None:return {'status':'ABSTAIN','reason':'ROUTED_RELATION_NOT_LOSSLESS_EPISTEMIC_EDGE','relation_id':rid}
            rows.append(edge);digests.append(edge.digest())
        sets.append(tuple(rows))
    return {'status':'CURRENT_OWNED_REFERENT_DECISION_SURFACE','live':live,'decision_context':EpistemicDecisionBearingContext(tuple(sets),()),'source_relation_digests':tuple(sorted(set(digests))),'truth_authority':'NONE','execution_authority':'NONE'}

def _content_sha(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

def run_ms2008(same_downstream=False)->dict[str,Any]:
    td,m,calls,bid,ba,bb=_setup(same_downstream=same_downstream)
    try:
        owned=derive_owned_referent_decision_context(m,bid,UNIQUE_A[:3],('P0','P1'));assert owned['status']=='CURRENT_OWNED_REFERENT_DECISION_SURFACE',owned
        live=owned['live'];probe=live['probe_surface'];assert probe['status']=='CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE' and probe['probe_action_id']=='P2',probe
        binding=m.action_outcome_learning.projection_conditioned_bindings[bid]
        hyp=projection_conditioned_hypothesis_surface_digest(binding,m.action_outcome_learning.relations)
        disc=_content_sha({'hypothesis':hyp,'survivors':list(live['surviving_bucket_ids']),'probe':'P2','partition':probe['informative_candidates'][0]['predicted_response_partition']})
        ue=m.append_evidence('MS2008-E-U',{'kind':'OWNED_PARTIAL_REFERENT_DECISION_AMBIGUITY','binding_id':bid,'survivors':list(live['surviving_bucket_ids']),'observed_actions':['P0','P1']},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED-MS2008')
        deficit=m.record_action_limited_unknown(deficit_id='MS2008-D',question_key='opaque-ref-decision-'+disc[:16],hypothesis_digest_sha256=hyp,unknown_evidence_id=ue.evidence_id,missing_discriminator_signature_sha256=disc,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),EpistemicCurrentnessAnchor('PROJECTION',binding.projection_id,binding.projection_epoch)),assistance_ancestry=('DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY','QUALIFIED_ROUTING_SURFACE','NO_CALLER_ALTERNATIVE_SET'))
        # Program candidate uses exactly the P2 edges from each live owned alternative, not all downstream edges.
        p2dig=[]
        for rows in owned['decision_context'].relation_sets:
            edge=next(r for r in rows if r.state_id=='s0' and r.capability_id=='P2');p2dig.append(edge.digest())
        candidate=GeneratedEpistemicProgramCandidate('MS2008-P2-CAND',('P2',),tuple(sorted(set(p2dig))),(('F',0),),assistance_ancestry=('OWNED_REFERENT_DECISION_SURFACE','UNIQUE_INFORMATIVE_P2'))
        trial=begin_generated_epistemic_program_trial(candidate,deficit_id=deficit.deficit_id,discrimination_signature_sha256=disc,capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),start_state_id='s0',start_state_evidence_id='MS2008-E-CS')
        opts,_=derive_current_grounded_feasibility_surface(capabilities=m.capabilities,operational_scope_id='S')
        priority=derive_current_decision_bearing_commitment_from_grounded_surface(trial=trial,deficit=deficit,decision_context=owned['decision_context'],feasibility_options=opts,capabilities=m.capabilities,values=m.values,current_frame_epochs=dict(m.frames.epochs),current_episode_epochs=dict(m.episodes.epochs),current_topology_epochs=dict(m.topologies.epochs),current_coordination_epochs=dict(m.coordinations.epochs))
        info=derive_current_program_discrimination_commitment(trial=trial,decision_context=owned['decision_context'],decision_bearing_commitment=priority)
        nomination=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial,owned['decision_context'],act_ob())
        if same_downstream:
            assert not priority.licenses_yes(),priority.serializable();assert nomination['status']=='ABSTAIN',nomination
            return {'status':'PASS','same_downstream_priority':priority.serializable(),'nomination_status':nomination['status'],'calls':calls}
        assert priority.licenses_yes(),priority.serializable();assert set(priority.qualifier('first_actions').split('|'))=={'A','B'},priority.serializable()
        assert info.licenses_yes() and info.reason=='PROGRAM_CAN_CHANGE_OBSERVABLE_EVIDENCE',info.serializable()
        assert nomination['status']=='ACTION_INTENT_NOMINATED',nomination;assert nomination['intent']['capability_id']=='P2';assert calls==[]
        return {'status':'PASS','surviving_buckets':list(live['surviving_bucket_ids']),'priority':priority.serializable(),'information':info.serializable(),'nominated_capability_id':'P2','handler_calls':calls,'caller_supplied_decision_alternatives':'NO','execution_authority':'NONE','truth_authority':'NONE'}
    finally:_close(m);td.cleanup()

def main():print(json.dumps({'decision_bearing':run_ms2008(False),'same_decision_negative':run_ms2008(True)},indent=2,sort_keys=True))
if __name__=='__main__':main()
