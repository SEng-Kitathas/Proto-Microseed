from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import nominate_by_boundary_coherence, derive_affordance_relative_referent_signature
from scratch.ms1964_noisy_referent_boundary_hostile import NoisyWorld, MAP


def observed_baseline_bound(samples):
    traces=tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    deltas=[abs(values[i]-values[i-1]) for values in traces for i in range(1,len(values))]
    return max(deltas) if deltas else 0


def calibrated_boundaries(traces,bound):
    # Strictly larger than every *observed calibration* adjacent delta.
    return tuple(tuple(i for i in range(1,len(values)) if abs(values[i]-values[i-1])>bound) for values in traces)


def run_one(phase_offset):
    w=NoisyWorld()
    try:
        w.call('reset')
        for _ in range(phase_offset): w.observe()
        baseline=[w.observe() for _ in range(9)]
        bound=observed_baseline_bound(baseline)
        assert bound==3,bound

        schedule=('FX-N','FX-A','FX-N','FX-B','FX-G','FX-N','FX-A','FX-B')
        samples=[w.observe()]
        for a in schedule:
            w.act(a); samples.append(w.observe())
        traces=tuple(tuple(sample[i] for sample in samples) for i in range(4))
        b=calibrated_boundaries(traces,bound)
        n=nominate_by_boundary_coherence(b)
        assert n.status=='REFERENT_PARTITION_NOMINATED',n
        signatures=[]
        for group in n.groups:
            latent={MAP[i] for i in group}; assert len(latent)==1
            sig=derive_affordance_relative_referent_signature(b,group,schedule)
            assert sig.status=='OPERATIONAL_REFERENT_SIGNATURE_DERIVED'
            signatures.append(sig.signature_sha256)
        return {
            'phase_offset':phase_offset,
            'observed_baseline_max_adjacent_delta':bound,
            'boundaries':b,
            'groups':n.groups,
            'signatures':sorted(signatures),
            'identity_authority':n.identity_authority,
        }
    finally:w.close()


def run_passive_calibration():
    runs=[run_one(i) for i in range(4)]
    assert all(r['groups']==((0,1),(2,3)) for r in runs)
    assert len({tuple(r['signatures']) for r in runs})==1
    return {
        'status':'PASS',
        'runs':runs,
        'earned':'PASSIVE_FIXED_STATE_OBSERVATIONS_CAN_SUPPLY_A_BOUNDED_JITTER_CALIBRATION_THAT_RECOVERS_PROTO_REFERENT_CHANGE_STRUCTURE_UNDER_THIS_NOISY_WORLD',
        'calibration_authority':'OBSERVED_BASELINE_BOUND_ONLY',
        'future_noise_bound_authority':'NONE',
        'noise_model_authority':'NONE',
        'identity_authority':'NONE',
        'remaining_boundary':'OBSERVED_BASELINE_JITTER_BOUND != GENERAL_NOISE_MODEL_OR_FUTURE_BOUND',
    }


def main(): print(json.dumps(run_passive_calibration(),indent=2,sort_keys=True))
if __name__=='__main__': main()
