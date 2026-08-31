from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Authority, CapabilityContract, Microseed, QualificationState, QueryObligation
from microseed.cognition.referents import derive_affordance_relative_referent_signature, nominate_by_boundary_coherence
from scratch.ms1958_proto_referent_boundary_coherence import boundaries

ACT = QueryObligation("BODY-ACT", "opaque current effect", Authority.EFFECT, operational_scope_id="S")
OBS = QueryObligation("BODY-OBS", "opaque sensor observation", Authority.OBSERVATION_ONLY, operational_scope_id="S")


class BodyWorld:
    def __init__(self, *, perfect_coupling: bool = False):
        self.perfect_coupling = bool(perfect_coupling)
        self.reset()

    def reset(self):
        self.state = [0, 0, 0]  # evaluator-only B/T/C slots
        self.connected = True
        self.mapping = (0, 0, 1, 1, 2, 2)
        self.scales = (1, 1, 1, 1, 1, 1)
        self.offsets = (7, 31, 79, 127, 181, 239)

    def configure_session_b(self):
        self.state = [0, 0, 0]
        self.connected = True
        self.mapping = (2, 0, 1, 2, 0, 1)
        self.scales = (11, 13, 17, 19, 23, 29)
        self.offsets = (307, 401, 503, 607, 709, 811)

    def move(self):
        self.state[0] += 1
        if self.connected or self.perfect_coupling:
            self.state[1] += 1
        return {"opaque_effect": "FX-MOVE"}

    def detach(self):
        if not self.perfect_coupling:
            self.connected = False
        return {"opaque_effect": "FX-DETACH"}

    def external_pulse(self):
        self.state[2] += 1

    def observe(self):
        counts = {0: 0, 1: 0, 2: 0}
        out = []
        for i, source in enumerate(self.mapping):
            local = counts[source]; counts[source] += 1
            x = self.state[source]
            raw = self.scales[i] * (x * x * (source + 5) + x * (source + 17) + 3 * local) + self.offsets[i]
            out.append(raw)
        return tuple(out)


def _cap(cid: str, authority: Authority, qid: str, handler):
    return CapabilityContract(
        cid, "opaque", {}, {}, ("NO_SEMANTIC_SELF_AUTHORITY",), (), authority,
        ("MS2044",), "CURRENT", {}, query_obligation_id=qid,
        qualification=QualificationState.SHADOW_QUALIFIED, handler=handler,
        operational_scope_id="S",
    )


def _build(root: Path, *, perfect_coupling: bool = False):
    ms = Microseed(root)
    world = BodyWorld(perfect_coupling=perfect_coupling)
    ms.register_capability(_cap("FX-MOVE", Authority.EFFECT, "BODY-ACT", lambda **_: world.move()))
    ms.register_capability(_cap("FX-DETACH", Authority.EFFECT, "BODY-ACT", lambda **_: world.detach()))
    ms.register_capability(_cap("OBS-BTC", Authority.OBSERVATION_ONLY, "BODY-OBS", lambda **_: {"channels": world.observe()}))
    return ms, world


def _observe(ms: Microseed) -> tuple[int, ...]:
    r = ms.capabilities.invoke("OBS-BTC", OBS)
    return tuple(r["value"]["channels"])


def _apply(ms: Microseed, world: BodyWorld, event: str) -> None:
    if event in {"FX-MOVE", "FX-DETACH"}:
        ms.capabilities.invoke(event, ACT)
    elif event == "EXT-PULSE":
        world.external_pulse()
    else:
        raise ValueError(event)


def _collect(ms: Microseed, world: BodyWorld, schedule: tuple[str, ...], evaluator_mapping: tuple[int, ...]):
    samples = [_observe(ms)]
    for event in schedule:
        _apply(ms, world, event); samples.append(_observe(ms))
    traces = tuple(tuple(sample[i] for sample in samples) for i in range(len(samples[0])))
    b = boundaries(traces)
    n = nominate_by_boundary_coherence(b)
    rows = []
    for group in n.groups:
        sources = tuple(sorted({evaluator_mapping[i] for i in group}))
        sig = derive_affordance_relative_referent_signature(b, group, schedule)
        assert sig.status == "OPERATIONAL_REFERENT_SIGNATURE_DERIVED"
        rows.append({
            "group": list(group),
            "evaluator_sources_for_test_only": list(sources),
            "signature": sig.signature_sha256,
            "response_rows": [[a, list(bits)] for a, bits in sig.action_response_rows],
        })
    return {"status": n.status, "groups": rows, "reason": n.reason, "identity_authority": n.identity_authority}


def _by_singleton_source(result):
    return {row["evaluator_sources_for_test_only"][0]: row for row in result["groups"] if len(row["evaluator_sources_for_test_only"]) == 1}


def _response_map(row):
    return {str(a): tuple(bool(x) for x in bits) for a, bits in row["response_rows"]}


def _derive_operational_roles(ms: Microseed, result: dict) -> dict:
    owned_effect_ids = {
        cid for cid, contract in ms.capabilities.contracts.items()
        if contract.authority == Authority.EFFECT and ms.capabilities.is_current(cid)
    }
    roles = []
    for row in result["groups"]:
        responses = _response_map(row)
        move = responses.get("FX-MOVE", ())
        ext = responses.get("EXT-PULSE", ())
        if move and all(move):
            relation = "EFFERENCE_CONTINGENT_OPERATIONAL_BODY_RELATION"
        elif ext and all(ext) and (not move or not any(move)):
            relation = "INDEPENDENTLY_CHANGING_OPERATIONAL_COUNTERPARTY_LIKE_RELATION"
        else:
            relation = "OTHER_OR_PARTIALLY_COUPLED_OPERATIONAL_RELATION"
        roles.append({
            "group": row["group"],
            "signature": row["signature"],
            "relation": relation,
            "owned_effect_ids": sorted(owned_effect_ids),
            "semantic_self_authority": "NONE",
            "numerical_body_identity_authority": "NONE",
            "other_agent_identity_authority": "NONE",
        })
    return {"roles": roles, "owned_effect_ids": sorted(owned_effect_ids)}


def run_normal() -> dict:
    with tempfile.TemporaryDirectory(prefix="ms2044-body-") as td:
        ms, world = _build(Path(td))
        try:
            s1 = ("FX-MOVE", "EXT-PULSE", "FX-MOVE", "FX-DETACH", "FX-MOVE", "EXT-PULSE", "FX-MOVE")
            a = _collect(ms, world, s1, (0, 0, 1, 1, 2, 2))
            assert a["status"] == "REFERENT_PARTITION_NOMINATED", a
            aa = _by_singleton_source(a); assert set(aa) == {0, 1, 2}, a
            roles_a = _derive_operational_roles(ms, a)

            world.configure_session_b()
            s2 = ("EXT-PULSE", "FX-MOVE", "FX-MOVE", "FX-DETACH", "EXT-PULSE", "FX-MOVE", "FX-MOVE")
            b = _collect(ms, world, s2, (2, 0, 1, 2, 0, 1))
            assert b["status"] == "REFERENT_PARTITION_NOMINATED", b
            bb = _by_singleton_source(b); assert set(bb) == {0, 1, 2}, b
            roles_b = _derive_operational_roles(ms, b)

            # Affordance signatures remain stable under sensor permutation, appearance transform,
            # and external-event ordering when the per-handle response structure is unchanged.
            assert {k: aa[k]["signature"] for k in aa} == {k: bb[k]["signature"] for k in bb}
            role_by_source_a = {src: next(x["relation"] for x in roles_a["roles"] if x["signature"] == aa[src]["signature"]) for src in aa}
            role_by_source_b = {src: next(x["relation"] for x in roles_b["roles"] if x["signature"] == bb[src]["signature"]) for src in bb}
            assert role_by_source_a == role_by_source_b
            assert role_by_source_a[0] == "EFFERENCE_CONTINGENT_OPERATIONAL_BODY_RELATION"
            assert role_by_source_a[1] == "OTHER_OR_PARTIALLY_COUPLED_OPERATIONAL_RELATION"
            assert role_by_source_a[2] == "INDEPENDENTLY_CHANGING_OPERATIONAL_COUNTERPARTY_LIKE_RELATION"
            assert roles_a["owned_effect_ids"] == ["FX-DETACH", "FX-MOVE"]
            return {
                "status": "PASS",
                "session_a": a,
                "session_b": b,
                "operational_roles_by_evaluator_source_for_test_only": {"B": role_by_source_a[0], "T": role_by_source_a[1], "C": role_by_source_a[2]},
                "owned_effect_ids": roles_a["owned_effect_ids"],
                "semantic_self_authority": "NONE",
                "numerical_body_identity_authority": "NONE",
                "other_agent_identity_authority": "NONE",
                "semantic_reference_authority": "NONE",
                "language_authority": "NONE",
            }
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def run_perfect_coupling_hostile() -> dict:
    with tempfile.TemporaryDirectory(prefix="ms2044-perfect-") as td:
        ms, world = _build(Path(td), perfect_coupling=True)
        try:
            schedule = ("FX-MOVE", "EXT-PULSE", "FX-MOVE", "FX-DETACH", "FX-MOVE", "EXT-PULSE", "FX-MOVE")
            r = _collect(ms, world, schedule, (0, 0, 1, 1, 2, 2))
            # Body-like and tool-like channels have exactly the same local boundary structure
            # and therefore remain one coherent operational group.
            merged = [row for row in r["groups"] if set(row["evaluator_sources_for_test_only"]) == {0, 1}]
            assert len(merged) == 1, r
            assert len(merged[0]["group"]) == 4
            roles = _derive_operational_roles(ms, r)
            merged_role = next(x for x in roles["roles"] if x["signature"] == merged[0]["signature"])
            assert merged_role["relation"] == "EFFERENCE_CONTINGENT_OPERATIONAL_BODY_RELATION"
            assert merged_role["semantic_self_authority"] == "NONE"
            return {
                "status": "PASS_SYMMETRY_BLOCK",
                "merged_sources_for_test_only": ["B", "T"],
                "merged_group": merged[0]["group"],
                "operational_relation": merged_role["relation"],
                "body_vs_tool_identity": "UNIDENTIFIABLE_FROM_LOCAL_EFFERENCE_STRUCTURE_ALONE",
                "required_breaker": "ASYMMETRIC_COUPLING_OR_ADDITIONAL_CONTINUITY_EVIDENCE",
                "semantic_self_authority": "NONE",
                "numerical_body_identity_authority": "NONE",
            }
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()


def run_ms2044() -> dict:
    normal = run_normal(); perfect = run_perfect_coupling_hostile()
    return {
        "status": "OPERATIONAL_BODY_COUNTERPARTY_BOUNDARY_EARNED",
        "normal": normal,
        "perfect_coupling_hostile": perfect,
        "earned": "OWNED_EFFECT_PLUS_ASYMMETRIC_COUPLING_BREAK_CAN_GROUND_A_BOUNDED_OPERATIONAL_BODY_RELATION_WITHOUT_SEMANTIC_SELF_AUTHORITY",
        "counterparty_law": "INDEPENDENTLY_CHANGING_COUNTERPARTY_RELATION_CAN_REMAIN_OPERATIONALLY_DISTINCT_FROM_EFFERENCE_CONTINGENT_BODY_RELATION",
        "symmetry_law": "PERFECT_COUPLING_SYMMETRY_BLOCKS_BODY_VS_TOOL_IDENTITY",
        "semantic_self_authority": "NONE",
        "language_authority": "NONE",
        "new_self_or_body_manager_required": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2044(), indent=2, sort_keys=True, default=str))
