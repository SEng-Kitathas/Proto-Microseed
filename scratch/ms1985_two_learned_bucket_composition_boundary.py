from __future__ import annotations

import json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, EpistemicStatus, ExternalProjectionQualifier, Microseed,
    OperationalFrameContract, ProjectionDiscoveryConfig, ProjectionSample,
    QualificationState,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'learned_bucket_composition_world_server.py'
QUADS=tuple(tuple(str((n>>shift)&1) for shift in (3,2,1,0)) for n in range(16))


class World:
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT)); assert self.proc.stdin and self.proc.stdout
    def call(self,op,**payload):
        assert self.proc.stdin and self.proc.stdout
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline(); assert line
        row=json.loads(line); assert row.get('status')=='OK',row; return row
    def reset(self,raw): self.call('reset',raw_tokens=list(raw))
    def apply(self,action): return self.call('apply',action_id=action)
    def close(self):
        if self.proc.poll() is None:
            try:self.call('close')
            except Exception:pass
        try:self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=5)


def build(root:Path):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract(
        'F','four-coordinate composition frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1985',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    return m


def process_samples(action:str,repetitions:int=4):
    world=World(); rows=[]
    try:
        i=0
        for rep in range(repetitions):
            for raw in QUADS:
                world.reset(raw); out=world.apply(action)
                rows.append(ProjectionSample(f'{action}-{i}',raw,action,out['next_state_id'],'S','F',0)); i+=1
        return tuple(rows)
    finally:world.close()


def admit_source_projection(m,action,expected_positions,projection_id):
    rows=process_samples(action,4)
    train=rows[:48]; validation=rows[48:]
    cfg=ProjectionDiscoveryConfig(max_subset=2,min_train_support=32,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=12)
    found=m.discover_epistemic_projection_candidates(train,validation,cfg); assert found,found
    cs=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
    exact=[c for c in cs if c.input_positions==tuple(expected_positions)]
    assert len(exact)==1,[(c.input_positions,c.validation_accuracy,c.lift) for c in cs]
    c=exact[0]; assert c.validation_accuracy==1.0
    q=m.append_evidence(f'Q-{projection_id}',{'kind':'SOURCE_PROJECTION_HOLDOUT','candidate_sha256':c.digest(),'action':action},EpistemicStatus.PRESSURE_SUPPORTED,source=f'EXTERNAL-{projection_id}')
    ticket=ExternalProjectionQualifier(m.evidence,qualifier_id=f'EXTERNAL-{projection_id}').qualify(c,qualification_evidence=(q,))
    rec=m.admit_epistemic_projection_candidate(ticket,projection_id=projection_id); assert rec.current
    return c,rec


def second_stage_samples(pa,pb,repetitions=4):
    world=World(); rows=[]
    try:
        i=0
        for rep in range(repetitions):
            for raw in QUADS:
                world.reset(raw); out=world.apply('Z')
                ba=pa.project(raw); bb=pb.project(raw)
                assert ba is not None and bb is not None
                rows.append(ProjectionSample(f'Z2-{i}',(ba,bb),'Z',out['next_state_id'],'S','F',0)); i+=1
        return tuple(rows)
    finally:world.close()


def external_holdout(candidate,pa,pb):
    world=World(); rows=[]; pred={(b,a):e for b,a,e in candidate.bucket_action_prediction}
    try:
        for raw in QUADS:
            world.reset(raw); out=world.apply('Z')
            source=(pa.project(raw),pb.project(raw)); assert None not in source
            bucket=candidate.project(source); assert bucket is not None
            assert pred[(bucket,'Z')]==out['next_state_id']
            rows.append({'raw':raw,'source_buckets':source,'second_stage_bucket':bucket,'actual_end':out['next_state_id']})
        return rows
    finally:world.close()


def run_ms1985():
    td=tempfile.TemporaryDirectory(prefix='ms1985-bucket-compose-'); m=build(Path(td.name))
    try:
        pa,ra=admit_source_projection(m,'A',(0,1),'P-MS1985-A')
        pb,rb=admit_source_projection(m,'B',(2,3),'P-MS1985-B')
        rows=second_stage_samples(pa,pb,4)
        assert len(rows)==64
        assert len({r.raw_tokens[0] for r in rows})==2 and len({r.raw_tokens[1] for r in rows})==2
        train=rows[:48]; validation=rows[48:]

        cfg1=ProjectionDiscoveryConfig(max_subset=1,min_train_support=32,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        one=m.discover_epistemic_projection_candidates(train,validation,cfg1)
        assert one==[],one

        cfg2=ProjectionDiscoveryConfig(max_subset=2,min_train_support=32,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
        found=m.discover_epistemic_projection_candidates(train,validation,cfg2); assert found,found
        cs=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
        exact=[c for c in cs if c.input_positions==(0,1) and c.digest() not in {pa.digest(),pb.digest()}]
        assert exact,[(c.input_positions,c.validation_accuracy,c.lift,c.candidate_id) for c in cs]
        c=exact[-1]
        assert c.validation_accuracy==1.0 and c.lift>=.49
        holdout=external_holdout(c,pa,pb); assert len(holdout)==16
        return {
            'status':'BOUNDARY_CONFIRMED',
            'source_projection_A_positions':list(pa.input_positions),
            'source_projection_B_positions':list(pb.input_positions),
            'source_projection_A_sha256':pa.digest(),
            'source_projection_B_sha256':pb.digest(),
            'second_stage_sample_count':len(rows),
            'single_source_bucket_candidates':0,
            'second_stage_positions':list(c.input_positions),
            'second_stage_validation_accuracy':c.validation_accuracy,
            'second_stage_lift':c.lift,
            'external_holdout_count':len(holdout),
            'earned':'EXISTING_PROJECTION_SEARCH_CAN_COMPOSE_TWO_INDEPENDENTLY_LEARNED_OPAQUE_BUCKETS_INTO_A_SECOND_STAGE_PREDICTIVE_PARTITION_WHEN_EACH_BUCKET_ALONE_IS_INSUFFICIENT',
            'missing_owner':'ENTITY_OWNED_CURRENT_PROJECTION_BUCKET_VECTOR_TO_PROJECTION_SAMPLE',
            'new_projection_search_mechanism_required':'NO',
            'source_bucket_authority':'HARNESS_DERIVED_FROM_EXACT_ADMITTED_SOURCE_PROJECTION_CONTENT',
            'semantic_symbol_authority':'NONE','semantic_composition_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:_close(m);td.cleanup()


def main():print(json.dumps(run_ms1985(),indent=2,sort_keys=True,default=str))
if __name__=='__main__':main()
