from __future__ import annotations
import json, subprocess
from pathlib import Path

PREVIOUS_CANON='ed2cde491962105b0d853b7fd82d8e8b3d81bd8a'
FINISH='1c42da8e53df54a11615a88150a667f9673dff67'
ADMISSION_AUDIT_V2='aaabf382f98bddc0bdcdfc84ffa11a8a942798d1'
EXPECTED_MICROSEED_TREE='88f5a058cc5a4e92b1006c36d31b95cf727d197f'
EXPECTED_DELTA=['microseed/runtime/entity.py']


def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


def test_current_promotion_candidate_preserves_tested_microseed_bytes_and_exact_delta():
    root=Path(__file__).resolve().parents[2]
    assert git(root,'rev-parse','HEAD:microseed')==EXPECTED_MICROSEED_TREE
    assert git(root,'rev-parse',FINISH+':microseed')==EXPECTED_MICROSEED_TREE
    assert git(root,'rev-parse',ADMISSION_AUDIT_V2+':microseed')==EXPECTED_MICROSEED_TREE
    changed=git(root,'diff','--name-only',PREVIOUS_CANON+'..HEAD','--','microseed').splitlines()
    assert changed==EXPECTED_DELTA
    assert subprocess.run(['git','merge-base','--is-ancestor',FINISH,'HEAD'],cwd=root).returncode==0
    assert subprocess.run(['git','merge-base','--is-ancestor',ADMISSION_AUDIT_V2,'HEAD'],cwd=root).returncode==0


def test_ms_substrate_hardening_receipt_preserves_authority_ceiling_before_tag_readback():
    root=Path(__file__).resolve().parents[2]
    r=json.loads((root/'evidence/MS_SUBSTRATE_HARDENING_V1_CANONICAL_PROMOTION_RECEIPT.json').read_text(encoding='utf-8'))
    assert r['production_delta']==EXPECTED_DELTA
    assert r['candidate_microseed_tree']==EXPECTED_MICROSEED_TREE
    assert r['tested_research_microseed_tree']==EXPECTED_MICROSEED_TREE
    assert r['bc_overlap_decision']['research_hardening_bc_nested_currentness_v1']=='QUARANTINED_EXCLUDED_FROM_THIS_PROMOTION'
    a=r['authority_boundary']
    assert all(v is False for v in a.values())
    assert r['status'] in {'PROMOTION_CANDIDATE_SEALED__TAG_PUSH_READBACK_PENDING','CANONICAL_PROMOTION_SEALED__LOCAL_TAG_CREATED__REMOTE_PUSH_PENDING','CANONICAL_PROMOTION_SEALED','CANONICAL_PROMOTION_SEALED__REMOTE_TAG_AND_BRANCH_READBACK_CONFIRMED__PUBLIC_MAIN_UNMOVED'}
