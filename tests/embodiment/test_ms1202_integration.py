from pathlib import Path
import hashlib
import tempfile
import pytest

from microseed import (
    Microseed, EpistemicStatus, EpistemicContrastBinding, EpistemicContrastRow,
)


def H(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def new():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1202-')
    return td,Microseed(Path(td.name))


def deficit(m: Microseed, did='D', hyp='hyp'):
    uid='u-'+did
    m.append_evidence(uid,{'opaque':True},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS1202-TEST')
    return m.record_action_limited_unknown(
        deficit_id=did,question_key='opaque',hypothesis_digest_sha256=H(hyp),
        unknown_evidence_id=uid,missing_discriminator_signature_sha256=H('missing-'+did),
    )


def projection(m: Microseed, pid='P'):
    return m.register_epistemic_projection(pid,H('projection:'+pid),assistance_ancestry=('SUPPLIED_OPAQUE_PROJECTION',))


def binding(m: Microseed, d, *, bid='B', pid='P', outcomes=None, condition=None):
    outcomes=outcomes or (('h0',H('A')),('h1',H('B')))
    b=EpistemicContrastBinding(
        binding_id=bid,deficit_id=d.deficit_id,hypothesis_digest_sha256=d.hypothesis_digest_sha256,
        rows=(EpistemicContrastRow(pid,m.epistemic_projections.records[pid].epoch,outcomes,condition),),
        assistance_ancestry=('SUPPLIED_OPAQUE_CONTRAST',),
    )
    return m.register_epistemic_contrast(b)


def ev(m: Microseed, eid: str, *, pid='P', outcome='A', epoch=None, condition=None):
    if epoch is None: epoch=m.epistemic_projections.records[pid].epoch
    meta={'projection_id':pid,'projection_epoch':epoch,'outcome_digest_sha256':H(outcome)}
    if condition is not None: meta['condition_signature_sha256']=condition
    return m.append_evidence(eid,{'epistemic_projection':meta},EpistemicStatus.PRESSURE_SUPPORTED,source='MS1202-TEST')


def test_discriminating_content_bound_evidence_creates_bearing_witness_and_requests_revisit():
    td,m=new()
    try:
        projection(m); d=deficit(m); b=binding(m,d)
        e=ev(m,'e',outcome='B')
        r=m.assess_epistemic_evidence_bearing('D','B',e.evidence_id)
        assert r['bearing_kind']=='DISCRIMINATES_LIVE_SET' and r['state']=='REVISIT_REQUIRED'
        ws=m.epistemic_bearing_witnesses('D'); assert len(ws)==1
        assert ws[0]['truth_authority']=='NONE' and ws[0]['answer_authority']=='NONE'
        assert ws[0]['semantic_question_authority']=='NONE'
    finally: td.cleanup()


def test_consensus_confirming_projection_does_not_request_revisit():
    td,m=new()
    try:
        projection(m); d=deficit(m)
        binding(m,d,outcomes=(('h0',H('A')),('h1',H('A'))))
        e=ev(m,'e',outcome='A')
        r=m.assess_epistemic_evidence_bearing('D','B',e.evidence_id)
        assert r['bearing_kind']=='CONSENSUS_NONDISCRIMINATING' and r['bearing'] is False
        assert m.epistemic_deficit_status('D')['state']=='ACTION_LIMITED'
        assert m.epistemic_bearing_witnesses('D')==()
    finally: td.cleanup()


def test_outcome_outside_all_live_predictions_is_model_space_challenge_not_resolution():
    td,m=new()
    try:
        projection(m); d=deficit(m); binding(m,d)
        e=ev(m,'e',outcome='Z')
        r=m.assess_epistemic_evidence_bearing('D','B',e.evidence_id)
        assert r['bearing_kind']=='MODEL_SPACE_CHALLENGE' and r['state']=='REVISIT_REQUIRED'
        assert not hasattr(m,'generate_replacement_hypothesis')
        assert 'RESOLVED' not in {x for x in ('ACTION_LIMITED','PROBE_AVAILABLE','REVISIT_REQUIRED','STALE')}
    finally: td.cleanup()


def test_projection_epoch_drift_stales_old_contrast_and_blocks_old_evidence_replay():
    td,m=new()
    try:
        projection(m); d=deficit(m); binding(m,d)
        old=ev(m,'old',outcome='B',epoch=0)
        ch=m.change_epistemic_projection('P',new_signature_sha256=H('projection:P:v1'),reason='MAPPING_DRIFT')
        assert ch['epoch']==1 and 'B' in ch['stale_binding_ids']
        assert m.epistemic_contrast_status('B')['state']=='STALE'
        r=m.assess_epistemic_evidence_bearing('D','B',old.evidence_id)
        assert r['bearing_kind']=='STALE_BINDING' and r['bearing'] is False
    finally: td.cleanup()


def test_hypothesis_revision_stales_deficit_and_contrast_without_rewriting_history():
    td,m=new()
    try:
        projection(m); d=deficit(m); binding(m,d)
        m.stale_epistemic_deficit('D',reason='BOUNDED_HYPOTHESIS_SET_CHANGED')
        assert m.epistemic_deficit_status('D')['state']=='STALE'
        assert m.epistemic_contrast_status('B')['state']=='STALE'
        assert m.epistemic_contrast_status('B')['hypothesis_digest_sha256']==H('hyp')
    finally: td.cleanup()


def test_conditioned_contrast_rejects_passive_surface_metadata_but_accepts_matching_condition():
    td,m=new()
    try:
        projection(m); d=deficit(m); cond=H('action-condition'); binding(m,d,condition=cond)
        passive=ev(m,'passive',outcome='B')
        r0=m.assess_epistemic_evidence_bearing('D','B',passive.evidence_id)
        assert r0['bearing_kind']=='CONDITION_MISMATCH' and r0['bearing'] is False
        active=ev(m,'active',outcome='B',condition=cond)
        r1=m.assess_epistemic_evidence_bearing('D','B',active.evidence_id)
        assert r1['bearing_kind']=='DISCRIMINATES_LIVE_SET' and r1['bearing'] is True
    finally: td.cleanup()


def test_evidence_without_opaque_projection_metadata_cannot_force_verified_bearing():
    td,m=new()
    try:
        projection(m); d=deficit(m); binding(m,d)
        e=m.append_evidence('raw',{'delta':1},EpistemicStatus.PRESSURE_SUPPORTED,source='MS1202-TEST')
        with pytest.raises(ValueError,match='OPAQUE_EPISTEMIC_PROJECTION_METADATA_REQUIRED'):
            m.assess_epistemic_evidence_bearing('D','B',e.evidence_id)
        assert m.epistemic_deficit_status('D')['state']=='ACTION_LIMITED'
    finally: td.cleanup()


def test_same_evidence_is_deduplicated_per_binding_without_duplicate_witness_pressure():
    td,m=new()
    try:
        projection(m); d=deficit(m); binding(m,d); e=ev(m,'e',outcome='B')
        a=m.assess_epistemic_evidence_bearing('D','B',e.evidence_id)
        b=m.assess_epistemic_evidence_bearing('D','B',e.evidence_id)
        assert a['witness_id'] is not None and b['duplicate'] is True and b['witness_id'] is None
        assert len(m.epistemic_bearing_witnesses('D'))==1
    finally: td.cleanup()


def test_one_evidence_packet_can_bear_on_multiple_deficits_only_through_each_registered_contrast():
    td,m=new()
    try:
        projection(m)
        d0=deficit(m,'D0','hyp0'); d1=deficit(m,'D1','hyp1'); d2=deficit(m,'D2','hyp2')
        binding(m,d0,bid='B0'); binding(m,d1,bid='B1')
        binding(m,d2,bid='B2',outcomes=(('h0',H('A')),('h1',H('A'))))
        e=ev(m,'e',outcome='B')
        assert m.assess_epistemic_evidence_bearing('D0','B0',e.evidence_id)['bearing']
        assert m.assess_epistemic_evidence_bearing('D1','B1',e.evidence_id)['bearing']
        # D2 consensus predicts A, so B challenges its model-space rather than broadcasting by ancestry.
        r2=m.assess_epistemic_evidence_bearing('D2','B2',e.evidence_id)
        assert r2['bearing_kind']=='MODEL_SPACE_CHALLENGE'
        assert len(m.epistemic_bearing_witnesses('D0'))==1
        assert len(m.epistemic_bearing_witnesses('D1'))==1
        assert len(m.epistemic_bearing_witnesses('D2'))==1
    finally: td.cleanup()


def test_restart_replays_projection_contrast_witness_and_revisit_without_discovery_authority():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1202-restart-')
    try:
        root=Path(td.name); m=Microseed(root)
        projection(m); d=deficit(m); binding(m,d); e=ev(m,'e',outcome='B')
        m.assess_epistemic_evidence_bearing('D','B',e.evidence_id)
        del m
        m2=Microseed(root)
        assert m2.status()['epistemic_projection_count']==1
        assert m2.epistemic_contrast_status('B')['state']=='CURRENT'
        assert len(m2.epistemic_bearing_witnesses('D'))==1
        assert m2.epistemic_deficit_status('D')['state']=='REVISIT_REQUIRED'
        assert not hasattr(m2,'discover_epistemic_projection')
        assert m2.status()['epistemic_projection_discovery'].startswith('BOUNDED_ACTION_CONDITIONED_PREDICTIVE_EQUIVALENCE')
    finally: td.cleanup()


def test_ms1202_status_and_authority_ceiling_with_ms1203_hard_stop():
    td,m=new()
    try:
        s=m.status()
        assert s['embodiment'].startswith('PROTO_MICROSEED_MAINDEV_INTEGRATION_V')
        assert s['research_terminal_ms']>=1202 and s['integration_evidence_through_ms']>=1202
        assert s['next_ms']>=1203 and s['next_ms'] >= 1278
        assert s['frontier'].startswith('ATTN-MS')
        assert s['epistemic_bearing_authority'].startswith('BOUNDED_OPERATIONAL_BEARING_ONLY')
        assert s['epistemic_projection_discovery'].startswith('BOUNDED_ACTION_CONDITIONED_PREDICTIVE_EQUIVALENCE')
        assert s['question_revisit_scheduler'].startswith('NOT_INTEGRATED')
        assert not hasattr(m,'schedule_question_revisits')
        assert s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
    finally: td.cleanup()
