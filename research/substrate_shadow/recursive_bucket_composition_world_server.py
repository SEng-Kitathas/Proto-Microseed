from __future__ import annotations

import json, os, sys

VALID={tuple(str((n>>shift)&1) for shift in (5,4,3,2,1,0)) for n in range(64)}


def main() -> None:
    raw=('0','0','0','0','0','0'); visible='ALIAS'; value=0.0
    for line in sys.stdin:
        try:
            msg=json.loads(line); op=str(msg.get('op',''))
            if op=='reset':
                vals=tuple(str(x) for x in msg.get('raw_tokens',()))
                if vals not in VALID: raise ValueError('BAD_RAW_SEXTET')
                raw=vals; visible='ALIAS'; value=0.0; result={'status':'OK'}
            elif op=='apply':
                aid=str(msg.get('action_id',''))
                pa=(int(raw[0])+int(raw[1]))%2
                pb=(int(raw[2])+int(raw[3]))%2
                pd=(int(raw[4])+int(raw[5]))%2
                cbit=0 if pa==pb else 1
                if visible!='ALIAS': raise ValueError(f'{aid}_WRONG_STATE')
                if aid=='A': visible='A0' if pa==0 else 'A1'
                elif aid=='B': visible='B0' if pb==0 else 'B1'
                elif aid=='D': visible='D0' if pd==0 else 'D1'
                elif aid=='C': visible='C-SAME' if cbit==0 else 'C-DIFF'
                elif aid=='E': visible='E-SAME' if cbit==pd else 'E-DIFF'
                else: raise ValueError('BAD_ACTION')
                value=2.2
                result={'status':'OK','receipt':aid,'next_state_id':visible,'raw_tokens':list(raw)}
            elif op in {'observe','observe_outcome'}:
                result={'status':'OK','next_state_id':visible,'value_id':'V','observed_value':value,'raw_tokens':list(raw),'pid':os.getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__': main()
