from __future__ import annotations
import json, subprocess
from pathlib import Path

PREVIOUS_CANON='0f6cf0b3d660c8a4bb9561a65d7f1fd95e1b99f7'
ADMISSION_AUDIT_V2='461e59a2f5ea2daf838542ea0463777a0588f512'
EXPECTED_MICROSEED_TREE='4c8051563279d20f2ea555d21d7b3305b039e771'
EXPECTED_DELTA=['microseed/development/rehearsal.py', 'microseed/runtime/entity.py']
EXPECTED_RECEIPT='evidence/BC_NESTED_CURRENTNESS_V1_CANONICAL_PROMOTION_RECEIPT.json'


def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


def test_current_promotion_candidate_preserves_tested_microseed_bytes_and_exact_delta():
    root=Path(__file__).resolve().parents[2]
    assert git(root,'rev-parse','HEAD:microseed')==EXPECTED_MICROSEED_TREE
    assert git(root,'rev-parse',ADMISSION_AUDIT_V2+':microseed')==EXPECTED_MICROSEED_TREE
    changed=git(root,'diff','--name-only',PREVIOUS_CANON+'..HEAD','--','microseed').splitlines()
    assert changed==EXPECTED_DELTA
    assert subprocess.run(['git','merge-base','--is-ancestor',PREVIOUS_CANON,'HEAD'],cwd=root).returncode==0
    assert subprocess.run(['git','merge-base','--is-ancestor',ADMISSION_AUDIT_V2,'HEAD'],cwd=root).returncode==0


def test_bc_nested_currentness_promotion_receipt_preserves_authority_ceiling():
    root=Path(__file__).resolve().parents[2]
    r=json.loads((root/EXPECTED_RECEIPT).read_text(encoding='utf-8'))
    assert r['production_delta']==EXPECTED_DELTA
    assert r['candidate_microseed_tree']==EXPECTED_MICROSEED_TREE
    assert r['tested_research_microseed_tree']==EXPECTED_MICROSEED_TREE
    assert r['admission_audit_v2_head']==ADMISSION_AUDIT_V2
    assert r['verification']['whole_suite_clean_confirmation']['pytest_return_code']==0
    assert r['verification']['whole_suite_clean_confirmation']['stderr_bytes']==0
    assert r['verification']['whole_suite_clean_confirmation']['v1_supervision_lost_caveat']=='SUPERSEDED_BY_V2_CLEAN_CAPTURED_CONFIRMATION'
    a=r['authority_boundary']
    assert all(v is False for v in a.values())
    assert r['status'] in {
        'PROMOTION_CANDIDATE_SEALED__TAG_PUSH_READBACK_PENDING',
        'CANONICAL_PROMOTION_SEALED__LOCAL_TAG_CREATED__REMOTE_PUSH_PENDING',
        'CANONICAL_PROMOTION_SEALED__REMOTE_TAG_BRANCH_AND_MAIN_READBACK_PENDING_FINAL_HEAD',
        'CANONICAL_PROMOTION_SEALED__PUBLIC_MAIN_FAST_FORWARD_CONFIRMED',
    }
