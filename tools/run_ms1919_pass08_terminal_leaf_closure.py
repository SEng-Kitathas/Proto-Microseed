from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import ast, hashlib, json, re, shutil, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports'/'ms1919_pass08_full_suite_final'/'aggregate_receipt.json'
REPORT=ROOT/'reports'/'ms1919_pass08_terminal_leaf_closure'
if REPORT.exists(): shutil.rmtree(REPORT)
REPORT.mkdir(parents=True,exist_ok=True)
MAX_PARALLEL=6
GROUP_TIMEOUT=30
CHUNK_SIZE=4


def source_snapshot():
    rows=[]; h=hashlib.sha256()
    for base in (ROOT/'microseed',ROOT/'tests'):
        for p in sorted(base.rglob('*.py')):
            rel=str(p.relative_to(ROOT)).replace('\\','/')
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            rows.append((rel,digest)); h.update(rel.encode()); h.update(b'\0'); h.update(digest.encode()); h.update(b'\n')
    return h.hexdigest(),rows

start_sha,start_rows=source_snapshot()
base=json.loads(BASE.read_text(encoding='utf-8'))
terminal_groups=tuple(base['terminal_unknown_groups'])
terminal_files=[]
for gid in terminal_groups:
    r=json.loads((ROOT/'reports'/'ms1919_pass08_full_suite_final'/gid/'receipt.json').read_text(encoding='utf-8'))
    terminal_files.extend(r['files'])
if len(terminal_files)!=len(set(terminal_files)):
    raise SystemExit('DUPLICATE_TERMINAL_FILES')


def tests_in_file(rel:str):
    p=ROOT/rel
    tree=ast.parse(p.read_text(encoding='utf-8'))
    return [n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_')]

pending=[]
for rel in terminal_files:
    names=tests_in_file(rel)
    if not names: raise SystemExit(f'NO_TESTS:{rel}')
    for i in range(0,len(names),CHUNK_SIZE):
        chunk=names[i:i+CHUNK_SIZE]
        gid=f"{Path(rel).stem}__{i//CHUNK_SIZE:02d}"
        pending.append((gid,rel,chunk,0))


def run_group(gid,rel,names,depth):
    d=REPORT/gid; d.mkdir(parents=True,exist_ok=True)
    outp=d/'pytest.stdout.log'; errp=d/'pytest.stderr.log'; recp=d/'receipt.json'
    nodes=[f'{rel}::{name}' for name in names]
    cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q','-p','no:cacheprovider',*nodes]
    started=time.time()
    try:
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=GROUP_TIMEOUT)
        code,out,err=r.returncode,r.stdout,r.stderr; marker='COMPLETE'; cls='PASS' if code==0 else 'NEGATIVE_OR_COMPATIBILITY_REVIEW_REQUIRED'
    except subprocess.TimeoutExpired as exc:
        code=None; out=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
        err=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
        marker='INCOMPLETE'; cls='UNKNOWN_INCOMPLETE_TIMEOUT'
    duration=round(time.time()-started,6)
    outp.write_text(out,encoding='utf-8'); errp.write_text(err,encoding='utf-8')
    m=re.search(r'(\d+) passed',out); passed=int(m.group(1)) if m else None
    rec={'schema':'microseed.ms1919.pass08.terminal-leaf-group.v1','group_id':gid,'depth':depth,'file':rel,'tests':names,'command':cmd,'duration_seconds':duration,'exit_code':code,'classification':cls,'completion_marker':marker,'passed_count':passed,'stdout_path':str(outp.relative_to(ROOT)),'stderr_path':str(errp.relative_to(ROOT)),'stdout_sha256':hashlib.sha256(out.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(err.encode()).hexdigest(),'stdout_tail':'\n'.join(out.splitlines()[-8:]),'stderr_tail':'\n'.join(err.splitlines()[-8:])}
    recp.write_text(json.dumps(rec,indent=2),encoding='utf-8')
    return rec

selected=[]; negatives=[]; terminal_unknown=[]; all_runs=[]; rounds=0
while pending:
    rounds+=1; current=pending; pending=[]
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        futures={pool.submit(run_group,gid,rel,names,depth):(gid,rel,names,depth) for gid,rel,names,depth in current}
        for fut in as_completed(futures):
            rec=fut.result(); all_runs.append(rec)
            if rec['classification']=='PASS' and rec['completion_marker']=='COMPLETE' and rec['exit_code']==0:
                selected.append(rec)
            elif rec['classification']=='UNKNOWN_INCOMPLETE_TIMEOUT':
                names=list(rec['tests']); depth=rec['depth']; rel=rec['file']
                if len(names)<=1:
                    terminal_unknown.append(rec)
                else:
                    mid=(len(names)+1)//2
                    pending.append((rec['group_id']+'a',rel,names[:mid],depth+1))
                    pending.append((rec['group_id']+'b',rel,names[mid:],depth+1))
            else:
                negatives.append(rec)
    if negatives or terminal_unknown: break
    if rounds>8: raise SystemExit('LEAF_RECURSION_DEPTH_GUARD')

expected_nodes=[]
for rel in terminal_files:
    expected_nodes.extend(f'{rel}::{n}' for n in tests_in_file(rel))
covered_nodes=[]
for rec in selected:
    covered_nodes.extend(f"{rec['file']}::{n}" for n in rec['tests'])
missing=sorted(set(expected_nodes)-set(covered_nodes)); extra=sorted(set(covered_nodes)-set(expected_nodes)); dup=sorted({x for x in covered_nodes if covered_nodes.count(x)>1})
coverage_ok=not missing and not extra and not dup and len(covered_nodes)==len(expected_nodes)
end_sha,end_rows=source_snapshot(); source_stable=(start_sha==end_sha and start_rows==end_rows and start_sha==base['source_snapshot_end_sha256'])
leaf_passed=sum(r['passed_count'] or 0 for r in selected)
classification='PASS' if coverage_ok and not negatives and not terminal_unknown and source_stable else 'REVIEW_REQUIRED'
agg={'schema':'microseed.ms1919.pass08.compatibility-closure.v1','purpose':'close MS1919 terminal timeout leaves from frozen full-suite run by bounded test-function decomposition','base_aggregate_receipt':str(BASE.relative_to(ROOT)),'frozen_source_sha256':start_sha,'source_stable':source_stable,'base_test_file_count':base['test_file_count'],'base_selected_passed_count':base['aggregate_passed_count'],'base_negative_groups':base['negative_groups'],'base_terminal_unknown_groups':terminal_groups,'terminal_files':terminal_files,'expected_leaf_test_count':len(expected_nodes),'leaf_selected_passed_count':leaf_passed,'aggregate_passed_count':base['aggregate_passed_count']+leaf_passed,'exact_test_file_coverage':base['test_file_count'],'leaf_coverage_ok':coverage_ok,'missing_test_nodes':missing,'extra_test_nodes':extra,'duplicate_test_nodes':dup,'negative_groups':[r['group_id'] for r in negatives],'remaining_unknown_groups':[r['group_id'] for r in terminal_unknown],'rounds':rounds,'run_count':len(all_runs),'classification':classification,'completion_marker':'COMPLETE' if classification=='PASS' else 'INCOMPLETE','claim_boundary':'compatibility breadth only; mutation adequacy remains separately owned by final MS1919 source-mutant receipt'}
(REPORT/'aggregate_receipt.json').write_text(json.dumps(agg,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str((REPORT/'aggregate_receipt.json').relative_to(ROOT)),'classification':classification,'source_stable':source_stable,'leaf_coverage_ok':coverage_ok,'leaf_passed':leaf_passed,'aggregate_passed':agg['aggregate_passed_count'],'test_files':agg['exact_test_file_coverage'],'negative':agg['negative_groups'],'remaining_unknown':agg['remaining_unknown_groups'],'rounds':rounds,'runs':len(all_runs)},indent=2))
raise SystemExit(0 if classification=='PASS' else 1)
