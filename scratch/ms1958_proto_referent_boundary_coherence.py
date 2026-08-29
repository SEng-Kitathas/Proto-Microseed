from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import nominate_by_boundary_coherence

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'referent_world_server.py'


class ReferentProcessWorld:
    def __init__(self,mapping):
        self.mapping=tuple(int(x) for x in mapping)
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        if self.proc.stdin is None or self.proc.stdout is None: raise RuntimeError('REFERENT_WORLD_PIPE_SETUP_FAILED')
        self.pid=self.proc.pid
        self._call('configure',mapping=list(self.mapping))
    def _call(self,op,**payload):
        if self.proc.poll() is not None: raise RuntimeError(f'REFERENT_WORLD_NOT_RUNNING:{self.proc.returncode}')
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline()
        if not line: raise RuntimeError('REFERENT_WORLD_EMPTY_RESPONSE')
        result=json.loads(line)
        if result.get('status')!='OK': raise RuntimeError(f'REFERENT_WORLD_ERROR:{result}')
        return result
    def reset(self): self._call('reset')
    def transform(self,source): self._call('transform',source=int(source))
    def global_transform(self): self._call('global_transform')
    def observe(self):
        r=self._call('observe'); return tuple(r['channels'])
    def close(self):
        if self.proc.poll() is None:
            try:self._call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill(); self.proc.wait(timeout=5)


def boundaries(traces):
    out=[]
    for values in traces:
        out.append(tuple(i for i in range(1,len(values)) if values[i]!=values[i-1]))
    return tuple(out)


def collect(mapping,schedule):
    w=ReferentProcessWorld(mapping)
    try:
        samples=[w.observe()]
        for op in schedule:
            if op=='G': w.global_transform()
            else: w.transform(int(op))
            samples.append(w.observe())
        traces=tuple(tuple(sample[i] for sample in samples) for i in range(4))
        b=boundaries(traces)
        nomination=nominate_by_boundary_coherence(b)
        return {
            'pid':w.pid,
            'mapping':mapping,
            'samples':samples,
            'boundaries':b,
            'nomination':{
                'status':nomination.status,
                'groups':nomination.groups,
                'reason':nomination.reason,
                'identity_authority':nomination.identity_authority,
            },
        }
    finally:w.close()


def group_latent_sets(result):
    mapping=result['mapping']
    return tuple(tuple(sorted({mapping[i] for i in group})) for group in result['nomination']['groups'])


def run_proto_reference():
    schedule=(0,0,1,'G',1,0,1)
    a=collect((0,0,1,1),schedule)
    b=collect((1,0,1,0),schedule)

    assert a['nomination']['status']=='REFERENT_PARTITION_NOMINATED'
    assert b['nomination']['status']=='REFERENT_PARTITION_NOMINATED'
    assert a['nomination']['identity_authority']==b['nomination']['identity_authority']=='NONE'
    # Each nominated group is pure with respect to evaluator-only latent source mapping.
    assert all(len(x)==1 for x in group_latent_sets(a)),group_latent_sets(a)
    assert all(len(x)==1 for x in group_latent_sets(b)),group_latent_sets(b)

    # Channel permutation changes concrete group indices. The current mechanism has
    # no cross-session stable referent identifier and does not pretend otherwise.
    assert a['nomination']['groups']!=b['nomination']['groups']

    # Symmetry hostile: when all channels share the same boundaries, do not invent
    # distinct referents from synchrony alone.
    sym=collect((0,0,1,1),('G','G','G','G'))
    assert sym['nomination']['status']=='UNKNOWN_INCOMPLETE'
    assert sym['nomination']['reason']=='BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS'
    assert sym['nomination']['identity_authority']=='NONE'

    return {
        'status':'PASS',
        'world_a':a,
        'world_b_permuted_channels':b,
        'symmetric_hostile':sym,
        'earned':'BOUNDARY_COHERENCE_CAN_NOMINATE_WITHIN_SESSION_OPAQUE_SOURCE_PARTITIONS_ACROSS_APPEARANCE_TRANSFORMATIONS_WITHOUT_OBJECT_IDENTITY_AUTHORITY',
        'remaining_boundary':'WITHIN_SESSION_PARTITION != CROSS_SESSION_REFERENT_IDENTITY',
        'semantic_reference_authority':'NONE',
        'language_authority':'NONE',
    }


def main(): print(json.dumps(run_proto_reference(),indent=2,sort_keys=True))
if __name__=='__main__': main()
