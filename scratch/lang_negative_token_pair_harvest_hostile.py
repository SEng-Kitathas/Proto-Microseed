from __future__ import annotations

from microseed import EpistemicStatus
from scratch.lang_b3_three_grounded_referents_fixture import fixture,_close
from scratch.lang_c08c_native_owned_affordance_relation import _external_control_state,_raw


def run_hostile() -> dict[str,object]:
    td,m,world,seeded=fixture(tokens=('R4','T9','W3'))
    try:
        world.set_passive_baseline(0,0,0)
        _external_control_state(m,'NEG-HARVEST-PRE');_raw(m,'NEG-HARVEST-PRE')
        world.bump('X')
        _external_control_state(m,'NEG-HARVEST-POST');_raw(m,'NEG-HARVEST-POST')
        loc=m.derive_and_record_current_owned_passive_operational_referent_localization(max_events=65536,max_records=65536)
        assert loc['status']=='CURRENT_OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZED',loc
        eid='E-NEG-HARVEST-TOKEN-R4';boot=m._current_runtime_boot_seq()
        m.append_evidence(eid,{
            'kind':'OPAQUE_EXTERNAL_TOKEN_OBSERVATION','capture_id':'NEG-HARVEST','opaque_token':'R4',
            'runtime_boot_seq':boot,'observation_authority':'OBSERVATION_ONLY',
        },EpistemicStatus.VIOLATED,negative=True,source='HOSTILE-NEGATIVE-EVIDENCE')
        harvested=m.harvest_current_opaque_evidence_association_pairs(max_records=65536)
        assert harvested['status']=='CURRENT_NATIVE_OPAQUE_ASSOCIATION_PAIRS_HARVESTED',harvested
        contaminated=tuple(row for row in harvested['harvested_pairs'] if row.get('token_evidence_id')==eid)
        violation=bool(contaminated)
        negative_unpaired=tuple(row for row in harvested['unpaired_tokens'] if row.get('token_evidence_id')==eid)
        return {
            'status':'VIOLATION_NEGATIVE_TOKEN_EVIDENCE_HARVESTED_AS_NATIVE_PAIR' if violation else 'NEGATIVE_TOKEN_HARVEST_GUARD_PRESENT',
            'negative_token_evidence_id':eid,
            'contaminated_pair_count':len(contaminated),
            'contaminated_pairs':contaminated,
            'negative_token_became_pair_source':violation,
            'negative_unpaired':negative_unpaired,
            'qualification_authority_from_negative_token':'NONE',
            'repair_scope':'TOKEN_EVIDENCE_ADMISSIBILITY_OWNER_SHARED_BY_HARVEST_AND_COMPOSITION',
        }
    finally:
        _close(m);td.cleanup()
