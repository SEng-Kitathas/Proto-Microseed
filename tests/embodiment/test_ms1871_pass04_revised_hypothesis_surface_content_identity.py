from dataclasses import replace
from microseed.development.action_learning import projection_conditioned_hypothesis_surface_digest
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_revised_hypothesis_surface_digest_is_content_bound_not_qualification_count_bound():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        d1=projection_conditioned_hypothesis_surface_digest(b,m.action_outcome_learning.relations)
        more=replace(b,qualification_evidence_ids=b.qualification_evidence_ids+('EXTRA-SUPPORT-EVIDENCE',),holdout_support=b.holdout_support+1)
        d2=projection_conditioned_hypothesis_surface_digest(more,m.action_outcome_learning.relations)
        assert d1==d2
        assert len(d1)==64
    finally: td.cleanup()


def test_revised_hypothesis_surface_digest_changes_when_routing_semantics_change():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        d1=projection_conditioned_hypothesis_surface_digest(b,m.action_outcome_learning.relations)
        changed=replace(b,bucket_action_overrides=(('s0','B','R-B-S2-1868'),))
        d2=projection_conditioned_hypothesis_surface_digest(changed,m.action_outcome_learning.relations)
        assert d1!=d2
    finally: td.cleanup()


def test_revised_hypothesis_surface_digest_requires_all_routed_relations():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        rels=dict(m.action_outcome_learning.relations); rels.pop('R-B-SX-1868')
        try:
            projection_conditioned_hypothesis_surface_digest(b,rels)
        except ValueError as e:
            assert 'HYPOTHESIS_RELATION_NOT_FOUND' in str(e)
        else:
            raise AssertionError('missing relation must not produce a surface identity')
    finally: td.cleanup()
