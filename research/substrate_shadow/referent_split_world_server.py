from __future__ import annotations

import json
import os
import sys


def main():
    phase='PARENT'; parent=0; left=0; right=0; background=0; replaced=False
    for raw in sys.stdin:
        try:
            msg=json.loads(raw); op=str(msg.get('op',''))
            if op=='reset':
                phase='PARENT'; parent=0; left=0; right=0; background=0; replaced=False; result={'status':'OK'}
            elif op=='transition':
                phase='CHILDREN'; replaced=bool(msg.get('replacement',False)); left=0; right=0
                result={'status':'OK','phase':phase}
            elif op=='act':
                aid=str(msg.get('action_id',''))
                if phase=='PARENT':
                    if aid in {'FX-L','FX-R'}: parent+=1
                    elif aid=='FX-BG': background+=1
                    elif aid!='FX-N': raise ValueError('BAD_ACTION')
                else:
                    if aid=='FX-L': left+=1
                    elif aid=='FX-R': right+=1
                    elif aid=='FX-BG': background+=1
                    elif aid!='FX-N': raise ValueError('BAD_ACTION')
                result={'status':'OK'}
            elif op=='observe':
                if phase=='PARENT':
                    channels=[11+parent*17,31+parent*23,401+background*13,431+background*19]
                else:
                    channels=[101+left*19,151+left*29,211+right*31,271+right*37,401+background*13,431+background*19]
                result={'status':'OK','phase':phase,'channels':channels,'pid':os.getpid()}
            elif op=='evaluator_lineage':
                result={'status':'OK','mode':'REPLACEMENT' if replaced else 'SPLIT','parent_generation':0,'child_parent_generation':None if replaced else 0}
            elif op=='close':
                print(json.dumps({'status':'OK'}),flush=True); return
            else: raise ValueError(f'UNKNOWN_OP:{op}')
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:
            print(json.dumps({'status':'ERROR','error':f'{type(exc).__name__}:{exc}'},separators=(',',':')),flush=True)

if __name__=='__main__':main()
