from microseed.development.action_closure import OpaqueControlStateWitness
from tests.embodiment.test_ms1865_pass18_current_history_derives_refinement_bucket import _install_routing
from tests.embodiment.test_ms1862_pass15_revisit_refinement_reuses_external_projection_admission import _qualified_refinement_fixture


def test_current_qualified_refined_bucket_can_resolve_use_after_old_deficit_stales_without_successor_pressure():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        bid=_install_routing(m,c)
        accepted=m.accept_revisit_hypothesis_revision('D',bid)
        assert accepted['status']=='OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        chosen=None
        for outcome in m.action_closure.outcomes.values():
            projected=m.derive_admitted_opaque_transition_sample(outcome.execution_id)
            if projected.get('status')!='ADMITTED_OPAQUE_TRANSITION_SAMPLE': continue
            row=projected['sample']
            if row.sample_id in c.source_sample_ids and row.start_token=='s0' and row.end_token=='s1':
                chosen=outcome;break
        assert chosen is not None
        m.action_closure.set_state(OpaqueControlStateWitness('s1',chosen.evidence_id))
        out=m.resolve_current_one_step_visible_history_projection_conditioned_relation(
            bid,action_id='B',task_id='REVISIT-1865',channel_id='opaque-control',horizon=1)
        assert out['status']=='CURRENT_PARTITION_SCOPED_RELATION'
        assert out['relation_id']=='R-B-SX-1865'
        assert m.epistemic_deficits.records['D'].state.value=='STALE'
        assert m.epistemic_development_pressure_ids()==()
        assert m.epistemic_revisit_required_ids()==()
        assert set(m.epistemic_deficits.records)=={'D'}
    finally: td.cleanup()
