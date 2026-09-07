from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import Microseed,EpistemicStatus
from scratch.lang_c08d_postrestart_native_relation_rederivation import (
    OpaqueTwoLocusWorld,_attach_runtime_surface,_close,_fresh_owned_relation,
)
from scratch.lang_systematic_heldout_native_b2_recombination import (
    _seed_current_native_referent_associations,_observe_sequence,
)


def _b2(ms: Microseed, tokens: tuple[str,str], *, phase: str, base: int):
    _observe_sequence(ms,tokens,phase=phase,base=base)
    out=ms.derive_and_record_current_native_b2_ordered_composition(max_records=16384)
    assert out['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
    return out


def run_campaign(token_x: str='R4', token_y: str='T9', sensor_transform=None) -> dict[str,object]:
    with tempfile.TemporaryDirectory(prefix='lang-recursive-b2-operand-') as td:
        root=Path(td); world=OpaqueTwoLocusWorld()
        if sensor_transform is not None:
            world.sensor_transform=sensor_transform
        ms1=Microseed(root)
        try:
            _attach_runtime_surface(ms1,world,'REC-B2-R1')
            seeded=_seed_current_native_referent_associations(ms1,world,token_x,token_y)
            sig_x=seeded['sig_x'];sig_y=seeded['sig_y'];records=seeded['records']

            xy=_b2(ms1,(token_x,token_y),phase='REC-B2-XY',base=1000)
            one=ms1.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert one['status']=='DEFER_UNKNOWN' and one['reason']=='TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED',one

            # A second evidence instance of the same XY content must not fake a distinct child.
            xy_duplicate=_b2(ms1,(token_x,token_y),phase='REC-B2-XY-DUP',base=1050)
            assert xy_duplicate['composition_content_digest_sha256']==xy['composition_content_digest_sha256']
            duplicate_only=ms1.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert duplicate_only['status']=='DEFER_UNKNOWN' and duplicate_only['reason']=='TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED',duplicate_only

            # A row that merely wears the B2 kind but lacks exact child lineage is not an operand.
            forged_payload={
                'kind':'OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
                'composition_content_digest_sha256':'f'*64,
                'components':[],
                'ordered_operational_referent_signatures':[sig_x,sig_y],
                'runtime_boot_seq':ms1._current_runtime_boot_seq(),
                'composition_operator':'ORDERED_EVIDENCE_TUPLE',
                'operator_owner':'MICROSEED_NATIVE_B2_ORDERED_COMPOSITION',
                'authority_gain':'NONE',
            }
            ms1.append_evidence('E-REC-B2-FORGED-CHILD',forged_payload,EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE_FORGED_CHILD')
            forged_ignored=ms1.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert forged_ignored['status']=='DEFER_UNKNOWN' and forged_ignored['reason']=='TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED',forged_ignored

            yx=_b2(ms1,(token_y,token_x),phase='REC-B2-YX',base=1100)
            parent=ms1.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert parent['status']=='CURRENT_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_RECORDED',parent
            assert parent['ordered_child_composition_content_digests']==(
                xy['composition_content_digest_sha256'],yx['composition_content_digest_sha256'])
            assert parent['composition_depth']==1
            assert parent['recursive_depth_limit']==1
            assert parent['caller_supplied_child_ids']==parent['caller_supplied_child_order']=='NO'
            assert parent['caller_supplied_grouping']==parent['caller_supplied_leaf_operands']=='NO'
            assert parent['flattening_authority']==parent['associativity_authority']=='NONE'
            assert all(len(child['validated_components'])==2 for child in parent['children'])
            parent_digest=str(parent['composition_content_digest_sha256'])

            same=ms1.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert same['composition_content_digest_sha256']==parent_digest
            assert same['composition_record_status']=='COMPOSITION_EVIDENCE_ALREADY_PRESENT'

            # A fresh XY child after YX reverses the current child-content chronology.
            xy2=_b2(ms1,(token_x,token_y),phase='REC-B2-XY2',base=1200)
            reverse=ms1.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert reverse['status']=='CURRENT_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_RECORDED',reverse
            assert reverse['ordered_child_composition_content_digests']==(
                yx['composition_content_digest_sha256'],xy2['composition_content_digest_sha256'])
            assert reverse['composition_content_digest_sha256']!=parent_digest
            reverse_digest=str(reverse['composition_content_digest_sha256'])

            # Child premise drift must erase all current B2 children rather than leave a stale parent usable.
            ms1.change_capability_dependency('QX',reason='REC-B2-CHILD-QX-DRIFT')
            drifted=ms1.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert drifted['status']=='DEFER_UNKNOWN' and drifted['reason']=='TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED',drifted
        finally:
            _close(ms1)

        ms2=Microseed(root)
        try:
            no_fresh=ms2.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert no_fresh['status']=='DEFER_UNKNOWN' and no_fresh['reason']=='TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED',no_fresh
            _attach_runtime_surface(ms2,world,'REC-B2-R2')
            fresh=_fresh_owned_relation(ms2,world,tag='REC-B2-R2-FRESH',serial_base=3000)
            profiles={p['exclusive_action_id']:p for p in fresh['profiles']['profiles']}
            assert str(profiles['QX']['operational_referent_signature_sha256'])==sig_x
            assert str(profiles['QY']['operational_referent_signature_sha256'])==sig_y
            for token,key in ((token_x,'QX'),(token_y,'QY')):
                live=ms2.assess_opaque_evidence_association_currentness(
                    records[token],witness_evidence_id=str(profiles[key]['evidence_id']))
                assert live['status']=='CURRENTNESS_CONFIRMED',live
            xy_r2=_b2(ms2,(token_x,token_y),phase='REC-B2-R2-XY',base=4000)
            yx_r2=_b2(ms2,(token_y,token_x),phase='REC-B2-R2-YX',base=4100)
            parent_r2=ms2.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=16384)
            assert parent_r2['status']=='CURRENT_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_RECORDED',parent_r2
            assert parent_r2['composition_content_digest_sha256']==parent_digest
            assert parent_r2['ordered_child_composition_content_digests']==(
                xy_r2['composition_content_digest_sha256'],yx_r2['composition_content_digest_sha256'])
            return {
                'status':'BOUNDED_ONE_EDGE_RECURSIVE_B2_COMPOSITION_AS_OPERAND_EARNED',
                'child_xy_digest_sha256':xy['composition_content_digest_sha256'],
                'child_yx_digest_sha256':yx['composition_content_digest_sha256'],
                'parent_xy_yx_digest_sha256':parent_digest,
                'reverse_yx_xy_digest_sha256':reverse_digest,
                'order_sensitive':parent_digest!=reverse_digest,
                'restart_rederived_same_parent':parent_r2['composition_content_digest_sha256']==parent_digest,
                'one_child_status':{'status':one['status'],'reason':one['reason']},
                'duplicate_same_content_child_status':{'status':duplicate_only['status'],'reason':duplicate_only['reason']},
                'forged_child_status':{'status':forged_ignored['status'],'reason':forged_ignored['reason']},
                'post_child_drift_status':{'status':drifted['status'],'reason':drifted['reason']},
                'restart_without_fresh_children':{'status':no_fresh['status'],'reason':no_fresh['reason']},
                'operator_owner':'MICROSEED_NATIVE_RECURSIVE_B2_COMPOSITION',
                'composition_operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
                'composition_depth':1,
                'caller_supplied_child_ids':'NO','caller_supplied_child_order':'NO',
                'caller_supplied_grouping':'NO','caller_supplied_leaf_operands':'NO',
                'flattening_authority':'NONE','associativity_authority':'NONE',
                'semantic_composition_authority':'NONE','grammar_authority':'NONE',
                'truth_authority':'NONE','execution_authority':'NONE','language_authority':'NONE',
                'distinct_leaf_b3_arity_generalization':'NOT_EARNED',
                'generic_recursive_depth':'NOT_EARNED',
                'unbounded_systematicity':'NOT_EARNED',
            }
        finally:
            _close(ms2)


def main():
    import json; print(json.dumps(run_campaign(),indent=2,sort_keys=True))

if __name__=='__main__': main()
