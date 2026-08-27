from microseed.development.epistemic import EpistemicDeficitState
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_off_model_actual_step_is_real_evidence_but_does_not_currently_create_revisit_or_model_challenge():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        t2 = _execute_first_and_advance(m, trial, dc, next_state="sx", evidence_id="E-OUT-1830-X")
        ev = m.evidence.get("E-OUT-1830-X")
        assert ev is not None and ev.get("sha256")
        assert t2.status == "OPEN"
        deficit = m.epistemic_deficits.records[trial.deficit_id]
        assert deficit.state == EpistemicDeficitState.ACTION_LIMITED
        # The generic action outcome deliberately carries no old projection/contrast metadata.
        assert "epistemic_projection" not in ev.get("payload", {})
        # No existing program-step path has requested revisit from the off-model intermediate result.
        assert not any(
            e.get("kind") == "EPISTEMIC_DEFICIT_REVISIT_REQUESTED" and e.get("payload", {}).get("evidence_id") == "E-OUT-1830-X"
            for e in m.store.events()
        )
        assert calls == ["A"]
    finally:
        td.cleanup()
