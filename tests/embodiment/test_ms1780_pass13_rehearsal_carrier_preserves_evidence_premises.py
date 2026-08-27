from pathlib import Path
import tempfile

from microseed import Authority, EpistemicStatus, FeasibilityState, Microseed, QualificationState, ValueVariableContract
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_priority import derive_regulatory_decision_bearing_commitment
from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.commitment import TernaryCommitment

LEGACY_DIGEST='0e23c40dede961645c0690fcf85a5859aa4bfca3a445091cd2364977b7e3b1da'


def fixture():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1780-')
    m=Microseed(Path(td.name))
    m.register_value_variable(ValueVariableContract('V','reg',0,10,'v'*64,Authority.REFERENCE_ONLY,('MS1780',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.observe_value_state('V',-1.0)
    m.append_evidence('E-U',{'u':1},EpistemicStatus.UNKNOWN_INCOMPLETE)
    m.record_action_limited_unknown(deficit_id='D',question_key='Q',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U',missing_discriminator_signature_sha256='d'*64,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),))
    return td,m


def rel(cap,effect,*,premise=True):
    return RehearsalTransitionRelation(
        's0',cap,'n'+cap,effect,8,1.0,(f'E-{cap}-{effect}',),0,('F',0),('EP',0),
        evidence_premise_epochs=((('BASIS',0),) if premise else ()),
        evidence_premise_signatures=((('BASIS','b'*64),) if premise else ()),
    )


def derive(m,sets,*,basis_epoch=0,basis_signature='b'*64):
    return derive_regulatory_decision_bearing_commitment(
        deficit=m.epistemic_deficits.records['D'],values=m.values,relation_sets=sets,
        options=(RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.FEASIBLE)),
        start_state_id='s0',current_capability_epochs={'A':0,'B':0,'BASIS':basis_epoch},
        current_capability_signatures={'BASIS':basis_signature},current_frame_epochs={'F':0},current_episode_epochs={'EP':0},
    )


def test_carrier_preserves_new_premise_ancestry_without_rewriting_legacy_digest():
    legacy=RehearsalTransitionRelation('s0','A','s1',1.0,8,1.0,('E',),0,('F',0),('EP',0))
    assert legacy.digest()==LEGACY_DIGEST
    r=rel('A',2)
    assert r.evidence_premise_epochs==(('BASIS',0),)
    assert r.evidence_premise_signatures==(('BASIS','b'*64),)
    assert r.digest()!=legacy.digest()


def test_priority_accepts_matching_premise_ancestry_and_rejects_epoch_or_signature_drift():
    td,m=fixture()
    try:
        h1={('s0','A'):rel('A',2),('s0','B'):rel('B',0)}
        h2={('s0','A'):rel('A',0),('s0','B'):rel('B',2)}
        assert derive(m,(h1,h2)).licenses_yes()
        stale_epoch=derive(m,(h1,h2),basis_epoch=1)
        assert stale_epoch.commitment==TernaryCommitment.UNKNOWN
        assert 'EVIDENCE_PREMISE_EPOCH_DRIFT:BASIS' in stale_epoch.reason
        stale_sig=derive(m,(h1,h2),basis_signature='c'*64)
        assert stale_sig.commitment==TernaryCommitment.UNKNOWN
        assert 'EVIDENCE_PREMISE_SIGNATURE_DRIFT:BASIS' in stale_sig.reason
    finally:
        td.cleanup()
