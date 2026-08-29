from __future__ import annotations

import json, random, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, ConstructorGrowthConfig, EpisodeSchemaContract, EpistemicStatus,
    ExternalConstructorQualifier, Observation, QualificationState,
)
from microseed.development.action_learning import (
    ExternalProjectionConditionedRelationQualifier,
    QualifiedActionOutcomePredictiveRelation,
)
from scratch.ms1981_temporal_raw_constructor_boundary import (
    BITS, World, build, obs_ob, proposals, step,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def train_constructor_projection(m,world):
    ps=proposals(m)
    # Acquire owned temporal raw/action history.
    for i in range(48):
        bits=BITS[i%4]
        world.reset(bits); m.observe_value_state('V',0.0)
        m.observe_opaque_control_state(Observation(f'C-T0-{i}','EXTERNAL','opaque-control','ALIAS0',authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-T-STATE0-{i}')
        r0=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-T-RAW0-{i}',capture_id=f'T0-{i}',max_coordinates=1); assert r0['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        a=step(m,ps['PREP'],f'T-{i}-PREP'); assert a['outcome']['actual_next_state_id']=='ALIAS1'
        r1=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-T-RAW1-{i}',capture_id=f'T1-{i}',max_coordinates=1); assert r1['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        b=step(m,ps[bits],f'T-{i}-B'); expected='SAME' if bits[0]==bits[1] else 'DIFF'; assert b['outcome']['actual_next_state_id']==expected

    owned=m.derive_admitted_raw_constructor_projection_samples(max_lag=1)
    target=[row for row in owned['samples'] if row.action_token=='B' and len(row.raw_history)==2]
    assert len(target)==48
    rr=list(target); random.Random(1984).shuffle(rr)
    train=tuple(rr[:28]); pressure=tuple(rr[28:38]); validation=tuple(rr[38:])
    cfg=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=1,min_train_support=20,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
    found=m.discover_epistemic_constructor_candidates(train,pressure,validation,cfg); assert found
    cs=[m.epistemic_constructor_candidates[x['candidate_id']] for x in found]
    exact=[c for c in cs if set(a.token() for a in c.atoms)=={'L0:P0','L1:P0'}]
    assert len(exact)==1
    c=exact[0]; assert c.validation_accuracy==1.0
    qe=m.append_evidence('Q-MS1984-CONSTRUCTOR',{'kind':'TEMPORAL_CONSTRUCTOR_HOLDOUT','candidate_sha256':c.digest()},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1984-CONSTRUCTOR')
    ticket=ExternalConstructorQualifier(m.evidence,qualifier_id='EXTERNAL-MS1984-CONSTRUCTOR').qualify(c,qualification_evidence=(qe,))
    rec=m.admit_epistemic_constructor_candidate(ticket,projection_id='P-MS1984'); assert rec.current
    return ps,c,rec


def add_relation_episode(m):
    m.register_episode_schema(EpisodeSchemaContract(
        'EP-ROUTE','routing-only episode','r'*64,Authority.DERIVED_READ_ONLY,('MS1984',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),
    ))


def add_relation(m,rid,end,tag):
    train=f'{tag}-TRAIN'; qual=f'{tag}-QUAL'
    m.append_evidence(train,{'kind':'RELATION_TRAIN','id':rid},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1984-REL')
    m.append_evidence(qual,{'kind':'RELATION_QUAL','id':rid},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1984-REL-QUAL')
    r=QualifiedActionOutcomePredictiveRelation(
        relation_id=rid,candidate_id='C-'+rid,candidate_sha256=(('c' if end=='SAME' else 'd')*64),
        start_state_id='ALIAS1',capability_id='B',next_state_id=end,value_effect=1.5,
        support=16,consistency=1.0,source_evidence_ids=(train,),qualification_evidence_ids=(qual,),
        holdout_support=16,holdout_accuracy=1.0,capability_epoch=0,frame_epochs=(('F',0),),
        episode_schema_epochs=(('EP-ROUTE',0),),value_epoch=('V',0),
    )
    m.action_outcome_learning.add_relation(r); assert m._action_outcome_relation_current(r)
    return r


def install_routing(m,c,rec):
    add_relation_episode(m)
    rs=add_relation(m,'R-MS1984-SAME','SAME','MS1984-SAME')
    rd=add_relation(m,'R-MS1984-DIFF','DIFF','MS1984-DIFF')
    pred={(bucket,action):effect for bucket,action,effect in c.bucket_action_prediction}
    bucket_same=next(bucket for (bucket,action),effect in pred.items() if action=='B' and effect=='SAME')
    bucket_diff=next(bucket for (bucket,action),effect in pred.items() if action=='B' and effect=='DIFF')
    prop=m.append_evidence('ROUTE-PROP-MS1984',{'kind':'ROUTING_PROPOSAL'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-PROPOSAL')
    route=m.nominate_projection_conditioned_relation_routing(
        projection_id='P-MS1984',task_id='MS1984',action_ids=('B',),channel_ids=('opaque-control',),horizon=1,
        default_action_relations=(('B',rd.relation_id),),bucket_action_overrides=((bucket_same,'B',rs.relation_id),),source_evidence_ids=(prop.evidence_id,),
    )
    refs=[]
    for i in range(16):
        bits=BITS[i%4]; raw=((bits[1],),(bits[0],)); bucket=c.project(raw); end='SAME' if bits[0]==bits[1] else 'DIFF'
        refs.append(m.append_evidence(f'ROUTE-HOLDOUT-MS1984-{i}',{
            'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':'P-MS1984','projection_epoch':0,
            'projection_signature_sha256':rec.signature_sha256,'projection_bucket_id':bucket,'task_id':'MS1984',
            'action_id':'B','channel_id':'opaque-control','horizon':1,'actual_next_state_id':end,'actual_value_effect':1.5,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1984-ROUTING-HOLDOUT'))
    rt=ExternalProjectionConditionedRelationQualifier(m.evidence,qualifier_id='EXTERNAL-MS1984-ROUTE').qualify(route,qualification_evidence=tuple(refs),relations=m.action_outcome_learning.relations)
    admitted=m.qualify_projection_conditioned_relation_routing(rt); assert admitted['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',admitted
    return admitted['binding']['binding_id'],bucket_same,bucket_diff


def prepare_current_temporal_history(m,world,ps,bits,index):
    world.reset(bits); m.observe_value_state('V',0.0)
    m.observe_opaque_control_state(Observation(f'C-CUR0-{index}','EXTERNAL','opaque-control','ALIAS0',authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-CUR-STATE0-{index}')
    first=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-CUR-RAW0-{index}',capture_id=f'CUR0-{index}',max_coordinates=1); assert first['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
    a=step(m,ps['PREP'],f'CUR-{index}-PREP'); assert a['outcome']['actual_next_state_id']=='ALIAS1'
    second=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-CUR-RAW1-{index}',capture_id=f'CUR1-{index}',max_coordinates=1); assert second['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
    return first,second


def run_ms1984():
    td=tempfile.TemporaryDirectory(prefix='ms1984-temporal-routing-'); world=World(); m=build(Path(td.name),world)
    try:
        ps,c,rec=train_constructor_projection(m,world)
        bid,bucket_same,bucket_diff=install_routing(m,c,rec)
        bits=('0','1'); expected_bucket=c.project(((bits[1],),(bits[0],))); assert expected_bucket==bucket_diff
        prepare_current_temporal_history(m,world,ps,bits,0)

        generic_wrong=m.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id=bucket_same,action_id='B',task_id='MS1984',channel_id='opaque-control',horizon=1)
        assert generic_wrong['status']=='CURRENT_PARTITION_SCOPED_RELATION' and generic_wrong['relation_id']=='R-MS1984-SAME'

        owned=m.resolve_current_raw_constructor_projection_conditioned_relation(bid,action_id='B',task_id='MS1984',channel_id='opaque-control',horizon=1)
        assert owned['status']=='CURRENT_PARTITION_SCOPED_RELATION',owned
        assert owned['projection_bucket_id']==bucket_diff
        assert owned['relation_id']=='R-MS1984-DIFF'
        assert owned['raw_history_lag_depth']==1
        assert len(owned['raw_history_evidence_ids'])==2
        assert owned['bucket_derivation_basis']=='CURRENT_AUTHENTICATED_RAW_HISTORY_PLUS_EXACT_ADMITTED_CONSTRUCTOR_PROJECTION'
        assert owned['bucket_selection_authority']==owned['semantic_coordinate_authority']==owned['semantic_temporal_relation_authority']==owned['semantic_projection_authority']==owned['truth_authority']==owned['execution_authority']=='NONE'

        return {
            'status':'PASS','candidate_sha256':c.digest(),'atoms':[a.token() for a in c.atoms],
            'generic_wrong_bucket_relation':generic_wrong['relation_id'],'owned_relation':owned['relation_id'],
            'raw_history_lag_depth':owned['raw_history_lag_depth'],'raw_history_evidence_ids':list(owned['raw_history_evidence_ids']),
            'bucket_derivation_basis':owned['bucket_derivation_basis'],
            'earned':'CURRENT_OWNED_TEMPORAL_RAW_HISTORY_CAN_BE_RECONSTRUCTED_THROUGH_AUTHENTICATED_ACTION_ANCESTRY_PROJECTED_BY_THE_EXACT_ADMITTED_CONSTRUCTOR_AND_REUSED_BY_EXISTING_QUALIFIED_RELATION_ROUTING',
            'new_routing_mechanism_added':'NO','new_constructor_mechanism_added':'NO','bucket_selection_authority':'NONE','semantic_temporal_relation_authority':'NONE','truth_authority':'NONE','execution_authority':'NONE','language_authority':'NONE',
        }
    finally:_close(m); world.close(); td.cleanup()


def main():print(json.dumps(run_ms1984(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
