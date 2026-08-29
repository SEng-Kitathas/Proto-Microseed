from __future__ import annotations

import json
import os
import sys


def main() -> None:
    latent=[0,0]
    mapping=[0,0,1,1]
    offsets=[3,17,41,73]
    for raw in sys.stdin:
        try:
            msg=json.loads(raw); op=str(msg.get('op',''))
            if op=='configure':
                candidate=[int(x) for x in msg.get('mapping',mapping)]
                if len(candidate)!=4 or any(x not in (0,1) for x in candidate):
                    raise ValueError('BAD_MAPPING')
                mapping=candidate; latent=[0,0]; result={'status':'OK'}
            elif op=='reset':
                latent=[0,0]; result={'status':'OK'}
            elif op=='transform':
                source=int(msg.get('source'))
                if source not in (0,1): raise ValueError('BAD_SOURCE')
                latent[source]+=1; result={'status':'OK','receipt':'TRANSFORMED'}
            elif op=='global_transform':
                latent[0]+=1; latent[1]+=1; result={'status':'OK','receipt':'GLOBAL_TRANSFORMED'}
            elif op=='observe':
                # Each channel has a different rendering function. Channels attached to
                # the same latent source change at the same external boundaries even
                # though their raw values are not equal.
                channels=[]
                for i,src in enumerate(mapping):
                    state=latent[src]
                    channels.append((state*state*(i+2)+state*11+offsets[i]) % 997)
                result={'status':'OK','channels':channels,'server_pid':os.getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK','closed':True}),flush=True); return
            else:
                raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)


if __name__=='__main__': main()
