from __future__ import annotations

import json
import os
import sys

OLD_MAP=(0,0,1,1)
NEW_MAP=(1,0,1,0)
OLD_OFFSETS=(3,17,41,73)
NEW_OFFSETS=(101,151,211,277)


def render(latent,mapping,offsets):
    out=[]
    for i,src in enumerate(mapping):
        state=latent[src]
        out.append((state*state*(i+3)+state*13+offsets[i]) % 1009)
    return out


def main():
    latent=[0,0]; phase='OLD'
    for raw in sys.stdin:
        try:
            msg=json.loads(raw); op=str(msg.get('op',''))
            if op=='reset': latent=[0,0]; phase='OLD'; result={'status':'OK'}
            elif op=='phase':
                phase=str(msg.get('phase','')).upper()
                if phase not in {'OLD','OVERLAP','NEW'}: raise ValueError('BAD_PHASE')
                result={'status':'OK','phase':phase}
            elif op=='act':
                aid=str(msg.get('action_id',''))
                if aid=='FX-A': latent[0]+=1
                elif aid=='FX-B': latent[1]+=1
                elif aid=='FX-G': latent[0]+=1; latent[1]+=1
                else: raise ValueError('BAD_ACTION')
                result={'status':'OK','receipt':'ACTED'}
            elif op=='observe':
                old=render(latent,OLD_MAP,OLD_OFFSETS)
                new=render(latent,NEW_MAP,NEW_OFFSETS)
                channels=old if phase=='OLD' else (new if phase=='NEW' else old+new)
                result={'status':'OK','phase':phase,'channels':channels,'pid':os.getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__': main()
