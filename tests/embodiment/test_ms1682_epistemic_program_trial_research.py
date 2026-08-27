import hashlib
from dataclasses import replace
from microseed import Authority, CapabilityContract, QualificationState, QueryObligation, OpaqueTransitionSample, discover_opaque_action_composition_candidates
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord, ActionOutcomeRecord
from microseed.development.epistemic_program import begin_epistemic_program_trial, advance_epistemic_program_trial, completed_program_evidence_payload
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment

def cap(cid,calls=None):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1682',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid, **_: (calls.append(_cid) if calls is not None else None),operational_scope_id='S')
def row(i,s,a,e,o):return OpaqueTransitionSample(i,o,s,a,e,'F',0)
def candidate():
    rs=[row('a0','s0','A','m0','oa0'),row('b0','m0','B','e0','ob0'),row('c0','s0','C','e0','oc0'),row('a1','s1','A','m1','oa1'),row('b1','m1','B','e1','ob1'),row('c1','s1','C','e1','oc1')]
    return [c for c in discover_opaque_action_composition_candidates(rs,min_positive_support=2) if (c.direct_action_token,c.first_action_token,c.second_action_token)==('C','A','B')][0]
def registry(calls=None):
    r=CapabilityRegistry();r.register(cap('A',calls));r.register(cap('B',calls));return r
def obligation():return QueryObligation('Q','probe',required_authority=Authority.EFFECT,operational_scope_id='S')
def intent(cid,idx=0,state_evidence=None):
    c=RelationalCommitment(f'cm{idx}',f't{idx}',TernaryCommitment.YES)
    return BoundedActionIntent(f'i{idx}',f'p{idx}',f'd{idx}',c,cid,0,f's{idx}',state_evidence or f'ce{idx}',f's{idx+1}',0.0,('V',0),'Q','S')
def execution(cid,idx=0):return ActionExecutionRecord(f'x{idx}',f'i{idx}',cid,0,f's{idx}','h')
def outcome(idx=0):
    c=RelationalCommitment(f'pc{idx}',f'pt{idx}',TernaryCommitment.YES)
    return ActionOutcomeRecord(f'o{idx}',f'x{idx}',f'e{idx}',f's{idx+1}',float(idx),'V',c,actual_value_effect=0.0)

def begin(r=None,calls=None):return begin_epistemic_program_trial(candidate(),deficit_id='D',discrimination_signature_sha256=hashlib.sha256(b'd').hexdigest(),capabilities=r or registry(calls),obligation=obligation(),current_frame_epochs={'F':0},start_state_id='s0',start_state_evidence_id='ce0')
def test_begin_binds_existing_components_without_invoking_handlers():
    calls=[];r=registry(calls);t=begin(r,calls);assert t.steps==('A','B') and calls==[] and t.execution_authority==t.truth_authority=='NONE'
def test_symbolic_action_is_not_created():
    r=registry();c=replace(candidate(),first_action_token='A_then_B')
    try: begin_epistemic_program_trial(c,deficit_id='D',discrimination_signature_sha256=hashlib.sha256(b'd').hexdigest(),capabilities=r,obligation=obligation(),current_frame_epochs={'F':0},start_state_id='s0',start_state_evidence_id='ce0'); assert False
    except ValueError as e: assert 'NO_PATH:A_then_B' in str(e)
def test_stale_component_blocks_begin():
    r=registry();r.invalidate('B')
    try: begin(r); assert False
    except ValueError as e: assert 'CAPABILITY_NOT_CURRENT:B' in str(e)
def test_two_different_step_proposals_bind_into_one_trial():
    r=registry();t=begin(r);t=advance_epistemic_program_trial(t,intent=intent('A',0),execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0});assert t.status=='OPEN'
    t=advance_epistemic_program_trial(t,intent=intent('B',1,'e0'),execution=execution('B',1),outcome=outcome(1),capabilities=r,current_frame_epochs={'F':0});assert t.status=='COMPLETE' and len(t.step_records)==2
    p=completed_program_evidence_payload(t);assert p['truth_authority']==p['physical_actuator_identity_authority']=='NONE'
def test_wrong_redeliberated_action_invalidates_trial():
    r=registry();r.register(cap('C'));t=begin(r);t=advance_epistemic_program_trial(t,intent=intent('C',0),execution=execution('C',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0});assert t.status=='INVALID' and 'PROGRAM_STEP_DEVIATION' in t.invalid_reason
def test_component_drift_between_steps_invalidates_trial():
    r=registry();t=begin(r);t=advance_epistemic_program_trial(t,intent=intent('A',0),execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0});r.change_dependency('B')
    t=advance_epistemic_program_trial(t,intent=intent('B',1,'e0'),execution=execution('B',1),outcome=outcome(1),capabilities=r,current_frame_epochs={'F':0});assert t.status=='INVALID' and 'PROGRAM_COMPONENT_NOT_CURRENT:B' in t.invalid_reason
def test_frame_drift_between_steps_invalidates_trial():
    r=registry();t=begin(r);t=advance_epistemic_program_trial(t,intent=intent('A',0),execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0})
    t=advance_epistemic_program_trial(t,intent=intent('B',1,'e0'),execution=execution('B',1),outcome=outcome(1),capabilities=r,current_frame_epochs={'F':1});assert t.status=='INVALID' and 'PROGRAM_FRAME_DRIFT:F' in t.invalid_reason
def test_replayed_execution_or_evidence_invalidates():
    r=registry();t=begin(r);t=advance_epistemic_program_trial(t,intent=intent('A',0),execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0})
    # Expected B but replayed A record: fails before replay can manufacture progress.
    t=advance_epistemic_program_trial(t,intent=intent('B',1),execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0});assert t.status=='INVALID'
def test_completed_evidence_carries_no_authority_gain():
    r=registry();t=begin(r);t=advance_epistemic_program_trial(t,intent=intent('A',0),execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0});t=advance_epistemic_program_trial(t,intent=intent('B',1,'e0'),execution=execution('B',1),outcome=outcome(1),capabilities=r,current_frame_epochs={'F':0});p=completed_program_evidence_payload(t);assert p['execution_authority_gain']==p['qualification_authority']=='NONE'

def test_wrong_start_state_evidence_invalidates_even_with_correct_action():
    r=registry();t=begin(r)
    bad=intent('A',0,state_evidence='different-evidence')
    t=advance_epistemic_program_trial(t,intent=bad,execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0})
    assert t.status=='INVALID' and t.invalid_reason=='PROGRAM_CONTROL_STATE_CONTINUITY_VIOLATION'

def test_wrong_obligation_or_scope_invalidates_trial_step():
    r=registry();t=begin(r);x=intent('A',0);x=replace(x,obligation_id='OTHER')
    t=advance_epistemic_program_trial(t,intent=x,execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0})
    assert t.status=='INVALID' and t.invalid_reason=='PROGRAM_STEP_OBLIGATION_OR_SCOPE_DRIFT'

def test_capability_content_signature_drift_blocks_use_even_if_epoch_is_forged_unchanged():
    r=registry();t=begin(r);r.contracts['B'].purpose='changed-content'
    t=advance_epistemic_program_trial(t,intent=intent('A',0),execution=execution('A',0),outcome=outcome(0),capabilities=r,current_frame_epochs={'F':0})
    assert t.status=='INVALID' and t.invalid_reason=='PROGRAM_COMPONENT_DRIFT:B'

def test_begin_rejects_non_effect_component():
    r=registry();r.contracts['B'].authority=Authority.DERIVED_READ_ONLY
    try: begin(r); assert False
    except ValueError as e: assert 'CAPABILITY_NOT_EFFECT_AUTHORIZED:B' in str(e)

def test_incomplete_trial_cannot_emit_epistemic_program_evidence():
    t=begin()
    try: completed_program_evidence_payload(t); assert False
    except ValueError as e: assert 'PROGRAM_TRIAL_NOT_COMPLETE' in str(e)


def test_program_trial_object_rejects_truth_or_execution_authority_escalation():
    t=begin()
    try: replace(t,truth_authority='DERIVED_READ_ONLY'); assert False
    except ValueError as e: assert 'EPISTEMIC_PROGRAM_TRIAL_AUTHORITY_ESCALATION' in str(e)
    try: replace(t,execution_authority='EFFECT'); assert False
    except ValueError as e: assert 'EPISTEMIC_PROGRAM_TRIAL_AUTHORITY_ESCALATION' in str(e)
