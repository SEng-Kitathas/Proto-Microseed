from __future__ import annotations
import json, shutil, sqlite3, tempfile
from pathlib import Path
import pytest
from microseed import Microseed
from microseed.persistence.biography import BiographyIntegrityError, DevelopmentalBiography


def close(m):
    m.store.conn.close(); m.evidence.conn.close(); m.biography.close()


def test_developmental_biography_reconstructs_across_restart():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td); m=Microseed(p)
        m.path.append("LAB_MARKER", {"x": 1})
        before=m.biography_witness(); count_before=len(m.path.events); close(m)
        m2=Microseed(p); after=m2.biography_witness()
        assert after["integrity"] == "VERIFIED"
        assert any(e["kind"] == "LAB_MARKER" for e in after["events"])
        assert len(m2.path.events) >= count_before
        assert after["identity_claim"] == "NOT_QUALIFIED"
        close(m2)


def test_biography_payload_tamper_is_rejected_on_restart():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td); m=Microseed(p); m.path.append("LAB_TAMPER", {"x":1}); close(m)
        db=sqlite3.connect(p/'biography.sqlite3')
        eid=db.execute("select event_id from biography_events where kind='LAB_TAMPER'").fetchone()[0]
        db.execute("update biography_events set payload=? where event_id=?", (json.dumps({"x":999}), eid)); db.commit(); db.close()
        with pytest.raises(BiographyIntegrityError): Microseed(p)


def test_copied_state_can_diverge_as_common_ancestry_without_selfhood_claim():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); a=root/'a'; m=Microseed(a); m.path.append("PREFIX", {"x":0}); close(m)
        b=root/'b'; shutil.copytree(a,b)
        ma=Microseed(a); mb=Microseed(b)
        ma.path.append("LEFT", {"x":1}); mb.path.append("RIGHT", {"x":2})
        assert ma.compare_biography(mb.biography_witness()) == "COMMON_ANCESTRY_DIVERGED"
        assert ma.biography_witness()["identity_claim"] == "NOT_QUALIFIED"
        assert mb.biography_witness()["identity_claim"] == "NOT_QUALIFIED"
        close(ma);close(mb)


def test_migrated_copy_with_only_one_continuation_is_descendant_lineage():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); a=root/'a'; m=Microseed(a); m.path.append("PREFIX", {"x":0}); base=m.biography_witness(); close(m)
        b=root/'b'; shutil.copytree(a,b); mb=Microseed(b); mb.path.append("CONTINUE", {"x":1})
        assert DevelopmentalBiography.relation(base, mb.biography_witness()) == "DESCENDANT_CONTINUATION"
        close(mb)


def test_digest_is_not_selfhood_or_semantic_sufficiency():
    with tempfile.TemporaryDirectory() as td:
        m=Microseed(Path(td)); w=m.biography_witness()
        assert w["graph_digest"]
        assert w["authority"] == "OPERATIONAL_DEVELOPMENTAL_LINEAGE_ONLY"
        assert w["identity_claim"] == "NOT_QUALIFIED"
        close(m)
