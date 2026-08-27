from __future__ import annotations
import tempfile
from pathlib import Path
from tests.embodiment.test_ms1754_pass07_relational_discovery_from_admitted_history import build_world, add_transition


def test_injected_execution_record_without_ordinary_execution_event_is_rejected_after_pass09_repair():
    with tempfile.TemporaryDirectory(prefix='ms1755-') as td:
        m,outcomes=build_world(Path(td))
        add_transition(m,outcomes,0,'s0','A','m0')
        assert not [e for e in m.store.events() if e['kind']=='BOUNDED_ACTION_EXECUTED']
        r=m.derive_admitted_opaque_transition_sample('X-0')
        assert r=={'status':'ABSTAIN','reason':'AUTHENTICATED_ORDINARY_EXECUTION_REQUIRED','authority':'NONE'}
