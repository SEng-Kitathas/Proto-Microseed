
from __future__ import annotations
import argparse,json,sys,subprocess,time,re,hashlib
from pathlib import Path
ORCH=Path(__file__).resolve().parents[1]
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ORCH/'tools'))
import run_ms_frontier_helix_wave1_v3 as v3
ARMS=['A_TARGET','B_DRIFT','D_CFE','E_IDENTITY','F_VALUE','G_NAKED','H_LANGUAGE','I_GROWTH','K_RED_TEAM']
CANON='ed2cde491962105b0d853b7fd82d8e8b3d81bd8a'
REQUIRED=['arm','authoritative_question','claim_class','measurement_frame','manipulation','matched_controls','incumbent_hypothesis','rival_hypothesis','incumbent_prediction','rival_prediction','measurement','falsifier','assistance_controls','authority_controls','currentness_restart_controls','minimal_embodiment','expected_files','stop_condition','next_if_incumbent','next_if_rival','next_if_nonidentifiable','pdver']

def validate(o,arm,q):
    e=[f'missing:{k}' for k in REQUIRED if k not in o]
    if o.get('arm')!=arm:e.append('arm_mismatch')
    if o.get('authoritative_question')!=q:e.append('question_mismatch')
    if o.get('pdver')!='PROBE -> DERIVE -> VERIFY -> EMBODY -> RECURSE':e.append('pdver_wrong')
    for k in ['measurement_frame','manipulation','incumbent_hypothesis','rival_hypothesis','incumbent_prediction','rival_prediction','measurement','falsifier','minimal_embodiment','stop_condition']:
        if len(str(o.get(k,'')).strip())<45:e.append('too_weak:'+k)
    if str(o.get('incumbent_prediction','')).strip()==str(o.get('rival_prediction','')).strip():e.append('predictions_identical')
    blob=json.dumps(o,ensure_ascii=False).lower()
    for bad in ['tbd','to be determined','generic planner','semantic truth from token','unknown therefore permitted']:
        if bad in blob:e.append('forbidden_or_tbd:'+bad)
    return e

def audit_spec(spec,arm,raw_dir):
    sysmsg=('You are CSC in audit-only mode with ZERO architecture-selection and ZERO promotion authority. Audit this discriminator specification for: real differential prediction, matched controls, HSP measurement adequacy, OARR rival quality, LOOP+ adjacency, assistance leakage, authority laundering, currentness/restart gaps, and whether the minimal embodiment can falsify at least one rival. Return JSON only: verdict PASS/REVIEW/BLOCK; errors[]; warnings[]; strongest_control; strongest_risk; embodiment_warranted boolean.')
    obj,meta=v3.chat(v3.REVIEWER,sysmsg,json.dumps({'arm':arm,'spec':spec},ensure_ascii=False),max_tokens=650,temp=.08,raw_dir=raw_dir,raw_tag='DISCRIMINATOR_CSC')
    obj['authority']='AUDIT_ONLY_NONE_PROMOTION';obj['model_meta']=meta;return obj

def build_one(arm):
    wt=ROOT/'.pcmmad_sync_runs'/('wt_frontier_'+arm.lower());adir=wt/'campaigns/MS_FRONTIER_HELIX_V1'/arm
    refr=json.loads((ORCH/'campaigns/MS_FRONTIER_HELIX_V1/V3_EXTERNAL_REFRAMES.json').read_text(encoding='utf-8'))['reframes'];q=refr[arm]
    # Existing pass state is context, not authority.
    ps=sorted(adir.glob('P[0-9][0-9].json'));last=json.loads(ps[-1].read_text(encoding='utf-8')) if ps else None
    chunks=v3.build_corpus(wt,arm);ev=v3.retrieve(chunks,q,json.dumps(last or {},ensure_ascii=False),k=10)
    evtxt='\n\n'.join(f'SOURCE {c.source}\n{c.text[:1100]}' for c in ev)
    sysmsg=(
      'You are the discriminator-design stage of an R3.1 Microseed research arm. Do NOT answer with a general discussion. Produce one concrete falsifiable experiment specification. '
      'The experiment must compare an incumbent explanation against one real rival under matched controls. It must identify a measurable differential prediction. '
      'PDVER is exactly PROBE -> DERIVE -> VERIFY -> EMBODY -> RECURSE. OARR must be embodied as a rival/removal/altered mechanism or matched counterexample. LOOP+ must name one adjacent causal explanation but must not widen the embodiment beyond the minimal discriminator. '
      'Research only: production mutation forbidden, promotion authority NONE. UNKNOWN does not become permission. Language tokens do not gain truth/semantic/execution authority. Higher-level prediction does not grant subordinate execution authority. '
      'Return JSON only with exact keys: arm, authoritative_question, claim_class, measurement_frame, manipulation, matched_controls, incumbent_hypothesis, rival_hypothesis, incumbent_prediction, rival_prediction, measurement, falsifier, assistance_controls, authority_controls, currentness_restart_controls, minimal_embodiment, expected_files, stop_condition, next_if_incumbent, next_if_rival, next_if_nonidentifiable, pdver. '
      'matched_controls/assistance_controls/authority_controls/currentness_restart_controls/expected_files may be arrays. Predictions must be observably different and the minimal embodiment must be implementable as research-only tests/fixtures or analysis artifacts without modifying microseed production.' )
    user=f'ARM {arm}\nAUTHORITATIVE QUESTION: {q}\n\nLAST VALID PASS STATE:\n{json.dumps(last,ensure_ascii=False)[:3500]}\n\nRETRIEVED EVIDENCE:\n{evtxt[:10000]}\n\nDesign the cheapest high-information discriminator that could actually change our belief.'
    raw_dir=adir/'DISCRIMINATOR_SPEC_V1_RAW';raw_dir.mkdir(parents=True,exist_ok=True)
    spec=None;errs=[]
    for i in range(1,4):
        cand,meta=v3.chat(v3.PRIMARY,sysmsg,user,max_tokens=1450,temp=.18 if i==1 else .08,raw_dir=raw_dir,raw_tag=f'SPEC_ATTEMPT{i}')
        cand['arm']=arm;cand['authoritative_question']=q;cand['pdver']='PROBE -> DERIVE -> VERIFY -> EMBODY -> RECURSE'
        errs=validate(cand,arm,q)
        if not errs: spec=cand;spec['model_meta']=meta;break
        (raw_dir/f'SPEC_ATTEMPT{i}_METHOD_REJECTED.json').write_text(json.dumps({'errors':errs,'candidate':cand},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        user += '\n\nRETRY: prior candidate failed these method gates: '+json.dumps(errs)+'. Produce a concrete differential experiment, not prose.'
    if spec is None:
        state={'arm':arm,'status':'DISCRIMINATOR_SPEC_METHOD_REJECTED','errors':errs,'promotion_authority':'NONE','production_mutation_allowed':False}
        (adir/'DISCRIMINATOR_SPEC_V1_STATE.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8');return state
    csc=audit_spec(spec,arm,raw_dir)
    wrapper={'arm':arm,'status':'DISCRIMINATOR_SPEC_READY' if csc.get('verdict')!='BLOCK' else 'DISCRIMINATOR_SPEC_BLOCKED','spec':spec,'csc':csc,'evidence_refs':[c.source for c in ev],'control_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ORCH,text=True).strip(),'arm_parent_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=wt,text=True).strip(),'promotion_authority':'NONE','production_mutation_allowed':False}
    b=json.dumps(wrapper,indent=2,ensure_ascii=False)+'\n';(adir/'DISCRIMINATOR_SPEC_V1.json').write_text(b,encoding='utf-8',newline='\n')
    wrapper['spec_sha256']=hashlib.sha256(b.encode('utf-8')).hexdigest();(adir/'DISCRIMINATOR_SPEC_V1_STATE.json').write_text(json.dumps({k:wrapper[k] for k in ['arm','status','spec_sha256','control_head','arm_parent_head','promotion_authority','production_mutation_allowed']},indent=2)+'\n',encoding='utf-8',newline='\n')
    return wrapper

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=ARMS);ap.add_argument('--all',action='store_true');ap.add_argument('--commit-push',action='store_true');args=ap.parse_args();arms=ARMS if args.all else [args.arm]
    results={}
    for arm in arms:
        r=build_one(arm);results[arm]=r
        if args.commit_push:
            wt=ROOT/'.pcmmad_sync_runs'/('wt_frontier_'+arm.lower());adir=Path('campaigns/MS_FRONTIER_HELIX_V1')/arm
            subprocess.run(['git','add',str(adir)],cwd=wt,check=True)
            chk=subprocess.run(['git','diff','--cached','--check'],cwd=wt,text=True,capture_output=True)
            if chk.returncode: raise RuntimeError(chk.stdout+chk.stderr)
            prod=subprocess.run(['git','diff','--cached','--name-only','--','microseed'],cwd=wt,text=True,capture_output=True).stdout.splitlines()
            if prod: raise RuntimeError('organism delta staged '+repr(prod))
            c=subprocess.run(['git','commit','-m',f'MS Frontier Helix v1: {arm} differential discriminator spec'],cwd=wt,text=True,capture_output=True)
            if c.returncode not in (0,1): raise RuntimeError(c.stdout+c.stderr)
            branch=subprocess.check_output(['git','branch','--show-current'],cwd=wt,text=True).strip();push=subprocess.run(['git','push','origin','HEAD:'+branch],cwd=wt,text=True,capture_output=True,timeout=300)
            results[arm]['git']={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=wt,text=True).strip(),'branch':branch,'push_rc':push.returncode,'push_stderr':push.stderr}
    print(json.dumps({a:{'status':r.get('status'),'csc':r.get('csc',{}).get('verdict') if isinstance(r,dict) else None,'git':r.get('git')} for a,r in results.items()},indent=2))
if __name__=='__main__':main()
