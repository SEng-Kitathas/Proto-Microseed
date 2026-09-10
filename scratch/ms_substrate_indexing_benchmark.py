from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import statistics
import time

from microseed import Microseed
from microseed.development.action_closure import ActionClosureRegistry, ActionExecutionRecord
from tests.embodiment.test_ms1402_integration import make_ms, setup_world, rows, opts, act_obligation


def _median_ms(fn, reps: int) -> float:
    samples=[]
    for _ in range(reps):
        t=time.perf_counter_ns(); fn(); samples.append((time.perf_counter_ns()-t)/1e6)
    return float(statistics.median(samples))


def run() -> dict[str, object]:
    execution_index=[]
    for n in (195,1108,5000,20000):
        reg=ActionClosureRegistry()
        for i in range(n):
            reg.add_execution(ActionExecutionRecord(f'E{i}',f'I{i}','C',0,'S','a'*64))
        membership=_median_ms(lambda: reg.has_executed_intent('NEVER'),5000)
        add_samples=[]
        for k in range(100):
            clone=ActionClosureRegistry()
            clone.executions=dict(reg.executions)
            clone._executed_intent_ids=set(reg._executed_intent_ids)
            x=ActionExecutionRecord(f'EN{k}',f'IN{k}','C',0,'S','a'*64)
            t=time.perf_counter_ns(); clone.add_execution(x); add_samples.append((time.perf_counter_ns()-t)/1e6)
        execution_index.append({'n':n,'membership_median_ms':membership,'add_median_ms':float(statistics.median(add_samples))})

    boot_index=[]
    for n in (195,1108,5000,20000):
        td=TemporaryDirectory(); m=Microseed(Path(td.name))
        try:
            current=len(m.store.events())
            for i in range(max(0,n-current)):
                m.store.append('BENCH',{'i':i,'payload':'x'*32})
            boot_index.append({'n':len(m.store.events()),'latest_boot_median_ms':_median_ms(m._current_runtime_boot_seq,500)})
        finally:
            try: m.evidence.conn.close(); m.store.conn.close(); m.biography.close()
            except Exception: pass
            td.cleanup()

    execute_path=[]
    for n in (195,1108,5000):
        td,m=make_ms()
        try:
            setup_world(m)
            proposal=m.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V')
            nominated=m.nominate_bounded_action_intent(proposal.proposal_id,act_obligation())
            proto=m.action_closure.intents[nominated['intent']['intent_id']]
            m.action_closure.executions={
                f'OLD-E-{i}':ActionExecutionRecord(f'OLD-E-{i}',f'OLD-I-{i}','A',0,'S0','a'*64)
                for i in range(n)
            }
            m.action_closure._executed_intent_ids={f'OLD-I-{i}' for i in range(n)}
            samples=[]
            for k in range(80):
                intent=replace(proto,intent_id=f'BENCH-I-{n}-{k}')
                m.action_closure.add_intent(intent)
                t=time.perf_counter_ns(); result=m.execute_bounded_action(intent.intent_id,act_obligation()); samples.append((time.perf_counter_ns()-t)/1e6)
                if result.get('status')!='ACTION_EXECUTED': raise RuntimeError(result)
            ordered=sorted(samples)
            execute_path.append({'n_prior_executions':n,'median_execute_ms':float(statistics.median(samples)),'mean_execute_ms':float(statistics.mean(samples)),'p95_ms':float(ordered[int(.95*len(ordered))-1])})
        finally:
            try: m.evidence.conn.close(); m.store.conn.close(); m.biography.close()
            except Exception: pass
            td.cleanup()

    return {
        'status':'PASS_MEASURED_INDEXED_SUBSTRATE',
        'execution_index':execution_index,
        'boot_index':boot_index,
        'execute_path':execute_path,
        'authority_gain':'NONE',
        'note':'Performance evidence only. Absolute milliseconds are machine-specific; scaling shape is the discriminator.',
    }


if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
