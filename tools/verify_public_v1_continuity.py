from __future__ import annotations
import json, subprocess, sys, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V1='0fa41f1ed4cf2fbd341b5f0b63adbc0034d4ac39'
V1_TREE='88a4014db5838848b1e36b904b96e55b2a5f670e'
NAKED='06a3cbd409262b2b948fb8d1c3b96ad78f2b6c91'
LANG='e4e4c961654794d5d2b26eaeadeded2c0075a5df'
POINTER=ROOT/'evidence/PRELINGUAL_SUBSTRATE_V1_PUBLIC_CONTINUITY_POINTER.json'
RECEIPT=ROOT/'evidence/PRELINGUAL_SUBSTRATE_V1_PROMOTION_CONTINUITY_RECEIPT.json'
SUITE_STDOUT=ROOT/'evidence/PRELINGUAL_SUBSTRATE_V1_EXACT_SUITE_STDOUT.log'

def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return p.stdout.strip()

def git_bytes(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8','replace').strip() or p.stdout.decode('utf-8','replace').strip())
    return p.stdout

issues=[]
# Single-branch clones do not necessarily contain tags that point at off-main genesis commits.
# Fetch only the exact public tags required for verification when they are absent locally.
for tag in ('prelingual-substrate-v1','naked-authority-design-v1-genesis','grounded-language-reference-v1-genesis'):
    probe=subprocess.run(['git','rev-parse','--verify','--quiet',tag+'^{}'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if probe.returncode != 0:
        fetch=subprocess.run(['git','fetch','--quiet','origin','tag',tag],cwd=ROOT,text=True,capture_output=True)
        if fetch.returncode != 0:
            issues.append('TAG_FETCH_FAILED:'+tag)

pointer_blob=git_bytes('show','HEAD:'+POINTER.relative_to(ROOT).as_posix())
receipt_blob=git_bytes('show','HEAD:'+RECEIPT.relative_to(ROOT).as_posix())
suite_stdout_blob=git_bytes('show','HEAD:'+SUITE_STDOUT.relative_to(ROOT).as_posix())
pointer=json.loads(pointer_blob.decode('utf-8'))
r=json.loads(receipt_blob.decode('utf-8'))
if r.get('promotion_commit')!=V1: issues.append('RECEIPT_PROMOTION_COMMIT')
if r.get('promotion_tree')!=V1_TREE: issues.append('RECEIPT_PROMOTION_TREE')

# Public mirrors bind the copied operator receipt and exact scientific stdout.
mirrors=pointer.get('public_mirrors',{})
receipt_sha=hashlib.sha256(receipt_blob).hexdigest()
stdout_sha=hashlib.sha256(suite_stdout_blob).hexdigest()
if mirrors.get('exact_promotion_receipt',{}).get('sha256')!=receipt_sha: issues.append('PUBLIC_RECEIPT_HASH')
if mirrors.get('exact_suite_stdout',{}).get('sha256')!=stdout_sha: issues.append('PUBLIC_SUITE_STDOUT_HASH')
if r.get('scheduler_stdout',{}).get('sha256')!=stdout_sha: issues.append('RECEIPT_SUITE_STDOUT_HASH')
if r.get('scheduler_stdout',{}).get('bytes')!=len(suite_stdout_blob): issues.append('RECEIPT_SUITE_STDOUT_BYTES')
if b'911 passed in 883.01s' not in suite_stdout_blob: issues.append('SUITE_STDOUT_VERDICT')
if git('rev-parse',V1+'^{tree}')!=V1_TREE: issues.append('V1_TREE')
if git('rev-parse','prelingual-substrate-v1^{}')!=V1: issues.append('V1_TAG')
if git('rev-parse','naked-authority-design-v1-genesis^{}')!=NAKED: issues.append('NAKED_TAG')
if git('rev-parse','grounded-language-reference-v1-genesis^{}')!=LANG: issues.append('LANG_TAG')
if git('rev-parse',NAKED+'^')!=V1: issues.append('NAKED_PARENT')
if git('rev-parse',LANG+'^')!=V1: issues.append('LANG_PARENT')
head=git('rev-parse','HEAD')
if subprocess.run(['git','merge-base','--is-ancestor',V1,head],cwd=ROOT).returncode!=0: issues.append('HEAD_NOT_DESCENDANT_OF_V1')
# Historical V1 remains immutable. A later canonical promotion may change organism bytes only with its own explicit promotion tag.
head_microseed=git('rev-parse','HEAD:microseed')
v1_microseed=git('rev-parse',V1+':microseed')
if head_microseed != v1_microseed:
    p1a_tag=subprocess.run(['git','rev-parse','--verify','--quiet','prelingual-substrate-v1-p1a-repair^{}'],cwd=ROOT,text=True,capture_output=True)
    if p1a_tag.returncode != 0:
        issues.append('MICROSEED_CHANGED_WITHOUT_P1A_CANONICAL_TAG')
    else:
        changed=git('diff','--name-only',V1+'..'+p1a_tag.stdout.strip(),'--','microseed').splitlines()
        if changed != ['microseed/runtime/entity.py']:
            issues.append('P1A_PRODUCTION_DELTA_NOT_NARROW')
# Confirm branch-genesis metadata in both the public pointer and the copied operator receipt.
g=pointer.get('research_branch_genesis',{})
if g.get('naked',{}).get('genesis_commit')!=NAKED or g.get('naked',{}).get('parent')!=V1: issues.append('POINTER_NAKED_GENESIS')
if g.get('grounded_language',{}).get('genesis_commit')!=LANG or g.get('grounded_language',{}).get('parent')!=V1: issues.append('POINTER_LANGUAGE_GENESIS')
heads=r.get('remote_heads',{})
tags=r.get('peeled_tags',{})
if heads.get('research/naked-authority-design-v1')!=NAKED or tags.get('naked-authority-design-v1-genesis')!=NAKED: issues.append('RECEIPT_NAKED_GENESIS')
if heads.get('research/grounded-language-reference-v1')!=LANG or tags.get('grounded-language-reference-v1-genesis')!=LANG: issues.append('RECEIPT_LANGUAGE_GENESIS')
status='PASS' if not issues else 'FAIL'
print(json.dumps({'status':status,'head':head,'canonical_v1':V1,'canonical_tree':V1_TREE,'head_microseed_tree':head_microseed,'v1_microseed_tree':v1_microseed,'public_receipt_sha256':receipt_sha,'suite_stdout_sha256':stdout_sha,'issues':issues},indent=2))
sys.exit(0 if not issues else 1)
