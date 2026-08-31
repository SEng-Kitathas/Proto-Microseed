from pathlib import Path
import tempfile

from microseed import (
    Microseed, Authority, QualificationState, FeasibilityState, EpistemicStatus,
    CapabilityContract, OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract,
    RecruitmentOption, RehearsalTransitionObservation, QueryObligation, Observation,
    ExternalActionOutcomeRelationQualifier,
)


class ChildController:
    """Harness-side autonomous subordinate controller; local means are not parent capabilities."""
    def __init__(self):
        self.state='C0'
        self.blocked={}
        self.receipts=[]

    def set_state(self,state): self.state=str(state)
    def set_feasibility(self,target,feasibility): self.blocked[str(target)]=FeasibilityState(feasibility)
    def feasibility(self,target): return self.blocked.get(str(target),FeasibilityState.FEASIBLE)

    def request(self,target):
        f=self.feasibility(target)
        if f != FeasibilityState.FEASIBLE:
            return {'status':f.value,'target':target,'local_mean':None}
        # Same requested target is solved by different local means as child state changes.
        table={('C0','T0'):'M0',('C1','T0'):'M1',('C0','T1'):'M1',('C1','T1'):'M0'}
        mean=table[(self.state,target)]
        r={'status':'WORKABLE','target':target,'child_state':self.state,'local_mean':mean}
        self.receipts.append(r)
        return r


def new_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms2060-request-means-')
    return td,Microseed(Path(td.name))


def request_cap(cid,target,child):
    return CapabilityContract(
        cid,'opaque-request-channel-effect',
        boundary={'request_target_handle':target,'local_means_owned_by_parent':False},
        interface={'input':'NO_PARENT_LOCAL_MEAN','output':'SUBORDINATE_REQUEST_RECEIPT'},
        invariants=('REQUEST_CHANNEL_EFFECT_NE_SUBORDINATE_LOCAL_ACTUATION_AUTHORITY',),
        hazards=('SUBORDINATE_MAY_REFUSE_OR_CHANGE_LOCAL_MEANS',),
        authority=Authority.EFFECT,lineage=('MS2060-RESEARCH',),currentness='CURRENT',resources={},
        query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda _target=target: child.request(_target),operational_scope_id='REQUEST-SCOPE',
    )


def setup(ms,child):
    ms.register_operational_frame(OperationalFrameContract(
        'F','opaque-request-effect-frame','f'*64,Authority.DERIVED_READ_ONLY,('MS2060-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    ms.register_value_variable(ValueVariableContract(
        'V','opaque-higher-regulatory',1.0,10.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS2060-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
    ))
    ms.observe_value_state('V',0.0)
    ms.register_capability(request_cap('REQ-T0','T0',child))
    ms.register_capability(request_cap('REQ-T1','T1',child))
    ms.register_episode_schema(EpisodeSchemaContract(
        'E','opaque-request-effect-episode','e'*64,Authority.DERIVED_READ_ONLY,('MS2060-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),
    ))


def obl(): return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='REQUEST-SCOPE')


def sched(ms,higher,cid,idx):
    rows=tuple(RehearsalTransitionObservation(
        f'SCHED-{higher}-{cid}-{idx}-{j}',higher,cid,f'WRONG-{higher}-{cid}',1.0,0,'F',0,'E',0
    ) for j in range(8))
    return ms.nominate_counterfactual_rehearsal(rows,(RecruitmentOption(cid,FeasibilityState.FEASIBLE),),start_state_id=higher,value_id='V')


def execute_request(ms,child,*,higher,cid,child_state,idx,next_state,effect):
    child.set_state(child_state)
    ms.observe_value_state('V',0.0)
    ms.observe_opaque_control_state(
        Observation(f'CS-{higher}-{cid}-{child_state}-{idx}','EXT','opaque-control',higher,authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-CS-{higher}-{cid}-{child_state}-{idx}',
    )
    p=sched(ms,higher,cid,idx); assert p is not None
    intent=ms.nominate_bounded_action_intent(p.proposal_id,obl()); assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],obl()); assert ex['status']=='ACTION_EXECUTED'
    # Child local means are observable only after the request was executed; parent never selected them.
    receipt=child.receipts[-1]
    eid=ex['execution']['execution_id']
    out=ms.record_bounded_action_outcome(
        eid,Observation(
            f'OUT-{higher}-{cid}-{child_state}-{idx}','EXT',f'action-execution:{eid}',
            {'next_state_id':next_state,'value_id':'V','observed_value':effect,'request_receipt':receipt},
            authority=Authority.OBSERVATION_ONLY,
        ),evidence_id=f'E-OUT-{higher}-{cid}-{child_state}-{idx}',
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return receipt


def holdouts(ms,c,prefix):
    base={
        'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,
        'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],
        'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),
        'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],
        'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs],
        'evidence_premise_signatures':[list(x) for x in c.evidence_premise_signatures],
        'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,
    }
    return tuple(ms.append_evidence(f'{prefix}-{i}',{**base,'i':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT') for i in range(12))


def qualify(ms):
    out={}
    for i,c in enumerate(ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)):
        t=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdouts(ms,c,f'H-{i}'))
        q=ms.qualify_action_outcome_predictive_relation(t); assert q['status']=='CURRENT_PREDICTIVE_RELATION'
        out[(c.start_state_id,c.capability_id)]=q['relation']['relation_id']
    return out


def train(ms,child):
    # Higher H0 prefers target T0; H1 prefers T1. Child alternates C0/C1, changing local means
    # while preserving the higher effect of each requested target.
    table={('H0','REQ-T0'):('H0-GOOD',2.0),('H0','REQ-T1'):('H0-BAD',-2.0),
           ('H1','REQ-T0'):('H1-BAD',-2.0),('H1','REQ-T1'):('H1-GOOD',2.0)}
    receipts=[]
    for (higher,cid),(ns,effect) in table.items():
        for i in range(8):
            receipts.append(execute_request(ms,child,higher=higher,cid=cid,child_state='C0' if i%2==0 else 'C1',idx=i,next_state=ns,effect=effect))
    return table,receipts,qualify(ms)


def request_options(child):
    return tuple(RecruitmentOption(cid,child.feasibility(target)) for cid,target in (('REQ-T0','T0'),('REQ-T1','T1')))


def test_same_requested_state_is_realized_by_different_local_means_without_parent_selecting_them():
    td,ms=new_ms(); child=ChildController()
    try:
        setup(ms,child); _,receipts,_=train(ms,child)
        t0={r['local_mean'] for r in receipts if r['target']=='T0'}
        t1={r['local_mean'] for r in receipts if r['target']=='T1'}
        assert t0=={'M0','M1'} and t1=={'M0','M1'}
        assert set(ms.capabilities.contracts)=={'REQ-T0','REQ-T1'}
        assert 'M0' not in ms.capabilities.contracts and 'M1' not in ms.capabilities.contracts
    finally: td.cleanup()


def test_parent_learns_request_effect_while_child_local_means_vary():
    td,ms=new_ms(); child=ChildController()
    try:
        setup(ms,child); table,_,rels=train(ms,child)
        assert len(rels)==4
        for higher,expected in [('H0','REQ-T0'),('H1','REQ-T1')]:
            ms.observe_value_state('V',0.0)
            ms.observe_opaque_control_state(Observation(f'Q-{higher}','EXT','opaque-control',higher,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-Q-{higher}')
            proposal=ms.nominate_counterfactual_rehearsal((),request_options(child),start_state_id=higher,value_id='V')
            assert proposal is not None and proposal.sequence==(expected,)
            assert proposal.predicted_step_value_effects==(2.0,)
    finally: td.cleanup()


def test_child_refusal_or_unknown_blocks_request_without_parent_override():
    td,ms=new_ms(); child=ChildController()
    try:
        setup(ms,child)
        for f in (FeasibilityState.REFUSED,FeasibilityState.UNKNOWN):
            child.set_feasibility('T0',f)
            try:
                ms.nominate_recruitment(request_options(child),('REQ-T0',),operational_scope_id='REQUEST-SCOPE')
            except ValueError as exc:
                assert f'RECRUITMENT_NOT_FEASIBLE:REQ-T0:{f.value}' in str(exc)
            else:
                raise AssertionError('parent overrode subordinate request feasibility')
        assert child.receipts==[]
    finally: td.cleanup()


def test_request_channel_capability_does_not_claim_local_actuation_or_semantic_goal_authority():
    td,ms=new_ms(); child=ChildController()
    try:
        setup(ms,child)
        for cid in ('REQ-T0','REQ-T1'):
            c=ms.capabilities.contracts[cid]
            assert c.authority==Authority.EFFECT
            assert c.boundary['local_means_owned_by_parent'] is False
            assert c.interface['input']=='NO_PARENT_LOCAL_MEAN'
            assert 'REQUEST_CHANNEL_EFFECT_NE_SUBORDINATE_LOCAL_ACTUATION_AUTHORITY' in c.invariants
        p=ms.nominate_recruitment(request_options(child),('REQ-T0',),operational_scope_id='REQUEST-SCOPE')
        assert p.semantic_goal_authority=='NONE' and p.authority==Authority.MODEL_OUTPUT_ONLY.value
    finally: td.cleanup()


def test_local_policy_means_can_change_without_changing_parent_request_identity_when_higher_effect_is_stable():
    td,ms=new_ms(); child=ChildController()
    try:
        setup(ms,child); _,_,rels=train(ms,child)
        rid=rels[('H0','REQ-T0')]
        assert ms.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        # State C0 vs C1 already realizes the same request through different means.
        # Request capability content/epoch is unchanged because local means are subordinate-owned.
        assert ms.capabilities.epochs['REQ-T0']==0
        assert ms.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
    finally: td.cleanup()


def test_finite_request_handles_are_still_supplied_and_not_misreported_as_endogenous_desired_state_construction():
    td,ms=new_ms(); child=ChildController()
    try:
        setup(ms,child)
        assert set(ms.capabilities.contracts)=={'REQ-T0','REQ-T1'}
        assert not hasattr(ms,'construct_subordinate_desired_state')
        assert not hasattr(ms,'desired_state_registry')
    finally: td.cleanup()
