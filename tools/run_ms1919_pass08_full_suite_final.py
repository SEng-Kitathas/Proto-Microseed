from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'/'ms1919_pass08_full_suite_final'
if REPORT.exists(): shutil.rmtree(REPORT)
REPORT.mkdir(parents=True,exist_ok=True)
INITIAL_SHARDS=36
MAX_PARALLEL=6
GROUP_TIMEOUT=35


def source_snapshot():
    rows=[]; h=hashlib.sha256()
    for base in (ROOT/'microseed', ROOT/'tests'):
        for p in sorted(base.rglob('*.py')):
            rel=str(p.relative_to(ROOT)).replace('\\','/')
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            rows.append((rel,digest)); h.update(rel.encode()); h.update(b'\0'); h.update(digest.encode()); h.update(b'\n')
    return h.hexdigest(), rows

start_source_sha,start_rows=source_snapshot()
all_files=sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'tests').rglob('test_*.py'))
pending=[(f's{i:02d}',all_files[i::INITIAL_SHARDS],0) for i in range(INITIAL_SHARDS) if all_files[i::INITIAL_SHARDS]]


def run_group(group_id,files,depth):
    d=REPORT/group_id; d.mkdir(parents=True,exist_ok=True)
    outp=d/'pytest.stdout.log'; errp=d/'pytest.stderr.log'; recp=d/'receipt.json'
    cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q','-p','no:cacheprovider',*files]
    started=time.time()
    try:
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=GROUP_TIMEOUT)
        code,out,err=r.returncode,r.stdout,r.stderr; marker='COMPLETE'; cls='PASS' if code==0 else 'NEGATIVE_OR_COMPATIBILITY_REVIEW_REQUIRED'
    except subprocess.TimeoutExpired as exc:
        code=None; out=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
        err=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
        marker='INCOMPLETE'; cls='UNKNOWN_INCOMPLETE_TIMEOUT'
    finished=time.time(); outp.write_text(out,encoding='utf-8'); errp.write_text(err,encoding='utf-8')
    m=re.search(r'(\d+) passed',out); passed=int(m.group(1)) if m else None
    rec={'schema':'microseed.ms1919.pass08.final-shard.v1','group_id':group_id,'depth':depth,'file_count':len(files),'files':files,'command':cmd,'duration_seconds':round(finished-started,6),'exit_code':code,'classification':cls,'completion_marker':marker,'passed_count':passed,'stdout_path':str(outp.relative_to(ROOT)),'stderr_path':str(errp.relative_to(ROOT)),'stdout_sha256':hashlib.sha256(out.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(err.encode()).hexdigest(),'stdout_tail':'\n'.join(out.splitlines()[-8:]),'stderr_tail':'\n'.join(err.splitlines()[-8:])}
    recp.write_text(json.dumps(rec,indent=2),encoding='utf-8')
    return rec

selected=[]; negatives=[]; terminal_unknown=[]; all_runs=[]; rounds=0
while pending:
    rounds+=1; current=pending; pending=[]
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        futures={pool.submit(run_group,gid,files,depth):(gid,files,depth) for gid,files,depth in current}
        for fut in as_completed(futures):
            rec=fut.result(); all_runs.append(rec)
            if rec['classification']=='PASS' and rec['completion_marker']=='COMPLETE' and rec['exit_code']==0:
                selected.append(rec)
            elif rec['classification']=='UNKNOWN_INCOMPLETE_TIMEOUT':
                files=rec['files']; depth=rec['depth']
                if len(files)<=1:
                    terminal_unknown.append(rec)
                else:
                    mid=(len(files)+1)//2
                    pending.append((rec['group_id']+'a',files[:mid],depth+1))
                    pending.append((rec['group_id']+'b',files[mid:],depth+1))
            else:
                negatives.append(rec)
    if negatives or terminal_unknown: break
    if rounds>8: raise SystemExit('RECURSION_DEPTH_GUARD_EXCEEDED')

covered=[f for r in selected for f in r['files']]
missing=sorted(set(all_files)-set(covered)); extra=sorted(set(covered)-set(all_files)); dup=sorted({x for x in covered if covered.count(x)>1})
coverage_ok=not missing and not extra and not dup and len(covered)==len(all_files)
passed_total=sum(r['passed_count'] or 0 for r in selected)
compile_cmd=[sys.executable,'-m','compileall','-q','microseed','tests']
try:
    cr=subprocess.run(compile_cmd,cwd=ROOT,capture_output=True,text=True,timeout=30)
    compile_code=cr.returncode; compile_out=cr.stdout; compile_err=cr.stderr
except subprocess.TimeoutExpired as exc:
    compile_code=None; compile_out=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or ''); compile_err=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
(REPORT/'compileall.stdout.log').write_text(compile_out,encoding='utf-8'); (REPORT/'compileall.stderr.log').write_text(compile_err,encoding='utf-8')
end_source_sha,end_rows=source_snapshot(); source_stable=(start_source_sha==end_source_sha and start_rows==end_rows)
classification='PASS' if coverage_ok and not negatives and not terminal_unknown and compile_code==0 and source_stable else 'REVIEW_REQUIRED'
agg={'schema':'microseed.ms1919.pass08.final-full-suite.v1','purpose':'exact bounded compatibility breadth after durable probe-lifecycle evidence recheck repair; mutation adequacy remains separate','source_snapshot_start_sha256':start_source_sha,'source_snapshot_end_sha256':end_source_sha,'source_stable':source_stable,'initial_shards':INITIAL_SHARDS,'max_parallel':MAX_PARALLEL,'group_timeout_seconds':GROUP_TIMEOUT,'rounds':rounds,'run_count':len(all_runs),'selected_pass_groups':len(selected),'test_file_count':len(all_files),'covered_file_count':len(covered),'coverage_ok':coverage_ok,'aggregate_passed_count':passed_total,'missing_files':missing,'extra_files':extra,'duplicate_files':dup,'negative_groups':[r['group_id'] for r in negatives],'terminal_unknown_groups':[r['group_id'] for r in terminal_unknown],'compileall_exit_code':compile_code,'compileall_pass':compile_code==0,'classification':classification,'completion_marker':'COMPLETE' if classification=='PASS' else 'INCOMPLETE','selected':[{'group_id':r['group_id'],'depth':r['depth'],'file_count':r['file_count'],'passed_count':r['passed_count'],'duration_seconds':r['duration_seconds']} for r in sorted(selected,key=lambda x:x['group_id'])]}
(REPORT/'aggregate_receipt.json').write_text(json.dumps(agg,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str((REPORT/'aggregate_receipt.json').relative_to(ROOT)),'classification':classification,'source_stable':source_stable,'coverage_ok':coverage_ok,'test_files':len(all_files),'passed_total':passed_total,'selected_groups':len(selected),'runs':len(all_runs),'rounds':rounds,'negative':agg['negative_groups'],'terminal_unknown':agg['terminal_unknown_groups'],'compileall_pass':agg['compileall_pass']},indent=2))
raise SystemExit(0 if classification=='PASS' else 1)
