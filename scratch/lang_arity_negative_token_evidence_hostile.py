from __future__ import annotations

from microseed import EpistemicStatus
from scratch.lang_b3_three_grounded_referents_fixture import fixture,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_arity_generic_prototype import derive_current_bounded_ordered_composition_prototype


def run_hostile() -> dict[str,object]:
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        boot=m._current_runtime_boot_seq()
        for i,t in enumerate(('R4','T9')):
            r=observe_opaque_token(m,t,11000+i,phase='ARITY-NEG-TOKEN');assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
        m.append_evidence(
            'E-ARITY-NEGATIVE-TOKEN-W3',
            {'kind':'OPAQUE_EXTERNAL_TOKEN_OBSERVATION','capture_id':'ARITY-NEG-W3','opaque_token':'W3','runtime_boot_seq':boot,'observation_authority':'OBSERVATION_ONLY'},
            EpistemicStatus.VIOLATED,negative=True,source='HOSTILE-NEGATIVE-EVIDENCE',
        )
        generic=derive_current_bounded_ordered_composition_prototype(m,max_arity=4)
        b3=m.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        # B3 output delimits; re-present T9 positive then W3 negative to attack B2 separately.
        r=observe_opaque_token(m,'T9',11100,phase='ARITY-NEG-B2');assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
        m.append_evidence(
            'E-ARITY-NEGATIVE-TOKEN-W3-B2',
            {'kind':'OPAQUE_EXTERNAL_TOKEN_OBSERVATION','capture_id':'ARITY-NEG-W3-B2','opaque_token':'W3','runtime_boot_seq':boot,'observation_authority':'OBSERVATION_ONLY'},
            EpistemicStatus.VIOLATED,negative=True,source='HOSTILE-NEGATIVE-EVIDENCE',
        )
        b2=m.derive_and_record_current_native_b2_ordered_composition(max_records=32768)
        gv=generic.get('status')=='CURRENT_BOUNDED_ORDERED_COMPOSITION_PROTOTYPE'
        b3v=b3.get('status')=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED'
        b2v=b2.get('status')=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED'
        return {
            'status':'VIOLATION_NEGATIVE_TOKEN_EVIDENCE_ACCEPTED_AS_COMPOSITION_OPERAND' if (gv or b3v or b2v) else 'NEGATIVE_TOKEN_GUARD_PRESENT',
            'generic_status':generic.get('status'),'generic_reason':generic.get('reason'),'generic_accepted_negative':gv,
            'b3_status':b3.get('status'),'b3_reason':b3.get('reason'),'b3_accepted_negative':b3v,
            'b2_status':b2.get('status'),'b2_reason':b2.get('reason'),'b2_accepted_negative':b2v,
            'negative_token_must_be_operand_authority':'NO',
            'arity_promotion_allowed':'NO',
        }
    finally:
        _close(m);td.cleanup()
