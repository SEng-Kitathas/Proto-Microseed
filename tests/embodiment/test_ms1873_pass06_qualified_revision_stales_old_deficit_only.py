from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_qualified_revision_stales_old_revisit_but_never_rewrites_or_creates_successor():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        old=m.epistemic_deficits.records['D']; old_digest=old.hypothesis_digest_sha256; old_unknown=old.unknown_evidence_id; old_rel=tuple(old.relevant_evidence_ids)
        before=set(m.epistemic_deficits.records)
        out=m.accept_revisit_hypothesis_revision('D',b.binding_id)
        assert out['status']=='OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        assert old.state.value=='STALE'
        assert old.hypothesis_digest_sha256==old_digest and old.unknown_evidence_id==old_unknown and tuple(old.relevant_evidence_ids)==old_rel
        assert set(m.epistemic_deficits.records)==before
        assert m.epistemic_development_pressure_ids()==() and m.epistemic_revisit_required_ids()==()
        assert out['truth_authority']==out['answer_authority']==out['model_switch_authority']==out['successor_deficit_authority']=='NONE'
    finally: td.cleanup()


def test_revision_acceptance_rederives_currentness_and_cannot_repeat_after_stale():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        assert m.accept_revisit_hypothesis_revision('D',b.binding_id)['status']=='OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        again=m.accept_revisit_hypothesis_revision('D',b.binding_id)
        assert again['status']=='REVISION_NOT_ACCEPTED' and again['reason']=='REVISIT_REQUIRED'
    finally: td.cleanup()
