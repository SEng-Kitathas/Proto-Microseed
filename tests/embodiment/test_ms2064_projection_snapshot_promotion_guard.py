from microseed.development.epistemic import (
    EpistemicDeficitRegistry,
    EpistemicProjectionRegistry,
    EpistemicProjectionRecord,
)


def test_ms2064_deficit_snapshot_does_not_reference_projection_capability_dependents():
    reg=EpistemicDeficitRegistry()
    assert reg.snapshot()=={}
    assert not hasattr(reg,'capability_dependents')


def test_ms2064_projection_snapshot_reports_capability_dependents_on_the_correct_registry():
    reg=EpistemicProjectionRegistry()
    reg.register(EpistemicProjectionRecord('P','a'*64))
    reg.bind_capability('P','CAP-Z')
    reg.bind_capability('P','CAP-A')
    snap=reg.snapshot()
    assert snap['P']['projection_id']=='P'
    assert snap['P']['signature_sha256']=='a'*64
    assert snap['P']['capability_dependents']==['CAP-A','CAP-Z']


def test_ms2064_projection_snapshot_empty_dependents_is_explicit_and_stable():
    reg=EpistemicProjectionRegistry()
    reg.register(EpistemicProjectionRecord('P','b'*64))
    assert reg.snapshot()['P']['capability_dependents']==[]
