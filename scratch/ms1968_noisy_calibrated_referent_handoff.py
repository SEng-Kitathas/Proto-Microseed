from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Authority, Microseed, OperationalFrameContract, QualificationState
from microseed.cognition.referents import nominate_by_boundary_coherence, derive_affordance_relative_referent_signature
from scratch.ms1965_passive_calibrated_change_frame import observed_baseline_bound, calibrated_boundaries
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'noisy_referent_handoff_world_server.py'
OLD_MAP=(0,0,1,1); NEW_MAP=(1,0,1,0)


def sha(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


class World:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        r=json.loads(line); assert r.get('status')=='OK',r; return r
    def phase(self,p): self.call('phase',phase=p)
    def act(self,a): self.call('act',action_id=a)
    def observe(self): return tuple(self.call('observe')['channels'])
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)


def mapping_for(phase):
    if phase=='OLD': return OLD_MAP
    if phase=='NEW': return NEW_MAP
    if phase=='OVERLAP': return OLD_MAP+NEW_MAP
    raise ValueError(phase)


def calibrate_frame(ms,w,phase):
    w.phase(phase)
    baseline=[w.observe() for _ in range(9)]
    bound=float(observed_baseline_bound(baseline))
    subject=sha({'world':'NOISY-HANDOFF','phase':phase,'channels':len(baseline[0]),'noise':'LOW-JITTER-V1'})
    evidence=sha({'subject':subject,'samples':[list(x) for x in baseline],'bound':bound})
    fid=f'CAL-{phase}'
    frame=OperationalFrameContract(fid,f'calibrated noisy {phase.lower()} sensor frame',sha({'subject':subject,'bound':bound,'evidence':evidence}),Authority.DERIVED_READ_ONLY,('MS1968',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=(f'EXTERNAL_SENSOR_LAYOUT:{subject}',f'PASSIVE_CALIBRATION:{evidence}',f'OBSERVED_BASELINE_BOUND:{bound}'),invariants=('FRAME_IDENTITY != REFERENT_IDENTITY','OBSERVED_BOUND != FUTURE_BOUND'))
    ms.register_operational_frame(frame)
    return {'frame_id':fid,'epoch':0,'subject':subject,'bound':bound,'evidence':evidence}


def collect(ms,w,phase,cal,schedule):
    assert ms.frames.is_current(cal['frame_id'],cal['epoch'])
    w.phase(phase)
    samples=[w.observe()]
    for a in schedule:w.act(a);samples.append(w.observe())
    traces=tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b=calibrated_boundaries(traces,cal['bound'])
    n=nominate_by_boundary_coherence(b); assert n.status=='REFERENT_PARTITION_NOMINATED',n
    mapping=mapping_for(phase); rows=[]
    for group in n.groups:
        latent={mapping[i] for i in group}; assert len(latent)==1,(phase,group,b)
        sig=derive_affordance_relative_referent_signature(b,group,schedule); assert sig.status=='OPERATIONAL_REFERENT_SIGNATURE_DERIVED'
        rows.append({'group':tuple(group),'signature':sig.signature_sha256,'latent':next(iter(latent))})
    return {'phase':phase,'boundaries':b,'groups':rows,'frame_id':cal['frame_id'],'frame_epoch':cal['epoch'],'bound':cal['bound']}


def run_ms1968():
    td=tempfile.TemporaryDirectory(prefix='ms1968-noisy-handoff-'); ms=Microseed(Path(td.name)); w=World()
    try:
        w.call('reset')
        schedule=('FX-A','FX-B','FX-G','FX-A','FX-B')

        old_cal=calibrate_frame(ms,w,'OLD')
        w.call('reset'); old=collect(ms,w,'OLD',old_cal,schedule)
        old_by={r['signature']:r for r in old['groups']}; assert len(old_by)==2

        # Layout changes: old calibration frame is historical, not current authority for overlap.
        ms.frames.change(old_cal['frame_id'],reason='SENSOR_LAYOUT_HANDOFF')
        assert not ms.frames.is_current(old_cal['frame_id'],old_cal['epoch'])
        w.call('reset'); ov_cal=calibrate_frame(ms,w,'OVERLAP')
        w.call('reset'); overlap=collect(ms,w,'OVERLAP',ov_cal,schedule)
        ov_by={r['signature']:r for r in overlap['groups']}; assert len(ov_by)==2

        ms.frames.change(ov_cal['frame_id'],reason='SENSOR_LAYOUT_HANDOFF')
        assert not ms.frames.is_current(ov_cal['frame_id'],ov_cal['epoch'])
        w.call('reset'); new_cal=calibrate_frame(ms,w,'NEW')
        w.call('reset'); new=collect(ms,w,'NEW',new_cal,schedule)
        new_by={r['signature']:r for r in new['groups']}; assert len(new_by)==2

        assert set(old_by)==set(ov_by)==set(new_by)
        alignment={}
        for sig in old_by:
            assert old_by[sig]['latent']==ov_by[sig]['latent']==new_by[sig]['latent']
            alignment[sig]=old_by[sig]['latent']

        # Historical signatures can support continuity evidence even though the source frames are stale.
        assert ms.frames.frames[old_cal['frame_id']].qualification==QualificationState.STALE
        assert ms.frames.frames[ov_cal['frame_id']].qualification==QualificationState.STALE
        assert ms.frames.is_current(new_cal['frame_id'],new_cal['epoch'])

        return {
            'status':'PASS','old':old,'overlap':overlap,'new':new,
            'alignment':alignment,
            'frame_statuses':{
                old_cal['frame_id']:ms.frames.frames[old_cal['frame_id']].qualification.value,
                ov_cal['frame_id']:ms.frames.frames[ov_cal['frame_id']].qualification.value,
                new_cal['frame_id']:ms.frames.frames[new_cal['frame_id']].qualification.value,
            },
            'earned':'SEPARATELY_CURRENT_CALIBRATED_SENSOR_FRAMES_CAN_SUPPORT_OPERATIONAL_PROTO_REFERENT_CONTINUITY_ACROSS_NOISY_LAYOUT_HANDOFF_WITHOUT_SHARED_FRAME_IDENTITY',
            'continuity_authority':'OPERATIONAL_REFERENT_CONTINUITY_ONLY',
            'frame_identity_authority':'NONE',
            'numerical_identity_authority':'NONE',
            'semantic_reference_authority':'NONE',
            'language_authority':'NONE',
        }
    finally:
        _close(ms);w.close();td.cleanup()


def main(): print(json.dumps(run_ms1968(),indent=2,sort_keys=True))
if __name__=='__main__':main()
