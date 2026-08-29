from __future__ import annotations

import json, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus, ExternalProjectionQualifier, ProjectionDiscoveryConfig
from scratch.ms1977_raw_coordinate_projection_boundary import (
    PAIRS, World, act_ob, basis_ob, build, external_holdout, obs_ob, proposals,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close
from microseed import Observation, Authority


def execute_owned(m, world, pair, proposal, index):
    world.reset(pair)
    m.observe_value_state('V',0.0)
    state_eid=f'E-STATE-{index}'
    m.observe_opaque_control_state(
        Observation(f'C-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),
        evidence_id=state_eid,
    )
    raw=m.record_bounded_raw_observation_coordinates(
        'OBS',obs_ob(),evidence_id=f'E-RAW-{index}',capture_id=f'RAW-{index}',max_coordinates=4,
    )
    assert raw['status']=='BOUNDED_RAW_OBSERVATION_RECORDED',raw
    assert raw['control_state_evidence_id']==state_eid
    assert raw['coordinate_count']==2

    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED',ex
    out=m.record_bounded_action_outcome_via_observation_basis(
        ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),
        basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-OUT-{index}',capture_id=f'CAP-{index}',
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    return out


def run_ms1978():
    td=tempfile.TemporaryDirectory(prefix='ms1978-owned-raw-'); world=World(); m=build(Path(td.name),world)
    try:
        ps=proposals(m)
        for i in range(48):
            pair=PAIRS[i%4]
            execute_owned(m,world,pair,ps[pair],i)

        owned=m.derive_admitted_projection_samples_from_owned_raw_observations()
        assert owned['status']=='ADMITTED_OWNED_RAW_PROJECTION_SAMPLES',owned
        assert owned['sample_count']==48,owned['sample_count']
        assert not owned['receipt_rejections'],owned['receipt_rejections']
        assert not owned['sample_rejections'],owned['sample_rejections']
        samples=tuple(owned['samples'])
        assert {row.raw_tokens for row in samples}==set(PAIRS)
        assert {row.effect_token for row in samples}=={'EVEN','ODD'}

        # Deterministic balanced split: repetitions preserve all four raw patterns.
        training=tuple(samples[:32]); validation=tuple(samples[32:])
        cfg1=ProjectionDiscoveryConfig(
            max_subset=1,min_train_support=20,min_key_action_support=3,
            min_validation_accuracy=.95,min_lift_over_action_baseline=.35,
            min_scope_accuracy=.95,max_candidates=4,
        )
        assert m.discover_epistemic_projection_candidates(training,validation,cfg1)==[]

        cfg2=ProjectionDiscoveryConfig(
            max_subset=2,min_train_support=20,min_key_action_support=3,
            min_validation_accuracy=.95,min_lift_over_action_baseline=.35,
            min_scope_accuracy=.95,max_candidates=4,
        )
        found=m.discover_epistemic_projection_candidates(training,validation,cfg2); assert found,found
        candidates=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
        exact=[c for c in candidates if c.input_positions==(0,1)]
        assert len(exact)==1,[(c.input_positions,c.validation_accuracy,c.lift) for c in candidates]
        c=exact[0]
        assert c.validation_accuracy==1.0
        assert c.lift>=0.49

        holdout=external_holdout(c)
        qe=m.append_evidence(
            'Q-MS1978-EXTERNAL-HOLDOUT',
            {'kind':'OWNED_RAW_XOR_PROJECTION_HOLDOUT','candidate_sha256':c.digest(),'rows':holdout},
            EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-PROCESS-MS1978-QUALIFIER',
        )
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-PROCESS-MS1978').qualify(c,qualification_evidence=(qe,))
        rec=m.admit_epistemic_projection_candidate(ticket,projection_id='P-MS1978')
        assert rec.current

        return {
            'status':'PASS',
            'owned_sample_count':owned['sample_count'],
            'history_basis':owned['history_basis'],
            'single_coordinate_candidates':0,
            'input_positions':list(c.input_positions),
            'validation_accuracy':c.validation_accuracy,
            'lift':c.lift,
            'external_holdout_count':len(holdout),
            'projection':rec.serializable(),
            'earned':'BOUNDED_CURRENT_RAW_OBSERVATION_RECEIPTS_CAN_BE_JOINED_WITH_AUTHENTICATED_ACTION_OUTCOMES_TO_FEED_EXISTING_PROJECTION_SEARCH_AND_EARN_A_TWO_COORDINATE_OPERATIONAL_DISCRIMINATOR',
            'new_projection_search_mechanism_added':'NO',
            'raw_coordinate_semantic_authority':'NONE',
            'semantic_projection_authority':'NONE',
            'truth_authority':'NONE',
            'language_authority':'NONE',
        }
    finally:
        _close(m); world.close(); td.cleanup()


def main(): print(json.dumps(run_ms1978(),indent=2,sort_keys=True,default=str))
if __name__=='__main__': main()
