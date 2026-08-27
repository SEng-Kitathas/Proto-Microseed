from pathlib import Path
import tempfile, json, sys
sys.path.insert(0,'/mnt/data/ms1533_research_descendant')
from microseed import *


def setup():
    td=tempfile.TemporaryDirectory(prefix='ms1531-p4-')
    m=Microseed(Path(td.name))
    m.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('TEST',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','opaque',4.0,8.0,'v'*64,Authority.DERIVED_READ_ONLY,('TEST',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_capability(CapabilityContract('A','opaque',{},{},(),(),Authority.EFFECT,('TEST',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_: {'ok':True},operational_scope_id='S'))
    m.register_episode_schema(EpisodeSchemaContract('E','opaque','e'*64,Authority.DERIVED_READ_ONLY,('TEST',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    m.observe_opaque_control_state(Observation('CS','EXT','control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS')
    return td,m


def rows(effect):
    return tuple(RehearsalTransitionObservation(f'R{i}','S0','A','S0',effect,0,'F',0,'E',0) for i in range(12))


def case(start,effect,new_value):
    td,m=setup()
    try:
        m.observe_value_state('V',start)
        p=m.nominate_counterfactual_rehearsal(rows(effect),(RecruitmentOption('A',FeasibilityState.FEASIBLE,local_cost=.1),),start_state_id='S0',value_id='V',config=CounterfactualRehearsalConfig(max_horizon=1))
        before=m.derive_bounded_action_commitment(p.proposal_id)
        m.observe_value_state('V',new_value)
        after=m.derive_bounded_action_commitment(p.proposal_id)
        # Ground-truth consequence under the same learned additive effect.
        low,high=4.0,8.0
        pressure=lambda x: low-x if x<low else x-high if x>high else 0.0
        actual_before=pressure(new_value); actual_after=pressure(new_value+effect)
        actual='YES' if actual_before>0 and actual_after<actual_before else ('NO' if actual_after>actual_before or actual_before<=0 else 'UNKNOWN')
        return {'start':start,'effect':effect,'new_value':new_value,'proposal_residual':p.residual_pressure,'before_commitment':before.commitment.value,'after_commitment':after.commitment.value,'actual_current_effect_stance':actual,'actual_current_pressure':actual_before,'actual_predicted_pressure':actual_after}
    finally: td.cleanup()

cases=[
    case(9.0,-1.0,3.0),   # old good action becomes harmful after crossing interval
    case(2.0,1.0,9.0),    # opposite crossing
    case(2.0,1.0,3.9),    # old residual can cause false negative near boundary
]
false_yes=[c for c in cases if c['after_commitment']=='YES' and c['actual_current_effect_stance']!='YES']
res={'campaign':'MS1528-1552','ms':1531,'pass':4,'purpose':'CANONICAL_REHEARSAL_VALUE_OBSERVATION_CURRENTNESS_PROBE','main_dev_mutation':'NONE','cases':cases,'false_yes_count':len(false_yes),'false_yes':false_yes,'confirmed':len(false_yes)>0,'law_if_confirmed':'VALUE_CONTRACT_EPOCH_CURRENT != VALUE_STATE_OBSERVATION_CURRENT','candidate_repair':'RECOMPUTE_RESIDUAL_FROM_CURRENT_VALUE_PLUS_EXISTING_PREDICTED_VALUE_EFFECT_AT_COMMITMENT_TIME'}
Path('/mnt/data/ms1528_1552_campaign_work/PASS04_REPAIRED_VALUE_CURRENTNESS_PROBE.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print(json.dumps(res,indent=2,sort_keys=True))
if not res['confirmed']: raise SystemExit(1)
