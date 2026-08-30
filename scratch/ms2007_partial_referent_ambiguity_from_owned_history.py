from __future__ import annotations

import json, sys, tempfile
from pathlib import Path
from typing import Any, Iterable
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier, QualifiedActionOutcomePredictiveRelation
from microseed.runtime.types import Authority, CapabilityContract, EpistemicStatus, QualificationState, ValueVariableContract
from scratch.ms2003_operational_referent_class_set_routing import _holdouts
from scratch.ms2005_bounded_referent_probe_reconstruction import (
    ACTIONS, UNIQUE_A, UNIQUE_B, _persist_context, _close,
    _scan_owned_signature_classes, reconstruct_class_set_for_bucket,
    derive_informative_probe_candidates,
)


def _relation(ms:Microseed,rid:str,next_state:str,effect:float,tag:str)->QualifiedActionOutcomePredictiveRelation:
    r=QualifiedActionOutcomePredictiveRelation(
        relation_id=rid,candidate_id=f'C-{rid}',candidate_sha256=(tag.lower()*64)[:64],
        start_state_id='S0',capability_id='ACT',next_state_id=next_state,value_effect=effect,
        support=24,consistency=1.0,source_evidence_ids=(f'SRC-{tag}',),qualification_evidence_ids=(f'QUAL-{tag}',),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=ms.capabilities.epochs['ACT'],
        frame_epochs=(),episode_schema_epochs=(),value_epoch=('V',ms.values.epochs['V']),
    ); ms.action_outcome_learning.add_relation(r); return r


def _qualify(ms:Microseed,projection,bucket_a:str,bucket_b:str,ra,rb)->str:
    prop=ms.append_evidence('MS2007-ROUTE-PROP',{
        'kind':'ROUTING_PROPOSAL','basis':'OWNED_OPERATIONAL_REFERENT_CLASS_SET_CONTEXT',
        'identity_authority':'NONE','semantic_reference_authority':'NONE',
    },EpistemicStatus.PRESSURE_SUPPORTED,source='MS2007-PROPOSAL')
    route=ms.nominate_projection_conditioned_relation_routing(
        projection_id=projection.projection_id,task_id='MS2007-LIVE-REF',action_ids=('ACT',),channel_ids=('opaque-control',),horizon=1,
        default_action_relations=(('ACT',ra.relation_id),),bucket_action_overrides=((bucket_b,'ACT',rb.relation_id),),
        source_evidence_ids=(prop.evidence_id,),
    )
    refs=_holdouts(ms,projection,'MS2007-LIVE-REF',bucket_a,ra,'MS2007-A')+_holdouts(ms,projection,'MS2007-LIVE-REF',bucket_b,rb,'MS2007-B')
    ticket=ExternalProjectionConditionedRelationQualifier(ms.evidence,qualifier_id='EXTERNAL-MS2007-ROUTING').qualify(
        route,qualification_evidence=refs,relations=ms.action_outcome_learning.relations,min_support=12,min_accuracy=.95)
    admitted=ms.qualify_projection_conditioned_relation_routing(ticket)
    assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',admitted
    return str(admitted['binding']['binding_id'])


def _partial_response_multiset(ms:Microseed, samples, observed_actions:tuple[str,...]) -> tuple[tuple[tuple[str,tuple[bool,...]],...],...]:
    d=ms.derive_operational_referent_signatures_from_raw_trace(samples,observed_actions)
    if d.get('status')!='OPERATIONAL_REFERENT_SIGNATURES_DERIVED_FROM_RAW_TRACE':
        raise ValueError(str(d))
    rows=[]
    for sig in d['signature_classes']:
        rows.append(tuple((str(a),tuple(bool(x) for x in bits)) for a,bits in sig['action_response_rows']))
    return tuple(sorted(rows))


def _class_set_projection(class_set:Iterable[str], classes:dict[str,tuple[tuple[str,tuple[bool,...]],...]], observed_actions:tuple[str,...]):
    out=[]
    for sha in class_set:
        full=dict(classes[str(sha)])
        out.append(tuple((a,tuple(full[a])) for a in observed_actions))
    return tuple(sorted(out))


def derive_current_partial_referent_ambiguity(
    ms:Microseed,binding_id:str,current_partial_samples,observed_actions:Iterable[str],*,max_records:int=4096,
)->dict[str,Any]:
    observed=tuple(str(x) for x in observed_actions)
    base={'truth_authority':'NONE','identity_authority':'NONE','semantic_reference_authority':'NONE','selection_authority':'NONE','execution_authority':'NONE'}
    if not observed:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_PARTIAL_PROBE_ACTIONS_REQUIRED'}
    binding=ms.action_outcome_learning.projection_conditioned_bindings.get(str(binding_id))
    if binding is None or not ms._projection_conditioned_binding_current(binding):
        return {**base,'status':'DEFER_UNKNOWN','reason':'QUALIFIED_REFERENT_ROUTING_BINDING_NOT_CURRENT'}
    rec=ms.epistemic_projections.records.get(binding.projection_id)
    if rec is None or rec.signature_sha256!=ms.operational_referent_class_set_projection_signature_sha256():
        return {**base,'status':'DEFER_UNKNOWN','reason':'OPERATIONAL_REFERENT_CLASS_SET_COORDINATE_MISMATCH'}
    scan=_scan_owned_signature_classes(ms,max_records=max_records)
    if scan.get('status')!='SATURATED_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SCAN':
        return {**base,'status':'DEFER_UNKNOWN','reason':scan.get('status','SIGNATURE_SCAN_NOT_SATURATED')}
    try: current=_partial_response_multiset(ms,current_partial_samples,observed)
    except ValueError as exc:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_PARTIAL_REFERENT_TRACE_NOT_DERIVABLE','detail':str(exc)}
    survivors=[]; recon=[]
    for bucket in tuple(binding.qualified_bucket_ids):
        r=reconstruct_class_set_for_bucket(ms,str(bucket),max_records=max_records)
        if r.get('status')!='OPERATIONAL_REFERENT_CLASS_SET_RECONSTRUCTED':
            return {**base,'status':'DEFER_UNKNOWN','reason':'QUALIFIED_BUCKET_CLASS_SET_NOT_RECONSTRUCTED','bucket_id':str(bucket),'detail':r}
        cs=tuple(r['operational_signature_classes']); projected=_class_set_projection(cs,scan['classes'],observed)
        recon.append((str(bucket),cs,projected))
        if projected==current: survivors.append(str(bucket))
    if not survivors:
        return {**base,'status':'DEFER_UNKNOWN','reason':'NO_QUALIFIED_REFERENT_ALTERNATIVE_MATCHES_CURRENT_PARTIAL_TRACE','current_partial_response_multiset':current}
    common={**base,'qualified_bucket_count':len(binding.qualified_bucket_ids),'surviving_bucket_ids':tuple(sorted(survivors)),'observed_actions':observed,'current_partial_response_multiset':current}
    if len(survivors)==1:
        return {**common,'status':'CURRENT_PARTIAL_REFERENT_CLASS_SET_RESOLVED','resolved_bucket_id':survivors[0]}
    remaining=tuple(a for a in ACTIONS if a not in observed)
    probes=derive_informative_probe_candidates(ms,tuple(sorted(survivors)),remaining,max_records=max_records)
    return {**common,'status':'CURRENT_PARTIAL_REFERENT_CLASS_SET_AMBIGUITY','probe_surface':probes}


def _setup():
    td=tempfile.TemporaryDirectory(prefix='ms2007-live-ref-'); ms=Microseed(Path(td.name))
    ms.register_value_variable(ValueVariableContract('V','opaque regulatory coordinate',-1,1,'c'*64,Authority.REFERENCE_ONLY,('MS2007',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    ms.register_capability(CapabilityContract('ACT','opaque effect',{}, {},(),(),Authority.EFFECT,('MS2007',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda:None))
    for eid in ('SRC-A','QUAL-A','SRC-B','QUAL-B'):
        ms.append_evidence(eid,{'kind':'PREEXISTING_RELATION_ANCESTRY','id':eid},EpistemicStatus.PRESSURE_SUPPORTED,source='MS2007-PREQUALIFIED')
    ra=_relation(ms,'MS2007-REL-A','SA',-.5,'A'); rb=_relation(ms,'MS2007-REL-B','SB',.5,'B')
    ca=_persist_context(ms,'MS2007-A',UNIQUE_A); cb=_persist_context(ms,'MS2007-B',UNIQUE_B)
    projection=ms.register_epistemic_projection('MS2007-REFSET',ms.operational_referent_class_set_projection_signature_sha256(),assistance_ancestry=('SUPPLIED_OPAQUE_OPERATIONAL_SIGNATURE_CLASS_SET_COORDINATE','NO_SEMANTIC_REFERENT_AUTHORITY'))
    bid=_qualify(ms,projection,str(ca['projection_bucket_id']),str(cb['projection_bucket_id']),ra,rb)
    return td,ms,bid,str(ca['projection_bucket_id']),str(cb['projection_bucket_id'])


def run_ms2007()->dict[str,Any]:
    td,ms,bid,ba,bb=_setup()
    try:
        # Current live world is A, but only P0/P1 have been observed. A/B are not supplied to the derivation.
        partial2=UNIQUE_A[:3]
        live=derive_current_partial_referent_ambiguity(ms,bid,partial2,('P0','P1'),max_records=256)
        assert live['status']=='CURRENT_PARTIAL_REFERENT_CLASS_SET_AMBIGUITY',live
        assert set(live['surviving_bucket_ids'])=={ba,bb},live
        ps=live['probe_surface']; assert ps['status']=='CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE',ps
        assert ps['probe_action_id']=='P2' and [x['action_id'] for x in ps['informative_candidates']]==['P2'],ps
        # Admit P2 into current raw trace; only A remains.
        partial3=UNIQUE_A[:4]
        resolved=derive_current_partial_referent_ambiguity(ms,bid,partial3,('P0','P1','P2'),max_records=256)
        assert resolved['status']=='CURRENT_PARTIAL_REFERENT_CLASS_SET_RESOLVED',resolved
        assert resolved['resolved_bucket_id']==ba,resolved
        # No routing binding => caller cannot invent the historical alternative set.
        no_binding=derive_current_partial_referent_ambiguity(ms,'MISSING',partial2,('P0','P1'),max_records=256)
        assert no_binding['status']=='DEFER_UNKNOWN'
        return {
            'status':'PASS','binding_id':bid,'qualified_buckets':[ba,bb],
            'partial_survivors':list(live['surviving_bucket_ids']),'unique_probe_action_id':ps['probe_action_id'],
            'post_probe_resolved_bucket':resolved['resolved_bucket_id'],
            'caller_supplied_alternative_buckets':'NO','caller_supplied_referent_class':'NO','caller_supplied_probe_schedule':'NO',
            'truth_authority':'NONE','identity_authority':'NONE','semantic_reference_authority':'NONE','selection_authority':'NONE','execution_authority':'NONE',
        }
    finally:
        _close(ms); td.cleanup()


def main(): print(json.dumps(run_ms2007(),indent=2,sort_keys=True))
if __name__=='__main__': main()
