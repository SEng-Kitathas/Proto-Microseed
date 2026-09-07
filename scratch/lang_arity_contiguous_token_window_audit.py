from __future__ import annotations

from microseed import EpistemicStatus
from scratch.lang_b3_three_grounded_referents_fixture import fixture,_close
from scratch.lang_distinct_leaf_b3_ordered_composition import _observe_sequence

KIND='OPAQUE_EXTERNAL_TOKEN_OBSERVATION'

def suffix(ms):
    boot=ms._current_runtime_boot_seq(); rows=ms.evidence.list(); out=[]
    for pos in range(len(rows)-1,-1,-1):
        row=rows[pos]; payload=row.get('payload') or {}
        if payload.get('kind')!=KIND or int(payload.get('runtime_boot_seq',-1))!=boot:
            break
        out.append((pos,row))
    return tuple(reversed(out))


def run_audit() -> dict[str,object]:
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        # Existing grounding/qualification history is non-token-delimited. New contiguous presentation owns a clean suffix.
        _observe_sequence(m,('R4','T9','W3'),phase='ARITY-SUFFIX-3',base=8000)
        s3=suffix(m)
        assert tuple((r.get('payload') or {}).get('opaque_token') for _,r in s3)==('R4','T9','W3')
        # Existing B3 output is a represented non-token event and therefore closes that run.
        b3=m.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert b3['status']=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',b3
        assert suffix(m)==()
        # A fresh B2-style run is independently visible without caller arity.
        _observe_sequence(m,('R4','T9'),phase='ARITY-SUFFIX-2',base=8100)
        s2=suffix(m)
        assert tuple((r.get('payload') or {}).get('opaque_token') for _,r in s2)==('R4','T9')
        # Represented unrelated evidence is an actual ledger boundary, not an invisible pause.
        m.append_evidence('E-ARITY-BOUNDARY',{
            'kind':'HOSTILE_UNRELATED_CURRENT_EVIDENCE',
            'runtime_boot_seq':m._current_runtime_boot_seq(),
            'observation_authority':'OBSERVATION_ONLY',
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-WORLD')
        _observe_sequence(m,('W3',),phase='ARITY-SUFFIX-BOUNDARY',base=8200)
        s1=suffix(m)
        assert tuple((r.get('payload') or {}).get('opaque_token') for _,r in s1)==('W3',)
        # A contiguous overlong run is represented exactly; a bounded generalized owner must reject, never silently crop.
        m.append_evidence('E-ARITY-BOUNDARY-2',{
            'kind':'HOSTILE_UNRELATED_CURRENT_EVIDENCE',
            'runtime_boot_seq':m._current_runtime_boot_seq(),
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-WORLD')
        _observe_sequence(m,('R4','T9','W3','R4','T9'),phase='ARITY-SUFFIX-5',base=8300)
        s5=suffix(m)
        assert len(s5)==5
        return {
            'status':'CONTIGUOUS_CURRENT_TOKEN_SUFFIX_IS_BOUNDED_ARITY_CARRIER_CANDIDATE',
            'suffix_after_xyz':3,
            'suffix_after_composition_evidence':0,
            'suffix_after_two_tokens':2,
            'suffix_after_represented_boundary_plus_one_token':1,
            'suffix_after_overlong_run':5,
            'represented_non_token_boundary_closes_window':'YES',
            'unrepresented_pause_creates_boundary':'NO',
            'silent_truncation_allowed':'NO',
            'candidate_rule':'EXACT_CONTIGUOUS_CURRENT_RUNTIME_TOKEN_SUFFIX_LENGTH',
            'candidate_bounds':'2_TO_EXPLICIT_MAX_ONLY',
            'semantic_grouping_authority':'NONE',
            'next_hostile':'prove same rule reproduces B2+B3 identities and fails closed for 1/>max before held-out arity4',
        }
    finally:
        _close(m);td.cleanup()
