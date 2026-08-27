from pathlib import Path
import hashlib
import random
import tempfile
import pytest

from microseed import (
    Microseed, Authority, EpistemicStatus, QualificationState, OperationalFrameContract,
    ProjectionSample, ProjectionDiscoveryConfig, ExternalProjectionQualifier,
    EpistemicContrastBinding, EpistemicContrastRow,
)


def H(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def new():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1227-')
    m=Microseed(Path(td.name))
    m.register_operational_frame(OperationalFrameContract(
        frame_id='F',purpose='opaque-raw-action-effect-boundary',signature_sha256=H('frame-v0'),
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS1203-1227',),currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('EXTERNAL_FRAME_QUALIFICATION',),
        invariants=('NO_SEMANTIC_FEATURE_AUTHORITY',),
    ))
    return td,m


def samples(seed=1227,n=3600,true=(1,4),noise=.02):
    rng=random.Random(seed); out=[]
    for i in range(n):
        raw=[str(rng.randint(0,1)) for _ in range(8)]
        action='a0' if rng.random()<.5 else 'a1'
        p=0
        for j in true:p^=int(raw[j])
        y=p^(1 if action=='a1' else 0)
        if rng.random()<noise:y^=1
        out.append(ProjectionSample(f's{i}',tuple(raw),action,f'e{y}',f'r{i%3}','F',0))
    return out


def discover_pair(m):
    rows=samples(); train=rows[:2400]; val=rows[2400:]
    found=m.discover_epistemic_projection_candidates(train,val,ProjectionDiscoveryConfig(max_subset=2))
    assert found
    return found[0], train, val


def ticket(m,cid,eid='Q'):
    ev=m.append_evidence(eid,{'heldout_accuracy':.98,'independent_scope':True},EpistemicStatus.PRESSURE_SUPPORTED,source='HSP_EXTERNAL')
    return ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1227').qualify(
        m.epistemic_projection_candidates[cid],qualification_evidence=(ev,)
    )


def test_bounded_predictive_equivalence_discovers_pair_without_semantic_operator():
    td,m=new()
    try:
        f,_,_=discover_pair(m)
        c=m.epistemic_projection_candidates[f['candidate_id']]
        assert c.input_positions==(1,4)
        assert c.validation_accuracy>.94
        assert c.bucket_count==2 and c.raw_key_count==4
        groups={}
        for key,bucket in c.key_to_bucket:groups.setdefault(bucket,set()).add(key)
        assert {frozenset(v) for v in groups.values()}=={
            frozenset({('0','0'),('1','1')}),frozenset({('0','1'),('1','0')})
        }
        assert not any('XOR' in x for x in c.assistance_ancestry)
    finally: td.cleanup()


def test_projection_candidate_is_proposal_only_and_unseen_raw_key_abstains():
    td,m=new()
    try:
        f,_,_=discover_pair(m); c=m.epistemic_projection_candidates[f['candidate_id']]
        assert c.proposal_authority=='NONE' and c.qualification_authority=='NONE'
        assert c.semantic_projection_authority=='NONE' and c.truth_authority=='NONE'
        assert c.candidate_id not in m.epistemic_projections.records
        raw=['0']*8; raw[1]='2'
        assert c.project(raw) is None
    finally: td.cleanup()


def test_unary_grammar_fails_pair_world_while_pair_grammar_reaches_it():
    td,m=new()
    try:
        rows=samples(); tr=rows[:2400]; va=rows[2400:]
        assert m.discover_epistemic_projection_candidates(
            tr,va,ProjectionDiscoveryConfig(max_subset=1,min_validation_accuracy=.72,min_lift_over_action_baseline=.08,min_scope_accuracy=.65)
        )==[]
        out=m.discover_epistemic_projection_candidates(tr,va,ProjectionDiscoveryConfig(max_subset=2))
        assert out and out[0]['input_positions']==[1,4]
    finally: td.cleanup()


def test_external_qualification_is_required_and_admitted_projection_preserves_ancestry():
    td,m=new()
    try:
        f,_,_=discover_pair(m); cid=f['candidate_id']; c=m.epistemic_projection_candidates[cid]
        bad=ExternalProjectionQualifier(m.evidence,qualifier_id='HSP-MS1227').qualify(c,qualification_evidence=())
        with pytest.raises(ValueError,match='NOT_ADMISSIBLE|NO_QUALIFICATION_EVIDENCE'):
            m.admit_epistemic_projection_candidate(bad,projection_id='P')
        t=ticket(m,cid)
        rec=m.admit_epistemic_projection_candidate(t,projection_id='P')
        assert rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'
        assert rec.proposal_candidate_sha256==c.digest()
        assert rec.qualification_evidence_ids==('Q',)
        assert rec.discovery_authority=='NONE' and rec.semantic_projection_authority=='NONE'
    finally: td.cleanup()


def test_forged_candidate_digest_ticket_is_rejected():
    td,m=new()
    try:
        f,_,_=discover_pair(m); t=ticket(m,f['candidate_id'])
        object.__setattr__(t,'candidate_sha256','0'*64)
        with pytest.raises(ValueError,match='CANDIDATE_DIGEST_MISMATCH'):
            m.admit_epistemic_projection_candidate(t)
    finally: td.cleanup()


def test_frame_drift_after_nomination_blocks_projection_admission():
    td,m=new()
    try:
        f,_,_=discover_pair(m); t=ticket(m,f['candidate_id'])
        m.change_operational_frame('F',reason='RAW_BOUNDARY_CHANGED')
        with pytest.raises(ValueError,match='FRAME_DRIFT_AFTER_NOMINATION'):
            m.admit_epistemic_projection_candidate(t)
    finally: td.cleanup()


def test_discovered_then_externally_qualified_projection_feeds_existing_bearing_without_answer_authority():
    td,m=new()
    try:
        f,_,_=discover_pair(m); m.admit_epistemic_projection_candidate(ticket(m,f['candidate_id']),projection_id='P')
        u=m.append_evidence('U',{'opaque':True},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS1227')
        d=m.record_action_limited_unknown(deficit_id='D',question_key='opaque',hypothesis_digest_sha256=H('hyp'),unknown_evidence_id=u.evidence_id,missing_discriminator_signature_sha256=H('missing'))
        cb=EpistemicContrastBinding('B','D',d.hypothesis_digest_sha256,(EpistemicContrastRow('P',0,(('h0',H('e0')),('h1',H('e1')))),),assistance_ancestry=('BOUND_AFTER_DISCOVERY',))
        m.register_epistemic_contrast(cb)
        e=m.append_evidence('E',{'epistemic_projection':{'projection_id':'P','projection_epoch':0,'outcome_digest_sha256':H('e1')}},EpistemicStatus.PRESSURE_SUPPORTED,source='MS1227')
        r=m.assess_epistemic_evidence_bearing('D','B','E')
        assert r['bearing_kind']=='DISCRIMINATES_LIVE_SET' and r['state']=='REVISIT_REQUIRED'
        assert r['truth_authority']=='NONE' and r['answer_authority']=='NONE'
    finally: td.cleanup()


def test_candidate_nomination_replays_across_restart_without_qualification_gain():
    td,m=new()
    try:
        f,_,_=discover_pair(m); cid=f['candidate_id']; sig=m.epistemic_projection_candidates[cid].digest()
        root=Path(td.name); del m
        m2=Microseed(root)
        assert cid in m2.epistemic_projection_candidates
        c=m2.epistemic_projection_candidates[cid]
        assert c.digest()==sig and c.qualification_authority=='NONE'
        assert cid not in m2.epistemic_projections.records
    finally: td.cleanup()


def test_admitted_discovered_projection_replays_with_qualification_ancestry():
    td,m=new()
    try:
        f,_,_=discover_pair(m); c=m.epistemic_projection_candidates[f['candidate_id']]
        m.admit_epistemic_projection_candidate(ticket(m,c.candidate_id),projection_id='P')
        root=Path(td.name); del m
        m2=Microseed(root); rec=m2.epistemic_projections.records['P']
        assert rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'
        assert rec.proposal_candidate_sha256==c.digest() and rec.qualification_evidence_ids==('Q',)
        assert rec.discovery_authority=='NONE'
    finally: td.cleanup()


def test_ms1227_status_and_ms1228_hard_stop():
    td,m=new()
    try:
        s=m.status()
        assert s['embodiment'].startswith('PROTO_MICROSEED_MAINDEV_INTEGRATION_V')
        assert s['research_terminal_ms']>=1227 and s['integration_evidence_through_ms']>=1227
        assert s['next_ms']>=1228 and s['next_ms'] >= 1278
        assert s['frontier'].startswith('ATTN-MS')
        assert s['epistemic_projection_discovery'].startswith('BOUNDED_ACTION_CONDITIONED_PREDICTIVE_EQUIVALENCE')
        assert not hasattr(m,'qualify_epistemic_projection_candidate')
        assert not hasattr(m,'discover_general_epistemic_projection')
        assert s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
    finally: td.cleanup()
