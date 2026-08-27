from __future__ import annotations

import pytest

from microseed import EpistemicStatus
from microseed.development.action_closure import ActionOutcomeRecord
from microseed.development.epistemic_action import derive_epistemic_program_step_commitment
from microseed.development.recruitment import RecruitmentOption, FeasibilityState
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, act_ob


def test_lower_epistemic_step_commitment_cannot_reopen_revisit_required_deficit():
    td,m,calls,world,trial,dc=fixture()
    try:
        ref=m.append_evidence('E-REVISIT-OWNER',{'bounded':'program-result'},EpistemicStatus.PRESSURE_SUPPORTED,source='OWNER-GUARD')
        rec=m.epistemic_deficits.request_revisit(trial.deficit_id,ref.evidence_id)
        assert rec.state.value=='REVISIT_REQUIRED'
        c=derive_epistemic_program_step_commitment(
            trial=trial,
            deficit=rec,
            feasibility=RecruitmentOption('A',FeasibilityState.FEASIBLE),
            capabilities=m.capabilities,
            obligation=act_ob(),
            current_frame_epochs=dict(m.frames.epochs),
            current_state=m.action_closure.current_state,
        )
        assert c.commitment==TernaryCommitment.UNKNOWN
        assert calls==[]
    finally:
        td.cleanup()


def test_state_only_action_outcome_constructor_rejects_any_value_representation():
    pc=RelationalCommitment('PC','prediction',TernaryCommitment.UNKNOWN,reason='OWNER-GUARD')
    with pytest.raises(ValueError,match='STATE_ONLY_MIXED_VALUE_REPRESENTATION'):
        ActionOutcomeRecord(
            outcome_id='O',execution_id='X',evidence_id='E',actual_next_state_id='s1',
            observed_value=1.0,value_id='V',prediction_commitment=pc,actual_value_effect=0.1,
            state_only=True,
        )


def test_lower_epistemic_step_commitment_requires_priority_even_if_information_says_yes():
    td,m,calls,world,trial,dc=fixture()
    try:
        deficit=m.epistemic_deficits.records[trial.deficit_id]
        priority=RelationalCommitment('P-NO','priority',TernaryCommitment.NO,reason='NO_NORMATIVE_PRIORITY')
        information=RelationalCommitment('I-YES','information',TernaryCommitment.YES,reason='TRACE_DIVERGES')
        c=derive_epistemic_program_step_commitment(
            trial=trial, deficit=deficit, feasibility=RecruitmentOption('A',FeasibilityState.FEASIBLE),
            capabilities=m.capabilities, obligation=act_ob(), current_frame_epochs=dict(m.frames.epochs),
            current_state=m.action_closure.current_state, priority_commitment=priority, information_commitment=information,
        )
        assert not c.licenses_yes()
        assert calls==[]
    finally:
        td.cleanup()
