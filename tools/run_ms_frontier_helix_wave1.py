
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, time, urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT=Path(__file__).resolve().parents[1]
CAMPAIGN_REL=Path('campaigns/MS_FRONTIER_HELIX_V1')
PRIMARY='http://127.0.0.1:8091/v1/chat/completions'
REVIEWER='http://127.0.0.1:8092/v1/chat/completions'
CANON='ed2cde491962105b0d853b7fd82d8e8b3d81bd8a'
TERMINAL={'RESOLVED_EXISTING_OWNERS','RESOLVED_NEGATIVE','UNKNOWN_INCOMPLETE','MISSING_EVIDENCE','NON_IDENTIFIABLE','MINIMAL_GAP_LOCALIZED','PRODUCTION_CANDIDATE','QUESTION_MALFORMED'}
TEXT={'.md','.txt','.json','.py','.csv','.yaml','.yml','.toml','.ini','.cfg','.rst'}
STOP=set('the a an and or of to in for on with is are be as by at from this that it its we our you your do does did not no if then than what which how why when where can could should would will must may into under current'.split())

@dataclass
class Chunk:
    source:str; text:str; terms:set[str]

def toks(s:str)->set[str]:
    return {x for x in re.findall(r'[A-Za-z0-9_+.-]{3,}',s.lower()) if x not in STOP}

def read_text(p:Path,max_bytes:int=400_000)->str:
    try:b=p.read_bytes()[:max_bytes]
    except:return ''
    if b'\x00' in b[:2048]: return ''
    for enc in ('utf-8','utf-8-sig','cp1252'):
        try:return b.decode(enc)
        except:pass
    return ''

def add_file(chunks:list[Chunk],p:Path,label:str|None=None):
    txt=read_text(p)
    if not txt.strip():return
    for i,para in enumerate(re.split(r'\n\s*\n',txt)):
        para=para.strip()
        if len(para)<40:continue
        for j in range(0,len(para),1400):
            sub=para[j:j+1600]
            chunks.append(Chunk(f'{label or p}#p{i}.{j//1400}',sub,toks(sub)))

def build_corpus(worktree:Path,arm:str)->list[Chunk]:
    chunks=[]
    # Current organism/source/evidence surface.
    for roots in ['microseed','tests/embodiment','methodology','evidence','campaigns/MS_FRONTIER_HELIX_V1']:
        base=worktree/roots
        if not base.exists():continue
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in TEXT and p.stat().st_size<500_000:
                add_file(chunks,p,str(p.relative_to(worktree)))
    # Current dedicated continuity state.
    cont=worktree.parent.parent/'rd_continuity_repo'
    for rel in ['state/current/CURRENT_STATE.md','state/next_steps/NEXT_STEPS.md','CURRENT_FRONTIER.md','state/trace_matrix/TRACE_MATRIX.md','state/revisit_ledger/REVISIT_LEDGER.md','SCARS_AND_DO_NOT_REINTRODUCE.md']:
        p=cont/rel
        if p.exists():add_file(chunks,p,'continuity/'+rel)
    # CFE donor/evidence quarry only where relevant, still non-authoritative.
    if arm=='D_CFE' or arm in {'I_GROWTH','H_LANGUAGE'}:
        cfe=worktree.parent/'cfe_readonly_audit'
        for rel in ['research/STARMAP_TO_CFE_SALVAGE_LEDGER_2026-08-31.md','research/STARMAP_ARCHAEOLOGY_CFE_EVIDENCE_DELTA_2026-08-31.md','docs/SCIENTIFIC_CLAIM_LEDGER.md','continuity/live_shadow.md','continuity/next_steps.md']:
            p=cfe/rel
            if p.exists():add_file(chunks,p,'cfe/'+rel)
    # Historical grounded-language branch: questions/evidence only, not current truth.
    if arm=='H_LANGUAGE':
        try:
            names=subprocess.check_output(['git','ls-tree','-r','--name-only','research/grounded-language-reference-v1'],cwd=worktree,text=True,timeout=30).splitlines()
            keep=[n for n in names if any(k in n.lower() for k in ['language','ground','reference','lang_']) and Path(n).suffix.lower() in TEXT][:80]
            for n in keep:
                try:
                    txt=subprocess.check_output(['git','show','research/grounded-language-reference-v1:'+n],cwd=worktree,timeout=10).decode('utf-8','replace')[:250_000]
                except:continue
                for i,para in enumerate(re.split(r'\n\s*\n',txt)):
                    para=para.strip()
                    if len(para)>=40: chunks.append(Chunk('old-language-branch/'+n+f'#p{i}',para[:1600],toks(para[:1600])))
        except:pass
    return chunks

def retrieve(chunks:list[Chunk],question:str,helix:str,k:int=8)->list[Chunk]:
    q=toks(question+' '+helix); scored=[]
    for c in chunks:
        ov=len(q & c.terms)
        if not ov:continue
        score=ov/(1+0.025*max(0,len(c.terms)-35))
        if c.source.startswith('continuity/'):score+=0.8
        if 'CURRENT_STATE' in c.source:score+=0.8
        scored.append((score,c))
    scored.sort(key=lambda x:(-x[0],x[1].source))
    return [c for _,c in scored[:k]]

def chat(url:str,system:str,user:str,max_tokens:int=900,temp:float=.22,retries:int=3)->tuple[dict[str,Any],dict[str,Any]]:
    last=None
    for attempt in range(1,retries+1):
        payload={'model':'local','messages':[{'role':'system','content':system},{'role':'user','content':user}], 'temperature':temp if attempt==1 else .08,'max_tokens':max_tokens+(200 if attempt>1 else 0),'stream':False,'response_format':{'type':'json_object'}}
        req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=240) as r: raw=json.loads(r.read().decode())
            content=raw['choices'][0]['message']['content'].strip(); content=re.sub(r'^```(?:json)?\s*|\s*```$','',content,flags=re.I|re.S).strip()
            return json.loads(content),{'attempt':attempt,'usage':raw.get('usage'),'timings':raw.get('timings'),'model':raw.get('model'),'fingerprint':raw.get('system_fingerprint')}
        except Exception as e:
            last=repr(e); system+='\nSTRICT RETRY: valid JSON object only; preserve required keys.'
    raise RuntimeError('model JSON failure: '+str(last))

def compact_helix(o:dict[str,Any]|None)->str:
    if not o:return '{}'
    return json.dumps({k:o.get(k) for k in ['survivors','scars','demotions','unresolved','next']},ensure_ascii=False)[:1800]

def validate(o:dict[str,Any],question:str)->list[str]:
    req=['question','evidence_contacted','measurement_frame','probe','derive','verify','oarr','loop_plus','embody','observed_consequence','survivors','scars','demotions','unresolved','attention_reservoir','disposition','next','terminal']
    errors=[f'missing:{k}' for k in req if k not in o]
    if o.get('question')!=question:errors.append('question_not_exact')
    if str(o.get('disposition')) not in TERMINAL|{'RESEARCH_CONTINUE'}:errors.append('bad_disposition')
    nq=str(o.get('next','')).strip()
    if not bool(o.get('terminal')) and not nq.endswith('?'):errors.append('next_not_question')
    return errors

def csc(records:list[dict[str,Any]],arm:str,stage:str)->dict[str,Any]:
    compact=[{k:r.get(k) for k in ['pass','question','disposition','terminal','next','survivors','scars','demotions','oarr','loop_plus']} for r in records[-5:]]
    sysmsg='You are CSC in audit-only shadow mode. ZERO promotion authority and ZERO architecture-selection authority. Audit methodological validity: exact question chain, evidence/inference separation, PDVER order PROBE->DERIVE->VERIFY->EMBODY->RECURSE, meaningful OARR, meaningful LOOP+, HSP measurement discipline, Helix continuity, UNKNOWN discipline, assistance/authority leakage, and no automatic organism claim. Return JSON: verdict (PASS/REVIEW/BLOCK), errors[], warnings[], strongest_survivor, strongest_scar, terminal_supported (bool).'
    obj,meta=chat(REVIEWER,sysmsg,json.dumps({'arm':arm,'stage':stage,'records':compact},ensure_ascii=False),max_tokens=550,temp=.08)
    obj['authority']='AUDIT_ONLY_NONE_PROMOTION'; obj['model_meta']=meta; return obj

def writej(p:Path,o:Any):p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

def run_arm(worktree:Path,arm:str,max_passes:int)->dict[str,Any]:
    croot=worktree/CAMPAIGN_REL; adir=croot/arm
    manifest=json.loads((adir/'ARM_MANIFEST.json').read_text(encoding='utf-8'))
    process=(croot/'R3_1_PROCESS_CONTRACT.md').read_text(encoding='utf-8')
    question=manifest['seed_question']; chunks=build_corpus(worktree,arm)
    records=[]; prev=None; ledger=['# '+arm+' — Pass Ledger','',f'Seed question: {question}','']
    for pnum in range(1,max_passes+1):
        ev=retrieve(chunks,question,compact_helix(prev),k=8)
        evtxt='\n\n'.join(f'SOURCE {c.source}\n{c.text[:900]}' for c in ev)
        system=(
          'You are one research pass in canonical Microseed MS_FRONTIER_HELIX_V1. Research only; promotion authority NONE; production mutation is forbidden in Wave 1. '
          'PDVER means exactly PROBE -> DERIVE -> VERIFY -> EMBODY -> RECURSE. VERIFY is before EMBODY. '
          'Pass N earns Pass N+1: do not prewrite later questions. HSP qualifies measurement. OARR must attack with a real rival/removal/altered/counterexample/assistance/old-owner/currentness/authority explanation where meaningful. LOOP+ widens an adjacent plausible causal branch before convergence. '
          'Semantic HELIX explicitly carries survivors, scars, demotions, unresolved. Attention Reservoir names neglected evidence or bounded-complete. '
          'Before claiming new mechanism classify failures among observation/channel/measurement-frame/identifiability/access/basis-representation/scope-context/currentness/search/authority/true-capability. '
          'EMBODY in Wave 1 may only be NO_MUTATION_WARRANTED or a bounded research artifact/experiment specification; it may NOT modify microseed production. '
          'Return JSON only with exact required keys: question, evidence_contacted, measurement_frame, probe, derive, verify, oarr, loop_plus, embody, observed_consequence, survivors, scars, demotions, unresolved, attention_reservoir, disposition, next, terminal. '
          'disposition must be one of RESEARCH_CONTINUE, RESOLVED_EXISTING_OWNERS, RESOLVED_NEGATIVE, UNKNOWN_INCOMPLETE, MISSING_EVIDENCE, NON_IDENTIFIABLE, MINIMAL_GAP_LOCALIZED, PRODUCTION_CANDIDATE, QUESTION_MALFORMED. terminal is boolean.' )
        predecessor='NONE' if prev is None else json.dumps({k:prev.get(k) for k in ['question','disposition','survivors','scars','demotions','unresolved','next']},ensure_ascii=False)[:1800]
        user=f'ARM {arm}; PASS {pnum}/{max_passes}\nAUTHORITATIVE QUESTION: {question}\n\nPREDECESSOR:\n{predecessor}\n\nRETRIEVED EVIDENCE:\n{evtxt[:7000]}\n\nPROCESS CONTRACT EXCERPT:\n{process[:2500]}\n\nAnswer only what admitted evidence supports. If embodiment is required, specify the smallest discriminating artifact/fixture/test and stop short of production mutation.'
        obj,meta=chat(PRIMARY,system,user,max_tokens=1050,temp=.22)
        obj['pass']=pnum; obj['model_meta']=meta; obj['source_refs']=[c.source for c in ev]; obj['promotion_authority']='NONE'; obj['production_mutation_allowed']=False
        errors=validate(obj,question)
        if errors:
            obj['method_errors']=errors; obj['disposition']='UNKNOWN_INCOMPLETE'; obj['terminal']=False; obj['next']=question
        writej(adir/f'P{pnum:02d}.json',obj)
        ledger += [f'## P{pnum:02d}',f'Question: {question}',f'Disposition: {obj.get("disposition")}',f'OARR: {obj.get("oarr")}',f'LOOP+: {obj.get("loop_plus")}',f'Survivors: {obj.get("survivors")}',f'Scars: {obj.get("scars")}',f'Demotions: {obj.get("demotions")}',f'Next: {obj.get("next")}','']
        records.append(obj); prev=obj
        if pnum%5==0:
            audit=csc(records,arm,f'P{pnum:02d}') ; writej(adir/f'CSC_P{pnum:02d}.json',audit)
        if bool(obj.get('terminal')) and str(obj.get('disposition')) in TERMINAL:
            audit=csc(records,arm,f'TERMINAL_P{pnum:02d}'); writej(adir/f'CSC_TERMINAL_P{pnum:02d}.json',audit)
            if str(audit.get('verdict','')).upper()=='PASS' and bool(audit.get('terminal_supported')): break
        nq=str(obj.get('next','')).strip()
        if not nq.endswith('?'): nq=question
        question=nq
    final_audit=csc(records,arm,'ARM_CLOSEOUT'); writej(adir/'CSC_ARM_CLOSEOUT.json',final_audit)
    last=records[-1]
    writej(adir/'HELIX.json',{'survivors':last.get('survivors',[]),'scars':last.get('scars',[]),'demotions':last.get('demotions',[]),'unresolved':last.get('unresolved',[]),'next':last.get('next'),'passes_completed':len(records)})
    writej(adir/'RESERVOIR.json',{'items':last.get('attention_reservoir',[]),'passes_completed':len(records)})
    (adir/'PASS_LEDGER.md').write_text('\n'.join(ledger).rstrip()+'\n',encoding='utf-8',newline='\n')
    close={'arm':arm,'passes_completed':len(records),'final_disposition':last.get('disposition'),'terminal':last.get('terminal'),'next':last.get('next'),'csc':final_audit,'promotion_authority':'NONE','production_delta':subprocess.check_output(['git','diff','--name-only',CANON+'..HEAD','--','microseed'],cwd=worktree,text=True).splitlines()}
    writej(adir/'ARM_CLOSEOUT.json',close); return close

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--worktree',required=True); ap.add_argument('--arm',required=True); ap.add_argument('--max-passes',type=int,default=20); ap.add_argument('--commit-push',action='store_true'); args=ap.parse_args()
    wt=Path(args.worktree).resolve(); arm=args.arm
    close=run_arm(wt,arm,args.max_passes)
    if args.commit_push:
        subprocess.run(['git','add',str(CAMPAIGN_REL/arm)],cwd=wt,check=True)
        chk=subprocess.run(['git','diff','--cached','--check'],cwd=wt,text=True,capture_output=True)
        if chk.returncode: raise RuntimeError(chk.stdout+chk.stderr)
        prod=subprocess.check_output(['git','diff','--name-only',CANON+'..HEAD','--','microseed'],cwd=wt,text=True).splitlines()
        if prod: raise RuntimeError('organism delta before research commit: '+repr(prod))
        c=subprocess.run(['git','commit','-m',f'MS Frontier Helix v1: {arm} Wave 1 research closeout'],cwd=wt,text=True,capture_output=True)
        if c.returncode not in (0,1): raise RuntimeError(c.stdout+c.stderr)
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=wt,text=True).strip()
        push=subprocess.run(['git','push','-u','origin','HEAD:'+branch],cwd=wt,text=True,capture_output=True,timeout=300)
        close['git']={'branch':branch,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=wt,text=True).strip(),'push_rc':push.returncode,'push_stdout':push.stdout,'push_stderr':push.stderr}
    print(json.dumps(close,indent=2,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
