from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Microseed
from scratch.lang_c08d_postrestart_native_relation_rederivation import (
    OpaqueTwoLocusWorld, _attach_runtime_surface, _close, _fresh_owned_relation,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_c08i_native_pair_harvest import (
    _passive_referent_exposure, _qualification_mapping, _registration_records,
)


def _observe_sequence(ms: Microseed, tokens: tuple[str,str], *, phase: str, base: int):
    out=[]
    for offset,token in enumerate(tokens):
        row=observe_opaque_token(ms,token,base+offset,phase=phase)
        assert row['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',row
        out.append(row)
    return out


def _seed_current_native_referent_associations(ms: Microseed, world: OpaqueTwoLocusWorld, token_x: str, token_y: str):
    shared=_fresh_owned_relation(ms,world,tag='SYS-RECOMB-SEED',serial_base=0)
    profiles={p['exclusive_action_id']:p for p in shared['profiles']['profiles']}
    sig_x=str(profiles['QX']['operational_referent_signature_sha256'])
    sig_y=str(profiles['QY']['operational_referent_signature_sha256'])
    for i in range(6):
        locus='X' if i%2==0 else 'Y'
        token=token_x if locus=='X' else token_y
        _passive_referent_exposure(
            ms,world,tag=f'SYS-RECOMB-REF-{i}',locus=locus,token=token,
            index=i,phase='SYS-RECOMB-REF',
        )
    lifecycle=ms.harvest_qualify_and_register_current_opaque_evidence_associations(max_records=16384)
    assert lifecycle['status']=='HARVESTED_NATIVE_OPAQUE_ASSOCIATIONS_EPISTEMICALLY_QUALIFIED_AND_REGISTERED',lifecycle
    assert tuple(lifecycle['qualifications']['scopes'])==('NATIVE_TOKEN_REFERENT',),lifecycle
    mapping=_qualification_mapping(lifecycle,'NATIVE_TOKEN_REFERENT')
    records=_registration_records(lifecycle,'NATIVE_TOKEN_REFERENT')
    assert mapping=={token_x:sig_x,token_y:sig_y},(mapping,sig_x,sig_y)
    for token,profile_key in ((token_x,'QX'),(token_y,'QY')):
        current=ms.assess_opaque_evidence_association_currentness(
            records[token],witness_evidence_id=str(profiles[profile_key]['evidence_id'])
        )
        assert current['status']=='CURRENTNESS_CONFIRMED',current
    qid=str(lifecycle['qualifications']['results']['NATIVE_TOKEN_REFERENT']['qualification']['qualification_id'])
    return {'profiles':profiles,'sig_x':sig_x,'sig_y':sig_y,'records':records,'qualification_id':qid}


def _composition_rows(ms: Microseed):
    return tuple(
        row for row in ms.evidence.list()
        if (row.get('payload') or {}).get('kind')=='OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE'
    )


def run_campaign(token_x: str='R4', token_y: str='T9', sensor_transform=None) -> dict[str,object]:
    with tempfile.TemporaryDirectory(prefix='lang-systematic-heldout-b2-') as td:
        root=Path(td); world=OpaqueTwoLocusWorld()
        if sensor_transform is not None:
            world.sensor_transform=sensor_transform
        ms1=Microseed(root)
        try:
            _attach_runtime_surface(ms1,world,'SYS-RECOMB-R1')
            seeded=_seed_current_native_referent_associations(ms1,world,token_x,token_y)
            sig_x=seeded['sig_x'];sig_y=seeded['sig_y'];records=seeded['records'];qid=seeded['qualification_id']
            action_ids_before=set(ms1.capabilities.contracts)
            assert _composition_rows(ms1)==()

            # Training-side composition evidence: only XY is ever composed.
            _observe_sequence(ms1,(token_x,token_y),phase='SYS-RECOMB-TRAIN-XY',base=1000)
            xy=ms1.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
            assert xy['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',xy
            assert xy['ordered_operational_referent_signatures']==(sig_x,sig_y)
            before_yx={str((row['payload'] or {}).get('composition_content_digest_sha256')) for row in _composition_rows(ms1)}
            assert before_yx=={xy['composition_content_digest_sha256']},before_yx

            # Held-out recombination: YX components are known/current, but YX composition has never existed.
            _observe_sequence(ms1,(token_y,token_x),phase='SYS-RECOMB-HELDOUT-YX',base=1100)
            yx=ms1.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
            assert yx['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',yx
            assert yx['ordered_operational_referent_signatures']==(sig_y,sig_x)
            assert yx['composition_content_digest_sha256'] not in before_yx
            assert yx['composition_content_digest_sha256']!=xy['composition_content_digest_sha256']
            assert yx['operator_owner']=='MICROSEED_NATIVE_B2_ORDERED_COMPOSITION'
            assert yx['caller_supplied_token_operands']==yx['caller_supplied_operand_order']=='NO'
            assert yx['caller_supplied_association_ids']==yx['caller_supplied_referent_identity']=='NO'
            assert yx['caller_supplied_output_evidence_id']=='NO'

            same=ms1.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
            assert same['composition_content_digest_sha256']==yx['composition_content_digest_sha256']
            assert same['composition_record_status']=='COMPOSITION_EVIDENCE_ALREADY_PRESENT'

            _observe_sequence(ms1,(token_x,token_x),phase='SYS-RECOMB-DUP',base=1200)
            duplicate=ms1.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
            assert duplicate['status']=='DEFER_UNKNOWN' and duplicate['reason']=='INDEPENDENT_NATIVE_REFERENT_OPERANDS_REQUIRED',duplicate

            _observe_sequence(ms1,(token_x,'UNSEEN'),phase='SYS-RECOMB-UNSEEN',base=1300)
            unseen=ms1.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
            assert unseen['status']=='DEFER_UNKNOWN' and unseen['reason']=='UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED',unseen
            assert set(ms1.capabilities.contracts)==action_ids_before
            xy_digest=str(xy['composition_content_digest_sha256']);yx_digest=str(yx['composition_content_digest_sha256'])
        finally:
            _close(ms1)

        ms2=Microseed(root)
        try:
            no_current=ms2.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
            assert no_current['status']=='DEFER_UNKNOWN' and no_current['reason']=='TWO_CURRENT_RUNTIME_OBSERVED_TOKEN_OPERANDS_REQUIRED',no_current
            _attach_runtime_surface(ms2,world,'SYS-RECOMB-R2')
            restarted=_fresh_owned_relation(ms2,world,tag='SYS-RECOMB-R2-SEED',serial_base=3000)
            profiles2={p['exclusive_action_id']:p for p in restarted['profiles']['profiles']}
            assert str(profiles2['QX']['operational_referent_signature_sha256'])==sig_x
            assert str(profiles2['QY']['operational_referent_signature_sha256'])==sig_y
            for token,key in ((token_x,'QX'),(token_y,'QY')):
                current=ms2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles2[key]['evidence_id']))
                assert current['status']=='CURRENTNESS_CONFIRMED',current
            _observe_sequence(ms2,(token_y,token_x),phase='SYS-RECOMB-R2-HELDOUT',base=4000)
            yx2=ms2.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
            assert yx2['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',yx2
            assert yx2['composition_content_digest_sha256']==yx_digest

            # New contradictory pair evidence invalidates qualified association currentness; composition must fail closed.
            _passive_referent_exposure(
                ms2,world,tag='SYS-RECOMB-CONTRADICTION',locus='X',token=token_y,index=5000,phase='SYS-RECOMB-CONTRADICTION'
            )
            contradiction=ms2.harvest_qualify_and_register_current_opaque_evidence_associations(max_records=16384)
            assert contradiction['status']=='PAIR_EVIDENCE_HARVESTED_QUALIFICATION_INCOMPLETE',contradiction
            assert contradiction['qualifications']['results']['NATIVE_TOKEN_REFERENT']['reason']=='PAIR_EVIDENCE_NOT_EXACT_BIJECTION'
            assert ms2.opaque_evidence_association_qualification_status(qid)['status']=='REVALIDATION_REQUIRED_EPISTEMIC_ASSOCIATION_QUALIFICATION'
            after_contradiction=ms2.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
            assert after_contradiction['status']=='DEFER_UNKNOWN',after_contradiction
            assert after_contradiction['reason']=='UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED',after_contradiction

            assert not hasattr(ms2,'grammar_registry')
            assert not hasattr(ms2,'predicate_registry')
            assert not hasattr(ms2,'meaning_registry')
            assert not hasattr(ms2,'language_module')
            return {
                'status':'BOUNDED_SYSTEMATIC_NATIVE_B2_HELDOUT_RECOMBINATION_EARNED',
                'xy_composition_digest_sha256':xy_digest,
                'heldout_yx_composition_digest_sha256':yx_digest,
                'heldout_yx_absent_before_test':yx_digest not in before_yx,
                'heldout_yx_rederived_after_restart':yx2['composition_content_digest_sha256']==yx_digest,
                'order_sensitive':xy_digest!=yx_digest,
                'operator_owner':'MICROSEED_NATIVE_B2_ORDERED_COMPOSITION',
                'composition_operator':'ORDERED_EVIDENCE_TUPLE',
                'training_compositions':['XY'],
                'heldout_composition':'YX',
                'duplicate_operands':{'status':duplicate['status'],'reason':duplicate['reason']},
                'unseen_operand':{'status':unseen['status'],'reason':unseen['reason']},
                'restart_without_current_tokens':{'status':no_current['status'],'reason':no_current['reason']},
                'contradictory_pair_pressure':{'status':contradiction['status'],'reason':'PAIR_EVIDENCE_NOT_EXACT_BIJECTION'},
                'post_contradiction_composition':{'status':after_contradiction['status'],'reason':after_contradiction['reason']},
                'caller_supplied_token_operands':'NO','caller_supplied_operand_order':'NO',
                'caller_supplied_association_ids':'NO','caller_supplied_output_evidence_id':'NO',
                'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY',
                'semantic_reference_authority':'NONE','predicate_authority':'NONE','grammar_authority':'NONE',
                'truth_authority':'NONE','execution_authority':'NONE','language_authority':'NONE',
                'generic_unbounded_systematicity':'NOT_EARNED',
                'arity_generalization':'NOT_EARNED',
                'semantic_compositionality':'NOT_EARNED',
            }
        finally:
            _close(ms2)


def main():
    import json; print(json.dumps(run_campaign(),indent=2,sort_keys=True))

if __name__=='__main__': main()
