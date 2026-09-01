
from __future__ import annotations

import random

from microseed import (
    Authority, CapabilityContract, EpistemicStatus, ExternalProjectionQualifier,
    ProjectionDiscoveryConfig, ProjectionSample, QualificationState,
)
from scratch.ms1996_endogenous_program_caller_choice_elimination import OBLIGATION, _close
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture
from tests.embodiment.test_ms1820_pass13_owned_three_locus_surface_generates_program import _add_value_step


def _learn_two_bucket_projection(m, *, projection_id: str, salt: int):
    rng = random.Random(91000 + salt)
    rows = []
    for i in range(900):
        x = str(rng.randint(0, 1))
        nuisance = str(rng.randint(0, 9))
        action = 'PX' if rng.random() < .5 else 'PY'
        # Opaque equivalence classes only. Salt swaps surface effect labels while
        # preserving the two-class predictive structure.
        left, right = (('E0', 'E1') if salt % 2 == 0 else ('Q7', 'Q3'))
        effect = (right if action == 'PX' else left) if x == '1' else (left if action == 'PX' else right)
        rows.append(ProjectionSample(f'A-TARGET-{salt}-{i}', (nuisance, x), action, effect, f'S-{i%3}', 'F', 0))
    found = m.discover_epistemic_projection_candidates(
        rows[:600], rows[600:], ProjectionDiscoveryConfig(
            max_subset=1, min_train_support=100, min_key_action_support=8,
            min_validation_accuracy=.95, min_lift_over_action_baseline=.35,
            min_scope_accuracy=.90, max_candidates=8,
        )
    )
    assert found
    cand = next(m.epistemic_projection_candidates[x['candidate_id']] for x in found
                if m.epistemic_projection_candidates[x['candidate_id']].input_positions == (1,))
    ev = m.append_evidence(
        f'A-TARGET-PROJ-QUAL-{salt}', {'candidate_sha256': cand.digest(), 'independent': True},
        EpistemicStatus.PRESSURE_SUPPORTED, source='EXTERNAL-A-TARGET'
    )
    ticket = ExternalProjectionQualifier(m.evidence, qualifier_id=f'EXTERNAL-A-TARGET-{salt}').qualify(
        cand, qualification_evidence=(ev,)
    )
    rec = m.admit_epistemic_projection_candidate(ticket, projection_id=projection_id)
    buckets = tuple(sorted({b for _, b in cand.key_to_bucket}))
    assert len(buckets) == 2
    return rec, cand, buckets


def _register_request_base(m, *, base_id: str, calls: list[tuple[str, str]]) -> None:
    def handler(*, target):
        calls.append((base_id, str(target)))
        return {'base': base_id, 'target': str(target)}
    m.register_capability(CapabilityContract(
        base_id, 'opaque-request-channel',
        boundary={'request_target_binding_mode':'OPAQUE_PROJECTION_BUCKET_SPECIALIZABLE','local_means_owned_by_parent':False},
        interface={'target':'opaque','output':'request-receipt'},
        invariants=('REQUEST_CHANNEL_EFFECT_NE_LOCAL_MEANS_AUTHORITY',),
        hazards=('SUBORDINATE_MAY_REFUSE',),
        authority=Authority.EFFECT, lineage=('A-TARGET-FRONTIER',), currentness='CURRENT', resources={},
        query_obligation_id='Q', qualification=QualificationState.SHADOW_QUALIFIED,
        handler=handler, operational_scope_id='S',
    ))


def _add_program_history(m, steps: tuple[str, str, str], prefix: str, effect: float, final_state: str) -> None:
    e1 = _add_value_step(m, xid=f'{prefix}-1', action=steps[0], start='s0', end='s1', effect=effect, control_evidence=f'E-ROOT-{prefix}')
    e2 = _add_value_step(m, xid=f'{prefix}-2', action=steps[1], start='s1', end='s2', effect=effect, control_evidence=e1)
    _add_value_step(m, xid=f'{prefix}-3', action=steps[2], start='s2', end=final_state, effect=effect, control_evidence=e2)


def _run_case(*, salt: int, base_id: str):
    td, m, calls, _, _, _ = fixture()
    req_calls: list[tuple[str, str]] = []
    try:
        rec, cand, buckets = _learn_two_bucket_projection(m, projection_id=f'TARGET-P-{salt}', salt=salt)
        _register_request_base(m, base_id=base_id, calls=req_calls)
        b0 = m.derive_bound_request_specialization(base_id, rec.projection_id, buckets[0])
        b1 = m.derive_bound_request_specialization(base_id, rec.projection_id, buckets[1])
        steps = (b0.capability_id, b1.capability_id, b0.capability_id)

        # Four recurrent lived-history shapes encode the relation. The generator
        # call below receives no sequence, preferred target, or semantic action name.
        for prefix, effect, end in (
            ('P1', +1.0, 'u'), ('P2', +1.0, 'u'),
            ('N1', -1.0, 'v'), ('N2', -1.0, 'v'),
        ):
            _add_program_history(m, steps, f'A{salt}-{prefix}', effect, end)

        before_intents = len(m.action_closure.intents)
        before_exec = len(m.action_closure.executions)
        generated = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=OBLIGATION, max_nodes=64,
        )
        assert generated['status'] == 'REPRESENTED_INFORMATIVE_PROGRAMS_FOUND', generated
        programs = {tuple(x) for x in generated['programs']}
        assert steps in programs
        chosen = next(c for c in generated['candidates'] if c.steps == steps)
        assert chosen.execution_authority == 'NONE'
        assert chosen.truth_authority == 'NONE'
        assert generated['execution_authority'] == 'NONE'
        assert generated['truth_authority'] == 'NONE'
        assert len(m.action_closure.intents) == before_intents
        assert len(m.action_closure.executions) == before_exec
        assert req_calls == []

        # Convert raw opaque capability IDs to the only structure the test oracle
        # is allowed to compare. No surface ID or target token is shared across cases.
        abstract = [0 if x == b0.capability_id else 1 if x == b1.capability_id else -1 for x in chosen.steps]
        assert abstract == [0, 1, 0]

        pre_ids = tuple(chosen.steps)
        pre_sigs = (b0.computed_signature_sha256(), b1.computed_signature_sha256())
        drift = m.change_epistemic_projection(rec.projection_id, new_signature_sha256=('a' if salt % 2 == 0 else 'b') * 64, reason='A-TARGET-PROJECTION-DRIFT')
        assert b0.capability_id in drift['stale_capability_ids'] and b1.capability_id in drift['stale_capability_ids']
        stale = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(
            obligation=OBLIGATION, max_nodes=64,
        )
        assert steps not in {tuple(x) for x in stale.get('programs', ())}
        assert stale['execution_authority'] == 'NONE'
        assert len(m.action_closure.intents) == before_intents
        assert len(m.action_closure.executions) == before_exec
        assert req_calls == []
        return {
            'abstract_program': abstract,
            'capability_ids': pre_ids,
            'capability_signatures': pre_sigs,
            'projection_candidate_sha256': cand.digest(),
            'target_tokens': buckets,
            'candidate_id': chosen.candidate_id,
            'candidate_sha256': chosen.digest(),
            'stale_status': stale['status'],
        }
    finally:
        _close(td, m)


def test_bound_request_specializations_compose_into_caller_free_nonexecuting_program_under_opaque_id_permutation() -> None:
    left = _run_case(salt=0, base_id='REQ-OPAQUE-X17')
    right = _run_case(salt=1, base_id='REQ-OPAQUE-Z93')
    assert left['abstract_program'] == right['abstract_program'] == [0, 1, 0]
    # Surface identities really did change; only the learned relational shape is common.
    assert left['capability_ids'] != right['capability_ids']
    assert left['capability_signatures'] != right['capability_signatures']
    assert left['projection_candidate_sha256'] != right['projection_candidate_sha256']
    assert left['target_tokens'] != right['target_tokens']
    assert left['stale_status'] in {'REPRESENTED_REACHABILITY_INCOMPLETE', 'NO_REPRESENTED_INFORMATIVE_PROGRAM'}
    assert right['stale_status'] in {'REPRESENTED_REACHABILITY_INCOMPLETE', 'NO_REPRESENTED_INFORMATIVE_PROGRAM'}
