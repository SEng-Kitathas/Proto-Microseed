
from __future__ import annotations

from tests.embodiment.test_hardening_sh6_endogenous_opaque_vocabulary_growth import (
    _discover_second_stage,
    _qualify_second_stage,
    _register_request_base,
)
from tests.embodiment.test_ms1986_owned_learned_bucket_composition import _prepare_owned_sources
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def test_source_projection_drift_stales_bound_request_specializations_through_derived_projection_dependency():
    td, world, m, pa, pb = _prepare_owned_sources('hardening-sh6-cascade-')
    calls = []
    try:
        _, candidate = _discover_second_stage(m, pa, pb)
        buckets = tuple(sorted({bucket for _, bucket in candidate.key_to_bucket}))
        admitted = _qualify_second_stage(m, candidate, pa, pb)
        _register_request_base(m, calls)
        bound = tuple(m.derive_bound_request_specialization('REQ-SH6', admitted.projection_id, bucket) for bucket in buckets)
        assert all(m.capabilities.is_current(x.capability_id) for x in bound)
        assert m.epistemic_projections.is_current(admitted.projection_id, admitted.epoch)

        packet = m.change_epistemic_projection(
            'P-MS1986-A', new_signature_sha256='b' * 64, reason='SH6_SOURCE_PROJECTION_DRIFT_CASCADE_HOSTILE'
        )

        assert admitted.projection_id in packet['stale_projection_ids'], packet
        assert set(x.capability_id for x in bound).issubset(set(packet['stale_capability_ids'])), packet
        assert not m.epistemic_projections.records[admitted.projection_id].current
        assert all(not m.capabilities.is_current(x.capability_id) for x in bound)
        assert calls == []
        assert packet['semantic_projection_authority'] == packet['raw_projection_discovery_authority'] == 'NONE'
    finally:
        _close(m); world.close(); td.cleanup()
