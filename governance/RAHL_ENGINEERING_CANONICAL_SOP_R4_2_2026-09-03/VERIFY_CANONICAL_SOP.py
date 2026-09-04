from __future__ import annotations
import hashlib, json, re, sys, zipfile
from pathlib import Path

PACKAGE_ID='RAHL_ENGINEERING_CANONICAL_SOP_R4_2_2026-09-03'
PARENT_SHA='af4364fbcf8e5d33aa2ad06e4da9c4669d4be2ffcbc332e416742bec1543f4d2'
R40_SHA='020fcfb642a304869f2d266080f4dcf21959ca09c5fa14f60c0ec06616273f0a'
GRANDPARENT_SHA='4d205becc2413889bdb37c6b6ff7513d6f759a7dff1d9f9b8fddaddd8235a278'
EVIDENCE={
'evidence/receiver_continuity_qualification/CANDIDATE_SEAL.json':'16c04f9460a1dcad12485db00ee6639f63f8382862262eadf26ea5af7829fdea',
'evidence/receiver_continuity_qualification/CONTINUITY_ENVELOPE_V0_1.patch':'59fef362ce36896a20379d1514ae865aad547b3ce57705fad9b8add382bc106a',
'evidence/receiver_continuity_qualification/QUALIFICATION_REPORT.md':'5a8d50cf7dcd95722756116db786dae32944efb7360d1cf7f47ad37e88115aa7',
'evidence/receiver_continuity_qualification/SOURCE_SNAPSHOT_MANIFEST.json':'20c83018ee217de05e714edaaef3b97ce49899d4d18db2cb6601f0d01c83d24f'}
FORBIDDEN_ACTIVE=['PCMMAD','HOSTILE-OS','Microseed','Proto-AGI','PAL','CFE','Singularity Works','Forge','StarMap','CIC-NERV','Steve Grand','Tommy','SPECIFICPROJECT_SENTINEL','E:\\\\','D:\\\\','C:\\\\Users\\\\']
REQUIRED_DOCS=[f'{i:02d}_' for i in range(0,16)]
REQUIRED_FIXED={
'PROMOTION_RECEIPT.md',
'RELEASE_VERIFICATION.md',
'VERIFY_CANONICAL_SOP.py',
'tests/RUN_HOSTILE_TESTS.py',
'machine/AUTHORITY_CLASSES.json',
'machine/BASE_TIER_ENGINEERING_METABOLISM.json',
'machine/CONTINUITY_INSTRUMENTS.json',
'machine/EXECUTION_AND_ENVIRONMENT.json',
'machine/SCARS.json',
'06A_SERVER_EXECUTION_METHODOLOGY_FOR_UNRELIABLE_PLANES.md',
'ancestry/RAHL_ENGINEERING_CANONICAL_SOP_R4_1_2026-09-03.zip',
'ancestry/RAHL_ENGINEERING_CANONICAL_SOP_R4_0_2026-09-02.zip',
'ancestry/RAHL_ENGINEERING_IN_HOUSE_SOP_SPLIT_CANDIDATE_R3_1_2026-08-29.zip',
'evidence/README.md',
'evidence/receiver_continuity_qualification/CANDIDATE_SEAL.json',
'evidence/receiver_continuity_qualification/CONTINUITY_ENVELOPE_V0_1.patch',
'evidence/receiver_continuity_qualification/QUALIFICATION_REPORT.md',
'evidence/receiver_continuity_qualification/SOURCE_SNAPSHOT_MANIFEST.json',
}

def h(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def fail(msg:str)->int: print('FAIL:',msg); return 2

def main(root:Path)->int:
    root=root.resolve()
    if root.name!=PACKAGE_ID:return fail(f'package id {root.name!r}')
    mf=root/'MANIFEST_SHA256.json'
    try:m=json.loads(mf.read_text(encoding='utf-8'))
    except Exception as e:return fail(f'manifest parse {e}')
    if m.get('package_id')!=PACKAGE_ID:return fail(f"manifest package id {m.get('package_id')!r}")
    if m.get('schema')!='rahl.sop.package-manifest.v1':return fail(f"manifest schema {m.get('schema')!r}")
    expected=set(m['files']); actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p!=mf}
    if not REQUIRED_FIXED.issubset(expected):return fail(f'required fixed members missing={sorted(REQUIRED_FIXED-expected)}')
    for prefix in REQUIRED_DOCS:
        matches=sorted(rel for rel in expected if '/' not in rel and rel.startswith(prefix) and rel.endswith('.md'))
        if len(matches)!=1:return fail(f'required canonical doc {prefix} count={len(matches)} matches={matches}')
    if expected!=actual:return fail(f'membership missing={sorted(expected-actual)} extra={sorted(actual-expected)}')
    for rel,meta in m['files'].items():
        p=root/rel
        if p.stat().st_size!=meta['bytes'] or h(p)!=meta['sha256']:return fail(f'hash/size {rel}')
    # canonical member identity
    if any('\\\\' in rel for rel in m['files']):return fail('backslash member identity in manifest')
    # active docs are universal; ancestry/evidence may preserve exact historical context
    active=[]
    for p in root.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(root).as_posix()
        if rel.startswith(('ancestry/','evidence/','tests/')):continue
        if p.suffix.lower() not in {'.md','.json','.py'}:continue
        try:t=p.read_text(encoding='utf-8')
        except UnicodeDecodeError:return fail(f'active utf8 {rel}')
        active.append((rel,t))
    for rel,t in active:
        if rel=='VERIFY_CANONICAL_SOP.py':continue
        for token in FORBIDDEN_ACTIVE:
            if token.endswith('\\') or ':\\' in token:
                hit = token.lower() in t.lower()
            else:
                hit = re.search(r'(?<![A-Za-z0-9_-])'+re.escape(token)+r'(?![A-Za-z0-9_-])', t, re.I) is not None
            if hit:return fail(f'project/person contamination {token!r} in {rel}')
    old_order='PROBE -> DERIVE -> EMBODY -> VERIFY -> RECURSE'
    for rel,t in active:
        if rel!='VERIFY_CANONICAL_SOP.py' and old_order in t:
            return fail(f'legacy PDVER ordering remains active in {rel}')
    # required semantic bindings
    bindings={
      '00_READ_ME_FIRST.md':['Rahl Engineering Canonical SOP — R4.2','CANONICAL_IN_HOUSE_SOP','CONTINUITY != PROOF','REMEMBERED_POINTER != CURRENT_STATE_EVIDENCE','BASE_TIER_FUNCTIONAL_OBLIGATIONS != MANDATORY_LINEAR_PIPELINE','TRIVIAL_TASK != FULL_CEREMONY','PDVER','AI co-processor strengths'],
      '01_AUTHORITY_CLASSES_AND_CONFLICT_RESOLUTION.md':['ADMISSIBILITY_CONSTRAINT','RESEARCH_SURVIVOR != UNIVERSAL_LAW'],
      '02_ENGINEERING_AUTHORITY_SURFACE.md':['C23 — Base-tier engineering metabolism for nontrivial work','BASE_TIER_FUNCTIONAL_OBLIGATIONS != OPTIONAL_FOR_NONTRIVIAL_WORK','C24 — Linear human read / semantic admission gate','it SHALL receive a complete linear semantic read','AUTOMATED_CHECKS != LINEAR_SEMANTIC_READ','C25 — Durable local execution / control-plane minimization','CONTROL_PLANE_RESPONSE_FAILURE != LOCAL_EXECUTION_FAILURE','C26 — Operator-side execution preference under instability','ASSISTANT_SIDE_CONVENIENCE != MATERIAL_ADVANTAGE'],
      '04_RESEARCH_GOVERNANCE.md':['PROBE -> DERIVE -> VERIFY -> EMBODY -> RECURSE','No fixed pass count is universal process law','Hostile engineering is standing adversarial pressure','AI co-processor value is additive base-tier capacity','Identifying vs developmental evaluation'],
      '05_RESEARCH_MACHINERY_AND_MODES.md':['Base-Tier Research Machinery','PDVER — recursive control fractal','Hostile engineering — adversarial survival pressure','OARR','Loop+','Semantic Helix','Attention Reservoir','CSC','AI co-processor obligation','BASE_TIER_FUNCTIONAL_OBLIGATIONS != OPTIONAL_FOR_NONTRIVIAL_WORK'],
      '06_EXECUTION_RELEASE_AND_ENVIRONMENT_DISCIPLINE.md':['SEALED_ARTIFACT != SEALED_ENVIRONMENT','IDENTITY_POLICY_IS_ARTIFACT_CLASS_RELATIVE','No fixed transport limit is universal SOP law','E13 — Linear semantic admission before authority transition','E14 — Durable local batch execution','E15 — Control plane is not the bulk data plane','E16 — Response-loss readback','CONTROL_PLANE_RESPONSE_FAILURE != LOCAL_EXECUTION_FAILURE','E17 — Execution-architecture escalation','E19 — Deterministic publication/release pattern','CONTROL_PLANE_MINIMIZATION != SEMANTIC_READ_SKIPPING','CONTROL_PLANE != BULK_DATA_PLANE','E20 — Strongest surviving operator-side plane','ASSISTANT_SIDE_CONVENIENCE != MATERIAL_ADVANTAGE'],
      '06A_SERVER_EXECUTION_METHODOLOGY_FOR_UNRELIABLE_PLANES.md':['Use the strongest surviving plane, not the prettiest plane.','Default to the operator-owned/local/server side for as much as possible.','Assistant-side convenience alone is not enough.','EXECUTION_PLANE_FALLBACK != AUTHORITY_BYPASS'],
      '07_CONTINUITY_SYSTEM.md':['Live Shadow','Design Thread Stream','Research Epistemic Shadow (RES)','RES does not create doctrine','MUTABLE_PROCESS != MUTABLE_PUBLISHED_OBSERVATION'],
      '07C_RESEARCH_EPISTEMIC_SHADOW_PROTOCOL.md':['RES = What we learned.','22. Research Re-entry / Exact Next Move','RES_CONTENT != GOVERNING_DOCTRINE'],
      '09_UNKNOWN_TRACE_AND_RECOVERY_RULE.md':['Never guess across the gap','TRACE_PRESENT != TRACE_UNDERSTOOD'],
      '12_COLD_START_PROTOCOL.md':['activate the base-tier functional obligations in `05` proportionally','A handoff is a continuity map, not current-state evidence','FRESH_THREAD != FRESH_EVALUATOR_IF_MEMORY_OR_HISTORY_IS_SHARED','Execution-surface routing rule','complete linear semantic-read gate'],
      '13_PACKAGE_ARCHIVE_AND_PROVENANCE.md':['one unique package identity SHALL map to one exact payload tree','logical member identities use `/` canonical separators','Semantic sealing gate','Package-construction execution plane'],
      '14_CHANGELOG_AND_CULL_LEDGER.md':['R4.2 integration — semantic admission + durable local execution','DO THE WORK WHERE THE STATE LIVES; RETURN ONLY THE EVIDENCE NEEDED TO CONTROL IT.','R4.1 correction — base-tier engineering metabolism'],
      '15_CLAIM_CEILING_AND_NONCLAIMS.md':['flawless engineering or elimination of human/model blind spots','fresh chat is a fresh blind evaluator','machine verifier, test suite, manifest, or hostile mutation suite substitutes for complete semantic reading']}
    for rel,need in bindings.items():
        t=(root/rel).read_text(encoding='utf-8')
        for s in need:
            if s not in t:return fail(f'binding missing {rel}: {s}')
    # machine registries
    for rel in ['machine/AUTHORITY_CLASSES.json','machine/BASE_TIER_ENGINEERING_METABOLISM.json','machine/CONTINUITY_INSTRUMENTS.json','machine/EXECUTION_AND_ENVIRONMENT.json','machine/SCARS.json']:
        try:json.loads((root/rel).read_text(encoding='utf-8'))
        except Exception as e:return fail(f'json {rel}: {e}')
    # exact ancestry + evidence
    par=root/'ancestry'/'RAHL_ENGINEERING_CANONICAL_SOP_R4_1_2026-09-03.zip'
    if h(par)!=PARENT_SHA:return fail('parent R4.1 ancestry hash')
    r40=root/'ancestry'/'RAHL_ENGINEERING_CANONICAL_SOP_R4_0_2026-09-02.zip'
    if h(r40)!=R40_SHA:return fail('retained R4.0 ancestry hash')
    gp=root/'ancestry'/'RAHL_ENGINEERING_IN_HOUSE_SOP_SPLIT_CANDIDATE_R3_1_2026-08-29.zip'
    if h(gp)!=GRANDPARENT_SHA:return fail('retained R3.1 ancestry hash')
    for label,ap in [('parent R4.1',par),('retained R4.0',r40),('retained R3.1',gp)]:
        try:
            with zipfile.ZipFile(ap) as z:
                if z.testzip() is not None:return fail(f'{label} zip crc')
        except Exception as e:return fail(f'{label} zip parse {e}')
    for rel,digest in EVIDENCE.items():
        if h(root/rel)!=digest:return fail(f'evidence identity {rel}')
    print('PASS: exact membership/hash, canonical member paths, active-surface universality, base-tier metabolism + semantic-admission + durable-local-execution bindings, machine registries, exact R4.1/R4.0/R3.1 ancestry, and exact continuity qualification evidence')
    return 0
if __name__=='__main__':
    target=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
    raise SystemExit(main(target))
