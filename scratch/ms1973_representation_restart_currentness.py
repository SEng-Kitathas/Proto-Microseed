from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, EpistemicStatus, ExternalProjectionQualifier,
    Microseed, OperationalFrameContract, QualificationState,
)
from scratch.ms1972_process_backed_representation_alias_growth import (
    AliasWorld, build, prepare_proposals, run_chain, external_holdout,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _first_life(root: Path):
    world=AliasWorld(); m=build(root,world)
    try:
        proposals=prepare_proposals(m)
        for context in ('s0','s0','r','r'):
            run_chain(m,world,proposals,context,len(m.action_closure.outcomes))
        surface=m.derive_admitted_one_step_visible_history_refinements()
        target=[c for c in surface.get('refinements',()) if (c.start_token,c.action_token)==('s1','B')]
        assert len(target)==1,target
        c=target[0]
        heldout=external_holdout(c)
        qe=m.append_evidence(
            'Q-MS1973-EXTERNAL-HOLDOUT',
            {'kind':'PROCESS_ALIAS_REFINEMENT_HOLDOUT','candidate_sha256':c.digest(),'rows':heldout},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source='EXTERNAL-PROCESS-MS1973-QUALIFIER',
        )
        ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-PROCESS-MS1973').qualify(c,qualification_evidence=(qe,))
        rec=m.admit_one_step_visible_history_refinement_projection(ticket,projection_id='P-MS1973')
        assert rec.current
        return c.digest(),ticket
    finally:
        _close(m); world.close()


def _attach_incompatible_runtime(m: Microseed, world: AliasWorld):
    # Same action/observation contracts as MS1972, but the same frame id/epoch is
    # rebound to different content. This isolates the exact frame-signature guard.
    m.register_operational_frame(OperationalFrameContract(
        'F','process-backed alias frame','0'*64,Authority.DERIVED_READ_ONLY,('MS1973-HOSTILE',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    for cid in ('PREP','B'):
        m.register_capability(CapabilityContract(
            cid,'opaque process effect',{}, {'output':'opaque-receipt'},('WORLD_EFFECT != WORLD_MODEL',),(),Authority.EFFECT,
            ('MS1972',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _cid=cid,**_:world.apply(_cid),operational_scope_id='S',
            assistance_ancestry=('EXTERNAL_PROCESS_EFFECT_CAPABILITY',)
        ))
    m.register_capability(CapabilityContract(
        'OBS','process observation',{}, {'output':'opaque-state'},('OBSERVATION != TRUTH_AUTHORITY',),(),Authority.OBSERVATION_ONLY,
        ('MS1972',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:world.observe(),operational_scope_id='S'
    ))
    m.register_capability(CapabilityContract(
        'BASIS','bounded observation basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,
        ('MS1972',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='S'
    ))
    for cid in ('PREP','B','OBS'): m.frames.bind_capability('F',cid)


def run_ms1973():
    td=tempfile.TemporaryDirectory(prefix='ms1973-restart-refinement-'); root=Path(td.name)
    try:
        digest,ticket=_first_life(root)

        # Restart with no live world/frame/capability attachment.
        m2=Microseed(root)
        try:
            rec=m2.epistemic_projections.records['P-MS1973']
            no_attach=m2.derive_admitted_one_step_visible_history_refinements()
            assert rec.signature_sha256==digest
            assert no_attach['status']=='NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT',no_attach
            assert not no_attach['refinements']
            rejected={reason for _,reason in no_attach['rejected_execution_reasons']}
            assert rejected & {'ACTION_CAPABILITY_NOT_CURRENT_FOR_RELATIONAL_SAMPLE','OPERATIONAL_FRAME_NOT_CURRENT','LIVE_OBSERVATION_ADMISSION_NOT_CURRENT'},rejected
            admission_error=None
            try:m2.admit_one_step_visible_history_refinement_projection(ticket,projection_id='P-MS1973-ILLEGAL')
            except Exception as exc: admission_error=f'{type(exc).__name__}:{exc}'
            assert admission_error and 'CURRENT_HISTORY_REFINEMENT_FOR_TICKET_NOT_FOUND' in admission_error
            no_attach_result={
                'persisted_projection_record_present':True,
                'projection_record_current_flag':rec.current,
                'derived_surface_status':no_attach['status'],
                'admission_error':admission_error,
                'rejected_reasons':sorted(rejected),
            }
        finally:_close(m2)

        # Same id/epoch but incompatible frame content must not make old history usable.
        world3=AliasWorld(); m3=Microseed(root)
        try:
            _attach_incompatible_runtime(m3,world3)
            hostile=m3.derive_admitted_one_step_visible_history_refinements()
            assert hostile['status']=='NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT',hostile
            reasons={reason for _,reason in hostile['rejected_execution_reasons']}
            assert reasons=={'OPERATIONAL_FRAME_CONTENT_DRIFT'},reasons
            incompatible_result={'derived_surface_status':hostile['status'],'rejected_reasons':sorted(reasons)}
        finally:
            _close(m3); world3.close()

        # Fresh compatible world attachment reconstructs the exact content from durable owned history.
        world4=AliasWorld(); m4=build(root,world4)
        try:
            recovered=m4.derive_admitted_one_step_visible_history_refinements()
            assert recovered['status']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENTS_FOUND',recovered
            matches=[c for c in recovered['refinements'] if c.digest()==digest]
            assert len(matches)==1,matches
            c=matches[0]
            assert set(c.context_outcomes)=={('s0','sx',2),('r','s2',2)}
            rec=m4.epistemic_projections.records['P-MS1973']
            assert rec.signature_sha256==c.digest()
            compatible_result={
                'derived_surface_status':recovered['status'],
                'candidate_sha256':c.digest(),
                'context_outcomes':c.context_outcomes,
                'persisted_projection_signature_matches_rederived_content':True,
                'projection_record_current_flag':rec.current,
            }
        finally:
            _close(m4); world4.close()

        return {
            'status':'PASS',
            'no_attachment':no_attach_result,
            'incompatible_same_id_frame':incompatible_result,
            'compatible_reattachment':compatible_result,
            'earned':'PERSISTED_HISTORY_REFINEMENT_RECORD_DOES_NOT_RESTORE_USABLE_REPRESENTATION_WITHOUT_CURRENT_EXACT_PREMISES_AND_COMPATIBLE_REATTACHMENT_REDERIVES_THE_SAME_OPAQUE_CONTENT',
            'registry_current_flag_authority':'INSUFFICIENT_ALONE',
            'semantic_category_authority':'NONE','hidden_state_authority':'NONE','language_authority':'NONE',
        }
    finally:td.cleanup()


def main(): print(json.dumps(run_ms1973(),indent=2,sort_keys=True,default=str))
if __name__=='__main__': main()
