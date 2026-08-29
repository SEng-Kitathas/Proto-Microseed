from __future__ import annotations

import json, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Authority, Microseed, Observation
from scratch.ms1977_raw_coordinate_projection_boundary import PAIRS, World, act_ob, basis_ob, build, obs_ob, proposals
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _one_trial(m,world,pair,proposal,index,*,raw_receipts=1):
    world.reset(pair); m.observe_value_state('V',0.0)
    state_eid=f'E-STATE-{index}'
    m.observe_opaque_control_state(Observation(f'C-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id=state_eid)
    receipts=[]
    for j in range(raw_receipts):
        receipts.append(m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id=f'E-RAW-{index}-{j}',capture_id=f'RAW-{index}-{j}',max_coordinates=4))
        assert receipts[-1]['status']=='BOUNDED_RAW_OBSERVATION_RECORDED',receipts[-1]
    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED',ex
    out=m.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-OUT-{index}',capture_id=f'CAP-{index}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    return state_eid,receipts,out


def run_ms1979():
    results={}

    # 1. Bound refusal: two-coordinate observation cannot cross a max_coordinates=1 ingress.
    td=tempfile.TemporaryDirectory(prefix='ms1979-limit-'); world=World(); m=build(Path(td.name),world)
    try:
        world.reset(('0','1'));m.observe_value_state('V',0.0)
        m.observe_opaque_control_state(Observation('C-LIM','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id='E-STATE-LIM')
        denied=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-RAW-LIM',capture_id='RAW-LIM',max_coordinates=1)
        assert denied['status']=='RAW_OBSERVATION_REJECTED' and denied['reason']=='BOUNDED_RAW_TOKENS_REQUIRED',denied
        assert m.evidence.get('E-RAW-LIM') is None
        results['coordinate_limit']={'status':'PASS','result':denied,'evidence_persisted':False}
    finally:_close(m);world.close();td.cleanup()

    # 2. Duplicate receipt hostile: never choose between two current raw receipts silently.
    td=tempfile.TemporaryDirectory(prefix='ms1979-dup-'); world=World(); m=build(Path(td.name),world)
    try:
        ps=proposals(m);_one_trial(m,world,('1','0'),ps[('1','0')],0,raw_receipts=2)
        surface=m.derive_admitted_projection_samples_from_owned_raw_observations()
        assert surface['sample_count']==0,surface
        assert any(reason=='EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_CONTROL_STATE_REQUIRED' for _,reason in surface['sample_rejections']),surface['sample_rejections']
        results['duplicate_receipt']={'status':'PASS','sample_count':surface['sample_count'],'sample_rejections':surface['sample_rejections']}
    finally:_close(m);world.close();td.cleanup()

    # 3. Frame drift in the same life makes both old raw evidence and transitions unusable.
    td=tempfile.TemporaryDirectory(prefix='ms1979-drift-'); world=World(); m=build(Path(td.name),world)
    try:
        ps=proposals(m);_one_trial(m,world,('1','1'),ps[('1','1')],0)
        before=m.derive_admitted_projection_samples_from_owned_raw_observations();assert before['sample_count']==1,before
        m.frames.change('F',reason='MS1979-SENSOR-FRAME-DRIFT')
        after=m.derive_admitted_projection_samples_from_owned_raw_observations();assert after['sample_count']==0,after
        assert any(reason=='RAW_OBSERVATION_FRAME_NOT_CURRENT' for _,reason in after['receipt_rejections']),after['receipt_rejections']
        results['frame_drift']={'status':'PASS','before_samples':1,'after_samples':0,'receipt_rejections':after['receipt_rejections'],'sample_rejections':after['sample_rejections']}
    finally:_close(m);world.close();td.cleanup()

    # 4. Restart: receipt persists, but no live runtime premises means no admitted sample.
    td=tempfile.TemporaryDirectory(prefix='ms1979-restart-');root=Path(td.name);world=World();m=build(root,world)
    try:
        ps=proposals(m);_one_trial(m,world,('0','1'),ps[('0','1')],0)
        first=m.derive_admitted_projection_samples_from_owned_raw_observations();assert first['sample_count']==1
    finally:_close(m);world.close()
    m2=Microseed(root)
    try:
        no_attach=m2.derive_admitted_projection_samples_from_owned_raw_observations();assert no_attach['sample_count']==0,no_attach
        assert any(reason=='RAW_OBSERVATION_CAPABILITY_NOT_CURRENT' for _,reason in no_attach['receipt_rejections']),no_attach['receipt_rejections']
        results['restart_no_attach']={'status':'PASS','sample_count':0,'receipt_rejections':no_attach['receipt_rejections']}
    finally:_close(m2)

    # 5. Compatible reattachment reuses durable receipt/history only after exact contracts return.
    world3=World();m3=build(root,world3)
    try:
        recovered=m3.derive_admitted_projection_samples_from_owned_raw_observations();assert recovered['sample_count']==1,recovered
        row=recovered['samples'][0]
        assert row.raw_tokens==('0','1') and row.effect_token=='ODD'
        results['compatible_reattachment']={'status':'PASS','sample_count':1,'raw_tokens':row.raw_tokens,'effect_token':row.effect_token}
    finally:_close(m3);world3.close();td.cleanup()

    return {
        'status':'PASS',
        'cases':results,
        'earned':'OWNED_RAW_OBSERVATION_RECEIPTS_ARE_BOUNDED_EXACT_PREMISE_EVIDENCE_NOT_TIMELESS_SENSOR_TRUTH_AND_COMPATIBLE_REATTACHMENT_CAN_REACTIVATE_THEIR_USE',
        'automatic_duplicate_arbitration':'NO',
        'automatic_restart_authority':'NO',
        'semantic_coordinate_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
    }


def main():print(json.dumps(run_ms1979(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
