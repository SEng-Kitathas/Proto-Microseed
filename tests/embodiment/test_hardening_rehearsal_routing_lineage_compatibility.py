
from __future__ import annotations

from dataclasses import replace

from microseed import Authority
from microseed.development.rehearsal import CounterfactualRehearsalProposal


def _legacy():
    return CounterfactualRehearsalProposal(
        proposal_id='REHEARSAL-legacy',start_state_id='S0',sequence=('A',),final_state_id='S1',
        predicted_value_effect=1.0,predicted_final_value=2.0,residual_pressure=0.0,
        transition_relation_digests=('r'*64,),source_evidence_ids=('E1',),
        capability_epochs=(('A',0),),frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
    )


def test_nonrouted_legacy_serialization_omits_new_optional_routing_fields_and_roundtrips_digest_exactly():
    p=_legacy(); packet=p.serializable()
    assert 'projection_routing_id' not in packet
    assert 'projection_bucket_id' not in packet
    q=CounterfactualRehearsalProposal.from_serializable(packet)
    assert q.projection_routing_id is None and q.projection_bucket_id is None
    assert q.serializable()==packet
    assert q.digest()==p.digest()


def test_routed_selection_identity_changes_by_bucket_while_nonrouting_semantics_stay_identical():
    base=_legacy()
    a=replace(base,projection_routing_id='BIND-X',projection_bucket_id='BUCKET-A')
    b=replace(base,projection_routing_id='BIND-X',projection_bucket_id='BUCKET-B')
    assert a.sequence==b.sequence and a.transition_relation_digests==b.transition_relation_digests
    assert a.digest()!=b.digest()
    assert a.serializable()['projection_bucket_id']=='BUCKET-A'
    assert b.serializable()['projection_bucket_id']=='BUCKET-B'
    assert CounterfactualRehearsalProposal.from_serializable(a.serializable()).digest()==a.digest()
