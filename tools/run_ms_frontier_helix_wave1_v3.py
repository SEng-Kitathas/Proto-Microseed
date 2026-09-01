
from __future__ import annotations
# Wave-1 recovery runner v2: preserves raw model failures, treats authoritative question as control-plane input, and turns successor saturation into an explicit research stop.
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
    for roots in ['microseed','tests/embodiment','methodology','evidence']:
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

def _escape_invalid_json_backslashes(text:str)->str:
    # Syntax-only repair: preserve valid JSON escapes; double only a backslash that cannot begin one.
    return re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)

def chat(url:str,system:str,user:str,max_tokens:int=900,temp:float=.22,retries:int=3,raw_dir:Path|None=None,raw_tag:str='model')->tuple[dict[str,Any],dict[str,Any]]:
    last=None
    raw_dir.mkdir(parents=True,exist_ok=True) if raw_dir else None
    for attempt in range(1,retries+1):
        payload={'model':'local','messages':[{'role':'system','content':system},{'role':'user','content':user}], 'temperature':temp if attempt==1 else .08,'max_tokens':max_tokens+(200 if attempt>1 else 0),'stream':False,'response_format':{'type':'json_object'}}
        req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        content=''
        try:
            with urllib.request.urlopen(req,timeout=240) as r: raw=json.loads(r.read().decode())
            content=raw['choices'][0]['message']['content'].strip(); content=re.sub(r'^```(?:json)?\s*|\s*```$','',content,flags=re.I|re.S).strip()
            if raw_dir:
                (raw_dir/f'{raw_tag}_ATTEMPT{attempt}_RAW.txt').write_text(content+'\n',encoding='utf-8',newline='\n')
            try:
                obj=json.loads(content); repaired=False
            except json.JSONDecodeError:
                repaired_text=_escape_invalid_json_backslashes(content)
                if repaired_text==content: raise
                obj=json.loads(repaired_text); repaired=True
                if raw_dir:
                    (raw_dir/f'{raw_tag}_ATTEMPT{attempt}_SYNTAX_REPAIR.txt').write_text(repaired_text+'\n',encoding='utf-8',newline='\n')
            return obj,{'attempt':attempt,'usage':raw.get('usage'),'timings':raw.get('timings'),'model':raw.get('model'),'fingerprint':raw.get('system_fingerprint'),'json_syntax_repaired':repaired}
        except Exception as e:
            last=repr(e)
            if raw_dir:
                writej(raw_dir/f'{raw_tag}_ATTEMPT{attempt}_FAILURE.json',{'status':'MODEL_FORMAT_OR_TRANSPORT_REJECTED__NOT_SCIENTIFIC_EVIDENCE','attempt':attempt,'error':last,'raw_content_file':f'{raw_tag}_ATTEMPT{attempt}_RAW.txt' if content else None})
            system+='\nSTRICT RETRY: valid JSON object only; preserve required keys. Do not use unescaped backslashes.'
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
    if not bool(o.get('terminal')):
        if not nq.endswith('?'):errors.append('next_not_question')
        if nq==question:errors.append('next_self_loop')
    for k in ['measurement_frame','probe','derive','verify','oarr','loop_plus']:
        if len(str(o.get(k,'')).strip())<35: errors.append('too_weak:'+k)
    return errors

def csc(records:list[dict[str,Any]],arm:str,stage:str)->dict[str,Any]:
    compact=[{k:r.get(k) for k in ['pass','question','disposition','terminal','next','survivors','scars','demotions','oarr','loop_plus']} for r in records[-5:]]
    sysmsg='You are CSC in audit-only shadow mode. ZERO promotion authority and ZERO architecture-selection authority. Audit methodological validity: exact question chain, evidence/inference separation, PDVER order PROBE->DERIVE->VERIFY->EMBODY->RECURSE, meaningful OARR, meaningful LOOP+, HSP measurement discipline, Helix continuity, UNKNOWN discipline, assistance/authority leakage, and no automatic organism claim. Return JSON: verdict (PASS/REVIEW/BLOCK), errors[], warnings[], strongest_survivor, strongest_scar, terminal_supported (bool).'
    obj,meta=chat(REVIEWER,sysmsg,json.dumps({'arm':arm,'stage':stage,'records':compact},ensure_ascii=False),max_tokens=550,temp=.08)
    obj['authority']='AUDIT_ONLY_NONE_PROMOTION'; obj['model_meta']=meta; return obj

def writej(p:Path,o:Any):p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

def load_existing_chain(adir:Path)->list[dict[str,Any]]:
    files=sorted(adir.glob('P[0-9][0-9].json'))
    records=[]
    expected_pass=1
    prev=None
    for f in files:
        if f.name != f'P{expected_pass:02d}.json':
            raise RuntimeError(f'NONCONTIGUOUS_EXISTING_CHAIN expected P{expected_pass:02d} got {f.name}')
        o=json.loads(f.read_text(encoding='utf-8'))
        if o.get('pass')!=expected_pass: raise RuntimeError(f'PASS_NUMBER_MISMATCH {f.name}')
        if o.get('method_errors'): raise RuntimeError(f'EXISTING_METHOD_ERRORS {f.name}: {o.get("method_errors")}')
        errs=validate(o,str(o.get('question','')))
        if errs: raise RuntimeError(f'INVALID_EXISTING_PASS {f.name}: {errs}')
        if prev is not None and prev.get('next')!=o.get('question'):
            raise RuntimeError(f'EXISTING_CHAIN_BREAK P{expected_pass-1:02d}->P{expected_pass:02d}')
        records.append(o); prev=o; expected_pass+=1
    return records

def terminal_has_csc_pass(adir:Path,pass_num:int)->bool:
    p=adir/f'CSC_TERMINAL_P{pass_num:02d}.json'
    if not p.exists(): return False
    try:o=json.loads(p.read_text(encoding='utf-8'))
    except:return False
    return str(o.get('verdict','')).upper()=='PASS' and bool(o.get('terminal_supported'))

def generate_reframe(worktree:Path,adir:Path,arm:str,records:list[dict[str,Any]],fallback_question:str)->str|None:
    prev=records[-1] if records else None
    sysmsg=('You are the R3.1 successor-question reframer. You do NOT answer the science question and have ZERO promotion/architecture authority. '
            'Given the last valid HELIX state, produce exactly one different, narrower or higher-information next scientific question that discriminates the strongest unresolved rival. '
            'Do not paraphrase the prior question. If no responsible successor can be earned from admitted evidence, return {"next": null, "reason": "QUESTION_SATURATED__REQUIRES_EXTERNAL_REFRAME"}. JSON only.')
    payload={'arm':arm,'prior_question':fallback_question,'last_pass':({k:prev.get(k) for k in ['question','disposition','survivors','scars','demotions','unresolved','attention_reservoir','next']} if prev else None)}
    try:
        obj,meta=chat(PRIMARY,sysmsg,json.dumps(payload,ensure_ascii=False),max_tokens=350,temp=.08,raw_dir=adir,raw_tag=f'REFRAME_AFTER_P{len(records):02d}')
    except Exception as e:
        writej(adir/f'REFRAME_FAILURE_AFTER_P{len(records):02d}.json',{'status':'QUESTION_SATURATED__REQUIRES_EXTERNAL_REFRAME','error':repr(e),'promotion_authority':'NONE'})
        return None
    nq=obj.get('next')
    if nq is None:return None
    nq=str(nq).strip()
    if nq and not nq.endswith('?'):nq=nq.rstrip('. !')+'?'
    prior={str(r.get('question','')).strip() for r in records}
    if not nq or nq in prior or nq==fallback_question:
        writej(adir/f'REFRAME_SATURATION_AFTER_P{len(records):02d}.json',{'status':'QUESTION_SATURATED__REQUIRES_EXTERNAL_REFRAME','candidate_next':nq,'prior_questions':sorted(prior),'promotion_authority':'NONE','model_meta':meta})
        return None
    writej(adir/f'REFRAME_ACCEPTED_AFTER_P{len(records):02d}.json',{'status':'REFRAME_ACCEPTED__NOT_SCIENTIFIC_PASS','next':nq,'model_meta':meta,'promotion_authority':'NONE'})
    return nq

def pass_bundle_sha(adir:Path)->str:
    h=hashlib.sha256()
    for p in sorted(adir.glob('P[0-9][0-9].json')):
        h.update(p.name.encode()); h.update(b'\0'); h.update(p.read_bytes()); h.update(b'\0')
    return h.hexdigest()

def write_v3_state(adir:Path,arm:str,records:list[dict[str,Any]],status:str,next_question:str|None,audit:dict[str,Any],session_start_count:int)->dict[str,Any]:
    last=records[-1] if records else None
    state={'arm':arm,'runtime':'V3','status':status,'scientific_closure':False,'total_admitted_passes':len(records),'session_new_passes':len(records)-session_start_count,'last_pass':({k:last.get(k) for k in ['pass','question','disposition','next','terminal']} if last else None),'resume_next':next_question,'pass_bundle_sha256':pass_bundle_sha(adir),'csc':audit,'promotion_authority':'NONE'}
    writej(adir/'ARM_STATE_V3.json',state)
    writej(adir/'HELIX_V3.json',{'survivors':last.get('survivors',[]) if last else [],'scars':last.get('scars',[]) if last else [],'demotions':last.get('demotions',[]) if last else [],'unresolved':last.get('unresolved',[]) if last else [],'next':next_question,'total_admitted_passes':len(records),'session_new_passes':len(records)-session_start_count})
    writej(adir/'V3_SESSION_RECEIPT.json',state)
    return state

def write_research_stop(adir:Path,arm:str,records:list[dict[str,Any]],reason:str,session_start_count:int=0,next_question:str|None=None)->dict[str,Any]:
    audit=csc(records,arm,'RESEARCH_INSTRUMENT_STOP_V3') if records else {'verdict':'REVIEW','terminal_supported':False,'authority':'AUDIT_ONLY_NONE_PROMOTION','errors':[],'warnings':['no admitted passes']}
    stop={'arm':arm,'runtime':'V3','status':reason,'scientific_closure':False,'passes_completed':len(records),'session_new_passes':len(records)-session_start_count,'last_valid_next':next_question if next_question is not None else (records[-1].get('next') if records else None),'pass_bundle_sha256':pass_bundle_sha(adir),'csc':audit,'promotion_authority':'NONE'}
    writej(adir/'RESEARCH_STOP_V3.json',stop)
    write_v3_state(adir,arm,records,reason,stop['last_valid_next'],audit,session_start_count)
    return stop

def run_arm(worktree:Path,arm:str,max_passes:int)->dict[str,Any]:
    croot=worktree/CAMPAIGN_REL; adir=croot/arm
    manifest=json.loads((adir/'ARM_MANIFEST.json').read_text(encoding='utf-8'))
    process=(croot/'R3_1_PROCESS_CONTRACT.md').read_text(encoding='utf-8')
    chunks=build_corpus(worktree,arm)
    records=load_existing_chain(adir)
    session_start_count=len(records)
    prev=records[-1] if records else None
    external_path=croot/'V3_EXTERNAL_REFRAMES.json'
    external=(json.loads(external_path.read_text(encoding='utf-8')).get('reframes',{}) if external_path.exists() else {})
    external_question=str(external.get(arm,'')).strip()
    prior_questions={str(r.get('question','')).strip() for r in records}
    use_external=bool(external_question and external_question not in prior_questions)
    question=(external_question if use_external else (str(prev.get('next')).strip() if prev else manifest['seed_question']))
    if use_external:
        writej(adir/'V3_EXTERNAL_REFRAME_ACCEPTED.json',{'status':'EXTERNAL_REFRAME_ACCEPTED__NOT_SCIENTIFIC_EVIDENCE','from_stop':json.loads((adir/'RESEARCH_STOP.json').read_text(encoding='utf-8')).get('status') if (adir/'RESEARCH_STOP.json').exists() else None,'prior_last_next':prev.get('next') if prev else None,'next':question,'promotion_authority':'NONE'})
    if prev and bool(prev.get('terminal')) and str(prev.get('disposition')) in TERMINAL and not use_external:
        if terminal_has_csc_pass(adir,int(prev.get('pass'))):
            final_audit=csc(records,arm,'RESUME_ALREADY_CSC_PASS_TERMINAL'); writej(adir/'CSC_ARM_CLOSEOUT.json',final_audit)
            return write_v3_state(adir,arm,records,'RESUME_ALREADY_CSC_PASS_TERMINAL',prev.get('next'),final_audit,session_start_count)
        # Terminal language without CSC PASS is not arm closure. Earn a distinct successor or stop explicitly for external reframe.
        reframed=generate_reframe(worktree,adir,arm,records,question)
        if not reframed:
            return write_research_stop(adir,arm,records,'QUESTION_SATURATED__REQUIRES_EXTERNAL_REFRAME',session_start_count,question)
        question=reframed
    ledger=['# '+arm+' — Pass Ledger','',f'Seed question: {manifest["seed_question"]}','']
    for r in records:
        ledger += [f'## P{r.get("pass"):02d}',f'Question: {r.get("question")}',f'Disposition: {r.get("disposition")}',f'OARR: {r.get("oarr")}',f'LOOP+: {r.get("loop_plus")}',f'Survivors: {r.get("survivors")}',f'Scars: {r.get("scars")}',f'Demotions: {r.get("demotions")}',f'Next: {r.get("next")}','']
    pnum=len(records)+1
    reframe_budget=2
    while pnum<=max_passes:
        ev=retrieve(chunks,question,compact_helix(prev),k=8)
        evtxt='\n\n'.join(f'SOURCE {c.source}\n{c.text[:900]}' for c in ev)
        system=(
          'You are one research pass in canonical Microseed MS_FRONTIER_HELIX_V1. Research only; promotion authority NONE; production mutation is forbidden in Wave 1. '
          'PDVER means exactly PROBE -> DERIVE -> VERIFY -> EMBODY -> RECURSE. VERIFY is before EMBODY. '
          'Pass N earns Pass N+1: do not prewrite later questions. For a non-terminal pass, NEXT must be a DIFFERENT, narrower or higher-information question than the current question. HSP qualifies measurement. OARR must attack with a real rival/removal/altered/counterexample/assistance/old-owner/currentness/authority explanation where meaningful. LOOP+ widens an adjacent plausible causal branch before convergence. '
          'Semantic HELIX explicitly carries survivors, scars, demotions, unresolved. Attention Reservoir names neglected evidence or bounded-complete. '
          'Before claiming new mechanism classify failures among observation/channel/measurement-frame/identifiability/access/basis-representation/scope-context/currentness/search/authority/true-capability. '
          'EMBODY in Wave 1 may only be NO_MUTATION_WARRANTED or a bounded research artifact/experiment specification; it may NOT modify microseed production. If no new execution occurs, observed_consequence must explicitly say SOURCE_EVIDENCE_ONLY__NO_NEW_WORLD_CONSEQUENCE and must not claim a new observed result. '
          'Return JSON only with exact required keys: question, evidence_contacted, measurement_frame, probe, derive, verify, oarr, loop_plus, embody, observed_consequence, survivors, scars, demotions, unresolved, attention_reservoir, disposition, next, terminal. '
          'disposition must be one of RESEARCH_CONTINUE, RESOLVED_EXISTING_OWNERS, RESOLVED_NEGATIVE, UNKNOWN_INCOMPLETE, MISSING_EVIDENCE, NON_IDENTIFIABLE, MINIMAL_GAP_LOCALIZED, PRODUCTION_CANDIDATE, QUESTION_MALFORMED. terminal is boolean.' )
        predecessor='NONE' if prev is None else json.dumps({k:prev.get(k) for k in ['question','disposition','survivors','scars','demotions','unresolved','next']},ensure_ascii=False)[:1800]
        user=f'ARM {arm}; PASS {pnum}/{max_passes}\nAUTHORITATIVE QUESTION: {question}\n\nPREDECESSOR:\n{predecessor}\n\nRETRIEVED EVIDENCE:\n{evtxt[:7000]}\n\nPROCESS CONTRACT EXCERPT:\n{process[:2500]}\n\nAnswer only what admitted evidence supports. If embodiment is required, specify the smallest discriminating artifact/fixture/test and stop short of production mutation.'
        obj=None; meta=None; errors=[]
        attempt_user=user
        for sem_attempt in range(1,4):
            candidate,meta=chat(PRIMARY,system,attempt_user,max_tokens=1050,temp=.22 if sem_attempt==1 else .08,raw_dir=adir,raw_tag=f'V3_P{pnum:02d}_MODEL_SEM{sem_attempt}')
            # The question field is an echoed control-plane input, not model-generated science. Preserve raw model output separately, then bind it exactly.
            candidate['question']=question
            # Normalize trivial NEXT punctuation before semantic validation; do not alter semantic content.
            nq=str(candidate.get('next','')).strip()
            if nq and not bool(candidate.get('terminal')) and not nq.endswith('?'):
                candidate['next']=nq.rstrip('. !')+'?'
            candidate['evidence_contacted']=[c.source for c in ev]
            # No execution in autonomous Wave 1 means there is no newly observed world consequence.
            emb=candidate.get('embody')
            if emb=='NO_MUTATION_WARRANTED' or (isinstance(emb,dict) and str(emb.get('status','')).upper() in {'NO_MUTATION_WARRANTED','SPEC_ONLY','RESEARCH_ARTIFACT_ONLY'}):
                candidate['observed_consequence']='SOURCE_EVIDENCE_ONLY__NO_NEW_WORLD_CONSEQUENCE'
            errors=validate(candidate,question)
            if not errors:
                obj=candidate; break
            writej(adir/f'V3_REJECTED_P{pnum:02d}_ATTEMPT{sem_attempt}.json',{'status':'METHOD_REJECTED__NOT_SCIENTIFIC_PASS','question':question,'errors':errors,'candidate':candidate,'promotion_authority':'NONE'})
            attempt_user=user+'\n\nMETHOD RETRY: the previous candidate was rejected for '+json.dumps(errors)+'. Correct those defects. Do not repeat the active question as NEXT unless terminal; produce a real OARR and LOOP+ discriminator, and do not claim a new observed consequence without execution.'
        if obj is None:
            reframed=generate_reframe(worktree,adir,arm,records,question)
            if reframed and reframe_budget>0:
                writej(adir/f'V3_P{pnum:02d}_SUCCESSOR_REFRAME_{reframe_budget}.json',{'status':'SUCCESSOR_REFRAMED_AFTER_METHOD_SATURATION__NOT_SCIENTIFIC_PASS','from_question':question,'next':reframed,'errors':errors,'promotion_authority':'NONE'})
                question=reframed
                reframe_budget-=1
                continue
            return write_research_stop(adir,arm,records,'QUESTION_SATURATED__REQUIRES_EXTERNAL_REFRAME',session_start_count,question)
        obj['pass']=pnum; obj['model_meta']=meta; obj['source_refs']=[c.source for c in ev]; obj['promotion_authority']='NONE'; obj['production_mutation_allowed']=False
        writej(adir/f'P{pnum:02d}.json',obj)
        ledger += [f'## P{pnum:02d}',f'Question: {question}',f'Disposition: {obj.get("disposition")}',f'OARR: {obj.get("oarr")}',f'LOOP+: {obj.get("loop_plus")}',f'Survivors: {obj.get("survivors")}',f'Scars: {obj.get("scars")}',f'Demotions: {obj.get("demotions")}',f'Next: {obj.get("next")}','']
        records.append(obj); prev=obj
        if pnum%5==0:
            audit=csc(records,arm,f'P{pnum:02d}') ; writej(adir/f'CSC_P{pnum:02d}.json',audit)
        if bool(obj.get('terminal')) and str(obj.get('disposition')) in TERMINAL:
            audit=csc(records,arm,f'TERMINAL_P{pnum:02d}'); writej(adir/f'CSC_TERMINAL_P{pnum:02d}.json',audit)
            if str(audit.get('verdict','')).upper()=='PASS' and bool(audit.get('terminal_supported')): break
            reframed=generate_reframe(worktree,adir,arm,records,question)
            if not reframed:
                return write_research_stop(adir,arm,records,'CSC_REVIEW_TERMINAL__REQUIRES_EXTERNAL_REFRAME',session_start_count,question)
            question=reframed
            pnum+=1
            reframe_budget=2
            continue
        nq=str(obj.get('next','')).strip()
        if not nq.endswith('?') or nq==question:
            reframed=generate_reframe(worktree,adir,arm,records,question)
            if not reframed:
                return write_research_stop(adir,arm,records,'QUESTION_SATURATED__REQUIRES_EXTERNAL_REFRAME',session_start_count,question)
            nq=reframed
        question=nq
        pnum+=1
        reframe_budget=2
    if not records:
        return write_research_stop(adir,arm,records,'NO_ADMITTED_PASS__REQUIRES_EXTERNAL_REFRAME',session_start_count,question)
    final_audit=csc(records,arm,'ARM_CLOSEOUT'); writej(adir/'CSC_ARM_CLOSEOUT.json',final_audit)
    last=records[-1]
    writej(adir/'HELIX.json',{'survivors':last.get('survivors',[]),'scars':last.get('scars',[]),'demotions':last.get('demotions',[]),'unresolved':last.get('unresolved',[]),'next':last.get('next'),'passes_completed':len(records)})
    writej(adir/'RESERVOIR.json',{'items':last.get('attention_reservoir',[]),'passes_completed':len(records)})
    (adir/'PASS_LEDGER.md').write_text('\n'.join(ledger).rstrip()+'\n',encoding='utf-8',newline='\n')
    close={'arm':arm,'runtime':'V3','passes_completed':len(records),'session_new_passes':len(records)-session_start_count,'final_disposition':last.get('disposition'),'terminal':last.get('terminal'),'next':last.get('next'),'pass_bundle_sha256':pass_bundle_sha(adir),'csc':final_audit,'promotion_authority':'NONE','production_delta':subprocess.check_output(['git','diff','--name-only',CANON+'..HEAD','--','microseed'],cwd=worktree,text=True).splitlines()}
    writej(adir/'ARM_CLOSEOUT_V3.json',close)
    write_v3_state(adir,arm,records,'MAX_PASS_SLICE_COMPLETE',last.get('next'),final_audit,session_start_count)
    return close

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
        c=subprocess.run(['git','commit','-m',f'MS Frontier Helix v1: {arm} V3 continuation closeout'],cwd=wt,text=True,capture_output=True)
        if c.returncode not in (0,1): raise RuntimeError(c.stdout+c.stderr)
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=wt,text=True).strip()
        push=subprocess.run(['git','push','-u','origin','HEAD:'+branch],cwd=wt,text=True,capture_output=True,timeout=300)
        close['git']={'branch':branch,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=wt,text=True).strip(),'push_rc':push.returncode,'push_stdout':push.stdout,'push_stderr':push.stderr}
    print(json.dumps(close,indent=2,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
