from pathlib import Path
import tempfile, hashlib
from microseed import Microseed, CapabilityContract, Authority, QualificationState, EpistemicStatus
from microseed.development.epistemic import EpistemicDeficitState
from microseed.cognition.hypothesis import Hypothesis


def new():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1152-')
    return td,Microseed(Path(td.name))


def test_zero_disagreement_candidate_is_not_advertised_as_probe():
    td,m=new()
    try:
        h0=Hypothesis('h0',lambda x:0 if x in ('a','b') else 0)
        h1=Hypothesis('h1',lambda x:0 if x in ('a','b') else (1 if x=='d' else 0))
        assert m.active_discrimination([h0,h1],['a','b'],[])['next_probe'] is None
        assert m.active_discrimination([h0,h1],['a','b','d'],[])['next_probe']=='d'
    finally: td.cleanup()


def test_action_limited_deficit_requires_unknown_evidence_and_has_no_truth_authority():
    td,m=new()
    try:
        ev=m.append_evidence('u',{'opaque':1},EpistemicStatus.UNKNOWN_INCOMPLETE,source='TEST')
        r=m.record_action_limited_unknown(deficit_id='D',question_key='Q0',hypothesis_digest_sha256='a'*64,unknown_evidence_id=ev.evidence_id,missing_discriminator_signature_sha256='b'*64)
        assert r.state==EpistemicDeficitState.ACTION_LIMITED
        assert r.truth_authority=='NONE' and r.semantic_question_authority=='NONE'
        bad=m.append_evidence('p',{'opaque':2},EpistemicStatus.PRESSURE_SUPPORTED,source='TEST')
        try:
            m.record_action_limited_unknown(deficit_id='D2',question_key='Q1',hypothesis_digest_sha256='c'*64,unknown_evidence_id=bad.evidence_id,missing_discriminator_signature_sha256='d'*64)
        except ValueError as e:
            assert 'UNKNOWN_INCOMPLETE' in str(e)
        else: raise AssertionError('non-UNKNOWN evidence admitted as deficit origin')
    finally: td.cleanup()


def test_probe_availability_never_auto_resolves_and_new_evidence_only_requests_revisit():
    td,m=new()
    try:
        ev=m.append_evidence('u',{'opaque':1},EpistemicStatus.UNKNOWN_INCOMPLETE,source='TEST')
        m.record_action_limited_unknown(deficit_id='D',question_key='Q0',hypothesis_digest_sha256='a'*64,unknown_evidence_id='u',missing_discriminator_signature_sha256='b'*64)
        c=CapabilityContract('probe','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1128-1152',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1)
        m.register_capability(c)
        st=m.bind_probe_capability('D','probe')
        assert st['state']=='PROBE_AVAILABLE'
        pev=m.append_evidence('probe-e',{'outcome':1},EpistemicStatus.PRESSURE_SUPPORTED,source='TEST')
        st=m.record_epistemic_probe_evidence('D',pev.evidence_id)
        assert st['state']=='REVISIT_REQUIRED'
        assert 'RESOLVED' not in st['state']
    finally: td.cleanup()


def test_probe_capability_drift_reopens_action_limited_unknown():
    td,m=new()
    try:
        m.append_evidence('u',{'opaque':1},EpistemicStatus.UNKNOWN_INCOMPLETE,source='TEST')
        m.record_action_limited_unknown(deficit_id='D',question_key='Q0',hypothesis_digest_sha256='a'*64,unknown_evidence_id='u',missing_discriminator_signature_sha256='b'*64)
        c=CapabilityContract('probe','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1128-1152',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1)
        m.register_capability(c); m.bind_probe_capability('D','probe')
        m.change_capability_dependency('probe',reason='TEST_DRIFT')
        assert m.epistemic_deficit_status('D')['state']=='ACTION_LIMITED'
    finally: td.cleanup()


def test_epistemic_deficit_persists_across_restart_without_becoming_selfhood_or_truth():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1152-restart-')
    try:
        root=Path(td.name); m=Microseed(root)
        m.append_evidence('u',{'opaque':1},EpistemicStatus.UNKNOWN_INCOMPLETE,source='TEST')
        m.record_action_limited_unknown(deficit_id='D',question_key='Q0',hypothesis_digest_sha256='a'*64,unknown_evidence_id='u',missing_discriminator_signature_sha256='b'*64)
        del m
        m2=Microseed(root); st=m2.epistemic_deficit_status('D')
        assert st['state']=='ACTION_LIMITED' and st['truth_authority']=='NONE'
        assert m2.status()['identity_claim']=='NOT_QUALIFIED'
    finally: td.cleanup()


def test_ms1152_bridge_remains_in_ancestry_after_later_main_dev_integration():
    td,m=new()
    try:
        s=m.status(); assert s['research_terminal_ms']>=1152 and s['integration_evidence_through_ms']>=1152
        assert s['next_ms']>1152 and s['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
        assert s['epistemic_deficit_lifecycle']
    finally: td.cleanup()
