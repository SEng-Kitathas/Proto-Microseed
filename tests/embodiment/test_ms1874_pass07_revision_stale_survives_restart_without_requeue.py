from pathlib import Path
from microseed import Microseed
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_accepted_revision_stale_state_survives_restart_without_requeue_or_revisit():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        root=Path(td.name)
        b=_qualify_revised_surface(m,c)
        out=m.accept_revisit_hypothesis_revision('D',b.binding_id)
        assert out['status']=='OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        old_digest=m.epistemic_deficits.records['D'].hypothesis_digest_sha256
        del m
        m2=Microseed(root)
        d=m2.epistemic_deficits.records['D']
        assert d.state.value=='STALE'
        assert d.hypothesis_digest_sha256==old_digest
        assert m2.epistemic_development_pressure_ids()==()
        assert m2.epistemic_revisit_required_ids()==()
        # Runtime executable handlers are intentionally not restored by history replay.
        assert all(c.handler is None for c in m2.capabilities.contracts.values())
    finally: td.cleanup()
