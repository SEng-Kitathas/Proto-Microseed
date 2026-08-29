from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import nominate_by_boundary_coherence, derive_affordance_relative_referent_signature
from scratch.ms1958_proto_referent_boundary_coherence import boundaries

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'referent_handoff_world_server.py'
OLD_MAP=(0,0,1,1)
NEW_MAP=(1,0,1,0)


class HandoffWorld:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        assert self.proc.stdin is not None and self.proc.stdout is not None
    def call(self,op,**payload):
        assert self.proc.stdin is not None and self.proc.stdout is not None
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
        except subprocess.TimeoutExpired:
            self.proc.kill(); self.proc.wait(timeout=5)


def collect_phase(world,phase,schedule):
    world.phase(phase)
    samples=[world.observe()]
    for action in schedule:
        world.act(action); samples.append(world.observe())
    traces=tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b=boundaries(traces)
    n=nominate_by_boundary_coherence(b)
    assert n.status=='REFERENT_PARTITION_NOMINATED',n
    rows=[]
    for group in n.groups:
        sig=derive_affordance_relative_referent_signature(b,group,schedule)
        assert sig.status=='OPERATIONAL_REFERENT_SIGNATURE_DERIVED',sig
        rows.append({'group':tuple(group),'signature':sig.signature_sha256,'response_rows':sig.action_response_rows})
    return {'phase':phase,'boundaries':b,'groups':tuple(rows)}


def latent_set(group,phase):
    if phase=='OLD': mapping=OLD_MAP
    elif phase=='NEW': mapping=NEW_MAP
    elif phase=='OVERLAP': mapping=OLD_MAP+NEW_MAP
    else: raise ValueError(phase)
    return {mapping[i] for i in group}


def run_overlap_continuity():
    w=HandoffWorld()
    try:
        w.call('reset')
        schedule=('FX-A','FX-B','FX-G','FX-A','FX-B')
        old=collect_phase(w,'OLD',schedule)
        overlap=collect_phase(w,'OVERLAP',schedule)
        new=collect_phase(w,'NEW',schedule)

        # Each phase recovers exactly two operational groups and each group is pure
        # against evaluator-only latent mapping.
        for phase_result in (old,overlap,new):
            assert len(phase_result['groups'])==2
            assert all(len(latent_set(row['group'],phase_result['phase']))==1 for row in phase_result['groups'])

        # Overlap groups must include channels from both the old and new sensor layouts.
        for row in overlap['groups']:
            g=set(row['group'])
            assert g & {0,1,2,3}
            assert g & {4,5,6,7}

        # Affordance signature is stable old -> overlap -> new.
        old_by={row['signature']:row for row in old['groups']}
        ov_by={row['signature']:row for row in overlap['groups']}
        new_by={row['signature']:row for row in new['groups']}
        assert set(old_by)==set(ov_by)==set(new_by) and len(old_by)==2

        # Evaluator-only check: each signature follows the same latent source through
        # old representation, bridging overlap, and new representation.
        alignment={}
        for sig in old_by:
            l0=next(iter(latent_set(old_by[sig]['group'],'OLD')))
            l1=next(iter(latent_set(ov_by[sig]['group'],'OVERLAP')))
            l2=next(iter(latent_set(new_by[sig]['group'],'NEW')))
            assert l0==l1==l2
            alignment[sig]=l0

        bridge={sig:{'old_group':old_by[sig]['group'],'overlap_group':ov_by[sig]['group'],'new_group':new_by[sig]['group']} for sig in old_by}
        return {
            'status':'PASS',
            'bridge':bridge,
            'evaluator_alignment':alignment,
            'earned':'REFERENT_SPECIFIC_OVERLAP_EVIDENCE_CAN_BRIDGE_OPERATIONAL_PROTO_REFERENT_REPRESENTATIONS_ACROSS_SENSOR_HANDOFF',
            'continuity_authority':'OPERATIONAL_REFERENT_CONTINUITY_ONLY',
            'numerical_identity_authority':'NONE',
            'semantic_reference_authority':'NONE',
            'remaining_boundary':'OVERLAP_BOUND_OPERATIONAL_CONTINUITY != NUMERICAL_OBJECT_IDENTITY',
        }
    finally:w.close()


def main(): print(json.dumps(run_overlap_continuity(),indent=2,sort_keys=True))
if __name__=='__main__': main()
