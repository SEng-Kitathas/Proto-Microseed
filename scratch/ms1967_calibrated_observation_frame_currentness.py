from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Authority, Microseed, OperationalFrameContract, QualificationState
from microseed.cognition.referents import nominate_by_boundary_coherence, derive_affordance_relative_referent_signature
from scratch.ms1964_noisy_referent_boundary_hostile import NoisyWorld, MAP
from scratch.ms1965_passive_calibrated_change_frame import observed_baseline_bound, calibrated_boundaries
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def sha(payload) -> str:
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class CalibrationWitness:
    frame_id: str
    frame_epoch: int
    subject_signature_sha256: str
    observed_bound: float
    evidence_digest_sha256: str
    authority: str = 'OBSERVED_BASELINE_BOUND_ONLY'
    future_noise_bound_authority: str = 'NONE'
    noise_model_authority: str = 'NONE'


def regime_signature(high_noise: bool) -> str:
    # External compatibility subject: opaque sensor/environment regime handle.
    # The label is harness instrumentation; the digest is what is bound into the frame.
    return sha({'sensor':'NOISY-REFERENT-WORLD','regime':'HIGH' if high_noise else 'LOW','channels':4})


def qualify_calibration_frame(ms: Microseed, world: NoisyWorld, *, high_noise: bool, frame_id: str) -> CalibrationWitness:
    world.call('noise_mode',high_noise=high_noise)
    baseline=[world.observe() for _ in range(9)]
    bound=float(observed_baseline_bound(baseline))
    subject=regime_signature(high_noise)
    evidence_digest=sha({'subject':subject,'samples':[list(x) for x in baseline],'observed_bound':bound})
    signature=sha({'subject':subject,'observed_bound':bound,'evidence_digest':evidence_digest,'authority':'OBSERVED_BASELINE_BOUND_ONLY'})
    frame=OperationalFrameContract(
        frame_id=frame_id,
        purpose='bounded calibrated observation-change frame',
        signature_sha256=signature,
        authority=Authority.DERIVED_READ_ONLY,
        lineage=('MS1967',),
        currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=(
            f'EXTERNAL_SENSOR_REGIME_SIGNATURE:{subject}',
            f'PASSIVE_CALIBRATION_EVIDENCE:{evidence_digest}',
            f'OBSERVED_BASELINE_BOUND:{bound}',
        ),
        invariants=(
            'CALIBRATION_EVIDENCE != NOISE_MODEL',
            'OBSERVED_BOUND != FUTURE_BOUND',
            'CALIBRATED_BOUNDARY != REFERENT_IDENTITY',
        ),
        hazards=('SENSOR_REGIME_DRIFT_STALES_FRAME',),
    )
    ms.register_operational_frame(frame)
    return CalibrationWitness(frame_id,ms.frames.epochs[frame_id],subject,bound,evidence_digest)


def calibrated_nomination(ms: Microseed, world: NoisyWorld, witness: CalibrationWitness, *, high_noise: bool):
    current_subject=regime_signature(high_noise)
    if current_subject!=witness.subject_signature_sha256:
        if ms.frames.is_current(witness.frame_id,witness.frame_epoch):
            ms.frames.change(witness.frame_id,reason='CALIBRATION_SENSOR_REGIME_SIGNATURE_DRIFT')
        return {
            'status':'UNKNOWN_INCOMPLETE',
            'reason':'CALIBRATION_FRAME_NOT_CURRENT_FOR_SENSOR_REGIME',
            'frame_current':False,
            'identity_authority':'NONE',
        }
    if not ms.frames.is_current(witness.frame_id,witness.frame_epoch):
        return {'status':'UNKNOWN_INCOMPLETE','reason':'CALIBRATION_FRAME_STALE','frame_current':False,'identity_authority':'NONE'}

    schedule=('FX-N','FX-A','FX-N','FX-B','FX-G','FX-N','FX-A','FX-B')
    samples=[world.observe()]
    for action in schedule:
        world.act(action); samples.append(world.observe())
    traces=tuple(tuple(sample[i] for sample in samples) for i in range(4))
    boundaries=calibrated_boundaries(traces,witness.observed_bound)
    nomination=nominate_by_boundary_coherence(boundaries)
    if nomination.status!='REFERENT_PARTITION_NOMINATED':
        return {'status':nomination.status,'reason':nomination.reason,'groups':nomination.groups,'frame_current':True,'identity_authority':nomination.identity_authority}
    signatures=[]
    for group in nomination.groups:
        assert len({MAP[i] for i in group})==1
        sig=derive_affordance_relative_referent_signature(boundaries,group,schedule)
        assert sig.status=='OPERATIONAL_REFERENT_SIGNATURE_DERIVED'
        signatures.append(sig.signature_sha256)
    return {
        'status':'REFERENT_PARTITION_NOMINATED',
        'groups':nomination.groups,
        'signatures':sorted(signatures),
        'frame_current':True,
        'frame_id':witness.frame_id,
        'frame_epoch':witness.frame_epoch,
        'identity_authority':'NONE',
    }


def run_ms1967():
    td=tempfile.TemporaryDirectory(prefix='ms1967-cal-frame-'); ms=Microseed(Path(td.name)); world=NoisyWorld()
    try:
        world.call('reset')
        low=qualify_calibration_frame(ms,world,high_noise=False,frame_id='CAL-FRAME-LOW')
        assert low.observed_bound==3.0,low
        world.call('reset'); world.call('noise_mode',high_noise=False)
        low_result=calibrated_nomination(ms,world,low,high_noise=False)
        assert low_result['status']=='REFERENT_PARTITION_NOMINATED',low_result
        assert low_result['groups']==((0,1),(2,3)),low_result

        # Reality changes. The old calibrated frame is checked against its exact
        # external compatibility subject and is staled before referent nomination.
        world.call('reset'); world.call('noise_mode',high_noise=True)
        drift=calibrated_nomination(ms,world,low,high_noise=True)
        assert drift['status']=='UNKNOWN_INCOMPLETE',drift
        assert not ms.frames.is_current(low.frame_id,low.frame_epoch)
        assert ms.frames.frames[low.frame_id].qualification==QualificationState.STALE

        # Fresh external calibration is a new content-bound frame artifact rather
        # than an in-place resurrection of the stale historical frame.
        world.call('reset')
        high=qualify_calibration_frame(ms,world,high_noise=True,frame_id='CAL-FRAME-HIGH')
        assert high.subject_signature_sha256!=low.subject_signature_sha256
        assert high.frame_id!=low.frame_id
        world.call('reset'); world.call('noise_mode',high_noise=True)
        high_result=calibrated_nomination(ms,world,high,high_noise=True)
        # The high-noise world may or may not be distinguishable under the newly
        # observed bound; the key result is currentness/subject gating, not success.
        assert high_result['frame_current'] is True,high_result

        return {
            'status':'PASS',
            'low_frame':low.__dict__,
            'low_result':low_result,
            'post_drift_old_frame':{
                'result':drift,
                'qualification':ms.frames.frames[low.frame_id].qualification.value,
                'currentness':ms.frames.frames[low.frame_id].currentness,
                'epoch_now':ms.frames.epochs[low.frame_id],
            },
            'fresh_high_frame':high.__dict__,
            'fresh_high_result':high_result,
            'earned':'EXISTING_OPERATIONAL_FRAME_CURRENTNESS_CAN_OWN_BOUNDED_CALIBRATION_LIFECYCLE_WHEN_EXTERNAL_SENSOR_REGIME_COMPATIBILITY_IS_EXPLICIT',
            'requalification_form':'NEW_CONTENT_BOUND_FRAME_ARTIFACT_NOT_IN_PLACE_RESURRECTION',
            'noise_model_authority':'NONE',
            'future_noise_bound_authority':'NONE',
            'identity_authority':'NONE',
            'semantic_reference_authority':'NONE',
        }
    finally:
        _close(ms); world.close(); td.cleanup()


def main(): print(json.dumps(run_ms1967(),indent=2,sort_keys=True,default=str))
if __name__=='__main__': main()
