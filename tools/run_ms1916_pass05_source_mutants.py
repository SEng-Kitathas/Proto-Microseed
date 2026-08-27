from __future__ import annotations

from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile, time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'reports'/'ms1916_pass05_source_mutants'
REPORT.mkdir(parents=True,exist_ok=True)
TEST='tests/embodiment/test_ms1916_pass05_direct_probe_authorization_ancestry.py'

MUTANTS={
 'DROP_DIRECT_PROBE_LOCUS_GATE':(
  'microseed/runtime/entity.py',
  '        if current.state_id!=conflict_slot[0]:\n',
  '        if False and current.state_id!=conflict_slot[0]:\n'),
 'ALLOW_REVISIT_AS_DECISION_PRESSURE':(
  'microseed/development/epistemic_priority.py',
  '    if deficit is None or deficit.state not in {EpistemicDeficitState.ACTION_LIMITED, EpistemicDeficitState.PROBE_AVAILABLE}:\n',
  '    if deficit is None or deficit.state not in {EpistemicDeficitState.ACTION_LIMITED, EpistemicDeficitState.PROBE_AVAILABLE, EpistemicDeficitState.REVISIT_REQUIRED}:\n'),
 'DROP_BOUND_PROBE_EPOCH_CURRENTNESS':(
  'microseed/development/epistemic_priority.py',
  '        if current_capability_epochs.get(probe_id) != probe_epoch:\n',
  '        if False and current_capability_epochs.get(probe_id) != probe_epoch:\n'),
 'DROP_BOUND_PROBE_RELATION_REQUIREMENT':(
  'microseed/development/epistemic_priority.py',
  '''            if rel is None or int(rel.capability_epoch) != int(probe_epoch):\n                return RelationalCommitment(\n                    _sha({"target": target, "probe_slot": probe_slot, "bound_epoch": probe_epoch}),\n                    target, TernaryCommitment.UNKNOWN, reason="BOUND_PROBE_RELATION_REQUIRED_AT_CURRENT_STATE",\n                    qualifiers=qnone, premise_ids=(deficit.deficit_id, probe_id),\n                )\n            probe_edges.append(rel.digest())\n''',
  '''            if rel is not None:\n                probe_edges.append(rel.digest())\n'''),
 'DROP_BACKGROUND_AMBIGUITY_ABSTENTION':(
  'microseed/runtime/entity.py',
  '        if ambiguous:\n',
  '        if False and ambiguous:\n'),
 'DROP_BOUND_PROBE_PREMISE_WITNESS':(
  'microseed/development/epistemic_priority.py',
  '        bound_probe_premises = (str(probe_id),)\n',
  '        bound_probe_premises = ()\n'),
}

def ignore(_path,names):
    return {'.git','reports','.pytest_cache','__pycache__'}

def apply(root:Path,name:str,target:str,old:str,new:str):
    p=root/target; raw=p.read_text(encoding='utf-8')
    if old not in raw: raise RuntimeError(f'MUTATION_PATTERN_NOT_FOUND:{name}')
    mutated=raw.replace(old,new,1); p.write_text(mutated,encoding='utf-8')
    return hashlib.sha256(raw.encode()).hexdigest(),hashlib.sha256(mutated.encode()).hexdigest()

def run(name,spec):
    target,old,new=spec; started=time.time()
    with tempfile.TemporaryDirectory(prefix=f'ms1916_{name}_') as td:
        dst=Path(td)/'repo'; shutil.copytree(ROOT,dst,ignore=ignore)
        clean_sha,mut_sha=apply(dst,name,target,old,new)
        cmd=[sys.executable,'tools/run_pytest_cleanup_neutral.py','-q',TEST]
        try:
            r=subprocess.run(cmd,cwd=dst,capture_output=True,text=True,timeout=22)
            code,out,err=r.returncode,r.stdout,r.stderr; marker='COMPLETE'; status='SURVIVED' if code==0 else 'REJECTED'
        except subprocess.TimeoutExpired as exc:
            code=None; out=(exc.stdout or b'').decode('utf-8',errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
            err=(exc.stderr or b'').decode('utf-8',errors='replace') if isinstance(exc.stderr,bytes) else (exc.stderr or '')
            marker='INCOMPLETE'; status='UNKNOWN_INCOMPLETE_TIMEOUT'
        op=REPORT/f'{name}.stdout.log'; ep=REPORT/f'{name}.stderr.log'; op.write_text(out,encoding='utf-8'); ep.write_text(err,encoding='utf-8')
        return {'mutant':name,'target':target,'status':status,'exit_code':code,'completion_marker':marker,'duration_seconds':round(time.time()-started,6),'clean_source_sha256':clean_sha,'mutant_source_sha256':mut_sha,'stdout_path':str(op.relative_to(ROOT)),'stderr_path':str(ep.relative_to(ROOT)),'stdout_tail':'\n'.join(out.splitlines()[-16:]),'stderr_tail':'\n'.join(err.splitlines()[-8:])}

started=time.time(); results=[run(name,spec) for name,spec in MUTANTS.items()]
receipt={'schema':'microseed.ms1916.pass05.source-mutants.v1','discriminator':'CURRENT_DIRECT_PROBE_RELEVANCE != LAWFUL_DECISION_BEARING_UNLESS_LOCUS_STATE_AND_BOUND_PROBE_ANCESTRY_ARE_CURRENT','started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)),'finished_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'results':results,'survivors':[r['mutant'] for r in results if r['status']=='SURVIVED'],'rejected':[r['mutant'] for r in results if r['status']=='REJECTED'],'unknown':[r['mutant'] for r in results if r['status'].startswith('UNKNOWN')],'completion_marker':'COMPLETE' if all(r['completion_marker']=='COMPLETE' for r in results) else 'INCOMPLETE'}
(REPORT/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'receipt':str((REPORT/'receipt.json').relative_to(ROOT)),'survivors':receipt['survivors'],'rejected':receipt['rejected'],'unknown':receipt['unknown'],'completion_marker':receipt['completion_marker']},indent=2))
raise SystemExit(0 if receipt['completion_marker']=='COMPLETE' and not receipt['survivors'] else 2)
