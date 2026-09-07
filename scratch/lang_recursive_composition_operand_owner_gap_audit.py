from __future__ import annotations

import inspect
from pathlib import Path

import microseed.runtime.entity as entity
from scratch.lang_systematic_heldout_native_b2_recombination import run_campaign

KIND='OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE'


def run_audit() -> dict[str,object]:
    earned=run_campaign('R4','T9')
    assert earned['status']=='BOUNDED_SYSTEMATIC_NATIVE_B2_HELDOUT_RECOMBINATION_EARNED',earned
    src=Path(inspect.getsourcefile(entity.Microseed)).read_text(encoding='utf-8')
    blocks=[]; current=None
    for line in src.splitlines():
        if line.startswith('    def '):
            if current is not None: blocks.append(current)
            current=[line]
        elif current is not None:
            current.append(line)
    if current is not None: blocks.append(current)
    producers=[]; consumers=[]
    for block in blocks:
        text='\n'.join(block)
        if KIND not in text: continue
        signature=block[0].strip()
        # Current owner writes the kind in a payload. A consumer would have to inspect/match
        # the kind or otherwise accept the evidence id/content as an operand in another owner.
        if f'"kind":"{KIND}"' in text or f"'kind':'{KIND}'" in text:
            producers.append(signature)
        if (f'payload.get("kind")=="{KIND}"' in text
                or f'payload.get("kind")!="{KIND}"' in text
                or f'==\"{KIND}\"' in text and 'payload.get' in text):
            consumers.append(signature)
    expected_consumer=('def derive_and_record_current_native_recursive_b2_ordered_composition(',)
    assert tuple(sorted(set(consumers)))==expected_consumer,consumers
    return {
        'status':'CURRENT_RECURSIVE_COMPOSITION_OPERAND_OWNER_PRESENT',
        'earned_b2_head':'80fb18a6922abf663928ab2638a23ca65f702529',
        'b2_evidence_kind':KIND,
        'production_methods_mentioning_exact_b2_kind':tuple(sorted(set(producers+consumers))),
        'production_b2_producers':tuple(sorted(set(producers))),
        'production_b2_consumers':tuple(sorted(set(consumers))),
        'historically_localized_missing_mechanism':'CURRENT_COMPOSITION_AS_GROUNDED_OPERAND_CARRIER_AND_CURRENTNESS_OWNER',
        'bridge_now_embodied':'YES_FIXED_DEPTH_ONE_ONLY',
        'b2_systematicity':'EARNED_BOUNDED',
        'recursive_composition_as_operand':'EARNED_BOUNDED_DEPTH_ONE',
        'arity_generalization':'NOT_EARNED',
        'new_planner_required':'NO_EVIDENCE_FOR_NEW_PLANNER',
        'semantic_authority':'NONE','grammar_authority':'NONE','truth_authority':'NONE','execution_authority':'NONE',
    }
