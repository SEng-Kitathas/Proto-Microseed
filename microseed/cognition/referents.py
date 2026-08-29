from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Hashable
import hashlib
import json


@dataclass(frozen=True)
class ReferentNomination:
    status: str
    groups: tuple[tuple[int,...],...]
    reason: str
    identity_authority: str = "NONE"


def nominate_by_boundary_coherence(channel_boundaries: Sequence[Sequence[Hashable]]) -> ReferentNomination:
    """Nominate channel partitions by boundary coherence, never object identity.

    Equal/coherent signatures may suggest grouping. Symmetric equally lawful groupings
    remain UNKNOWN rather than receiving an invented object label.
    """
    sig_to_channels: dict[tuple[Hashable,...], list[int]]={}
    for i,b in enumerate(channel_boundaries):
        sig_to_channels.setdefault(tuple(b),[]).append(i)
    groups=tuple(tuple(v) for _,v in sorted(sig_to_channels.items(),key=lambda kv:kv[1][0]))
    if len(groups)==1 and len(channel_boundaries)>1:
        return ReferentNomination("UNKNOWN_INCOMPLETE",groups,
                                  "BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS")
    return ReferentNomination("REFERENT_PARTITION_NOMINATED",groups,
                              "BOUNDARY_COHERENCE_ONLY")


@dataclass(frozen=True)
class OperationalReferentSignature:
    status: str
    signature_sha256: str | None
    action_response_rows: tuple[tuple[str, tuple[bool, ...]], ...]
    reason: str
    authority: str = "NONE"
    identity_authority: str = "NONE"
    semantic_reference_authority: str = "NONE"


def derive_affordance_relative_referent_signature(
    channel_boundaries: Sequence[Sequence[int]],
    group: Sequence[int],
    opaque_action_sequence: Sequence[Hashable],
) -> OperationalReferentSignature:
    """Derive a protocol-relative content signature for one nominated channel group.

    The signature records which *opaque action handles* coincide with changes in an
    already-nominated boundary-coherent group. It can support re-association across
    channel permutation and protocol order changes when the action handles remain
    current/stable. It does not establish numerical object identity, semantic
    reference, or action meaning. Joint sensor+actuator alias symmetry remains
    unidentifiable without additional continuity/asymmetric evidence.
    """
    members=tuple(int(i) for i in group)
    if not members:
        return OperationalReferentSignature(
            "UNKNOWN_INCOMPLETE",None,(),"EMPTY_REFERENT_GROUP"
        )
    if any(i < 0 or i >= len(channel_boundaries) for i in members):
        return OperationalReferentSignature(
            "UNKNOWN_INCOMPLETE",None,(),"REFERENT_GROUP_CHANNEL_OUT_OF_RANGE"
        )
    signatures={tuple(int(x) for x in channel_boundaries[i]) for i in members}
    if len(signatures)!=1:
        return OperationalReferentSignature(
            "UNKNOWN_INCOMPLETE",None,(),"GROUP_NOT_BOUNDARY_COHERENT"
        )
    boundary=set(next(iter(signatures)))
    actions=tuple(str(x) for x in opaque_action_sequence)
    if not actions:
        return OperationalReferentSignature(
            "UNKNOWN_INCOMPLETE",None,(),"EMPTY_OPAQUE_ACTION_SEQUENCE"
        )
    rows=[]
    for action in sorted(set(actions)):
        positions=tuple(i+1 for i,a in enumerate(actions) if a==action)
        rows.append((action,tuple(pos in boundary for pos in positions)))
    frozen=tuple(rows)
    digest=hashlib.sha256(
        json.dumps({"opaque_action_response":frozen},sort_keys=True,separators=(",",":"),default=str).encode()
    ).hexdigest()
    return OperationalReferentSignature(
        "OPERATIONAL_REFERENT_SIGNATURE_DERIVED",digest,frozen,
        "AFFORDANCE_RELATIVE_BOUNDARY_RESPONSE_ONLY"
    )
