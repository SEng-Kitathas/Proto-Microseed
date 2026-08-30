from __future__ import annotations

import json, os, sys


def _valid(raw: tuple[str,...]) -> bool:
    return len(raw)==8 and all(x in {'0','1'} for x in raw)


def main() -> None:
    raw=('0',)*8; visible='ALIAS'; value=0.0
    for line in sys.stdin:
        try:
            msg=json.loads(line); op=str(msg.get('op',''))
            if op=='reset':
                vals=tuple(str(x) for x in msg.get('raw_tokens',()))
                if not _valid(vals): raise ValueError('BAD_RAW_OCTET')
                raw=vals; visible='ALIAS'; value=0.0; result={'status':'OK'}
            elif op=='apply':
                aid=str(msg.get('action_id',''))
                if visible!='ALIAS': raise ValueError(f'{aid}_WRONG_STATE')
                pa=(int(raw[0])+int(raw[1]))%2
                pb=(int(raw[2])+int(raw[3]))%2
                pd=(int(raw[4])+int(raw[5]))%2
                pf=(int(raw[6])+int(raw[7]))%2
                cbit=pa^pb
                ebit=cbit^pd
                if aid=='A': visible=f'A{pa}'
                elif aid=='B': visible=f'B{pb}'
                elif aid=='D': visible=f'D{pd}'
                elif aid=='F': visible=f'F{pf}'
                elif aid=='C': visible=f'C{cbit}'
                elif aid=='E': visible=f'E{ebit}'
                elif aid=='G': visible='G-SAME' if ebit==pf else 'G-DIFF'
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
