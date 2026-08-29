from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from research.substrate_shadow.environment_adapter import ShadowEnvironmentAdapter, AdapterConfig
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'research'/'substrate_shadow'/'process_world_server.py'
COMPAT=hashlib.sha256(b'PROCESS-CHARGE-WORLD:v1:PROC-CHARGE->PROC-LEVEL-2:value2.4').hexdigest()


class ProcessChargeWorld:
    name='PROCESS-CHARGE-WORLD'
    action_ids=('PROC-CHARGE',)
    compatibility_sha256=COMPAT
    def __init__(self):
        self.proc=subprocess.Popen([sys.executable,str(SERVER)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=str(ROOT))
        if self.proc.stdin is None or self.proc.stdout is None: raise RuntimeError('PROCESS_WORLD_PIPE_SETUP_FAILED')
        self.pid=self.proc.pid
    def _call(self,op,**payload):
        if self.proc.poll() is not None: raise RuntimeError(f'PROCESS_WORLD_NOT_RUNNING:{self.proc.returncode}')
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps({'op':op,**payload},separators=(',',':'))+'\n'); self.proc.stdin.flush()
        line=self.proc.stdout.readline()
        if not line: raise RuntimeError('PROCESS_WORLD_EMPTY_RESPONSE')
        result=json.loads(line)
        if result.get('status')!='OK': raise RuntimeError(f'PROCESS_WORLD_ERROR:{result}')
        return result
    def reset(self): self._call('reset')
    def apply(self,action_id): return self._call('apply',action_id=action_id)
    def observe(self):
        r=self._call('observe'); r.pop('status',None); return r
    def observe_outcome(self):
        r=self._call('observe_outcome'); r.pop('status',None); return r
    def fork(self): return ProcessChargeWorld()
    def close(self):
        if self.proc.poll() is None:
            try: self._call('close')
            except Exception: pass
        try: self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill(); self.proc.wait(timeout=5)


class ProcessQualificationSource:
    provider_id='QUAL-PROCESS'
    compatibility_sha256=COMPAT
    def __init__(self): self.sample_pids=[]
    def sample(self,action_id):
        world=ProcessChargeWorld()
        try:
            self.sample_pids.append(world.pid)
            world.reset(); before=world.observe(); world.apply(action_id); after=world.observe_outcome(); return before,after
        finally: world.close()


def run_process_world():
    td=tempfile.TemporaryDirectory(prefix='ms1956-proc-'); root=Path(td.name)
    world=ProcessChargeWorld(); source=ProcessQualificationSource(); adapter=ShadowEnvironmentAdapter(world,AdapterConfig(adapter_instance_id='PROC-ADAPTER'),qualification_source=source); ms=Microseed(root)
    try:
        live_pid=world.pid
        adapter.attach(ms)
        relation_id,_=adapter.train_actual_history(ms,'PROC-CHARGE')
        proposal=adapter.zero_row_rehearsal(ms,'PROC-CHARGE'); assert proposal is not None
        assert proposal.final_state_id=='PROC-LEVEL-2' and proposal.predicted_value_effect==2.4
        cmt=ms.derive_bounded_action_commitment(proposal.proposal_id); assert cmt.commitment.value=='YES'
        adapter.reset_control(ms,'FINAL')
        intent=ms.nominate_bounded_action_intent(proposal.proposal_id,adapter.act_obligation()); assert intent['status']=='ACTION_INTENT_NOMINATED'
        ex=ms.execute_bounded_action(intent['intent']['intent_id'],adapter.act_obligation()); assert ex['status']=='ACTION_EXECUTED'
        out=adapter.record_execution_outcome(ms,ex['execution']['execution_id'],evidence_id='E-MS1956-FINAL',capture_id='CAP-MS1956-FINAL')
        assert out['status']=='ACTION_OUTCOME_OBSERVED' and out['outcome']['actual_next_state_id']=='PROC-LEVEL-2'
        assert ms.action_outcome_predictive_relation_status(relation_id)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert source.sample_pids and all(pid!=live_pid for pid in source.sample_pids)
        return {
            'status':'PASS','live_world_pid':live_pid,'qualification_sample_pids':source.sample_pids,
            'distinct_qualification_processes':len(set(source.sample_pids)),
            'predicted_final_state':proposal.final_state_id,'actual_final_state':out['outcome']['actual_next_state_id'],
            'relation_id':relation_id,
            'earned':'SHADOW_SUBSTRATE_OPERATES_ACROSS_SERIALIZED_PROCESS_BOUNDARY_WITH_SEPARATE_QUALIFICATION_PROCESSES',
            'shared_python_object_state':'NO',
        }
    finally:
        _close(ms); world.close(); td.cleanup()


def main(): print(json.dumps(run_process_world(),indent=2,sort_keys=True))
if __name__=='__main__': main()
