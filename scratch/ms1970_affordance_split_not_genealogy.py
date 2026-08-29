from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed.cognition.referents import nominate_by_boundary_coherence, derive_affordance_relative_referent_signature
from scratch.ms1958_proto_referent_boundary_coherence import boundaries

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'referent_split_world_server.py'


class SplitWorld:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        r=json.loads(line); assert r.get('status')=='OK',r; return r
    def act(self,a): self.call('act',action_id=a)
    def observe(self): return tuple(self.call('observe')['channels'])
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)


def collect(world,schedule):
    samples=[world.observe()]
    for a in schedule: world.act(a); samples.append(world.observe())
    traces=tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b=boundaries(traces)
    n=nominate_by_boundary_coherence(b); assert n.status=='REFERENT_PARTITION_NOMINATED',n
    rows=[]
    for group in n.groups:
        sig=derive_affordance_relative_referent_signature(b,group,schedule); assert sig.status=='OPERATIONAL_REFERENT_SIGNATURE_DERIVED'
        rows.append({'group':tuple(group),'signature':sig.signature_sha256,'response_rows':sig.action_response_rows})
    return {'boundaries':b,'groups':rows}


def response_map(rows):
    return {action:tuple(bool(x) for x in bits) for action,bits in rows}


def run_case(replacement):
    w=SplitWorld()
    try:
        w.call('reset')
        schedule=('FX-L','FX-N','FX-R','FX-BG','FX-N')
        parent=collect(w,schedule)
        assert len(parent['groups'])==2,parent
        parent_rows=[(row,response_map(row['response_rows'])) for row in parent['groups']]
        parent_candidates=[(row,m) for row,m in parent_rows if any(m.get('FX-L',())) and any(m.get('FX-R',())) and not any(m.get('FX-BG',()))]
        assert len(parent_candidates)==1,parent_rows
        parent_row,parent_map=parent_candidates[0]
        assert parent_map=={'FX-BG':(False,),'FX-L':(True,),'FX-N':(False,False),'FX-R':(True,)}

        w.call('transition',replacement=replacement)
        children=collect(w,schedule)
        assert len(children['groups'])==3,children
        all_child=[(row,response_map(row['response_rows'])) for row in children['groups']]
        descendant_rows=[(row,m) for row,m in all_child if not any(m.get('FX-BG',())) and (any(m.get('FX-L',())) or any(m.get('FX-R',())))]
        assert len(descendant_rows)==2,all_child
        child_maps=[m for _,m in descendant_rows]
        # Parent response is exactly the per-action OR of the two current descendant responses.
        union={a:tuple(any(m[a][i] for m in child_maps) for i in range(len(parent_map[a]))) for a in parent_map}
        assert union==parent_map
        # Descendants are functionally differentiated.
        assert len({tuple(sorted(m.items())) for m in child_maps})==2
        lineage=w.call('evaluator_lineage')
        return {
            'replacement':replacement,'parent':parent,'parent_target':parent_row,'children':children,
            'parent_response':parent_map,'child_responses':child_maps,'union_response':union,
            'evaluator_lineage':lineage,
        }
    finally:w.close()


def run_ms1970():
    split=run_case(False); replacement=run_case(True)
    # Operational parent/child evidence is identical whether evaluator says a real
    # split occurred or two new same-affordance children replaced the parent.
    assert split['parent']==replacement['parent']
    assert split['children']==replacement['children']
    assert split['union_response']==replacement['union_response']
    assert split['evaluator_lineage']['mode']=='SPLIT'
    assert replacement['evaluator_lineage']['mode']=='REPLACEMENT'
    return {
        'status':'BOUNDARY_CONFIRMED',
        'genuine_split_case':split,
        'hidden_replacement_case':replacement,
        'earned':'PARENT_AFFORDANCE_CAN_DECOMPOSE_INTO_MULTIPLE_CURRENT_CHILD_AFFORDANCES_WITHOUT_ESTABLISHING_GENEALOGICAL_SPLIT_OR_IDENTITY_INHERITANCE',
        'affordance_decomposition_authority':'OPERATIONAL_RELATION_ONLY',
        'genealogy_authority':'NONE',
        'numerical_identity_inheritance_authority':'NONE',
        'semantic_reference_authority':'NONE',
        'language_authority':'NONE',
        'remaining_boundary':'AFFORDANCE_DECOMPOSITION != GENEALOGICAL_SPLIT',
    }


def main():print(json.dumps(run_ms1970(),indent=2,sort_keys=True))
if __name__=='__main__':main()
