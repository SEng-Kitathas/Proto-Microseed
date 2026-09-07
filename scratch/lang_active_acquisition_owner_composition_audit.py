from __future__ import annotations

import inspect
import tempfile
from pathlib import Path

from microseed import Microseed
from scratch.lang_c08d_postrestart_native_relation_rederivation import (
    OpaqueTwoLocusWorld, _attach_runtime_surface, _close,
    _observe_action_state_s0, _raw, _execute,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.ms2014_endogenous_referent_opportunity_enumeration import run_unique


def _action_generated_grounded_source_then_token() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix='active-acq-owner-audit-') as td:
        world=OpaqueTwoLocusWorld(); ms=Microseed(Path(td))
        try:
            _attach_runtime_surface(ms,world,'ACTIVE-ACQ-AUDIT')
            world.set_passive_baseline(0,0)
            _observe_action_state_s0(ms,'ACTIVE-ACQ-START')
            _raw(ms,'ACTIVE-ACQ-P0')
            for offset,(cid,tag) in enumerate((('QX','X0'),('QX','X1'),('QY','Y0'),('QY','Y1'))):
                _execute(ms,cid,f'ACTIVE-ACQ-{tag}',7000+offset)
                _raw(ms,f'ACTIVE-ACQ-P{offset+1}')
            profiles=ms.record_current_owned_affordance_effect_profiles(
                evidence_id_prefix='E-ACTIVE-ACQ-PROFILE',max_probe_steps=4,
            )
            assert profiles['status']=='CURRENT_OWNED_AFFORDANCE_EFFECT_PROFILES_RECORDED',profiles
            before_pairs=len(ms.opaque_evidence_associations.pair_witnesses)
            token=observe_opaque_token(ms,'R4',9000,phase='ACTIVE-ACQ-AUDIT')
            assert token['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',token
            harvest=ms.harvest_current_opaque_evidence_association_pairs(max_records=16384)
            action_generated=[
                row for row in ms.evidence.list()
                if (row.get('payload') or {}).get('kind')=='OWNED_AFFORDANCE_EFFECT_PROFILE_WITNESS'
            ]
            return {
                'profile_count':len(action_generated),
                'profile_kinds':sorted({(row.get('payload') or {}).get('kind') for row in action_generated}),
                'token_evidence_id':token['evidence_id'],
                'harvest_status':harvest.get('status'),
                'harvest_reason':harvest.get('reason'),
                'unpaired_tokens':tuple(harvest.get('unpaired_tokens',())),
                'pair_witness_delta':len(ms.opaque_evidence_associations.pair_witnesses)-before_pairs,
                'effect_authority_from_harvest':harvest.get('effect_authority'),
                'execution_authority_from_harvest':harvest.get('execution_authority'),
            }
        finally:
            _close(ms)


def _source_owner_coupling_audit() -> dict[str, object]:
    # Source audit is deliberately exact and narrow: identify whether any current Microseed
    # method simultaneously consumes association registry state and the mature referent
    # opportunity surface.  This is evidence of wiring, not proof of behavioral impossibility.
    import microseed.runtime.entity as entity
    src=Path(inspect.getsourcefile(entity.Microseed)).read_text(encoding='utf-8')
    blocks=[]
    current=None
    for line in src.splitlines():
        if line.startswith('    def '):
            if current is not None: blocks.append(current)
            current=[line]
        elif current is not None:
            current.append(line)
    if current is not None: blocks.append(current)
    coupled=[]
    for block in blocks:
        text='\n'.join(block)
        if 'opaque_evidence_associations' in text and ('referent_epistemic_opportun' in text or '_current_owned_referent_epistemic_opportunities' in text):
            coupled.append(block[0].strip())
    return {'coupled_methods':tuple(coupled)}


def run_campaign() -> dict[str, object]:
    selection=run_unique()
    source_boundary=_action_generated_grounded_source_then_token()
    coupling=_source_owner_coupling_audit()
    assert selection['enumeration_status']=='CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY',selection
    assert selection['probe_action_ids']==['P2'],selection
    assert selection['caller_supplied_binding_id']==selection['caller_supplied_deficit_id']=='NO',selection
    assert source_boundary['profile_count']>=2,source_boundary
    assert source_boundary['harvest_reason']=='NO_CURRENT_NATIVE_OPAQUE_ASSOCIATION_PAIR_HARVESTED',source_boundary
    assert source_boundary['pair_witness_delta']==0,source_boundary
    assert coupling['coupled_methods']==(),coupling
    return {
        'status':'STOP_ACTIVE_ACQUISITION_OWNER_BINDING_MISSING',
        'existing_selection_owner':'CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY',
        'existing_selected_probe_action_id':'P2',
        'caller_selected_binding_or_deficit':'NO',
        'action_generated_grounded_evidence_kind':'OWNED_AFFORDANCE_EFFECT_PROFILE_WITNESS',
        'c08i_pair_harvest_from_action_generated_grounded_evidence':'NO',
        'pair_witness_delta':source_boundary['pair_witness_delta'],
        'association_to_opportunity_coupled_methods':list(coupling['coupled_methods']),
        'localized_missing_mechanism':'NATIVE_ASSOCIATION_PRESSURE_TO_CURRENT_GROUNDED_ACQUISITION_OPPORTUNITY_BINDING',
        'new_planner_required':'NO_EVIDENCE_FOR_NEW_PLANNER',
        'information_value_effect_authority_conflated':'NO',
        'effect_authority':source_boundary['effect_authority_from_harvest'],
        'execution_authority':source_boundary['execution_authority_from_harvest'],
    }
