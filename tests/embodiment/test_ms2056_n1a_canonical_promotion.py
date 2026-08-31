from __future__ import annotations

import json
import subprocess
from pathlib import Path

P1A='2c3e225fd1fcaa89965da80d6048bc178c521740'
RESEARCH='9caaac51ecfdac7b5e48c98faf585d4b36ed09e8'
TAG='prelingual-substrate-v1-p1a-n1a'
EXPECTED=[
    "microseed/development/action_closure.py",
    "microseed/development/experimental_warrant.py",
    "microseed/persistence/store.py",
    "microseed/runtime/entity.py",
]

def test_ms2056_n1a_tag_is_descendant_of_tested_research_head_and_preserves_tested_production_bytes():
    root=Path(__file__).resolve().parents[2]
    promoted=subprocess.check_output(["git","rev-parse",TAG+"^{}"],cwd=root,text=True).strip()
    assert subprocess.run(["git","merge-base","--is-ancestor",RESEARCH,promoted],cwd=root).returncode==0
    assert subprocess.check_output(["git","rev-parse",promoted+":microseed"],cwd=root,text=True).strip()==subprocess.check_output(["git","rev-parse",RESEARCH+":microseed"],cwd=root,text=True).strip()
    changed=subprocess.check_output(["git","diff","--name-only",P1A+".."+promoted,"--","microseed"],cwd=root,text=True).splitlines()
    assert changed==EXPECTED

def test_ms2056_public_receipt_records_green_whole_suite_and_no_authority_laundering():
    root=Path(__file__).resolve().parents[2]
    r=json.loads((root/"evidence/MS2056_N1A_CANONICAL_PROMOTION_RECEIPT.json").read_text(encoding="utf-8"))
    assert r["whole_suite"]["pytest"]=="926/926 PASS"
    assert r["whole_suite"]["stderr_bytes"]==0
    assert r["authority_boundary"]["unknown_safe"] is False
    assert r["authority_boundary"]["unknown_selected"] is False
    assert r["authority_boundary"]["unknown_permitted_without_warrant"] is False
    assert r["authority_boundary"]["selection_authority"]=="UNIQUE_ELIGIBILITY_ONLY"
