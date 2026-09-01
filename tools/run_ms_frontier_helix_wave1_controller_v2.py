
from __future__ import annotations
from pathlib import Path
import subprocess,sys,json,time,urllib.request,traceback,os
ORCHESTRATION=Path(__file__).resolve().parents[1]
ROOT=Path(__file__).resolve().parents[3]
RUNTIME=ROOT/'.pcmmad_sync_runs'/'frontier_helix_runtime'
ARMS=['A_TARGET','B_DRIFT','D_CFE','E_IDENTITY','F_VALUE','G_NAKED','H_LANGUAGE','I_GROWTH','K_RED_TEAM']
PY=r'C:\Users\ancal\AppData\Local\Programs\Python\Python312\python.exe'
CANON='ed2cde491962105b0d853b7fd82d8e8b3d81bd8a'
CONTROL='408c265bfdc8052a614b6cb4cbe51a60673a73eb'
def health(port):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=5) as r:return r.status==200
    except:return False
def write_summary(o):
    RUNTIME.mkdir(parents=True,exist_ok=True)
    (RUNTIME/'wave1_v2_controller_summary.json').write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')
summary={'started_epoch':time.time(),'controller_pid':os.getpid(),'canonical_parent':CANON,'control_head':CONTROL,'promotion_authority':'NONE','arms':{},'status':'RUNNING'}
write_summary(summary)
if not (health(8091) and health(8092)):
    summary['status']='BLOCKED_MODEL_SERVER_HEALTH';write_summary(summary);raise SystemExit(2)
for arm in ARMS:
    wt=ROOT/'.pcmmad_sync_runs'/('wt_frontier_'+arm.lower())
    out=RUNTIME/f'{arm}.v2.stdout.log';err=RUNTIME/f'{arm}.v2.stderr.log'
    entry={'started_epoch':time.time(),'worktree':str(wt),'status':'STARTING'};summary['arms'][arm]=entry;write_summary(summary)
    try:
        of=out.open('ab'); ef=err.open('ab')
        child=subprocess.Popen([PY,str(wt/'tools/run_ms_frontier_helix_wave1_v2.py'),'--worktree',str(wt),'--arm',arm,'--max-passes','20','--commit-push'],cwd=wt,stdout=of,stderr=ef)
        entry.update({'status':'RUNNING','child_pid':child.pid});write_summary(summary)
        rc=child.wait();of.close();ef.close()
        entry.update({'return_code':rc,'finished_epoch':time.time(),'stdout_bytes':out.stat().st_size,'stderr_bytes':err.stat().st_size})
        prod=subprocess.run(['git','diff','--name-only',CANON+'..HEAD','--','microseed'],cwd=wt,text=True,capture_output=True).stdout.splitlines()
        entry['organism_delta']=prod
        entry['head']=subprocess.run(['git','rev-parse','HEAD'],cwd=wt,text=True,capture_output=True).stdout.strip()
        entry['branch']=subprocess.run(['git','branch','--show-current'],cwd=wt,text=True,capture_output=True).stdout.strip()
        entry['status']='COMPLETE' if rc==0 and not prod else ('BLOCKED_ORGANISM_DELTA' if prod else 'FAILED')
    except Exception as e:
        entry.update({'status':'CONTROLLER_EXCEPTION','error':repr(e),'traceback':traceback.format_exc(),'finished_epoch':time.time()})
    write_summary(summary)
summary['finished_epoch']=time.time();summary['status']='COMPLETE' if all(x.get('status')=='COMPLETE' for x in summary['arms'].values()) else 'PARTIAL_OR_FAILED';write_summary(summary)
print(json.dumps(summary,indent=2),flush=True)
