
from __future__ import annotations

import inspect

from microseed import Microseed
from tests.embodiment.test_frontier_a_target_bound_request_program_construction import (
    _learn_two_bucket_projection,_register_request_base,_add_program_history,
)
from scratch.ms1996_endogenous_program_caller_choice_elimination import OBLIGATION,_close
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture


def test_projection_learning_endogenously_produces_opaque_target_vocabulary_without_semantic_target_names():
    td,m,calls,_,_,_=fixture()
    try:
        rec,cand,buckets=_learn_two_bucket_projection(m,projection_id='HARD-A-P',salt=11)
        assert len(buckets)==2
        assert set(buckets)=={b for _,b in cand.key_to_bucket}
        assert all(isinstance(x,str) and x for x in buckets)
        assert rec.projection_origin=='ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'
        # No semantic target/goal vocabulary is part of the learned record.
        blob=str(rec.serializable()).lower()+str(cand.serializable()).lower()
        assert 'desired_state' not in blob and 'semantic_goal' not in blob
    finally:_close(td,m)


def test_bound_request_specialization_still_requires_explicit_exact_learned_bucket_materialization():
    sig=inspect.signature(Microseed.derive_bound_request_specialization)
    assert 'target_token' in sig.parameters
    td,m,calls,_,_,_=fixture();req_calls=[]
    try:
        rec,cand,buckets=_learn_two_bucket_projection(m,projection_id='HARD-A-P2',salt=12)
        _register_request_base(m,base_id='REQ-HARD-A',calls=req_calls)
        before=set(m.capabilities.contracts)
        # Learning/qualifying the projection alone does not silently mint executable
        # target-specialized capabilities.
        assert not any(cid.startswith('bound-request-') for cid in before)
        b0=m.derive_bound_request_specialization('REQ-HARD-A',rec.projection_id,buckets[0])
        after0=set(m.capabilities.contracts)
        assert b0.capability_id in after0-before
        # The sibling learned bucket still has no executable specialization until an
        # explicit materialization call is made for that exact bucket.
        sibling=[cid for cid,c in m.capabilities.contracts.items() if cid!=b0.capability_id and getattr(c,'boundary',{}).get('fixed_target_bucket')==buckets[1]]
        assert sibling==[]
    finally:_close(td,m)


def test_program_constructor_cannot_use_unmaterialized_target_atom_but_becomes_caller_sequence_free_after_all_atoms_exist():
    td,m,calls,_,_,_=fixture();req_calls=[]
    try:
        rec,cand,buckets=_learn_two_bucket_projection(m,projection_id='HARD-A-P3',salt=13)
        _register_request_base(m,base_id='REQ-HARD-A3',calls=req_calls)
        b0=m.derive_bound_request_specialization('REQ-HARD-A3',rec.projection_id,buckets[0])
        # Histories cannot contain/use a capability that does not yet exist in the
        # organism's current EFFECT alphabet. This localizes the remaining scaffold.
        effect_ids={cid for cid,c in m.capabilities.contracts.items() if m.capabilities.is_current(cid) and c.authority.value=='EFFECT'}
        assert b0.capability_id in effect_ids
        assert not any(m.capabilities.is_current(cid) and getattr(c,'boundary',{}).get('fixed_target_bucket')==buckets[1] for cid,c in m.capabilities.contracts.items())
        b1=m.derive_bound_request_specialization('REQ-HARD-A3',rec.projection_id,buckets[1])
        steps=(b0.capability_id,b1.capability_id,b0.capability_id)
        for prefix,effect,end in [('P1',1.0,'u'),('P2',1.0,'u'),('N1',-1.0,'v'),('N2',-1.0,'v')]:
            _add_program_history(m,steps,f'HA-{prefix}',effect,end)
        generated=m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(obligation=OBLIGATION,max_nodes=64)
        assert steps in {tuple(x) for x in generated['programs']}
        assert generated['execution_authority']=='NONE'
        assert req_calls==[]
    finally:_close(td,m)
