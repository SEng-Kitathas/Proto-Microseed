from __future__ import annotations

import json
import os
import sys

MAP=(0,0,1,1)
OFFSETS=(11,37,71,113)
NOISE_PATTERNS=((0,1,-1,2),(1,-1,2,0),(-1,2,0,-2),(2,0,-2,1))


def main():
    latent=[0,0]; obs_index=0; high_noise=False
    for raw in sys.stdin:
        try:
            msg=json.loads(raw); op=str(msg.get('op',''))
            if op=='reset': latent=[0,0]; obs_index=0; high_noise=False; result={'status':'OK'}
            elif op=='noise_mode':
                high_noise=bool(msg.get('high_noise',False)); result={'status':'OK','high_noise':high_noise}
            elif op=='act':
                aid=str(msg.get('action_id',''))
                if aid=='FX-A': latent[0]+=10
                elif aid=='FX-B': latent[1]+=10
                elif aid=='FX-G': latent[0]+=10; latent[1]+=10
                elif aid=='FX-N': pass
                else: raise ValueError('BAD_ACTION')
                result={'status':'OK'}
            elif op=='observe':
                noise=NOISE_PATTERNS[obs_index % len(NOISE_PATTERNS)]; obs_index+=1
                channels=[]
                for i,src in enumerate(MAP):
                    # Large source changes + small independent channel jitter. In
                    # hostile high-noise mode, channel 0 receives extra unmodeled
                    # jitter large enough to exceed the earlier calibration bound.
                    base=latent[src]*(i+2)+OFFSETS[i]
                    extra=(12 if (high_noise and i==0 and obs_index%2==0) else 0)
                    channels.append(base+noise[i]+extra)
                result={'status':'OK','channels':channels,'pid':os.getpid()}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__': main()
