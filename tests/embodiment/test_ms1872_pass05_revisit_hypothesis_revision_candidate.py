from dataclasses import replace
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_exact_revisit_ancestry_plus_changed_current_surface_yields_zero_authority_revision_candidate():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        out=m.derive_revisit_hypothesis_revision_candidate('D',b.binding_id)
        assert out['status']=='REVISIT_HYPOTHESIS_REVISION_CANDIDATE'
        assert out['old_hypothesis_digest_sha256']==m.epistemic_deficits.records['D'].hypothesis_digest_sha256
        assert out['revised_hypothesis_digest_sha256']!=out['old_hypothesis_digest_sha256']
        assert out['authority']==out['truth_authority']==out['model_switch_authority']==out['deficit_transition_authority']=='NONE'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
    finally: td.cleanup()


def test_unrelated_or_noncurrent_revisit_cannot_hitchhike_on_revised_model():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        # The binding is explicitly lineage-bound to D, not to an arbitrary other revisit.
        assert m.derive_revisit_hypothesis_revision_candidate('NOPE',b.binding_id)['reason']=='DEFICIT_NOT_FOUND'
        m.epistemic_deficits.records['D'].state=m.epistemic_deficits.records['D'].state.__class__.STALE
        assert m.derive_revisit_hypothesis_revision_candidate('D',b.binding_id)['reason']=='REVISIT_REQUIRED'
    finally: td.cleanup()
