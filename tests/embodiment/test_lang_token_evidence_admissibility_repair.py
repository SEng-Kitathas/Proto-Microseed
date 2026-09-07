from microseed import EpistemicStatus
from scratch.lang_b3_three_grounded_referents_fixture import fixture,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_arity_generic_prototype import derive_current_bounded_ordered_composition_prototype


def _present_two(m,phase,base):
    for i,t in enumerate(('R4','T9')):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def test_violated_disposition_without_negative_flag_is_not_an_admitted_token_operand():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        _present_two(m,'ARITY-FORGE-DISPOSITION',12100)
        m.append_evidence('E-ARITY-FORGE-DISPOSITION-W3',{
            'kind':'OPAQUE_EXTERNAL_TOKEN_OBSERVATION','capture_id':'FORGE-DISPOSITION','opaque_token':'W3',
            'runtime_boot_seq':m._current_runtime_boot_seq(),'observation_authority':'OBSERVATION_ONLY',
        },EpistemicStatus.VIOLATED,negative=False,source='HOSTILE-FORGE')
        g=derive_current_bounded_ordered_composition_prototype(m);b3=m.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert g['status']==b3['status']=='DEFER_UNKNOWN'
        assert g['reason']==b3['reason']=='TOKEN_EVIDENCE_DISPOSITION_NOT_ADMITTED'
    finally:
        _close(m);td.cleanup()


def test_non_observation_authority_token_kind_row_is_not_an_admitted_token_operand():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        _present_two(m,'ARITY-FORGE-AUTHORITY',12200)
        m.append_evidence('E-ARITY-FORGE-AUTHORITY-W3',{
            'kind':'OPAQUE_EXTERNAL_TOKEN_OBSERVATION','capture_id':'FORGE-AUTHORITY','opaque_token':'W3',
            'runtime_boot_seq':m._current_runtime_boot_seq(),'observation_authority':'EFFECT',
        },EpistemicStatus.PRESSURE_SUPPORTED,negative=False,source='HOSTILE-FORGE')
        g=derive_current_bounded_ordered_composition_prototype(m);b3=m.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert g['status']==b3['status']=='DEFER_UNKNOWN'
        assert g['reason']==b3['reason']=='TOKEN_EVIDENCE_OBSERVATION_AUTHORITY_REQUIRED'
    finally:
        _close(m);td.cleanup()
