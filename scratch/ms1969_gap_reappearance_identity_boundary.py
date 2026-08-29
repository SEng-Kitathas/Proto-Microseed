from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import nominate_by_boundary_coherence, derive_affordance_relative_referent_signature
from scratch.ms1958_proto_referent_boundary_coherence import boundaries

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'referent_gap_world_server.py'
MAP=(0,0,1,1)


class GapWorld:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n');self.proc.stdin.flush()
        line=self.proc.stdout.readline();assert line
        r=json.loads(line);assert r.get('status')=='OK',r;return r
    def act(self,a):self.call('act',action_id=a)
    def observe(self):return tuple(self.call('observe')['channels'])
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)


def collect(world,schedule):
    samples=[world.observe()]
    for a in schedule:world.act(a);samples.append(world.observe())
    traces=tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b=boundaries(traces)
    n=nominate_by_boundary_coherence(b);assert n.status=='REFERENT_PARTITION_NOMINATED',n
    rows=[]
    for group in n.groups:
        assert len({MAP[i] for i in group})==1
        sig=derive_affordance_relative_referent_signature(b,group,schedule);assert sig.status=='OPERATIONAL_REFERENT_SIGNATURE_DERIVED'
        rows.append({'group':tuple(group),'signature':sig.signature_sha256,'latent_slot':next(iter({MAP[i] for i in group}))})
    return {'boundaries':b,'groups':rows}


def run_case(substitute):
    w=GapWorld()
    try:
        w.call('reset');schedule=('FX-A','FX-B','FX-G','FX-A','FX-B')
        pre=collect(w,schedule)
        pre_generation=tuple(w.call('evaluator_identity')['generations'])
        w.call('gap');assert w.observe()==()
        w.call('reappear',substitute=substitute)
        post_generation=tuple(w.call('evaluator_identity')['generations'])
        post=collect(w,schedule)
        pre_by={r['signature']:r for r in pre['groups']};post_by={r['signature']:r for r in post['groups']}
        assert set(pre_by)==set(post_by) and len(pre_by)==2
        return {
            'substitute':substitute,'pre':pre,'post':post,
            'pre_generation':pre_generation,'post_generation':post_generation,
            'signature_set':sorted(pre_by),
            'evaluator_persistence':pre_generation==post_generation,
        }
    finally:w.close()


def run_ms1969():
    continuous=run_case(False);replaced=run_case(True)
    assert continuous['signature_set']==replaced['signature_set']
    assert continuous['evaluator_persistence'] is True
    assert replaced['evaluator_persistence'] is False
    # The operational evidence is identical across a world where individuals persist
    # and a world where same-affordance successors replace them during the gap.
    assert continuous['pre']['groups']==replaced['pre']['groups']
    assert continuous['post']['groups']==replaced['post']['groups']
    return {
        'status':'BOUNDARY_CONFIRMED',
        'continuous_case':continuous,
        'hidden_substitution_case':replaced,
        'earned':'AFFORDANCE_SIGNATURE_REAPPEARANCE_SUPPORTS_OPERATIONAL_REASSOCIATION_BUT_CANNOT_ESTABLISH_INDIVIDUAL_PERSISTENCE_ACROSS_UNOBSERVED_SUBSTITUTION',
        'operational_reassociation_authority':'AFFORDANCE_RELATIVE_ONLY',
        'individual_persistence_authority':'NONE',
        'numerical_identity_authority':'NONE',
        'semantic_reference_authority':'NONE',
        'language_authority':'NONE',
        'remaining_boundary':'NO_OVERLAP_REAPPEARANCE_NEEDS_EXTRA_CONTINUITY_EVIDENCE_FOR_INDIVIDUAL_PERSISTENCE',
    }


def main():print(json.dumps(run_ms1969(),indent=2,sort_keys=True))
if __name__=='__main__':main()
