from pathlib import Path
from tempfile import TemporaryDirectory
import inspect

import pytest

from microseed import Microseed
from microseed.development.action_closure import ActionClosureRegistry, ActionExecutionRecord
from microseed.persistence.store import StateStore
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_obs,_close


def _execution(i: int, intent: str | None = None) -> ActionExecutionRecord:
    return ActionExecutionRecord(
        execution_id=f'E-{i}', intent_id=intent or f'I-{i}', capability_id='C', capability_epoch=0,
        start_state_id='S', handler_result_sha256='a'*64,
    )


def test_action_closure_executed_intent_index_preserves_duplicate_semantics_without_values_scan():
    reg=ActionClosureRegistry()
    for i in range(2000): reg.add_execution(_execution(i))
    assert reg.has_executed_intent('I-0')
    assert reg.has_executed_intent('I-1999')
    assert not reg.has_executed_intent('I-MISSING')
    with pytest.raises(ValueError,match='ACTION_INTENT_ALREADY_EXECUTED'):
        reg.add_execution(_execution(3000,'I-1999'))
    # The implementation must be index-backed rather than a hidden full values scan.
    src=inspect.getsource(ActionClosureRegistry.add_execution)
    assert '.values()' not in src and 'has_executed_intent' in src


def test_action_closure_index_is_rebuilt_by_same_add_execution_path_used_during_replay():
    reg=ActionClosureRegistry()
    original=tuple(_execution(i) for i in range(11))
    for row in original: reg.add_execution(row)
    rebuilt=ActionClosureRegistry()
    for row in reg.executions.values(): rebuilt.add_execution(ActionExecutionRecord.from_serializable(row.serializable()))
    assert rebuilt.executions==reg.executions
    assert rebuilt._executed_intent_ids=={row.intent_id for row in original}
    assert all(rebuilt.has_executed_intent(row.intent_id) for row in original)


def test_state_store_latest_event_seq_and_suffix_are_exact_equivalents_of_full_history_queries():
    with TemporaryDirectory(prefix='substrate-store-index-') as td:
        store=StateStore(Path(td)/'state.sqlite3')
        try:
            seqs=[]
            for i,kind in enumerate(('BOOT','A','B','BOOT','A','BOOT','C')):
                seqs.append(store.append(kind,{'i':i}))
            all_rows=store.events()
            assert store.latest_event_seq('BOOT')==max(r['seq'] for r in all_rows if r['kind']=='BOOT')
            assert store.latest_event_seq('NEVER') is None
            pivot=seqs[2]
            assert store.events_after(pivot)==[r for r in all_rows if r['seq']>pivot]
            assert store.events_after(pivot,kinds=('A','C'))==[r for r in all_rows if r['seq']>pivot and r['kind'] in {'A','C'}]
            assert store.events_after(pivot,limit=2)==[r for r in all_rows if r['seq']>pivot][:2]
            indexes={r[1] for r in store.conn.execute("pragma index_list('events')").fetchall()}
            assert 'idx_events_kind_seq' in indexes
        finally:
            store.conn.close()


def test_current_runtime_boot_seq_uses_indexed_latest_event_query_not_full_event_materialization():
    td,m,world,seeded=_setup('SUBSTRATE-BOOT-INDEX')
    try:
        expected=m.store.latest_event_seq('BOOT')
        assert expected is not None
        original=m.store.events
        def forbidden():
            raise AssertionError('FULL_EVENT_MATERIALIZATION_FORBIDDEN_FOR_BOOT_SEQ')
        m.store.events=forbidden
        assert m._current_runtime_boot_seq()==expected
        m.store.events=original
    finally:
        _close(m);td.cleanup()


def test_store_aware_operand_window_uses_post_boot_suffix_query_not_full_event_materialization():
    td,m,world,seeded=_setup('SUBSTRATE-SUFFIX-INDEX')
    try:
        _obs(m,('R4','T9'),410000,'SUBSTRATE-SUFFIX')
        original=m.store.events
        def forbidden():
            raise AssertionError('FULL_EVENT_MATERIALIZATION_FORBIDDEN_FOR_OPERAND_SUFFIX')
        m.store.events=forbidden
        out=m._derive_current_store_aware_bounded_operand_window(max_events=65536,min_arity=2,max_arity=4)
        assert out['status']=='CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW',out
        assert out['derived_arity']==2
        m.store.events=original
    finally:
        _close(m);td.cleanup()


def test_indexing_surfaces_carry_no_new_authority_or_mutation_semantics():
    store_src=inspect.getsource(StateStore)
    assert 'update events' not in store_src.lower()
    assert 'delete from events' not in store_src.lower()
    assert 'create index if not exists idx_events_kind_seq' in store_src.lower()
    assert 'latest_event_seq' in store_src and 'events_after' in store_src
    closure_src=inspect.getsource(ActionClosureRegistry)
    assert '_executed_intent_ids' in closure_src
    assert 'Authority.' not in inspect.getsource(ActionClosureRegistry.has_executed_intent)
