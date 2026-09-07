from __future__ import annotations

import inspect
from pathlib import Path
import microseed.runtime.entity as entity
from scratch.lang_c08g_native_b2_ordered_composition import run_campaign


def run_audit() -> dict[str,object]:
    c08g=run_campaign('R4','T9')
    assert c08g['status']=='C08G_NATIVE_B2_ORDERED_COMPOSITION_REEMBODIED',c08g
    src=Path(inspect.getsourcefile(entity.Microseed)).read_text(encoding='utf-8')
    owned_methods=[]
    current=None; blocks=[]
    for line in src.splitlines():
        if line.startswith('    def '):
            if current is not None: blocks.append(current)
            current=[line]
        elif current is not None:
            current.append(line)
    if current is not None: blocks.append(current)
    for block in blocks:
        text='\n'.join(block)
        if ('ORDERED_EVIDENCE_TUPLE' in text or 'composition_operator' in text or 'composition_content_digest_sha256' in text):
            owned_methods.append(block[0].strip())
    return {
        'status':'STOP_SYSTEMATIC_RECOMBINATION_OWNER_MISSING',
        'c08g_xy_available_in_research_helper':c08g['xy_composition_digest_sha256'],
        'c08g_yx_available_in_research_helper':c08g['yx_composition_digest_sha256'],
        'c08g_order_sensitive':c08g['order_sensitive'],
        'production_owned_composition_methods':owned_methods,
        'localized_missing_mechanism':'MICROSEED_OWNED_BOUNDED_ORDERED_COMPOSITION_OPERATOR',
        'new_planner_required':'NO',
        'grammar_authority':'NONE','semantic_authority':'NONE','truth_authority':'NONE','execution_authority':'NONE',
    }
