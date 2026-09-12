from pathlib import Path
import tempfile

from scratch.grounded_language_readout_prototype import grounded_referent_control,derive_grounded_language_readout,attempt_surface_selected_referent
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _build,_history,derive_binding_candidate


def _candidate(prefix:str):
    td=tempfile.TemporaryDirectory(prefix=prefix);ms,world=_build(Path(td.name));train,hold=_history(ms,world);candidate=derive_binding_candidate(ms,train,hold);assert candidate["status"]=="QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE";return td,ms,world,candidate


def _close(td,ms):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()


def test_readable_and_opaque_surfaces_preserve_same_grounded_competence():
    td,ms,world,c=_candidate("lang-readout-")
    try:
        control=grounded_referent_control(ms,c);sig=control["operational_referent_signature_sha256"]
        readable=derive_grounded_language_readout(ms,c,{sig:"target"})
        opaque=derive_grounded_language_readout(ms,c,{sig:"ZXQ-731"})
        assert control["status"]=="CURRENT_GROUNDED_REFERENT_CONTROL"
        for x in (readable,opaque):
            assert x["operational_referent_signature_sha256"]==sig
            assert x["binding_id"]==control["binding_id"]
            assert x["grounded_source_episode_sha256"]==control["grounded_source_episode_sha256"]
            assert x["authority_gain"]==x["language_authority"]=="NONE"
        assert readable["surface_label"]!=opaque["surface_label"]
    finally:_close(td,ms)


def test_surface_alias_or_permutation_cannot_change_referent_identity():
    td,ms,world,c=_candidate("lang-permute-")
    try:
        sig=c["binding"]["operational_referent_signature_sha256"]
        labels=["cup","vessel","R7","◇"]
        outs=[derive_grounded_language_readout(ms,c,{sig:l}) for l in labels]
        assert {o["operational_referent_signature_sha256"] for o in outs}=={sig}
        assert {o["binding_id"] for o in outs}=={c["binding_id"]}
        assert {o["surface_label"] for o in outs}==set(labels)
    finally:_close(td,ms)


def test_fluent_ungrounded_surface_cannot_create_or_select_referent():
    r=attempt_surface_selected_referent(surface_text="the correct object is the red cup",available_referents=("A","B","C"))
    assert r["status"]=="DEFER_UNKNOWN"
    assert r["reason"]=="GROUNDED_BINDING_REQUIRED_BEFORE_LANGUAGE_READOUT"
    assert r["language_authority"]==r["semantic_reference_authority"]==r["execution_authority"]=="NONE"


def test_language_readout_fails_closed_when_grounded_binding_becomes_stale():
    td,ms,world,c=_candidate("lang-stale-")
    try:
        ms.change_capability_dependency("SIG-X",reason="LANGUAGE-READOUT-STALE")
        o=derive_grounded_language_readout(ms,c,{})
        assert o["status"]=="DEFER_UNKNOWN"
        assert o["readout_status"]=="NO_LANGUAGE_READOUT"
    finally:_close(td,ms)


def test_language_disabled_control_retains_grounded_referent_competence():
    td,ms,world,c=_candidate("lang-disabled-")
    try:
        control=grounded_referent_control(ms,c)
        readout=derive_grounded_language_readout(ms,c,{control["operational_referent_signature_sha256"]:"readable-name"})
        assert control["status"]=="CURRENT_GROUNDED_REFERENT_CONTROL"
        assert control["operational_referent_signature_sha256"]==readout["operational_referent_signature_sha256"]
        assert control["binding_id"]==readout["binding_id"]
        assert "surface_label" not in control
    finally:_close(td,ms)
