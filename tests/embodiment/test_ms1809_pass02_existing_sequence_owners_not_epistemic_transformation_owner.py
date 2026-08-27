from microseed.development.discovery import CandidateFinding, DiscoveryConfig
from microseed.development.relational_algebra import OpaqueActionCompositionCandidate
from microseed.runtime.composer import CompositionResult
from microseed.runtime.types import Authority


def test_existing_length_generic_sequence_carriers_do_not_own_opaque_action_transformation_semantics():
    # Developmental motif discovery already admits length-3 motifs, but its
    # object is a value/effect residual candidate, not an opaque state-action
    # transformation or executable epistemic program.
    cfg = DiscoveryConfig()
    assert cfg.max_len >= 3
    finding = CandidateFinding(
        motif=("A", "B", "C"), operational_scope_id="S", support=8,
        distinct_scopes=2, residual=(1.0,), consistency=0.9, score=1.0,
        source_trace_ids=("T1", "T2"), dependency_epochs=(("A",0),("B",0),("C",0)),
    )
    payload = finding.structural_payload()
    assert finding.motif == ("A", "B", "C")
    assert "start_state_id" not in payload and "next_state_id" not in payload
    assert not isinstance(finding, OpaqueActionCompositionCandidate)

    # Runtime composer can return arbitrarily long dependency plans, but the plan
    # has no claimed action-transition meaning and composition cannot infer EFFECT authority.
    composed = CompositionResult("COMPOSED_EPHEMERAL", ("A", "B", "C"), (), Authority.NONE)
    assert composed.plan == ("A", "B", "C")
    assert composed.authority is Authority.NONE

    # Therefore both owners are useful donor mechanisms, but neither closes the
    # Pass-1 grammar/reach seam by itself.
