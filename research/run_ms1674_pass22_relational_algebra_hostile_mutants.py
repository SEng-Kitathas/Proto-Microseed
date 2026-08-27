from __future__ import annotations
import json,os,shutil,subprocess,tempfile
from pathlib import Path
OUT=Path(__file__).with_name('MS1674_PASS22_RELATIONAL_ALGEBRA_HOSTILE_MUTANTS.json')
ROOT=Path(__file__).parents[1]
MOD=ROOT/'microseed/development/relational_algebra.py'
TEST=ROOT/'tests/embodiment/test_ms1673_relational_algebra_research.py'
mutants={
 'IGNORE_OBSERVED_COUNTEREXAMPLES':("if positive < int(min_positive_support) or negative:\n            continue","if positive < int(min_positive_support):\n            continue"),
 'EVENT_ID_AS_ORIGIN':("return sha256_bytes(canonical_json(sorted({row.origin_id for row in rows})))","return sha256_bytes(canonical_json(sorted({row.sample_id for row in rows})))"),
 'LAST_WRITE_WINS_CONFLICT':("if len({row.end_token for row in rows}) == 1:\n            out[key] = rows[0]","out[key] = rows[-1]"),
 'FORCE_FIRST_RELATIONAL_DISAGREEMENT':("if len(values) == 1:\n        return {","if len(values) >= 1:\n        return {"),
 'ALLOW_MIXED_FRAME_EPOCHS':("if len(frame_epochs) != 1:\n        return ()","if False and len(frame_epochs) != 1:\n        return ()"),
 'PREDICTION_EXECUTION_AUTHORITY_LEAK':('"authority": "MODEL_OUTPUT_ONLY",\n            "truth_authority": "NONE",\n            "execution_authority": "NONE",','"authority": "MODEL_OUTPUT_ONLY",\n            "truth_authority": "NONE",\n            "execution_authority": "EFFECT",'),
}
def main():
 base=MOD.read_text(); results={}
 for name,(old,new) in mutants.items():
  if old not in base:
   results[name]={'rejected':False,'reason':'PATCH_TARGET_NOT_FOUND'};continue
  with tempfile.TemporaryDirectory(prefix='ms1674-mut-') as td:
   td=Path(td);shutil.copytree(ROOT/'microseed',td/'microseed');(td/'tests').mkdir();shutil.copy2(TEST,td/'tests/test_rel.py')
   mp=td/'microseed/development/relational_algebra.py';mp.write_text(mp.read_text().replace(old,new,1))
   env=dict(os.environ);env['PYTHONPATH']=str(td)
   p=subprocess.run(['python','-m','pytest','-q',str(td/'tests/test_rel.py')],cwd=td,env=env,capture_output=True,text=True,timeout=20)
   results[name]={'rejected':p.returncode!=0,'returncode':p.returncode,'tail':(p.stdout+p.stderr)[-1500:]}
 out={'milestone':'MS1674','pass':22,'mutants':results,'rejected':sum(v['rejected'] for v in results.values()),'total':len(results),'pass_all':all(v['rejected'] for v in results.values())}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps({'rejected':out['rejected'],'total':out['total'],'pass_all':out['pass_all'],'status':{k:v['rejected'] for k,v in results.items()}},indent=2))
if __name__=='__main__':main()
