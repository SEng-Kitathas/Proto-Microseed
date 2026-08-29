from __future__ import annotations

import json, os, sys

VALID={tuple(str((n>>shift)&1) for shift in (3,2,1,0)) for n in range(16)}


def main() -> None:
    raw=('0','0','0','0')
    for line in sys.stdin:
        try:
            msg=json.loads(line); op=str(msg.get('op',''))
            if op=='reset':
                vals=tuple(str(x) for x in msg.get('raw_tokens',()))
                if vals not in VALID: raise ValueError('BAD_RAW_QUAD')
                raw=vals; result={'status':'OK'}
            elif op=='apply':
                aid=str(msg.get('action_id',''))
                pa=(int(raw[0])+int(raw[1]))%2
                pb=(int(raw[2])+int(raw[3]))%2
                if aid=='A': end='A-EVEN' if pa==0 else 'A-ODD'
                elif aid=='B': end='B-EVEN' if pb==0 else 'B-ODD'
                elif aid=='Z': end='SAME' if pa==pb else 'DIFF'
                else: raise ValueError('BAD_ACTION')
                result={'status':'OK','action_id':aid,'next_state_id':end,'raw_tokens':list(raw)}
            elif op=='observe':
                result={'status':'OK','raw_tokens':list(raw),'pid':os.getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__': main()
