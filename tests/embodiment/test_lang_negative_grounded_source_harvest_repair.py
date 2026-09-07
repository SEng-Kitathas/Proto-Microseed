from microseed import EpistemicStatus
from scratch.lang_b3_three_grounded_referents_fixture import fixture,_close
from scratch.lang_c08c_native_owned_affordance_relation import _external_control_state,_raw
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def test_negative_grounded_localization_candidate_is_not_selected_as_native_pair_source():
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        world.set_passive_baseline(0,0,0)
        _external_control_state(m,'NEG-SOURCE-PRE');_raw(m,'NEG-SOURCE-PRE')
        world.bump('X')
        _external_control_state(m,'NEG-SOURCE-POST');_raw(m,'NEG-SOURCE-POST')
        loc=m.derive_and_record_current_owned_passive_operational_referent_localization(max_events=65536,max_records=65536)
        assert loc['status']=='CURRENT_OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZED',loc
        rows=m.evidence.list()
        positives=[row for row in rows if (row.get('payload') or {}).get('kind')=='OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZATION_WITNESS' and not row.get('negative')]
        assert positives
        positive=positives[-1]
        fake_id='E-NEGATIVE-GROUNDED-LOCALIZATION-CANDIDATE'
        m.append_evidence(fake_id,dict(positive['payload']),EpistemicStatus.VIOLATED,negative=True,source='HOSTILE-NEGATIVE-GROUNDED-SOURCE')
        tok=observe_opaque_token(m,'R4',12300,phase='NEG-SOURCE-HARVEST');assert tok['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',tok
        harvested=m.harvest_current_opaque_evidence_association_pairs(max_records=65536)
        matches=[row for row in harvested['harvested_pairs'] if row.get('token_evidence_id')==tok['evidence_id']]
        assert len(matches)==1,matches
        assert matches[0]['pair_source_evidence_id']==positive['evidence_id']
        assert matches[0]['pair_source_evidence_id']!=fake_id
    finally:
        _close(m);td.cleanup()
