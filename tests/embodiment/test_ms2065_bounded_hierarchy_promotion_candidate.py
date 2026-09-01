from __future__ import annotations
import json, subprocess
from pathlib import Path

BASE='0312459457223feb79bb2d0d71ab8387fbc28b1c'
RESEARCH='a9e4baaa8be3bcab749532160f57ab388839b368'
REPAIRED='f005670814511e3f8d5bf3aca33e577c43bca1d1'
EXPECTED=['microseed/development/epistemic.py','microseed/runtime/entity.py']


def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


def test_ms2065_candidate_preserves_repaired_tested_microseed_bytes_and_exact_delta():
    root=Path(__file__).resolve().parents[2]
    assert git(root,'rev-parse','HEAD:microseed')==git(root,'rev-parse',REPAIRED+':microseed')
    assert git(root,'rev-parse',RESEARCH+':microseed')==git(root,'rev-parse',REPAIRED+':microseed')
    changed=git(root,'diff','--name-only',BASE+'..HEAD','--','microseed').splitlines()
    assert changed==EXPECTED
    assert subprocess.run(['git','merge-base','--is-ancestor',RESEARCH,'HEAD'],cwd=root).returncode==0


def test_ms2065_receipt_preserves_authority_ceiling_before_promotion():
    root=Path(__file__).resolve().parents[2]
    r=json.loads((root/'evidence/MS2065_BOUNDED_HIERARCHY_CANONICAL_PROMOTION_RECEIPT.json').read_text(encoding='utf-8'))
    assert r['production_delta']==EXPECTED
    assert r['tested_research_microseed_tree']==git(root,'rev-parse',REPAIRED+':microseed')
    a=r['authority_boundary']
    assert all(v is False for v in a.values())
    assert r['status'] in {'PREPROMOTION_GATE_PENDING','PROMOTION_GATES_GREEN__SEAL_PENDING','PROMOTION_COMMIT_PENDING_TAG_PUSH_READBACK','CANONICAL_PROMOTION_SEALED'}
