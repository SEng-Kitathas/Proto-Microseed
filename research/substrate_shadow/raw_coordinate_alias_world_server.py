from __future__ import annotations

import json
import os
import sys


def main() -> None:
    raw=('0','0'); visible='ALIAS'; value=0.0
    for line in sys.stdin:
        try:
            msg=json.loads(line); op=str(msg.get('op',''))
            if op=='reset':
                vals=tuple(str(x) for x in msg.get('raw_tokens',()))
                if vals not in {('0','0'),('0','1'),('1','0'),('1','1')}:
                    raise ValueError('BAD_RAW_PAIR')
                raw=vals; visible='ALIAS'; value=0.0; result={'status':'OK'}
            elif op=='apply':
                if msg.get('action_id')!='B' or visible!='ALIAS': raise ValueError('BAD_ACTION')
                parity=(int(raw[0])+int(raw[1]))%2
                visible='EVEN' if parity==0 else 'ODD'; value=2.2
                result={'status':'OK','receipt':'B','visible':visible}
            elif op in {'observe','observe_outcome'}:
                result={'status':'OK','next_state_id':visible,'value_id':'V','observed_value':value,'raw_tokens':list(raw),'pid':os.getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__':main()
