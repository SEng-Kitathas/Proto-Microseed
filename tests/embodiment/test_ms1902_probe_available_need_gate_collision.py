from microseed import EpistemicStatus
from microseed.development.epistemic_action import derive_epistemic_program_step_local_precheck
from microseed.development.epistemic_program import EpistemicProgramTrial
from microseed.development.recruitment import RecruitmentOption
from microseed.runtime.types import FeasibilityState
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()


def test_bound_single_probe_crosses_need_gate_only_with_independent_program_satisfaction():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c);m.accept_revisit_hypothesis_revision('D',b.binding_id)
        fresh=m.append_evidence('E-U-1902',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
        m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1902',unknown_evidence_id=fresh.evidence_id)
        bound=m.bind_current_revised_surface_direct_probe(old_deficit_id='D',successor_deficit_id='D-1902')
        assert bound['status']=='PROBE_AVAILABLE'
        formed=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1902',obligation=act_ob())
        assert formed['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
        trial=formed['trial']; sat=m.derive_current_program_discriminator_satisfaction(trial)
        assert sat.licenses_yes(),sat.serializable()
        cmt=derive_epistemic_program_step_local_precheck(
            trial=trial,deficit=m.epistemic_deficits.records['D-1902'],
            feasibility=RecruitmentOption('B',FeasibilityState.FEASIBLE),capabilities=m.capabilities,
            obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),current_state=m.action_closure.current_state,
            program_discriminator_satisfaction=sat,
        )
        assert cmt.reason=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_ALL_LICENSED',cmt.serializable()
        assert cmt.commitment.value=='YES'
    finally:_close(m,td)


def _trial(m,s,steps,disc=None,epochs=None):
    caps=tuple((cid,m.capabilities.epochs[cid]) for cid in steps) if epochs is None else tuple(epochs)
    sigs=tuple((cid,m.capabilities.contracts[cid].computed_signature_sha256()) for cid in steps)
    return EpistemicProgramTrial(
        trial_id='T-NEG-'+'-'.join(steps),deficit_id='D-1902',
        discrimination_signature_sha256=s.missing_discriminator_signature_sha256 if disc is None else disc,
        relation_candidate_id='R-NEG',relation_candidate_sha256='b'*64,steps=tuple(steps),
        capability_epochs=caps,capability_signatures=sigs,frame_epochs=tuple(),obligation_id='Q',operational_scope_id='S',
        start_state_id=m.action_closure.current_state.state_id,start_state_evidence_id=m.action_closure.current_state.evidence_id,
    )

def _bound_fixture():
    td,m,calls,c=_qualified_refinement_fixture();b=_qualify_revised_surface(m,c);m.accept_revisit_hypothesis_revision('D',b.binding_id)
    fresh=m.append_evidence('E-U-1902-N',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
    s=m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1902',unknown_evidence_id=fresh.evidence_id)
    assert m.bind_current_revised_surface_direct_probe(old_deficit_id='D',successor_deficit_id='D-1902')['status']=='PROBE_AVAILABLE'
    return td,m,calls,s

def _commit(m,s,t):
    return derive_epistemic_program_step_local_precheck(
        trial=t,deficit=m.epistemic_deficits.records['D-1902'],
        feasibility=RecruitmentOption(t.steps[0],FeasibilityState.FEASIBLE),capabilities=m.capabilities,
        obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),current_state=m.action_closure.current_state,
    )

def test_probe_available_does_not_license_wrong_primitive():
    td,m,calls,s=_bound_fixture()
    try:
        cmt=_commit(m,s,_trial(m,s,('A',)))
        assert cmt.commitment.value=='UNKNOWN' and cmt.reason=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_UNRESOLVED'
    finally:_close(m,td)

def test_probe_available_does_not_license_multi_step_program():
    td,m,calls,s=_bound_fixture()
    try:
        cmt=_commit(m,s,_trial(m,s,('B','A')))
        assert cmt.commitment.value=='UNKNOWN' and cmt.reason=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_UNRESOLVED'
    finally:_close(m,td)

def test_probe_available_does_not_license_wrong_discriminator():
    td,m,calls,s=_bound_fixture()
    try:
        cmt=_commit(m,s,_trial(m,s,('B',),disc='f'*64))
        assert cmt.commitment.value=='UNKNOWN' and cmt.reason=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_UNRESOLVED'
    finally:_close(m,td)

def test_probe_available_does_not_license_stale_bound_epoch():
    td,m,calls,s=_bound_fixture()
    try:
        t=_trial(m,s,('B',),epochs=(('B',m.capabilities.epochs['B']+1),))
        cmt=_commit(m,s,t)
        assert cmt.commitment.value=='UNKNOWN' and cmt.reason=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_UNRESOLVED'
    finally:_close(m,td)
