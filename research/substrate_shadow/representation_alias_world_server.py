from __future__ import annotations

import json
import os
import sys


def main() -> None:
    visible='s0'; latent_context='s0'; value=0.0
    for raw in sys.stdin:
        try:
            msg=json.loads(raw); op=str(msg.get('op',''))
            if op=='reset':
                context=str(msg.get('context',''))
                if context not in {'s0','r'}: raise ValueError('BAD_CONTEXT')
                visible=context; latent_context=context; value=0.0
                result={'status':'OK'}
            elif op=='apply':
                action=str(msg.get('action_id',''))
                if action=='PREP':
                    if visible not in {'s0','r'}: raise ValueError('PREP_WRONG_STATE')
                    visible='s1'; value=1.0
                elif action=='B':
                    if visible!='s1': raise ValueError('B_WRONG_STATE')
                    visible='sx' if latent_context=='s0' else 's2'; value=2.2
                else: raise ValueError('BAD_ACTION')
                result={'status':'OK','receipt':f'APPLIED:{action}','visible':visible,'value':value}
            elif op in {'observe','observe_outcome'}:
                result={'status':'OK','next_state_id':visible,'value_id':'V','observed_value':value,'pid':os.getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__': main()
