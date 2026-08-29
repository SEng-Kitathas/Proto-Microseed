from __future__ import annotations

import json, os, sys


def main() -> None:
    first='0'; second='0'; stage=0; visible='ALIAS0'; value=0.0
    for line in sys.stdin:
        try:
            msg=json.loads(line); op=str(msg.get('op',''))
            if op=='reset':
                bits=tuple(str(x) for x in msg.get('bits',()))
                if bits not in {('0','0'),('0','1'),('1','0'),('1','1')}: raise ValueError('BAD_BITS')
                first,second=bits; stage=0; visible='ALIAS0'; value=0.0; result={'status':'OK'}
            elif op=='apply':
                aid=str(msg.get('action_id',''))
                if aid=='PREP':
                    if stage!=0: raise ValueError('PREP_WRONG_STAGE')
                    stage=1; visible='ALIAS1'; value=.7
                elif aid=='B':
                    if stage!=1: raise ValueError('B_WRONG_STAGE')
                    stage=2; visible='SAME' if first==second else 'DIFF'; value=2.2
                else: raise ValueError('BAD_ACTION')
                result={'status':'OK','receipt':aid,'visible':visible}
            elif op in {'observe','observe_outcome'}:
                token=first if stage==0 else second
                result={'status':'OK','next_state_id':visible,'value_id':'V','observed_value':value,'raw_tokens':[token],'pid':os.getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__': main()
