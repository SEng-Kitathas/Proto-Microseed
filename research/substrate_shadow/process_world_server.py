from __future__ import annotations

import json
import sys


def main() -> None:
    level=0
    for raw in sys.stdin:
        try:
            msg=json.loads(raw)
            op=str(msg.get('op',''))
            if op=='reset':
                level=0; result={'status':'OK'}
            elif op=='apply':
                if msg.get('action_id')!='PROC-CHARGE': raise ValueError('UNKNOWN_ACTION')
                level=2; result={'status':'OK','receipt':'process-charge','level':level}
            elif op in {'observe','observe_outcome'}:
                result={'status':'OK','next_state_id':f'PROC-LEVEL-{level}','observed_value':2.4 if level>=2 else 0.0,'server_pid':__import__('os').getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK','closed':True}),flush=True); return
            else:
                raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
