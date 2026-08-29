from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import nominate_by_boundary_coherence
from scratch.ms1964_noisy_referent_boundary_hostile import NoisyWorld
from scratch.ms1965_passive_calibrated_change_frame import observed_baseline_bound, calibrated_boundaries


def run_calibration_drift():
    w=NoisyWorld()
    try:
        w.call('reset')
        baseline=[w.observe() for _ in range(9)]
        bound=observed_baseline_bound(baseline)
        assert bound==3

        # Reality changes after calibration. The old observed bound is not
        # automatically current evidence about the new noise regime.
        w.call('noise_mode',high_noise=True)
        schedule=('FX-N','FX-A','FX-N','FX-B','FX-G','FX-N','FX-A','FX-B')
        samples=[w.observe()]
        for a in schedule:
            w.act(a); samples.append(w.observe())
        traces=tuple(tuple(sample[i] for sample in samples) for i in range(4))
        b=calibrated_boundaries(traces,bound)
        nomination=nominate_by_boundary_coherence(b)

        # Channel 0 now has extra nuisance boundaries and separates from channel 1,
        # so the old calibration can no longer support the prior referent partition.
        assert tuple(b[0])!=tuple(b[1]),b
        assert nomination.groups != ((0,1),(2,3))

        return {
            'status':'BOUNDARY_CONFIRMED',
            'old_observed_baseline_bound':bound,
            'post_drift_boundaries':b,
            'post_drift_nomination':{
                'status':nomination.status,
                'groups':nomination.groups,
                'reason':nomination.reason,
                'identity_authority':nomination.identity_authority,
            },
            'earned':'PASSIVE_CALIBRATION_CAN_BECOME_STALE_UNDER_SENSOR_NOISE_DRIFT_AND_MUST_NOT_BE_TREATED_AS_TIMELESS_FRAME_TRUTH',
            'missing_owner':'CALIBRATION_OR_OBSERVATION_FRAME_CURRENTNESS_AND_REQUALIFICATION',
            'noise_model_authority':'NONE',
            'identity_authority':'NONE',
        }
    finally:w.close()


def main(): print(json.dumps(run_calibration_drift(),indent=2,sort_keys=True))
if __name__=='__main__': main()
