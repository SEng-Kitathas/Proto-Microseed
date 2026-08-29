from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority, CapabilityContract, CounterfactualRehearsalConfig,
    EpisodeSchemaContract, EpistemicStatus, ExternalActionOutcomeRelationQualifier,
    FeasibilityState, Microseed, Observation, OperationalCoordinationContract,
    OperationalCounterpartyContract, OperationalFrameContract, QualificationState,
    QueryObligation, RecruitmentOption, RehearsalTransitionObservation,
    ValueVariableContract,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _reset_start, _close


def act_ob(): return QueryObligation('ACT','emit opaque token',Authority.EFFECT,operational_scope_id='S')
def obs_ob(): return QueryObligation('OBS-Q','observe opaque response',Authority.OBSERVATION_ONLY,operational_scope_id='S')
def basis_ob(): return QueryObligation('BASIS-Q','bounded use basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S')


def build(root: Path, mapping: dict[str,str]):
    ms=Microseed(root); world={'emitted':None}
    ms.register_operational_frame(OperationalFrameContract('F','opaque-frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1948',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    ms.register_value_variable(ValueVariableContract('V','opaque-regulatory',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS1948',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL')))
    ms.observe_value_state('V',0.0)
    cp=OperationalCounterpartyContract('CP','opaque-independent-causal-source','',Authority.DERIVED_READ_ONLY,('MS1948',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_COUNTERPARTY_CURRENTNESS',)); cp.signature_sha256=cp.computed_signature_sha256(); ms.register_operational_counterparty(cp)
    coord=OperationalCoordinationContract('R','opaque-both-token-response-relation',(('CP',0),),'',Authority.DERIVED_READ_ONLY,('MS1948',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_COORDINATION_CONTRACT',),invariants=('SIGNAL != REFERENCE','TOKEN_EMITTED != TOKEN_MEANS','EQUAL_ACCEPTANCE != SEMANTIC_EQUIVALENCE')); coord.signature_sha256=coord.computed_signature_sha256(); ms.register_operational_coordination(coord)
    def make_emit(token):
        def emit(**_): world['emitted']=token; return {'opaque_emitted_token':token}
        return emit
    for cid,token in mapping.items():
        ms.register_capability(CapabilityContract(cid,'opaque-effect-token-emission',{}, {'output':'opaque-token'},('SIGNAL != REFERENCE','TOKEN_EMITTED != TOKEN_MEANS','NO_SEMANTIC_MESSAGE_AUTHORITY'),(),Authority.EFFECT,('MS1948',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=make_emit(token),operational_scope_id='S',assistance_ancestry=('SUPPLIED_REPRESENTED_OPAQUE_SIGNAL_ALTERNATIVE',)),counterparty_dependencies=(('CP',0),),coordination_dependencies=(('R',0),))
    def observe(**_):
        ok=world['emitted'] in set(mapping.values())
        return {'next_state_id':'CP-ACK' if ok else 'CP-NOACK','value_id':'V','observed_value':2.2 if ok else 0.0,'opaque_counterparty_response':'ACK' if ok else 'NO_ACK'}
    ms.register_capability(CapabilityContract('OBS-CP','opaque-counterparty-response-observation',{}, {'output':'opaque-response'},('NO_REFERENCE_AUTHORITY','NO_MEANING_AUTHORITY'),(),Authority.OBSERVATION_ONLY,('MS1948',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=observe,operational_scope_id='S'),counterparty_dependencies=(('CP',0),))
    ms.register_capability(CapabilityContract('OBS-BASIS','bounded-use-basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1948',),'CURRENT',{},dependencies=('OBS-CP',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='S'))
    ms.register_episode_schema(EpisodeSchemaContract('E','opaque-episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1948',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),counterparty_epochs=(('CP',0),),coordination_epochs=(('R',0),)))
    ms.observe_opaque_control_state(Observation('CTRL-S0','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CTRL-S0')
    return ms,world


def option(cid): return RecruitmentOption(cid,FeasibilityState.FEASIBLE,local_cost=0.1)

def seed_rows(cid):
    return tuple(RehearsalTransitionObservation(f'MS1948-SEED-{cid}-{i}','S0',cid,'CP-ACK',2.2,0,'F',0,'E',0,None,None,'R',0) for i in range(12))

def holdouts(ms,candidate):
    base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':candidate.start_state_id,'capability_id':candidate.capability_id,'capability_epoch':candidate.capability_epoch,'frame_epochs':[list(x) for x in candidate.frame_epochs],'episode_schema_epochs':[list(x) for x in candidate.episode_schema_epochs],'value_epoch':list(candidate.value_epoch),'topology_epochs':[list(x) for x in candidate.topology_epochs],'coordination_epochs':[list(x) for x in candidate.coordination_epochs],'evidence_premise_epochs':[list(x) for x in candidate.evidence_premise_epochs],'evidence_premise_signatures':[list(x) for x in candidate.evidence_premise_signatures]}
    return tuple(ms.append_evidence(f'MS1948-HOLDOUT-{candidate.capability_id}-{i}',{**base,'actual_next_state_id':'CP-ACK','actual_value_effect':2.2,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT') for i in range(16))

def learn(ms,world,cid,index_base):
    p=ms.nominate_counterfactual_rehearsal(seed_rows(cid),(option(cid),),start_state_id='S0',value_id='V',config=CounterfactualRehearsalConfig(max_horizon=1)); assert p and p.sequence==(cid,)
    for i in range(12):
        if i or index_base: _reset_start(ms,world,index_base+i)
        intent=ms.nominate_bounded_action_intent(p.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED'
        ex=ms.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED'
        out=ms.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS-CP',observation_obligation=obs_ob(),basis_capability_id='OBS-BASIS',basis_obligation=basis_ob(),evidence_id=f'E-MS1948-{cid}-{i}',capture_id=f'CAP-MS1948-{cid}-{i}')
        assert out['status']=='ACTION_OUTCOME_OBSERVED' and out['outcome']['actual_next_state_id']=='CP-ACK'
    target=[c for c in ms.nominate_action_outcome_predictive_candidates() if c.capability_id==cid and c.next_state_id=='CP-ACK']; assert len(target)==1
    c=target[0]; assert c.support==12 and c.consistency==1.0
    t=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdouts(ms,c)); q=ms.qualify_action_outcome_predictive_relation(t); assert q['status']=='CURRENT_PREDICTIVE_RELATION'
    return q['relation']['relation_id']

def run_world(mapping,label):
    td=tempfile.TemporaryDirectory(prefix=f'ms1948-{label}-'); ms,world=build(Path(td.name),mapping)
    try:
        coord=(ms.coordinations.epochs['R'],ms.coordinations.contracts['R'].computed_signature_sha256())
        rels={cid:learn(ms,world,cid,1000+k*100) for k,cid in enumerate(sorted(mapping))}
        _reset_start(ms,world,9000)
        opts=tuple(option(cid) for cid in mapping)
        proposal=ms.nominate_counterfactual_rehearsal((),opts,start_state_id='S0',value_id='V',config=CounterfactualRehearsalConfig(max_horizon=1)); assert proposal
        winner=proposal.sequence[0]
        assert winner==sorted(mapping)[0]
        assert proposal.predicted_value_effect==2.2 and proposal.residual_pressure==0.0
        # Both alternatives independently earn the same YES when isolated.
        singles={}
        winner_cmt=ms.derive_bounded_action_commitment(proposal.proposal_id); assert winner_cmt.commitment.value=='YES'
        singles[winner]=winner_cmt.reason
        loser=next(cid for cid in sorted(mapping) if cid!=winner)
        _reset_start(ms,world,9101)
        sp=ms.nominate_counterfactual_rehearsal((),(option(loser),),start_state_id='S0',value_id='V',config=CounterfactualRehearsalConfig(max_horizon=1)); assert sp and sp.sequence==(loser,)
        loser_cmt=ms.derive_bounded_action_commitment(sp.proposal_id); assert loser_cmt.commitment.value=='YES'
        singles[loser]=loser_cmt.reason
        _reset_start(ms,world,9200)
        cmt=winner_cmt
        intent=ms.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED' and intent['intent']['capability_id']==winner
        ex=ms.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED'
        out=ms.record_bounded_action_outcome_via_observation_basis(ex['execution']['execution_id'],observation_capability_id='OBS-CP',observation_obligation=obs_ob(),basis_capability_id='OBS-BASIS',basis_obligation=basis_ob(),evidence_id=f'E-MS1948-FINAL-{label}',capture_id=f'CAP-MS1948-FINAL-{label}'); assert out['outcome']['actual_next_state_id']=='CP-ACK'
        assert (ms.coordinations.epochs['R'],ms.coordinations.contracts['R'].computed_signature_sha256())==coord
        assert not hasattr(ms,'signal_policy') and not hasattr(ms,'token_meanings') and not hasattr(ms,'semantic_convention_registry')
        return {'winner_capability':winner,'winner_physical_token':mapping[winner],'single_commitments':singles,'relation_ids':rels,'coordination_subject_unchanged':True,'language':ms.status()['language']}
    finally:
        _close(ms); td.cleanup()

def main():
    a=run_world({'SIG-A':'T0','SIG-Z':'T1'},'A')
    b=run_world({'SIG-Z':'T0','SIG-A':'T1'},'B')
    assert a['winner_capability']==b['winner_capability']=='SIG-A'
    assert a['winner_physical_token']=='T0' and b['winner_physical_token']=='T1'
    print(json.dumps({'status':'PASS','world_a':a,'world_b':b,'earned':'DETERMINISTIC_SEQUENCE_ID_TIEBREAK_IS_OPERATIONAL_ARBITRATION_AMONG_EQUAL_MODELED_OPTIONS_NOT_LEARNED_SIGNAL_PREFERENCE','semantic_preference_authority':'NONE','truth_authority':'NONE','meaning_authority':'NONE'},indent=2,sort_keys=True))
if __name__=='__main__': main()
