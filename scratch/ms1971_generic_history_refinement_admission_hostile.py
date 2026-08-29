from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus, ExternalProjectionQualifier
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1858_pass11_live_second_step_challenge_participates_in_owned_history_refinement import _install, _add_history_pair


def run_hostile():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        outcomes={}; _install(m,outcomes)
        # Earn two recurrent previous-visible contexts for the same current s1/B slot
        # without creating a REVISIT_REQUIRED model-space challenge.
        _add_history_pair(m,outcomes,0,'s0','sx')
        _add_history_pair(m,outcomes,1,'s0','sx')
        _add_history_pair(m,outcomes,2,'r','s2')
        _add_history_pair(m,outcomes,3,'r','s2')

        surface=m.derive_admitted_one_step_visible_history_refinements()
        assert surface['status']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENTS_FOUND',surface
        target=[c for c in surface['refinements'] if (c.start_token,c.action_token)==('s1','B')]
        assert len(target)==1,target
        c=target[0]
        assert set(c.context_outcomes)=={('s0','sx',2),('r','s2',2)}

        q=m.append_evidence(
            'Q-MS1971-REFINEMENT',
            {'kind':'REFINEMENT_HOLDOUT','candidate_sha256':c.digest(),'heldout':'supported'},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source='EXTERNAL-MS1971-QUALIFIER',
        )
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1971-PROJECTION').qualify(
            c, qualification_evidence=(q,)
        )
        assert ticket.candidate_id==c.candidate_id
        assert ticket.candidate_sha256==c.digest()

        # The only endogenous history-refinement admission route is revisit-scoped.
        revisit_error=None
        try:
            m.admit_revisit_one_step_visible_history_refinement_projection('D',ticket,projection_id='P-MS1971-REVISIT')
        except Exception as exc:
            revisit_error=f'{type(exc).__name__}:{exc}'
        assert revisit_error is not None

        # A generic supplied projection route exists, but using it here would lie about
        # provenance: the coordinate was derived by Microseed from owned history.
        supplied_only_doc='Register one supplied opaque evidence coordinate; never discover one.' in (m.register_epistemic_projection.__doc__ or '')
        assert supplied_only_doc

        generic_method_present=hasattr(m,'admit_one_step_visible_history_refinement_projection')
        if not generic_method_present:
            return {
                'status':'SCOPING_GAP_CONFIRMED',
                'candidate_id':c.candidate_id,
                'candidate_sha256':c.digest(),
                'context_outcomes':c.context_outcomes,
                'external_ticket_state':ticket.state.value,
                'revisit_route_error':revisit_error,
                'generic_endogenous_admission_method_present':False,
                'supplied_registry_route_is_explicitly_supplied_only':supplied_only_doc,
                'earned':'HISTORY_REFINEMENT_DERIVATION_AND_EXTERNAL_QUALIFICATION_EXIST_BUT_GENERIC_ENDOGENOUS_PROJECTION_ADMISSION_IS_ARTIFICIALLY_REVISIT_SCOPED',
                'missing_mechanism':'NO_NEW_REPRESENTATION_DISCOVERY_MECHANISM_DEMONSTRATED',
                'missing_embodiment_route':'GENERIC_CURRENT_EXTERNALLY_QUALIFIED_ENDOGENOUS_REFINEMENT_ADMISSION',
                'truth_authority':'NONE','hidden_state_authority':'NONE','semantic_category_authority':'NONE',
            }

        rec=m.admit_one_step_visible_history_refinement_projection(ticket,projection_id='P-MS1971-GENERIC')
        assert rec.current
        assert rec.signature_sha256==c.digest()
        assert rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'
        assert rec.proposal_candidate_sha256==c.digest()
        assert 'ONE_STEP_VISIBLE_HISTORY_REFINEMENT' in rec.assistance_ancestry
        assert all('DEFICIT:' not in x for x in rec.assistance_ancestry)
        event=[e['payload'] for e in m.store.events() if e['kind']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENT_PROJECTION_ADMITTED' and e['payload']['projection_id']=='P-MS1971-GENERIC']
        assert len(event)==1
        assert event[0]['truth_authority']==event[0]['hidden_state_authority']==event[0]['semantic_category_authority']=='NONE'
        return {
            'status':'GENERIC_ADMISSION_COMPOSED',
            'candidate_id':c.candidate_id,'candidate_sha256':c.digest(),'context_outcomes':c.context_outcomes,
            'external_ticket_state':ticket.state.value,'revisit_route_error':revisit_error,
            'generic_endogenous_admission_method_present':True,
            'projection':rec.serializable(),
            'admission_event':event[0],
            'supplied_registry_route_is_explicitly_supplied_only':supplied_only_doc,
            'earned':'OWNED_HISTORY_DERIVED_REFINEMENT_CAN_BE_EXTERNALLY_QUALIFIED_AND_GENERically_ADMITTED_AS_OPAQUE_CURRENT_PROJECTION_WITHOUT_REVISIT_OR_SEMANTIC_AUTHORITY',
            'new_discovery_mechanism_added':'NO',
            'truth_authority':'NONE','hidden_state_authority':'NONE','semantic_category_authority':'NONE',
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def main(): print(json.dumps(run_hostile(),indent=2,sort_keys=True,default=str))
if __name__=='__main__': main()
