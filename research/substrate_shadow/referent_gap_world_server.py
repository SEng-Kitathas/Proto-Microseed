from __future__ import annotations

import json
import os
import sys

MAP=(0,0,1,1)
OFFSETS=(7,31,79,127)


def render(latent):
    out=[]
    for i,src in enumerate(MAP):
        state=latent[src]
        out.append((state*state*(i+5)+state*17+OFFSETS[i]) % 1013)
    return out


def main():
    latent=[0,0]; visible=True; generations=[0,0]
    for raw in sys.stdin:
        try:
            msg=json.loads(raw); op=str(msg.get('op',''))
            if op=='reset':
                latent=[0,0]; visible=True; generations=[0,0]; result={'status':'OK'}
            elif op=='gap':
                visible=False; result={'status':'OK'}
            elif op=='reappear':
                substitute=bool(msg.get('substitute',False))
                latent=[0,0]
                if substitute: generations=[g+1 for g in generations]
                visible=True
                result={'status':'OK','substituted':substitute}
            elif op=='act':
                aid=str(msg.get('action_id',''))
                if aid=='FX-A': latent[0]+=1
                elif aid=='FX-B': latent[1]+=1
                elif aid=='FX-G': latent[0]+=1; latent[1]+=1
                else: raise ValueError('BAD_ACTION')
                result={'status':'OK'}
            elif op=='observe':
                result={'status':'OK','channels':render(latent) if visible else [],'visible':visible,'pid':os.getpid()}
            elif op=='evaluator_identity':
                result={'status':'OK','generations':generations}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__':main()
