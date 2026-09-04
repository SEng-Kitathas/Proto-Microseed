from __future__ import annotations
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
PY=sys.executable

def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(root:Path):
    return subprocess.run([PY,'-S',str(root/'VERIFY_CANONICAL_SOP.py'),str(root)],capture_output=True,text=True)

def rehash(root:Path, rel:str):
    mf=root/'MANIFEST_SHA256.json'
    m=json.loads(mf.read_text(encoding='utf-8'))
    p=root/rel
    m['files'][rel]={'bytes':p.stat().st_size,'sha256':sha(p)}
    mf.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')

def mutate(root:Path, rel:str, old:str, new:str, *, remanifest:bool=True):
    p=root/rel
    t=p.read_text(encoding='utf-8')
    if old not in t:raise RuntimeError(f'mutation anchor missing {rel}: {old}')
    p.write_text(t.replace(old,new,1),encoding='utf-8',newline='\n')
    if remanifest:
        rehash(root,rel)

def append_and_rehash(root:Path, rel:str, text:str):
    p=root/rel
    p.write_text(p.read_text(encoding='utf-8')+text,encoding='utf-8',newline='\n')
    rehash(root,rel)

def delete_and_remanifest(root:Path, rel:str):
    p=root/rel
    p.unlink()
    mf=root/'MANIFEST_SHA256.json'
    m=json.loads(mf.read_text(encoding='utf-8'))
    m['files'].pop(rel,None)
    mf.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')

def mutate_manifest_package_id(root:Path):
    mf=root/'MANIFEST_SHA256.json'
    m=json.loads(mf.read_text(encoding='utf-8'))
    m['package_id']='RAHL_ENGINEERING_CANONICAL_SOP_R4_1_2026-09-03'
    mf.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')

def main():
    cases=[]
    # Semantic mutations are deliberately re-manifested so rejection must come from
    # semantic/authority guards rather than the trivial fact that bytes changed.
    cases.append(('candidate_id_collision',lambda r: mutate(r,'00_READ_ME_FIRST.md','R4.2','R4.1')))
    cases.append(('continuity_becomes_proof',lambda r: mutate(r,'00_READ_ME_FIRST.md','CONTINUITY != PROOF','CONTINUITY = PROOF')))
    cases.append(('remembered_pointer_becomes_current',lambda r: mutate(r,'00_READ_ME_FIRST.md','REMEMBERED_POINTER != CURRENT_STATE_EVIDENCE','REMEMBERED_POINTER = CURRENT_STATE_EVIDENCE')))
    cases.append(('base_tier_becomes_optional',lambda r: mutate(r,'05_RESEARCH_MACHINERY_AND_MODES.md','BASE_TIER_FUNCTIONAL_OBLIGATIONS != OPTIONAL_FOR_NONTRIVIAL_WORK','BASE_TIER_FUNCTIONAL_OBLIGATIONS = OPTIONAL_FOR_NONTRIVIAL_WORK')))
    cases.append(('pdver_order_regresses',lambda r: mutate(r,'04_RESEARCH_GOVERNANCE.md','PROBE -> DERIVE -> VERIFY -> EMBODY -> RECURSE','PROBE -> DERIVE -> EMBODY -> VERIFY -> RECURSE')))
    cases.append(('ai_coprocessor_removed',lambda r: mutate(r,'05_RESEARCH_MACHINERY_AND_MODES.md','## AI co-processor obligation','## Optional AI assistance')))
    cases.append(('res_self_promotes',lambda r: mutate(r,'07C_RESEARCH_EPISTEMIC_SHADOW_PROTOCOL.md','RES_CONTENT != GOVERNING_DOCTRINE','RES_CONTENT = GOVERNING_DOCTRINE')))
    cases.append(('environment_identity_collapsed',lambda r: mutate(r,'06_EXECUTION_RELEASE_AND_ENVIRONMENT_DISCIPLINE.md','SEALED_ARTIFACT != SEALED_ENVIRONMENT','SEALED_ARTIFACT = SEALED_ENVIRONMENT')))
    cases.append(('fixed_transport_limit_reintroduced',lambda r: mutate(r,'06_EXECUTION_RELEASE_AND_ENVIRONMENT_DISCIPLINE.md','No fixed transport limit is universal SOP law','Universal archive part limit is 200000000 bytes')))
    cases.append(('unknown_guessing_allowed',lambda r: mutate(r,'09_UNKNOWN_TRACE_AND_RECOVERY_RULE.md','Never guess across the gap','Guess across the gap when convenient')))
    cases.append(('fresh_chat_blindness_collapse',lambda r: mutate(r,'12_COLD_START_PROTOCOL.md','FRESH_THREAD != FRESH_EVALUATOR_IF_MEMORY_OR_HISTORY_IS_SHARED','FRESH_THREAD = FRESH_EVALUATOR_IF_MEMORY_OR_HISTORY_IS_SHARED')))
    cases.append(('extra_unmanifested_file',lambda r: (r/'SURPRISE.txt').write_text('x',encoding='utf-8')))
    cases.append(('project_specific_contamination',lambda r: append_and_rehash(r,'02_ENGINEERING_AUTHORITY_SURFACE.md','\nSpecific project: SPECIFICPROJECT_SENTINEL\n')))
    def corrupt_parent(r:Path):
        p=r/'ancestry'/'RAHL_ENGINEERING_CANONICAL_SOP_R4_1_2026-09-03.zip'
        with p.open('ab') as f:f.write(b'X')
        rehash(r,'ancestry/RAHL_ENGINEERING_CANONICAL_SOP_R4_1_2026-09-03.zip')
    cases.append(('parent_ancestry_corrupted_but_remanifested',corrupt_parent))
    cases.append(('semantic_read_gate_demoted',lambda r: mutate(r,'02_ENGINEERING_AUTHORITY_SURFACE.md','it SHALL receive a complete linear semantic read','it MAY receive a partial semantic skim')) )
    cases.append(('automated_checks_replace_semantic_read',lambda r: mutate(r,'02_ENGINEERING_AUTHORITY_SURFACE.md','AUTOMATED_CHECKS != LINEAR_SEMANTIC_READ','AUTOMATED_CHECKS = LINEAR_SEMANTIC_READ')) )
    cases.append(('response_failure_becomes_execution_failure',lambda r: mutate(r,'06_EXECUTION_RELEASE_AND_ENVIRONMENT_DISCIPLINE.md','CONTROL_PLANE_RESPONSE_FAILURE != LOCAL_EXECUTION_FAILURE','CONTROL_PLANE_RESPONSE_FAILURE = LOCAL_EXECUTION_FAILURE')) )
    cases.append(('control_plane_becomes_bulk_plane',lambda r: mutate(r,'06_EXECUTION_RELEASE_AND_ENVIRONMENT_DISCIPLINE.md','CONTROL_PLANE != BULK_DATA_PLANE','CONTROL_PLANE = BULK_DATA_PLANE')) )
    cases.append(('semantic_read_skipped_for_transport',lambda r: mutate(r,'06_EXECUTION_RELEASE_AND_ENVIRONMENT_DISCIPLINE.md','CONTROL_PLANE_MINIMIZATION != SEMANTIC_READ_SKIPPING','CONTROL_PLANE_MINIMIZATION = SEMANTIC_READ_SKIPPING')) )
    cases.append(('canonical_path_regression',lambda r: (r/'MANIFEST_SHA256.json').write_text((r/'MANIFEST_SHA256.json').read_text(encoding='utf-8').replace('machine/AUTHORITY_CLASSES.json','machine\\\\AUTHORITY_CLASSES.json',1),encoding='utf-8')))
    cases.append(('required_doc_deleted_and_remanifested',lambda r: delete_and_remanifest(r,'03_PROJECT_OBLIGATION_INTERFACE.md')))
    cases.append(('operator_side_default_demoted',lambda r: mutate(r,'06A_SERVER_EXECUTION_METHODOLOGY_FOR_UNRELIABLE_PLANES.md','Default to the operator-owned/local/server side for as much as possible.','Default to assistant-side execution for as much as possible.')) )
    cases.append(('prettiest_plane_promoted',lambda r: mutate(r,'06A_SERVER_EXECUTION_METHODOLOGY_FOR_UNRELIABLE_PLANES.md','Use the strongest surviving plane, not the prettiest plane.','Use the prettiest plane, not the strongest surviving plane.')) )
    cases.append(('assistant_convenience_becomes_enough',lambda r: mutate(r,'06A_SERVER_EXECUTION_METHODOLOGY_FOR_UNRELIABLE_PLANES.md','Assistant-side convenience alone is not enough.','Assistant-side convenience alone is enough.')) )
    cases.append(('fallback_becomes_authority_bypass',lambda r: mutate(r,'06A_SERVER_EXECUTION_METHODOLOGY_FOR_UNRELIABLE_PLANES.md','EXECUTION_PLANE_FALLBACK != AUTHORITY_BYPASS','EXECUTION_PLANE_FALLBACK = AUTHORITY_BYPASS')) )
    cases.append(('manifest_package_id_drift',mutate_manifest_package_id))

    passed=[]; failed=[]
    for name,fn in cases:
        with tempfile.TemporaryDirectory() as td:
            dst=Path(td)/BASE.name
            shutil.copytree(BASE,dst)
            fn(dst)
            cp=run(dst)
            if cp.returncode!=0:
                passed.append({'name':name,'verifier_output':cp.stdout.strip().splitlines()[-1:]})
            else:
                failed.append({'name':name,'stdout':cp.stdout,'stderr':cp.stderr})
    result={'hostile_cases':len(cases),'rejected_as_expected':len(passed),'rejections':passed,'unexpected_passes':failed}
    print(json.dumps(result,indent=2))
    return 0 if not failed else 2

if __name__=='__main__':raise SystemExit(main())
