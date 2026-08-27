import inspect
from microseed.development.relational_algebra import OpaqueActionCompositionCandidate
from microseed.development.epistemic_program import begin_epistemic_program_trial


def test_two_step_endpoint_equivalence_candidate_cannot_lawfully_carry_generated_longer_program():
    fields=OpaqueActionCompositionCandidate.__dataclass_fields__
    assert 'direct_action_token' in fields
    assert 'first_action_token' in fields and 'second_action_token' in fields
    assert 'steps' not in fields
    assert 'positive_support' in fields and 'support_origin_signatures' in fields
    src=inspect.getsource(begin_epistemic_program_trial)
    assert 'candidate.first_action_token' in src and 'candidate.second_action_token' in src
    assert 'candidate.direct_action_token' not in src  # direct token is relation provenance, not a program step
    # A three-step discriminator with no observed direct equivalent therefore needs
    # a distinct proposal carrier; coercing it into this type would fabricate a relation.
