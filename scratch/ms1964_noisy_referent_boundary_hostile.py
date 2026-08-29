from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import nominate_by_boundary_coherence
from scratch.ms1958_proto_referent_boundary_coherence import boundaries

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'noisy_referent_world_server.py'
MAP=(0,0,1,1)


class NoisyWorld:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        assert self.proc.stdin is not None and self.proc.stdout is not None
    def call(self,op,**payload):
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        r=json.loads(line); assert r.get('status')=='OK',r; return r
    def observe(self): return tuple(self.call('observe')['channels'])
    def act(self,a): self.call('act',action_id=a)
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill(); self.proc.wait(timeout=5)


def threshold_boundaries(traces,threshold):
    out=[]
    for values in traces:
        out.append(tuple(i for i in range(1,len(values)) if abs(values[i]-values[i-1])>=threshold))
    return tuple(out)


def run_noisy_hostile():
    w=NoisyWorld()
    try:
        w.call('reset')
        schedule=('FX-N','FX-A','FX-N','FX-B','FX-G','FX-N','FX-A','FX-B')
        samples=[w.observe()]
        for a in schedule:
            w.act(a); samples.append(w.observe())
        traces=tuple(tuple(sample[i] for sample in samples) for i in range(4))

        exact=boundaries(traces)
        exact_nom=nominate_by_boundary_coherence(exact)
        # Independent jitter causes every raw channel to change almost every sample,
        # collapsing exact boundary coherence into global synchrony/ambiguity.
        assert exact_nom.status=='UNKNOWN_INCOMPLETE',exact_nom
        assert exact_nom.identity_authority=='NONE'

        # Counterfactual evaluator-only robust detector. Threshold is supplied and
        # must not be promoted as organism-owned evidence by this campaign.
        robust=threshold_boundaries(traces,threshold=8)
        robust_nom=nominate_by_boundary_coherence(robust)
        assert robust_nom.status=='REFERENT_PARTITION_NOMINATED',robust_nom
        assert robust_nom.identity_authority=='NONE'
        for group in robust_nom.groups:
            latent={MAP[i] for i in group}; assert len(latent)==1

        return {
            'status':'BOUNDARY_CONFIRMED',
            'exact_boundaries':exact,
            'exact_nomination':{'status':exact_nom.status,'groups':exact_nom.groups,'reason':exact_nom.reason,'identity_authority':exact_nom.identity_authority},
            'supplied_threshold_boundaries':robust,
            'supplied_threshold_nomination':{'status':robust_nom.status,'groups':robust_nom.groups,'reason':robust_nom.reason,'identity_authority':robust_nom.identity_authority},
            'threshold':8,
            'earned':'RAW_NOISY_OBSERVATIONS_DEFEAT_EXACT_REFERENT_BOUNDARY_COHERENCE_WHILE_SUPPLIED_ROBUST_CHANGE_DETECTION_RECOVERS_THE_PARTITION',
            'missing_owner':'ROBUST_OBSERVATION_FRAME_OR_CHANGE_DETECTOR_NOT_REFERENT_IDENTITY',
            'noise_model_authority':'NONE',
            'identity_authority':'NONE',
            'semantic_reference_authority':'NONE',
        }
    finally:w.close()


def main(): print(json.dumps(run_noisy_hostile(),indent=2,sort_keys=True))
if __name__=='__main__': main()
