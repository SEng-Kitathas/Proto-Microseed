from __future__ import annotations

import json, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, EpistemicStatus, ExternalProjectionQualifier, Observation,
    ProjectionDiscoveryConfig,
)
from microseed.development.action_learning import (
    ExternalProjectionConditionedRelationQualifier,
    QualifiedActionOutcomePredictiveRelation,
)
from scratch.ms1977_raw_coordinate_projection_boundary import PAIRS, World, build, obs_ob, proposals
from scratch.ms1978_owned_raw_coordinate_projection import execute_owned
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def add_relation(m,rid,end,effect,tag):
    train=f'{tag}-TRAIN'; qual=f'{tag}-QUAL'
    m.append_evidence(train,{'kind':'RELATION_TRAIN','id':rid},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1983-REL')
    m.append_evidence(qual,{'kind':'RELATION_QUAL','id':rid},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1983-REL-QUAL')
    r=QualifiedActionOutcomePredictiveRelation(
        relation_id=rid,candidate_id='C-'+rid,candidate_sha256=(('a' if end=='EVEN' else 'b')*64),
        start_state_id='ALIAS',capability_id='B',next_state_id=end,value_effect=float(effect),
        support=16,consistency=1.0,source_evidence_ids=(train,),qualification_evidence_ids=(qual,),
        holdout_support=16,holdout_accuracy=1.0,capability_epoch=0,frame_epochs=(('F',0),),
        episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
    )
    m.action_outcome_learning.add_relation(r)
    assert m._action_outcome_relation_current(r)
    return r


def train_projection_and_routing(m,world):
    ps=proposals(m)
    for i in range(48):
        pair=PAIRS[i%4]; execute_owned(m,world,pair,ps[pair],i)
    owned=m.derive_admitted_projection_samples_from_owned_raw_observations(); assert owned['sample_count']==48
    samples=tuple(owned['samples'])
    cfg=ProjectionDiscoveryConfig(max_subset=2,min_train_support=24,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=4)
    found=m.discover_epistemic_projection_candidates(samples[:32],samples[32:],cfg); assert found
    cs=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
    c=[x for x in cs if x.input_positions==(0,1)][0]
    qe=m.append_evidence('Q-MS1983-PROJ',{'kind':'RAW_PROJ_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1983-PROJ')
    pt=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1983-PROJ').qualify(c,qualification_evidence=(qe,))
    rec=m.admit_epistemic_projection_candidate(pt,projection_id='P-MS1983'); assert rec.current

    predictions={(bucket,action):effect for bucket,action,effect in c.bucket_action_prediction}
    bucket_even=next(bucket for (bucket,action),effect in predictions.items() if action=='B' and effect=='EVEN')
    bucket_odd=next(bucket for (bucket,action),effect in predictions.items() if action=='B' and effect=='ODD')
    re=add_relation(m,'R-MS1983-EVEN','EVEN',2.2,'MS1983-EVEN')
    ro=add_relation(m,'R-MS1983-ODD','ODD',2.2,'MS1983-ODD')
    prop=m.append_evidence('ROUTE-PROP-MS1983',{'kind':'ROUTING_PROPOSAL'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-PROPOSAL')
    route=m.nominate_projection_conditioned_relation_routing(
        projection_id='P-MS1983',task_id='MS1983',action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
        default_action_relations=(('B',ro.relation_id),),bucket_action_overrides=((bucket_even,'B',re.relation_id),),
        source_evidence_ids=(prop.evidence_id,),
    )
    refs=[]
    for i in range(16):
        pair=PAIRS[i%4]; bucket=c.project(pair); end='EVEN' if (int(pair[0])+int(pair[1]))%2==0 else 'ODD'
        refs.append(m.append_evidence(f'ROUTE-HOLDOUT-MS1983-{i}',{
            'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':'P-MS1983','projection_epoch':0,
            'projection_signature_sha256':rec.signature_sha256,'projection_bucket_id':bucket,'task_id':'MS1983',
            'action_id':'B','channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':2.2,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1983-ROUTING-HOLDOUT'))
    rt=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='EXTERNAL-MS1983-ROUTE').qualify(route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
    admitted=m.qualify_projection_conditioned_relation_routing(rt); assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',admitted
    return c,admitted['binding']['binding_id'],bucket_even,bucket_odd


def prepare_current_raw(m,world,pair,index):
    world.reset(pair); m.observe_value_state('V',0.0)
    state_eid=f'E-MS1983-CURRENT-STATE-{index}'
    m.observe_opaque_control_state(Observation(f'C-MS1983-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id=state_eid)
    raw=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-MS1983-CURRENT-RAW-{index}',capture_id=f'RAW-MS1983-{index}',max_coordinates=4)
    assert raw['status']=='BOUNDED_RAW_OBSERVATION_RECORDED' and tuple(raw['raw_tokens'])==pair
    return state_eid,raw


def run_ms1983():
    td=tempfile.TemporaryDirectory(prefix='ms1983-owned-routing-'); world=World(); m=build(Path(td.name),world)
    try:
        c,bid,bucket_even,bucket_odd=train_projection_and_routing(m,world)
        pair=('0','0'); expected_bucket=c.project(pair); assert expected_bucket==bucket_even
        prepare_current_raw(m,world,pair,0)

        # Existing generic API can be asked to use the other qualified bucket.
        generic_wrong=m.resolve_projection_conditioned_action_outcome_relation(
            bid,projection_bucket_id=bucket_odd,action_id='B',task_id='MS1983',channel_id='opaque-control',horizon=1)
        assert generic_wrong['status']=='CURRENT_PARTITION_SCOPED_RELATION'
        assert generic_wrong['relation_id']=='R-MS1983-ODD'

        owned=m.resolve_current_raw_projection_conditioned_relation(
            bid,action_id='B',task_id='MS1983',channel_id='opaque-control',horizon=1)
        assert owned['status']=='CURRENT_PARTITION_SCOPED_RELATION',owned
        assert owned['projection_bucket_id']==bucket_even
        assert owned['relation_id']=='R-MS1983-EVEN'
        assert owned['bucket_derivation_basis']=='CURRENT_BOUNDED_RAW_OBSERVATION_PLUS_EXACT_ADMITTED_PROJECTION'
        assert owned['bucket_selection_authority']==owned['semantic_coordinate_authority']==owned['semantic_projection_authority']==owned['truth_authority']==owned['execution_authority']=='NONE'

        return {
            'status':'PASS','candidate_sha256':c.digest(),'input_positions':list(c.input_positions),
            'generic_wrong_bucket_relation':generic_wrong['relation_id'],
            'owned_bucket':owned['projection_bucket_id'],'owned_relation':owned['relation_id'],
            'bucket_derivation_basis':owned['bucket_derivation_basis'],
            'earned':'CURRENT_OWNED_RAW_OBSERVATION_CAN_BE_PROJECTED_THROUGH_THE_EXACT_ADMITTED_OPAQUE_PROJECTION_AND_REUSED_BY_EXISTING_EXTERNALLY_QUALIFIED_RELATION_ROUTING_WITHOUT_CALLER_BUCKET_AUTHORITY',
            'new_routing_mechanism_added':'NO','bucket_selection_authority':'NONE','semantic_projection_authority':'NONE','truth_authority':'NONE','execution_authority':'NONE','language_authority':'NONE',
        }
    finally:_close(m);world.close();td.cleanup()


def main():print(json.dumps(run_ms1983(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
