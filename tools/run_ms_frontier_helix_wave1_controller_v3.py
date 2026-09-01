
from __future__ import annotations
from pathlib import Path
import subprocess,json,time,urllib.request,traceback,os
ORCH=Path(__file__).resolve().parents[1]
ROOT=Path(__file__).resolve().parents[3]
RUNTIME=ROOT/'.pcmmad_sync_runs'/'frontier_helix_runtime_v3'
ARMS=['A_TARGET','B_DRIFT','D_CFE','E_IDENTITY','F_VALUE','G_NAKED','H_LANGUAGE','I_GROWTH','K_RED_TEAM']
PY=r'C:\Users\ancal\AppData\Local\Programs\Python\Python312\python.exe'
RUNNER=ORCH/'tools'/'run_ms_frontier_helix_wave1_v3.py'
CANON='ed2cde491962105b0d853b7fd82d8e8b3d81bd8a'
def health(port):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=5) as r:return r.status==200
    except:return False
def write(o):RUNTIME.mkdir(parents=True,exist_ok=True);(RUNTIME/'controller_v3_summary.json').write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')
summary={'started_epoch':time.time(),'controller_pid':os.getpid(),'orchestration_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ORCH,text=True).strip(),'canonical_parent':CANON,'promotion_authority':'NONE','arms':{},'status':'RUNNING'};write(summary)
if not (health(8091) and health(8092)):summary['status']='BLOCKED_MODEL_HEALTH';write(summary);raise SystemExit(2)
for arm in ARMS:
 wt=ROOT/'.pcmmad_sync_runs'/('wt_frontier_'+arm.lower());out=RUNTIME/f'{arm}.stdout.log';err=RUNTIME/f'{arm}.stderr.log';entry={'status':'STARTING','worktree':str(wt),'started_epoch':time.time()};summary['arms'][arm]=entry;write(summary)
 try:
  of=out.open('ab');ef=err.open('ab');child=subprocess.Popen([PY,str(RUNNER),'--worktree',str(wt),'--arm',arm,'--max-passes','12','--commit-push'],cwd=wt,stdout=of,stderr=ef);entry.update({'status':'RUNNING','child_pid':child.pid});write(summary);rc=child.wait();of.close();ef.close()
  prod=subprocess.run(['git','diff','--name-only',CANON+'..HEAD','--','microseed'],cwd=wt,text=True,capture_output=True).stdout.splitlines();entry.update({'return_code':rc,'finished_epoch':time.time(),'organism_delta':prod,'head':subprocess.run(['git','rev-parse','HEAD'],cwd=wt,text=True,capture_output=True).stdout.strip(),'branch':subprocess.run(['git','branch','--show-current'],cwd=wt,text=True,capture_output=True).stdout.strip(),'stderr_bytes':err.stat().st_size if err.exists() else 0});entry['status']='COMPLETE' if rc==0 and not prod else ('BLOCKED_ORGANISM_DELTA' if prod else 'FAILED')
 except Exception as e:entry.update({'status':'CONTROLLER_EXCEPTION','error':repr(e),'traceback':traceback.format_exc(),'finished_epoch':time.time()})
 write(summary)
summary['finished_epoch']=time.time();summary['status']='COMPLETE' if all(v.get('status')=='COMPLETE' for v in summary['arms'].values()) else 'PARTIAL_OR_FAILED';write(summary);print(json.dumps(summary,indent=2),flush=True)
