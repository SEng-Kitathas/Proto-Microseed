from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from microseed import Authority, EpistemicStatus, FeasibilityState, Microseed, QualificationState, ValueVariableContract
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.recruitment import RecruitmentOption
from microseed.development.rehearsal import CounterfactualRehearsalConfig, RehearsalTransitionRelation, propose_counterfactual_rehearsal
from microseed.runtime.commitment import RelationalCommitment,TernaryCommitment


def rel(cap,effect,next_state):
    return RehearsalTransitionRelation('s0',cap,next_state,effect,8,1.0,(f'E-{cap}-{effect}',),0,('F',0),('EPI',0))

def decision_pressure(m, deficit_id, relation_sets, options):
    d=m.epistemic_deficits.records.get(deficit_id); target=f'deficit:{deficit_id}:decision-bearing'
    if d is None or d.state.value!='ACTION_LIMITED':
        return RelationalCommitment('DB-NONE',target,TernaryCommitment.UNKNOWN,reason='DEFICIT_NOT_CURRENT',qualifiers=(('authority_gain','NONE'),))
    anchors=[a for a in d.premise_anchors if a.kind=='VALUE']
    if len(anchors)!=1:
        return RelationalCommitment('DB-ANCHOR',target,TernaryCommitment.UNKNOWN,reason='CURRENT_VALUE_ANCHOR_REQUIRED',qualifiers=(('authority_gain','NONE'),))
    a=anchors[0];vp=m.value_pressure(a.object_id)
    if vp.get('status')!='CURRENT' or int(vp.get('epoch',-1))!=a.epoch:
        return RelationalCommitment('DB-VSTALE',target,TernaryCommitment.UNKNOWN,reason='VALUE_PREMISE_NOT_CURRENT',qualifiers=(('authority_gain','NONE'),))
    if float(vp.get('pressure_magnitude',0.0))<=0.0:
        return RelationalCommitment('DB-NOPRESSURE',target,TernaryCommitment.NO,reason='NO_CURRENT_REGULATORY_PRESSURE',qualifiers=(('authority_gain','NONE'),))
    vc=m.values.contracts[a.object_id]; latest=m.values.latest[a.object_id][1]
    cfg=CounterfactualRehearsalConfig(max_horizon=1,max_nodes=16,min_support=1,min_consistency=.99)
    first=[]
    for rs in relation_sets:
        p=propose_counterfactual_rehearsal(rs,start_state_id='s0',start_value=latest,viable_low=vc.viable_low,viable_high=vc.viable_high,value_epoch=(a.object_id,a.epoch),options=options,cfg=cfg)
        if p is None or not p.sequence:
            return RelationalCommitment('DB-UNRES',target,TernaryCommitment.UNKNOWN,reason='HYPOTHESIS_CONDITIONED_ACTION_UNRESOLVED',qualifiers=(('authority_gain','NONE'),))
        first.append(p.sequence[0])
    stance=TernaryCommitment.YES if len(set(first))>1 else TernaryCommitment.NO
    reason='DISCRIMINATION_CAN_CHANGE_CURRENT_REGULATORY_ACTION' if stance==TernaryCommitment.YES else 'DISCRIMINATION_CANNOT_CHANGE_CURRENT_EXECUTABLE_ACTION'
    blob={'deficit':d.serializable(),'value_pressure':vp,'first_actions':first,'options':[o.serializable() for o in options]}
    cid='DB-'+hashlib.sha256(json.dumps(blob,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:20]
    return RelationalCommitment(cid,target,stance,reason=reason,qualifiers=(('authority_gain','NONE'),('semantic_goal_authority','NONE'),('truth_authority','NONE')),premise_ids=(d.deficit_id,d.unknown_evidence_id,a.object_id))

def fixture(value=-1.0):
    td=tempfile.TemporaryDirectory(prefix='ms1707-');m=Microseed(Path(td.name))
    m.register_value_variable(ValueVariableContract('V','opaque-regulatory',0.0,10.0,'v'*64,Authority.REFERENCE_ONLY,('MS1707',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.observe_value_state('V',value)
    m.append_evidence('E-U',{'unknown':'which relation controls action consequence?'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS1707')
    m.record_action_limited_unknown(deficit_id='D',question_key='Q',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U',missing_discriminator_signature_sha256='d'*64,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),))
    return td,m

def run():
    opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption('B',FeasibilityState.FEASIBLE,local_cost=.1))
    h1={('s0','A'):rel('A',2.0,'sa'),('s0','B'):rel('B',0.0,'sb')}
    h2={('s0','A'):rel('A',0.0,'sa'),('s0','B'):rel('B',2.0,'sb')}
    same={('s0','A'):rel('A',2.0,'sa'),('s0','B'):rel('B',0.0,'sb')}
    td,m=fixture(-1.0)
    try:
        yes=decision_pressure(m,'D',(h1,h2),opts);assert yes.licenses_yes()
        no=decision_pressure(m,'D',(h1,same),opts);assert no.licenses_no()
        blocked_opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.UNKNOWN))
        unavailable=decision_pressure(m,'D',(h1,h2),blocked_opts);assert unavailable.licenses_no() or unavailable.commitment==TernaryCommitment.UNKNOWN
        m.change_value_variable('V',reason='VALUE_EPOCH_CHANGED')
        stale=decision_pressure(m,'D',(h1,h2),opts);assert stale.commitment==TernaryCommitment.UNKNOWN
    finally:td.cleanup()
    td2,n=fixture(5.0)
    try:
        zero=decision_pressure(n,'D',(h1,h2),opts);assert zero.licenses_no()
    finally:td2.cleanup()
    out={'pass':'MS1707_PASS05','decision_bearing':'YES','same_action_under_all_live_relations':'NO','blocked_candidate_case':unavailable.commitment.value,'zero_regulatory_pressure':'NO','stale_value_premise':'UNKNOWN',
         'disposition':'SURVIVED__CURRENT_REGULATORY_PRESSURE_PLUS_VALUE_ANCHORED_ACTION_LIMITED_UNKNOWN_PLUS_HYPOTHESIS_CONDITIONED_REHEARSAL_DIVERGENCE_COMPOSE_INTO_BOUNDED_DECISION_BEARING_EPISTEMIC_PRESSURE',
         'scars':['EPISTEMIC_UNCERTAINTY != NORMATIVE_PRIORITY','CURRENT_REGULATORY_PRESSURE != REASON_TO_RESOLVE_EVERY_UNKNOWN','DISCRIMINATION_IS_LOAD_BEARING_ONLY_IF_LIVE_RELATIONAL_ALTERNATIVES_CHANGE_THE_CURRENT_EXECUTABLE_ACTION','NO_CURRENT_REGULATORY_PRESSURE => NO_EPISTEMIC_INITIATION_PRESSURE','DECISION_BEARING_COMMITMENT_GRANTS_ZERO_EXECUTION_OR_TRUTH_AUTHORITY']}
    Path(__file__).with_name('MS1707_PASS05_DECISION_BEARING_EPISTEMIC_PRESSURE.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':run()
