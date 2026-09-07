from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Microseed
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.ms2014_endogenous_referent_opportunity_enumeration import _base_fixture
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()


def _one(token: str) -> dict[str, object]:
    td,m,*_=_base_fixture()
    try:
        tok=observe_opaque_token(m,token,9100,phase='ACTIVE-ACQ-NEW-PAIR-AUDIT')
        assert tok['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',tok
        harvest=m.harvest_current_opaque_evidence_association_pairs(max_records=16384)
        assert harvest['status']=='DEFER_UNKNOWN',harvest
        assert harvest['reason']=='NO_CURRENT_NATIVE_OPAQUE_ASSOCIATION_PAIR_HARVESTED',harvest
        unpaired=tuple(x for x in harvest.get('unpaired_tokens',()) if x.get('token_evidence_id')==tok['evidence_id'])
        assert len(unpaired)==1,harvest
        surface=m.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
        assert surface['status']=='CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY',surface
        op=surface['opportunities'][0]
        internal=next(
            x for x in m._current_owned_referent_epistemic_opportunities(act_ob())
            if str(x['content_signature_sha256'])==str(op['content_signature_sha256'])
        )
        # Inspect both the public packet and the internal load-bearing carriers.
        carriers='\n'.join((
            str(op),
            str(internal['deficit'].serializable()),
            str(internal['trial'].serializable()),
            str(vars(internal['decision_context'])),
            str(internal['priority'].serializable()),
            str(internal['trace_information'].serializable()),
            str(internal['contrast_information'].serializable()),
            str(internal['commitment'].serializable()),
            str(internal['consequence']),
        ))
        return {
            'opaque_token':token,
            'token_evidence_id':tok['evidence_id'],
            'unpaired_reason':unpaired[0]['reason'],
            'opportunity_status':surface['status'],
            'probe_action_id':op['probe_action_id'],
            'opportunity_content_signature_sha256':op['content_signature_sha256'],
            'deficit_id':str(op['deficit_id']),
            'trial_id':internal['trial'].trial_id,
            'token_value_present_in_opportunity_carriers':token in carriers,
            'token_evidence_present_in_opportunity_carriers':tok['evidence_id'] in carriers,
            'caller_supplied_binding_or_deficit':'NO',
        }
    finally:
        _close(m,td)


def run_campaign() -> dict[str, object]:
    a=_one('OPAQUE-NEW-TOKEN-A')
    b=_one('OPAQUE-NEW-TOKEN-B')
    assert a['unpaired_reason']==b['unpaired_reason']=='NO_CURRENT_SUPPORTED_PAIR_SOURCE_SINCE_PREVIOUS_TOKEN'
    assert a['probe_action_id']==b['probe_action_id']=='P2'
    assert a['opportunity_content_signature_sha256']==b['opportunity_content_signature_sha256']
    assert a['deficit_id']==b['deficit_id'] and a['trial_id']==b['trial_id']
    assert not a['token_value_present_in_opportunity_carriers'] and not b['token_value_present_in_opportunity_carriers']
    assert not a['token_evidence_present_in_opportunity_carriers'] and not b['token_evidence_present_in_opportunity_carriers']
    return {
        'status':'STOP_NEW_PAIR_ACTIVE_ACQUISITION_NOT_TOKEN_CONDITIONED',
        'token_a':a,'token_b':b,
        'generic_probe_action_id':'P2',
        'generic_opportunity_invariant_to_token_identity':'YES',
        'token_specific_information_bearing_premise':'ABSENT',
        'active_localization_alone_would_establish_new_pair':'NO',
        'localized_missing_mechanism':'TOKEN_CONDITIONED_GROUNDED_ACQUISITION_RELEVANCE_OR_ENVIRONMENTAL_COUPLING',
        'new_pair_registration_authority':'NONE',
        'effect_authority_from_unknown_token':'NONE',
    }
