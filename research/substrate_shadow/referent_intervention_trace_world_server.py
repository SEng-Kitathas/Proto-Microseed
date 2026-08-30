from __future__ import annotations

import json
import os
import sys

MAP=(0,0,1,1)
OFFSETS=(7,31,79,127)
MARK_OFFSETS=(211,307,0,0)


def render(latent, marked):
    out=[]
    for i,src in enumerate(MAP):
        state=latent[src]
        mark_term=MARK_OFFSETS[i] if marked[src] else 0
        out.append((state*state*(i+5)+state*17+OFFSETS[i]+mark_term) % 10007)
    return out


def main():
    latent=[0,0]
    marked=[False,False]
    generations=[0,0]
    visible=True
    for raw in sys.stdin:
        try:
            msg=json.loads(raw); op=str(msg.get('op',''))
            if op=='reset':
                latent=[0,0]; marked=[False,False]; generations=[0,0]; visible=True
                result={'status':'OK'}
            elif op=='act':
                aid=str(msg.get('action_id',''))
                if aid=='FX-A': latent[0]+=1
                elif aid=='FX-B': latent[1]+=1
                elif aid=='FX-G': latent[0]+=1; latent[1]+=1
                elif aid=='FX-MARK-A': marked[0]=True
                else: raise ValueError('BAD_ACTION')
                result={'status':'OK','action_id':aid}
            elif op=='gap':
                visible=False; result={'status':'OK'}
            elif op=='reappear':
                variant=str(msg.get('variant','PERSIST'))
                if variant=='PERSIST':
                    pass
                elif variant=='REPLACE_UNMARKED':
                    generations[0]+=1; marked[0]=False
                elif variant=='REPLACE_PERFECT_COPY':
                    generations[0]+=1
                else: raise ValueError('BAD_VARIANT')
                visible=True
                result={'status':'OK','variant':variant}
            elif op=='observe':
                result={'status':'OK','channels':render(latent,marked) if visible else [],'visible':visible,'pid':os.getpid()}
            elif op=='evaluator_identity':
                result={'status':'OK','generations':list(generations),'marked':list(marked),'latent':list(latent)}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else:
                raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
