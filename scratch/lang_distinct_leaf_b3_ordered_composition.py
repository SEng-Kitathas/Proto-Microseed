from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Microseed
from scratch.lang_b3_three_grounded_referents_fixture import (
    OpaqueThreeLocusWorld, attach_three_runtime_surface, fresh_three_owned_profiles,
    seed_three_current_native_referent_associations, _close,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _observe_sequence(ms:Microseed,tokens:tuple[str,str,str],*,phase:str,base:int):
    out=[]
    for offset,token in enumerate(tokens):
        row=observe_opaque_token(ms,token,base+offset,phase=phase)
        assert row['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',row
        out.append(row)
    return tuple(out)


def _b3_rows(ms:Microseed):
    return tuple(row for row in ms.evidence.list()
                 if (row.get('payload') or {}).get('kind')=='OWNED_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE')


def run_campaign(tokens=('R4','T9','W3'),sensor_transform=None)->dict[str,object]:
    td=TemporaryDirectory(prefix='lang-distinct-leaf-b3-')
    root=Path(td.name); world=OpaqueThreeLocusWorld()
    if sensor_transform is not None: world.sensor_transform=sensor_transform
    ms1=Microseed(root)
    try:
        attach_three_runtime_surface(ms1,world,'B3-R1')
        seeded=seed_three_current_native_referent_associations(ms1,world,tokens=tokens)
        profiles=seeded['profiles']; mapping=seeded['mapping']; records=seeded['records']
        sig_x=str(profiles['QX']['operational_referent_signature_sha256'])
        sig_y=str(profiles['QY']['operational_referent_signature_sha256'])
        sig_z=str(profiles['QZ']['operational_referent_signature_sha256'])
        tx,ty,tz=tokens
        assert mapping=={tx:sig_x,ty:sig_y,tz:sig_z},mapping
        assert _b3_rows(ms1)==()
        action_ids_before=set(ms1.capabilities.contracts)

        # First direct B3 content: XYZ. No B3 evidence exists before this invocation.
        _observe_sequence(ms1,(tx,ty,tz),phase='B3-XYZ',base=1000)
        xyz=ms1.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert xyz['status']=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',xyz
        assert xyz['ordered_operational_referent_signatures']==(sig_x,sig_y,sig_z)
        assert xyz['arity']==3
        assert xyz['operator_owner']=='MICROSEED_NATIVE_B3_ORDERED_COMPOSITION'
        assert xyz['composition_operator']=='ORDERED_EVIDENCE_TUPLE'
        assert xyz['caller_supplied_token_operands']==xyz['caller_supplied_operand_order']=='NO'
        assert xyz['caller_supplied_association_ids']==xyz['caller_supplied_referent_identity']=='NO'
        assert xyz['caller_supplied_grouping']==xyz['caller_supplied_output_evidence_id']=='NO'
        assert xyz['flattening_authority']==xyz['associativity_authority']=='NONE'
        xyz_digest=str(xyz['composition_content_digest_sha256'])
        before_xzy={str((row.get('payload') or {}).get('composition_content_digest_sha256')) for row in _b3_rows(ms1)}
        assert before_xzy=={xyz_digest},before_xzy

        # Held-out order XZY uses already-current leaves but has no prior B3 content.
        _observe_sequence(ms1,(tx,tz,ty),phase='B3-XZY',base=1100)
        xzy=ms1.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert xzy['status']=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',xzy
        assert xzy['ordered_operational_referent_signatures']==(sig_x,sig_z,sig_y)
        xzy_digest=str(xzy['composition_content_digest_sha256'])
        assert xzy_digest not in before_xzy
        assert xzy_digest!=xyz_digest

        # Same latest three operands are idempotent.
        repeat=ms1.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert repeat['composition_content_digest_sha256']==xzy_digest
        assert repeat['composition_record_status']=='COMPOSITION_EVIDENCE_ALREADY_PRESENT'

        _observe_sequence(ms1,(tx,ty,tx),phase='B3-DUP',base=1200)
        duplicate=ms1.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert duplicate['status']=='DEFER_UNKNOWN' and duplicate['reason']=='THREE_DISTINCT_NATIVE_REFERENT_OPERANDS_REQUIRED',duplicate

        _observe_sequence(ms1,(tx,ty,'UNSEEN-B3'),phase='B3-UNSEEN',base=1300)
        unseen=ms1.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert unseen['status']=='DEFER_UNKNOWN' and unseen['reason']=='UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED',unseen

        # Restore XYZ then attack the third leaf currentness specifically.
        _observe_sequence(ms1,(tx,ty,tz),phase='B3-DRIFT-PRE',base=1400)
        live_before_drift=ms1.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert live_before_drift['status']=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',live_before_drift
        ms1.change_capability_dependency('QZ',reason='B3-QZ-DRIFT')
        qz_drift=ms1.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert qz_drift['status']=='DEFER_UNKNOWN' and qz_drift['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED',qz_drift
        assert set(ms1.capabilities.contracts)==action_ids_before
    finally:
        _close(ms1)

    # Restart: persisted association/history is not fresh B3 authority.
    ms2=Microseed(root)
    try:
        no_fresh=ms2.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert no_fresh['status']=='DEFER_UNKNOWN' and no_fresh['reason']=='THREE_CURRENT_RUNTIME_OBSERVED_TOKEN_OPERANDS_REQUIRED',no_fresh
        attach_three_runtime_surface(ms2,world,'B3-R2')
        profiles2=fresh_three_owned_profiles(ms2,world,tag='R2-FRESH',serial_base=3000)
        assert str(profiles2['QX']['operational_referent_signature_sha256'])==sig_x
        assert str(profiles2['QY']['operational_referent_signature_sha256'])==sig_y
        assert str(profiles2['QZ']['operational_referent_signature_sha256'])==sig_z
        for token,key in ((tx,'QX'),(ty,'QY'),(tz,'QZ')):
            current=ms2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles2[key]['evidence_id']))
            assert current['status']=='CURRENTNESS_CONFIRMED',current
        _observe_sequence(ms2,(tx,ty,tz),phase='B3-R2-XYZ',base=4000)
        xyz2=ms2.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert xyz2['status']=='CURRENT_NATIVE_B3_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',xyz2
        assert xyz2['composition_content_digest_sha256']==xyz_digest

        # Frame drift invalidates all profile support even while association records remain present.
        ms2.change_operational_frame('F',reason='B3-FRAME-DRIFT')
        frame_drift=ms2.derive_and_record_current_native_b3_ordered_composition(max_records=32768)
        assert frame_drift['status']=='DEFER_UNKNOWN' and frame_drift['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED',frame_drift

        return {
            'status':'BOUNDED_DISTINCT_LEAF_B3_ORDERED_COMPOSITION_EARNED',
            'xyz_digest_sha256':xyz_digest,
            'xzy_digest_sha256':xzy_digest,
            'xzy_absent_before_test':xzy_digest not in before_xzy,
            'order_sensitive':xyz_digest!=xzy_digest,
            'restart_rederived_xyz':xyz2['composition_content_digest_sha256']==xyz_digest,
            'duplicate_operands':{'status':duplicate['status'],'reason':duplicate['reason']},
            'unseen_operand':{'status':unseen['status'],'reason':unseen['reason']},
            'qz_drift':{'status':qz_drift['status'],'reason':qz_drift['reason']},
            'frame_drift':{'status':frame_drift['status'],'reason':frame_drift['reason']},
            'restart_without_fresh_tokens':{'status':no_fresh['status'],'reason':no_fresh['reason']},
            'operator_owner':'MICROSEED_NATIVE_B3_ORDERED_COMPOSITION',
            'composition_operator':'ORDERED_EVIDENCE_TUPLE',
            'arity':3,
            'caller_supplied_token_operands':'NO','caller_supplied_operand_order':'NO',
            'caller_supplied_association_ids':'NO','caller_supplied_referent_identity':'NO',
            'caller_supplied_grouping':'NO','caller_supplied_output_evidence_id':'NO',
            'flattening_authority':'NONE','associativity_authority':'NONE',
            'semantic_composition_authority':'NONE','grammar_authority':'NONE',
            'truth_authority':'NONE','execution_authority':'NONE','language_authority':'NONE',
            'generic_nary_arity_generalization':'NOT_EARNED',
            'b4_arity':'NOT_EARNED',
        }
    finally:
        _close(ms2);td.cleanup()
