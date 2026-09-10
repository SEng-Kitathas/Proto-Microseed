from pathlib import Path
from tempfile import TemporaryDirectory
import inspect

from microseed.persistence.biography import DevelopmentalBiography


def test_incremental_biography_heads_match_full_reference_for_chain_and_explicit_branch():
    with TemporaryDirectory(prefix='bio-head-index-') as td:
        b=DevelopmentalBiography(Path(td)/'bio.sqlite3')
        try:
            genesis=b.heads(); assert len(genesis)==1
            a=b.append('A',{'x':1})
            assert b.heads()==(a.event_id,)
            # Add one branch from genesis while A remains a head.
            branch=b.append('BRANCH',{'x':2},parents=genesis)
            expected={a.event_id,branch.event_id}
            assert set(b.heads())==expected
            # Default append consumes all current heads exactly as the old full-scan law did.
            joined=b.append('JOIN',{'x':3})
            assert set(joined.parents)==expected
            assert b.heads()==(joined.event_id,)
            full=set(b._events)-{p for ev in b._events.values() for p in ev.parents}
            assert set(b.heads())==full
        finally:b.close()


def test_biography_head_index_rebuilds_exactly_from_durable_events_on_restart():
    with TemporaryDirectory(prefix='bio-head-restart-') as td:
        path=Path(td)/'bio.sqlite3'
        b1=DevelopmentalBiography(path)
        try:
            g=b1.heads(); a=b1.append('A',{'n':1}); b1.append('BRANCH',{'n':2},parents=g)
            before=b1.heads(); before_events=b1.events
        finally:b1.close()
        b2=DevelopmentalBiography(path)
        try:
            assert b2.events==before_events
            assert b2.heads()==before
            assert b2.verify()==(True,())
        finally:b2.close()


def test_biography_verify_detects_derived_head_cache_drift_without_promoting_cache_to_authority():
    with TemporaryDirectory(prefix='bio-head-drift-') as td:
        b=DevelopmentalBiography(Path(td)/'bio.sqlite3')
        try:
            b.append('A',{'n':1})
            b._heads.add('f'*64)
            ok,errors=b.verify()
            assert not ok
            assert errors==('in_memory_database_head_set_mismatch',)
        finally:b.close()


def test_biography_append_and_heads_no_longer_recompute_all_parents_on_normal_append_path():
    heads_src=inspect.getsource(DevelopmentalBiography.heads)
    append_src=inspect.getsource(DevelopmentalBiography.append)
    assert 'self._events.values()' not in heads_src
    assert 'self._heads' in heads_src
    assert 'self.heads()' not in append_src
    assert 'self._heads' in append_src
    assert '_heads.difference_update' in append_src and '_heads.add' in append_src


def test_biography_event_identity_and_parent_set_remain_content_bound_after_indexing():
    with TemporaryDirectory(prefix='bio-head-identity-') as td:
        b=DevelopmentalBiography(Path(td)/'bio.sqlite3')
        try:
            a=b.append('A',{'v':1})
            c=b.append('C',{'v':2})
            assert c.parents==(a.event_id,)
            # Idempotent same append from a different frontier is not falsely reused.
            d=b.append('A',{'v':1})
            assert d.event_id!=a.event_id
            assert d.parents==(c.event_id,)
            assert b.verify()==(True,())
        finally:b.close()
