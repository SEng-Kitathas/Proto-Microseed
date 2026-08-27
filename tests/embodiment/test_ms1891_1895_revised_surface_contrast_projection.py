from microseed import EpistemicStatus
from microseed.development.action_closure import OpaqueControlStateWitness
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()


def test_qualified_revised_routing_projects_content_bound_contrast_and_internal_successor_hash():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        accepted=m.accept_revisit_hypothesis_revision('D',b.binding_id)
        out=m.derive_current_revised_surface_missing_discriminator('D')
        assert out['status']=='CURRENT_UNIQUE_REVISED_SURFACE_MISSING_DISCRIMINATOR',out
        rows=out['witnesses'][0]['rows']
        assert len(rows)==1 and rows[0].projection_id==b.projection_id
        assert {x[0] for x in rows[0].candidate_outcome_digests}=={'s0','r'}
        assert len({x[1] for x in rows[0].candidate_outcome_digests})==2
        fresh=m.append_evidence('E-U-1893',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
        successor=m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1893',unknown_evidence_id=fresh.evidence_id)
        assert successor.missing_discriminator_signature_sha256==out['missing_discriminator_signature_sha256']
        assert 'MISSING_DISCRIMINATOR_DERIVED_FROM_CURRENT_REVISED_SURFACE' in successor.assistance_ancestry
        assert successor.state.value=='ACTION_LIMITED'
        assert calls==['A','B']
    finally:_close(m,td)


def test_current_admitted_history_that_resolves_bucket_suppresses_false_missing_pressure():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        m.accept_revisit_hypothesis_revision('D',b.binding_id)
        chosen=None
        for outcome in m.action_closure.outcomes.values():
            projected=m.derive_admitted_opaque_transition_sample(outcome.execution_id)
            if projected.get('status')!='ADMITTED_OPAQUE_TRANSITION_SAMPLE':continue
            row=projected['sample']
            if row.sample_id in c.source_sample_ids and row.start_token=='s0' and row.end_token=='s1':
                chosen=outcome;break
        assert chosen is not None
        m.action_closure.set_state(OpaqueControlStateWitness('s1',chosen.evidence_id))
        out=m.derive_current_revised_surface_missing_discriminator('D')
        assert out['status']=='CURRENT_CONTEXT_ALREADY_RESOLVES_REVISED_SURFACE',out
        fresh=m.append_evidence('E-U-1895',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
        try:
            m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1895',unknown_evidence_id=fresh.evidence_id)
        except ValueError as e:
            assert 'CURRENT_CONTEXT_ALREADY_RESOLVES_REVISED_SURFACE' in str(e)
        else:
            raise AssertionError('resolved current context must not manufacture missing-discriminator pressure')
    finally:_close(m,td)
