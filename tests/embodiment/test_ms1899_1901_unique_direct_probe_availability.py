from microseed import EpistemicStatus, Authority, CapabilityContract, QualificationState
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()

def _successor():
    td,m,calls,c=_qualified_refinement_fixture()
    b=_qualify_revised_surface(m,c);m.accept_revisit_hypothesis_revision('D',b.binding_id)
    fresh=m.append_evidence('E-U-1899',{'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
    s=m.record_revised_surface_action_limited_unknown(old_deficit_id='D',new_deficit_id='D-1899',unknown_evidence_id=fresh.evidence_id)
    return td,m,b,s


def test_exact_current_discriminator_finds_unique_current_direct_probe_without_executing_it():
    td,m,b,s=_successor()
    try:
        before=len(m.action_closure.executions)
        out=m.current_revised_surface_direct_probe_availability(old_deficit_id='D',successor_deficit_id='D-1899')
        assert out['status']=='CURRENT_UNIQUE_DIRECT_PROBE_AVAILABLE',out
        assert out['probe_capability_id']=='B'
        assert out['probe_capability_epoch']==m.capabilities.epochs['B']
        assert out['missing_discriminator_signature_sha256']==s.missing_discriminator_signature_sha256
        assert out['probe_selection_authority']==out['execution_authority']=='NONE'
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_unique_direct_probe_reuses_existing_probe_available_lifecycle_inertly():
    td,m,b,s=_successor()
    try:
        before=len(m.action_closure.executions)
        out=m.bind_current_revised_surface_direct_probe(old_deficit_id='D',successor_deficit_id='D-1899')
        assert out['status']=='PROBE_AVAILABLE',out
        rec=m.epistemic_deficits.records['D-1899']
        assert rec.state.value=='PROBE_AVAILABLE'
        assert rec.probe_capability_id=='B' and rec.probe_capability_epoch==m.capabilities.epochs['B']
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_wrong_or_noncurrent_direct_probe_never_becomes_available():
    td,m,b,s=_successor()
    try:
        m.change_capability_dependency('B',reason='MS1899_PROBE_DRIFT')
        out=m.current_revised_surface_direct_probe_availability(old_deficit_id='D',successor_deficit_id='D-1899')
        # Relation ancestry is itself dependent on B, so exact pressure should already stale.
        assert out['status']=='ABSTAIN' and out['reason']=='CURRENT_SUCCESSOR_DEFICIT_REQUIRED',out
    finally:_close(m,td)
