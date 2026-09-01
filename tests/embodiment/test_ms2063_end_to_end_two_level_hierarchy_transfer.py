from pathlib import Path
import random
import tempfile

from microseed import (
    Microseed, Authority, EpistemicStatus, QualificationState, FeasibilityState,
    CapabilityContract, OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract,
    ProjectionSample, ProjectionDiscoveryConfig, ExternalProjectionQualifier,
    ExternalActionOutcomeRelationQualifier, ExternalProjectionConditionedRelationQualifier,
    RecruitmentOption, RehearsalTransitionObservation, QueryObligation, Observation,
)


class TwoLevelWorld:
    """Harness world. Parent emits opaque request tokens; child owns local means."""
    def __init__(self):
        self.higher='H0'; self.child_state='C0'; self.n1='N0'; self.n2='M0'
        self.targets=()
        self.feasibility={}
        self.last_next='PRE'; self.last_effect=0.0
        self.receipts=[]

    def bind_targets(self, targets):
        self.targets=tuple(targets)
        assert len(self.targets)==2 and self.targets[0]!=self.targets[1]

    def set_context(self, higher, child_state, n1='N0', n2='M0'):
        self.higher=str(higher); self.child_state=str(child_state); self.n1=str(n1); self.n2=str(n2)
        self.last_next='PRE'; self.last_effect=0.0

    def raw_tokens(self):
        return (self.n1,self.higher,self.child_state,self.n2)

    def class_index(self):
        hb={'H0':0,'H1':1}.get(self.higher)
        cb={'C0':0,'C1':1}.get(self.child_state)
        if hb is None or cb is None:
            return None
        return hb ^ cb

    def set_feasibility(self,target,state):
        self.feasibility[str(target)]=FeasibilityState(state)

    def target_feasibility(self,target):
        return self.feasibility.get(str(target),FeasibilityState.FEASIBLE)

    def request(self,target):
        target=str(target)
        f=self.target_feasibility(target)
        if f!=FeasibilityState.FEASIBLE:
            receipt={'status':f.value,'target':target,'child_state':self.child_state,'local_mean':None}
            self.receipts.append(receipt)
            return receipt
        idx=self.targets.index(target)
        child_bit=0 if self.child_state=='C0' else 1
        # Same target is realized through different child-local means as child state changes.
        mean='M0' if idx==child_bit else 'M1'
        wanted=self.class_index()
        good=(wanted is not None and idx==wanted)
        self.last_next='HIGHER-GOOD' if good else 'HIGHER-BAD'
        self.last_effect=2.0 if good else -2.0
        receipt={
            'status':'WORKABLE','target':target,'child_state':self.child_state,
            'local_mean':mean,'higher_context':self.higher,
        }
        self.receipts.append(receipt)
        return receipt

    def observe(self):
        return {
            'raw_tokens':list(self.raw_tokens()),
            'next_state_id':self.last_next,
            'value_id':'V',
            'observed_value':self.last_effect,
        }


def new_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms2063-e2e-hierarchy-')
    return td,Microseed(Path(td.name)),TwoLevelWorld()


def act_ob(): return QueryObligation('ACT','request',Authority.EFFECT,operational_scope_id='SCOPE')
def obs_ob(): return QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='SCOPE')
def basis_ob(): return QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='SCOPE')


def register_runtime(ms,world,*,register_frame_state=True):
    if register_frame_state:
        ms.register_operational_frame(OperationalFrameContract(
            'F','opaque two-level world frame','f'*64,Authority.DERIVED_READ_ONLY,('MS2063-RESEARCH',),'CURRENT',
            qualification=QualificationState.SHADOW_QUALIFIED,
        ))
        ms.register_value_variable(ValueVariableContract(
            'V','opaque higher regulatory coordinate',1.0,10.0,'v'*64,Authority.DERIVED_READ_ONLY,
            ('MS2063-RESEARCH',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,
            assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
        ))
        ms.observe_value_state('V',0.0)
        ms.register_episode_schema(EpisodeSchemaContract(
            'E','opaque two-level episode','e'*64,Authority.DERIVED_READ_ONLY,('MS2063-RESEARCH',),'CURRENT',
            qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),
        ))
    def request_handler(*,target):
        return world.request(target)
    ms.register_capability(CapabilityContract(
        'REQ-BASE','opaque subordinate request channel',
        boundary={'request_target_binding_mode':'OPAQUE_PROJECTION_BUCKET_SPECIALIZABLE','local_means_owned_by_parent':False},
        interface={'target':'opaque','output':'subordinate-request-receipt'},
        invariants=('REQUEST_CHANNEL_EFFECT_NE_SUBORDINATE_LOCAL_MEANS_AUTHORITY',),
        hazards=('SUBORDINATE_MAY_REFUSE_OR_CHANGE_LOCAL_MEANS',),
        authority=Authority.EFFECT,lineage=('MS2063-RESEARCH',),currentness='CURRENT',resources={},
        query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=request_handler,operational_scope_id='SCOPE',
    ))
    ms.register_capability(CapabilityContract(
        'OBS','opaque raw/current outcome observation',{}, {'output':'opaque-state-plus-raw'},(),(),
        Authority.OBSERVATION_ONLY,('MS2063-RESEARCH',),'CURRENT',{},query_obligation_id='OBS-Q',
        qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:world.observe(),operational_scope_id='SCOPE',
    ))
    ms.register_capability(CapabilityContract(
        'BASIS','bounded observation use basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS2063-RESEARCH',),'CURRENT',{},
        dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'claim':'BOUND'},operational_scope_id='SCOPE',
    ))
    ms.frames.bind_capability('F','OBS')


def learn_target_projection(ms):
    rng=random.Random(2063)
    rows=[]
    for i in range(900):
        x=str(rng.randint(0,1)); nuisance=str(rng.randint(0,7)); action='A' if rng.random()<.5 else 'B'
        effect=('E1' if action=='A' else 'E0') if x=='1' else ('E0' if action=='A' else 'E1')
        rows.append(ProjectionSample(f'TARGET-S-{i}',(nuisance,x),action,effect,f'TARGET-SCOPE-{i%3}','F',0))
    found=ms.discover_epistemic_projection_candidates(
        rows[:600],rows[600:],ProjectionDiscoveryConfig(
            max_subset=1,min_train_support=100,min_key_action_support=8,
            min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.90,max_candidates=8,
        )
    )
    assert found
    c=next(ms.epistemic_projection_candidates[x['candidate_id']] for x in found if ms.epistemic_projection_candidates[x['candidate_id']].input_positions==(1,))
    q=ms.append_evidence('MS2063-TARGET-PROJ-QUAL',{'candidate_sha256':c.digest(),'independent':True},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS2063-TARGET')
    ticket=ExternalProjectionQualifier(ms.evidence,qualifier_id='EXTERNAL-MS2063-TARGET').qualify(c,qualification_evidence=(q,))
    rec=ms.admit_epistemic_projection_candidate(ticket,projection_id='TARGET-P')
    t0=c.project(('N-HELD','0')); t1=c.project(('N-HELD','1'))
    assert t0 and t1 and t0!=t1
    return rec,c,(t0,t1)


def derive_bound_requests(ms,world,target_rec,target_tokens):
    world.bind_targets(target_tokens)
    caps=[]
    for token in target_tokens:
        c=ms.derive_bound_request_specialization('REQ-BASE',target_rec.projection_id,token)
        ms.frames.bind_capability('F',c.capability_id)
        caps.append(c)
    assert len({x.capability_id for x in caps})==2
    return tuple(caps)


def exposure_proposal(ms,cid,tag):
    # Identical +1 scheduling assistance for every target/context; never the learned label.
    rows=tuple(RehearsalTransitionObservation(
        f'MS2063-SCHED-{tag}-{j}','ALIAS',cid,'SCHED-WRONG',1.0,0,'F',0,'E',0
    ) for j in range(8))
    return ms.nominate_counterfactual_rehearsal(
        rows,(RecruitmentOption(cid,FeasibilityState.FEASIBLE),),start_state_id='ALIAS',value_id='V'
    )


def execute_episode(ms,world,cid,raw,index):
    n1,h,c,n2=raw
    world.set_context(h,c,n1,n2)
    ms.observe_value_state('V',0.0)
    state_eid=f'MS2063-STATE-{index}'
    ms.observe_opaque_control_state(
        Observation(f'MS2063-C-{index}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),
        evidence_id=state_eid,
    )
    raw_receipt=ms.record_bounded_raw_observation_coordinates(
        'OBS',obs_ob(),evidence_id=f'MS2063-RAW-{index}',capture_id=f'MS2063-RAW-CAP-{index}',max_coordinates=8,
    )
    assert raw_receipt['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
    assert tuple(raw_receipt['raw_tokens'])==tuple(raw)
    p=exposure_proposal(ms,cid,index); assert p is not None
    intent=ms.nominate_bounded_action_intent(p.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED'
    receipt=ex['handler_value']; assert receipt['target'] in world.targets
    out=ms.record_bounded_action_outcome_via_observation_basis(
        ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),
        basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'MS2063-OUT-{index}',capture_id=f'MS2063-OUT-CAP-{index}',
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return receipt,out


def relation_holdouts(ms,c,prefix,n=12):
    base={
        'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,
        'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],
        'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),
        'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],
        'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs],
        'evidence_premise_signatures':[list(x) for x in c.evidence_premise_signatures],
        'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,
    }
    return tuple(ms.append_evidence(
        f'{prefix}-{i}',{**base,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS2063-REL-HOLDOUT'
    ) for i in range(n))


def qualify_candidates(ms,candidates,prefix):
    out={}
    for i,c in enumerate(candidates):
        t=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=relation_holdouts(ms,c,f'{prefix}-{i}'))
        q=ms.qualify_action_outcome_predictive_relation(t); assert q['status']=='CURRENT_PREDICTIVE_RELATION',q
        out[c.capability_id]=q['relation']['relation_id']
    return out


def phase_rows(kind,n=16):
    base=(('N0','H0','C0','M0'),('N1','H1','C1','M1')) if kind==0 else (('N2','H0','C1','M2'),('N3','H1','C0','M3'))
    return tuple(base[i%2] for i in range(n))


def discover_context_projection(ms):
    owned=ms.derive_admitted_projection_samples_from_owned_raw_observations()
    assert owned['status']=='ADMITTED_OWNED_RAW_PROJECTION_SAMPLES'
    assert owned['sample_count']>=64
    assert not owned['receipt_rejections'] and not owned['sample_rejections']
    rows=list(owned['samples']); random.Random(2063001).shuffle(rows)
    cut=44
    found=ms.discover_epistemic_projection_candidates(
        tuple(rows[:cut]),tuple(rows[cut:]),ProjectionDiscoveryConfig(
            max_subset=2,min_train_support=32,min_key_action_support=4,
            min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.90,max_candidates=12,
        )
    )
    assert found
    candidates=[ms.epistemic_projection_candidates[x['candidate_id']] for x in found]
    exact=[x for x in candidates if x.input_positions==(1,2)]
    assert len(exact)==1,[(x.input_positions,x.validation_accuracy,x.lift) for x in candidates]
    c=exact[0]
    assert c.validation_accuracy>=.99
    q=ms.append_evidence('MS2063-CTX-PROJ-QUAL',{
        'kind':'OWNED_RAW_CONTEXT_PROJECTION_HOLDOUT','candidate_sha256':c.digest(),
        'heldout_contexts':[list(x) for x in phase_rows(0,4)+phase_rows(1,4)],
    },EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS2063-CTX')
    t=ExternalProjectionQualifier(ms.evidence,qualifier_id='EXTERNAL-MS2063-CTX').qualify(c,qualification_evidence=(q,))
    rec=ms.admit_epistemic_projection_candidate(t,projection_id='CTX-P')
    b0=c.project(('NX','H0','C0','MX')); b1=c.project(('NY','H0','C1','MY'))
    assert b0 and b1 and b0!=b1
    assert c.project(('NZ','H1','C1','MZ'))==b0
    assert c.project(('NW','H1','C0','MW'))==b1
    return owned,rec,c,b0,b1


def qualify_routing(ms,ctx_rec,b0,b1,cap_ids,old_rel,new_rel):
    prop=ms.append_evidence('MS2063-ROUTE-PROP',{'kind':'ROUTING_PROPOSAL_ONLY'},EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-MS2063-PROPOSAL')
    route=ms.nominate_projection_conditioned_relation_routing(
        projection_id=ctx_rec.projection_id,task_id='MS2063',action_ids=cap_ids,channel_ids=('opaque-control',),horizon=2,
        default_action_relations=tuple((cid,new_rel[cid]) for cid in cap_ids),
        bucket_action_overrides=tuple((b0,cid,old_rel[cid]) for cid in cap_ids),
        source_evidence_ids=(prop.evidence_id,),
    )
    refs=[]
    for bucket,rels in ((b0,old_rel),(b1,new_rel)):
        for cid in cap_ids:
            rel=ms.action_outcome_learning.relations[rels[cid]]
            for i in range(4):
                refs.append(ms.append_evidence(
                    f'MS2063-ROUTE-H-{bucket[-5:]}-{cid[-8:]}-{i}',{
                        'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT',
                        'projection_id':ctx_rec.projection_id,'projection_epoch':ctx_rec.epoch,
                        'projection_signature_sha256':ctx_rec.signature_sha256,'projection_bucket_id':bucket,
                        'task_id':'MS2063','action_id':cid,'channel_id':'opaque-control','horizon':2,
                        'actual_next_state_id':rel.next_state_id,'actual_value_effect':rel.value_effect,
                    },EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS2063-ROUTE-HOLDOUT'
                ))
    ticket=ExternalProjectionConditionedRelationQualifier(ms.evidence,qualifier_id='EXTERNAL-MS2063-ROUTE').qualify(
        route,qualification_evidence=tuple(refs),relations=ms.action_outcome_learning.relations,
    )
    out=ms.qualify_projection_conditioned_relation_routing(ticket)
    assert out['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING',out
    return out['binding']['binding_id']


def build_integrated():
    td,ms,world=new_ms()
    register_runtime(ms,world)
    target_rec,target_candidate,target_tokens=learn_target_projection(ms)
    bound=derive_bound_requests(ms,world,target_rec,target_tokens)
    cap_ids=tuple(x.capability_id for x in bound)

    # Phase 0: the first two contexts share one target-effect law.
    idx=0
    phase0_receipts=[]
    for cid in cap_ids:
        for raw in phase_rows(0,16):
            r,_=execute_episode(ms,world,cid,raw,idx); phase0_receipts.append(r); idx+=1
    initial=ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)
    assert {x.capability_id for x in initial}==set(cap_ids)
    old_rel=qualify_candidates(ms,initial,'MS2063-OLD-QUAL')

    # Phase 1 reverses which request is useful while keeping the same opaque ALIAS start-state.
    phase1_receipts=[]
    for cid in cap_ids:
        for raw in phase_rows(1,16):
            r,_=execute_episode(ms,world,cid,raw,idx); phase1_receipts.append(r); idx+=1
    new_rel={}
    for cid in cap_ids:
        old_id=old_rel[cid]
        w=ms.assess_action_outcome_predictive_currentness(old_id)
        assert w['status']=='DRIFT_WITNESS',w
        reps=ms.nominate_action_outcome_replacement_candidates(old_id,w['witness']['witness_id'])
        assert len(reps)==1 and reps[0].capability_id==cid
        new_rel.update(qualify_candidates(ms,reps,f'MS2063-NEW-QUAL-{cid[-6:]}'))
        assert ms.action_outcome_predictive_relation_status(old_id)['status']=='STALE_PREDICTIVE_RELATION'
        assert ms.action_outcome_predictive_relation_status(new_rel[cid])['status']=='CURRENT_PREDICTIVE_RELATION'

    owned,ctx_rec,ctx_candidate,b0,b1=discover_context_projection(ms)
    routing_id=qualify_routing(ms,ctx_rec,b0,b1,cap_ids,old_rel,new_rel)
    return {
        'td':td,'ms':ms,'world':world,'target_rec':target_rec,'target_candidate':target_candidate,
        'target_tokens':target_tokens,'bound':bound,'cap_ids':cap_ids,'old_rel':old_rel,'new_rel':new_rel,
        'ctx_rec':ctx_rec,'ctx_candidate':ctx_candidate,'bucket0':b0,'bucket1':b1,'routing_id':routing_id,
        'phase0_receipts':phase0_receipts,'phase1_receipts':phase1_receipts,'owned':owned,
    }


def options(fx):
    w=fx['world']; pairs=zip(fx['bound'],fx['target_tokens'])
    return tuple(RecruitmentOption(c.capability_id,w.target_feasibility(t)) for c,t in pairs)


def prepare_current(fx,raw,tag):
    ms=fx['ms']; w=fx['world']; n1,h,c,n2=raw
    w.set_context(h,c,n1,n2); ms.observe_value_state('V',0.0)
    ms.observe_opaque_control_state(
        Observation(f'MS2063-Q-{tag}','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'MS2063-Q-STATE-{tag}',
    )
    rr=ms.record_bounded_raw_observation_coordinates(
        'OBS',obs_ob(),evidence_id=f'MS2063-Q-RAW-{tag}',capture_id=f'MS2063-Q-RAW-CAP-{tag}',max_coordinates=8,
    )
    assert rr['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
    return rr


def current_proposal(fx,raw,tag):
    prepare_current(fx,raw,tag)
    return fx['ms'].nominate_current_raw_projection_conditioned_rehearsal(
        (),options(fx),start_state_id='ALIAS',value_id='V',projection_routing_id=fx['routing_id'],
        routing_task_id='MS2063',routing_channel_id='opaque-control',
    )


def test_ms2063_end_to_end_owned_context_selects_bound_request_and_child_keeps_local_means():
    fx=build_integrated(); ms=fx['ms']; w=fx['world']
    try:
        assert fx['target_candidate'].input_positions==(1,)
        assert fx['ctx_candidate'].input_positions==(1,2)
        assert fx['ctx_candidate'].validation_accuracy>=.99
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        # Historical phase-0 relations remain globally stale; only the qualified bucket scope may reuse them.
        assert all(ms.action_outcome_predictive_relation_status(r)['status']=='STALE_PREDICTIVE_RELATION' for r in fx['old_rel'].values())

        # The training history already proves the same request target was realized
        # through both child-local means under C0/C1.  Do not renominate an
        # identical deterministic rehearsal for the second equivalent class-0
        # context merely to re-prove that MS2060 autonomy fact.
        t0=fx['target_tokens'][0]
        means={r['local_mean'] for r in fx['phase0_receipts'] if r['target']==t0}
        assert means=={'M0','M1'}
        assert all(x not in ms.capabilities.contracts for x in ('M0','M1'))

        # Query one context from each learned class.  Caller supplies raw current
        # observation only; bucket, relation, request target and predicted effect
        # remain internally derived.
        p0=current_proposal(fx,('QA','H0','C0','MA'),'A'); assert p0 is not None
        assert p0.sequence==(fx['bound'][0].capability_id,) and p0.predicted_step_value_effects==(2.0,)
        assert all(not o.predicted_effect for o in options(fx))
        i0=ms.nominate_bounded_action_intent(p0.proposal_id,act_ob()); assert i0['status']=='ACTION_INTENT_NOMINATED'
        x0=ms.execute_bounded_action(i0['intent']['intent_id'],act_ob()); assert x0['status']=='ACTION_EXECUTED'
        assert x0['handler_value']['target']==fx['target_tokens'][0]

        p1=current_proposal(fx,('QC','H0','C1','MC'),'C'); assert p1 is not None
        assert p1.sequence==(fx['bound'][1].capability_id,) and p1.predicted_step_value_effects==(2.0,)
        i1=ms.nominate_bounded_action_intent(p1.proposal_id,act_ob()); assert i1['status']=='ACTION_INTENT_NOMINATED'
        x1=ms.execute_bounded_action(i1['intent']['intent_id'],act_ob()); assert x1['status']=='ACTION_EXECUTED'
        assert x1['handler_value']['target']==fx['target_tokens'][1]
        # No hierarchy/semantic-goal manager emerged.
        assert not hasattr(ms,'parent_manager') and not hasattr(ms,'hierarchy_manager') and not hasattr(ms,'desired_state_registry')
    finally:
        fx['td'].cleanup()


def test_ms2063_refused_unknown_and_unseen_child_context_fail_closed():
    for state in (FeasibilityState.REFUSED,FeasibilityState.UNKNOWN):
        fx=build_integrated(); ms=fx['ms']; w=fx['world']
        try:
            w.set_feasibility(fx['target_tokens'][0],state)
            before=len(w.receipts)
            p=current_proposal(fx,('QR','H0','C0','MR'),state.value)
            if p is not None:
                intent=ms.nominate_bounded_action_intent(p.proposal_id,act_ob())
                assert intent['status']=='ABSTAIN'
            assert len(w.receipts)==before
        finally:
            fx['td'].cleanup()

    fx=build_integrated()
    try:
        # Child-state token never covered by the admitted projection: no caller tie-break or fallback.
        assert current_proposal(fx,('QU','H0','C-UNSEEN','MU'),'UNSEEN') is None
    finally:
        fx['td'].cleanup()


def test_ms2063_projection_and_request_currentness_fail_closed_without_history_erasure():
    # Target-representation drift stales bound request caps and therefore learned relations/routing.
    fx=build_integrated(); ms=fx['ms']
    try:
        old_ids=tuple(fx['old_rel'].values()); new_ids=tuple(fx['new_rel'].values()); bid=fx['routing_id']
        out=ms.change_epistemic_projection('TARGET-P',new_signature_sha256='a'*64,reason='MS2063-TARGET-DRIFT')
        assert set(x.capability_id for x in fx['bound']).issubset(set(out['stale_capability_ids']))
        assert all(ms.action_outcome_predictive_relation_status(r)['status']=='STALE_PREDICTIVE_RELATION' for r in old_ids+new_ids)
        assert ms.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert all(r in ms.action_outcome_learning.relations for r in old_ids+new_ids)
    finally: fx['td'].cleanup()

    # Base request-channel drift transitively stales the same specializations.
    fx=build_integrated(); ms=fx['ms']
    try:
        stale=ms.change_capability_dependency('REQ-BASE',reason='MS2063-BASE-REQUEST-DRIFT')
        assert set(x.capability_id for x in fx['bound']).issubset(set(stale))
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
    finally: fx['td'].cleanup()

    # Context projection drift stales only the routing surface; relations/history remain present.
    fx=build_integrated(); ms=fx['ms']
    try:
        old_new=tuple(fx['old_rel'].values())+tuple(fx['new_rel'].values()); bid=fx['routing_id']
        ms.change_epistemic_projection('CTX-P',new_signature_sha256='b'*64,reason='MS2063-CONTEXT-DRIFT')
        assert ms.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert bid in ms.action_outcome_learning.projection_conditioned_bindings
        assert all(r in ms.action_outcome_learning.relations for r in old_new)
    finally: fx['td'].cleanup()


def test_ms2063_restart_preserves_lineage_but_requires_explicit_runtime_reregistration():
    fx=build_integrated(); ms=fx['ms']; root=Path(fx['td'].name)
    try:
        ids=tuple(x.capability_id for x in fx['bound']); sigs=tuple(x.computed_signature_sha256() for x in fx['bound'])
        bid=fx['routing_id']; old_rel=dict(fx['old_rel']); new_rel=dict(fx['new_rel']); tokens=tuple(fx['target_tokens'])
        ms2=Microseed(root)
        assert 'TARGET-P' in ms2.epistemic_projections.records and 'CTX-P' in ms2.epistemic_projections.records
        assert bid in ms2.action_outcome_learning.projection_conditioned_bindings
        assert all(r in ms2.action_outcome_learning.relations for r in tuple(old_rel.values())+tuple(new_rel.values()))
        assert 'REQ-BASE' not in ms2.capabilities.contracts and all(cid not in ms2.capabilities.contracts for cid in ids)
        assert ms2.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'

        world2=TwoLevelWorld(); world2.bind_targets(tokens)
        register_runtime(ms2,world2,register_frame_state=True)
        target_rec=ms2.epistemic_projections.records['TARGET-P']
        rebound=derive_bound_requests(ms2,world2,target_rec,tokens)
        assert tuple(x.capability_id for x in rebound)==ids
        assert tuple(x.computed_signature_sha256() for x in rebound)==sigs
        assert ms2.projection_conditioned_relation_routing_status(bid)['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'

        fx2={**fx,'ms':ms2,'world':world2,'bound':rebound}
        p=current_proposal(fx2,('RST','H0','C1','RST2'),'RST'); assert p is not None
        assert p.sequence==(rebound[1].capability_id,)
        intent=ms2.nominate_bounded_action_intent(p.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED'
        ex=ms2.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED'
        assert ex['handler_value']['target']==tokens[1]
    finally:
        fx['td'].cleanup()
