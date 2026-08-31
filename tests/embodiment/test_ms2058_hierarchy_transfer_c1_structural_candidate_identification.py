from pathlib import Path
import tempfile

from microseed import (
    Microseed, Authority, QualificationState, FeasibilityState, EpistemicStatus,
    CapabilityContract, OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract,
    RecruitmentOption, RehearsalTransitionObservation, QueryObligation, Observation,
    ExternalActionOutcomeRelationQualifier,
)


def new_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms2058-c1-')
    return td,Microseed(Path(td.name))


def cap(cid, *, obligation='ACT', scope='SCOPE', authority=Authority.EFFECT):
    return CapabilityContract(
        cid,'opaque-capability',{},{},(),(),authority,('MS2058-RESEARCH',),'CURRENT',{},
        query_obligation_id=obligation,qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda _cid=cid, **_: {'receipt':_cid},operational_scope_id=scope,
    )


def setup(ms):
    ms.register_operational_frame(OperationalFrameContract(
        'F','opaque-c1','f'*64,Authority.DERIVED_READ_ONLY,('MS2058-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    ms.register_value_variable(ValueVariableContract(
        'V','opaque-regulatory',1.0,10.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS2058-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'),
    ))
    ms.observe_value_state('V',0.0)
    # U1/U2 are useful learned-effect candidates. U3 is current but has no learned relation.
    # U4 has a learned relation but wrong obligation. U5 has a learned relation but wrong scope.
    # R is read-only and can never be an executable request candidate.
    ms.register_capability(cap('U1')); ms.register_capability(cap('U2')); ms.register_capability(cap('U3'))
    ms.register_capability(cap('U4',obligation='OTHER')); ms.register_capability(cap('U5',scope='OTHER'))
    ms.register_capability(cap('R',authority=Authority.DERIVED_READ_ONLY))
    ms.register_episode_schema(EpisodeSchemaContract(
        'E','opaque-c1-episode','e'*64,Authority.DERIVED_READ_ONLY,('MS2058-RESEARCH',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),
    ))


def obligation():
    return QueryObligation('ACT','opaque',required_authority=Authority.EFFECT,operational_scope_id='SCOPE')


def scheduler(ms,state,capid,idx):
    rows=tuple(
        RehearsalTransitionObservation(
            f'SCHED-{state}-{capid}-{idx}-{j}',state,capid,f'WRONG-{state}-{capid}',1.0,0,'F',0,'E',0
        ) for j in range(8)
    )
    return ms.nominate_counterfactual_rehearsal(
        rows,(RecruitmentOption(capid,FeasibilityState.FEASIBLE),),start_state_id=state,value_id='V'
    )


def execute_outcome(ms,state,capid,idx,next_state,effect, *, obl=None):
    ms.observe_value_state('V',0.0)
    ms.observe_opaque_control_state(
        Observation(f'CS-{state}-{capid}-{idx}','EXT','opaque-control',state,authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-CS-{state}-{capid}-{idx}',
    )
    prop=scheduler(ms,state,capid,idx); assert prop is not None
    q=obl or QueryObligation(ms.capabilities.contracts[capid].query_obligation_id,'opaque',required_authority=Authority.EFFECT,operational_scope_id=ms.capabilities.contracts[capid].operational_scope_id)
    intent=ms.nominate_bounded_action_intent(prop.proposal_id,q); assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],q); assert ex['status']=='ACTION_EXECUTED'
    eid=ex['execution']['execution_id']
    out=ms.record_bounded_action_outcome(
        eid,Observation(
            f'OUT-{state}-{capid}-{idx}','EXT',f'action-execution:{eid}',
            {'next_state_id':next_state,'value_id':'V','observed_value':effect},authority=Authority.OBSERVATION_ONLY,
        ),evidence_id=f'E-OUT-{state}-{capid}-{idx}',
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED'


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


def qualify_learned(ms):
    out={}
    for i,c in enumerate(ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)):
        t=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdouts(ms,c,f'H{i}'))
        q=ms.qualify_action_outcome_predictive_relation(t); assert q['status']=='CURRENT_PREDICTIVE_RELATION'
        out[(c.start_state_id,c.capability_id)]=q['relation']['relation_id']
    return out


def populate(ms):
    rows={
        ('HA','U1'):('HA-GOOD',2.0),('HA','U2'):('HA-BAD',-2.0),
        ('HB','U1'):('HB-BAD',-2.0),('HB','U2'):('HB-GOOD',2.0),
        ('HA','U4'):('HA-U4',4.0),('HA','U5'):('HA-U5',5.0),
        ('HA','R'):('HA-R',9.0),
    }
    for (state,cid),(ns,effect) in rows.items():
        # R cannot execute through bounded EFFECT lane, so do not fabricate experience for it.
        if cid=='R':
            continue
        for i in range(8): execute_outcome(ms,state,cid,i,ns,effect)
    return qualify_learned(ms)


def relation_backed_current_effect_candidates(ms, *, start_state_id, obligation):
    """Research-only C1 projection from already-earned owners; grants no authority."""
    out=[]
    for rel in ms.action_outcome_learning.relations.values():
        if rel.start_state_id != start_state_id:
            continue
        if ms.action_outcome_predictive_relation_status(rel.relation_id)['status']!='CURRENT_PREDICTIVE_RELATION':
            continue
        cid=rel.capability_id
        c=ms.capabilities.contracts.get(cid)
        if c is None or not ms.capabilities.is_current(cid):
            continue
        if c.authority != Authority.EFFECT:
            continue
        if c.query_obligation_id != obligation.obligation_id:
            continue
        if c.operational_scope_id != obligation.operational_scope_id:
            continue
        out.append((cid,rel.relation_id,rel.value_effect))
    return tuple(sorted(out))


def test_c1_relation_backed_projection_removes_external_request_shortlist():
    td,ms=new_ms()
    try:
        setup(ms); populate(ms)
        ha=relation_backed_current_effect_candidates(ms,start_state_id='HA',obligation=obligation())
        hb=relation_backed_current_effect_candidates(ms,start_state_id='HB',obligation=obligation())
        assert tuple(x[0] for x in ha)==('U1','U2')
        assert tuple(x[0] for x in hb)==('U1','U2')
        # No learned relation => excluded; wrong obligation/scope => excluded despite strong effects.
        assert all(x[0] not in {'U3','U4','U5','R'} for x in ha+hb)
    finally: td.cleanup()


def test_c1_projection_is_state_specific_not_global_capability_enumeration():
    td,ms=new_ms()
    try:
        setup(ms); populate(ms)
        assert relation_backed_current_effect_candidates(ms,start_state_id='UNSEEN',obligation=obligation())==()
        assert len(ms.capabilities.contracts) > len(relation_backed_current_effect_candidates(ms,start_state_id='HA',obligation=obligation()))
    finally: td.cleanup()


def test_c1_stale_relation_or_capability_is_removed_without_deleting_history():
    td,ms=new_ms()
    try:
        setup(ms); rels=populate(ms); rid=rels[('HA','U1')]
        before=relation_backed_current_effect_candidates(ms,start_state_id='HA',obligation=obligation())
        assert 'U1' in {x[0] for x in before}
        ms.change_capability_dependency('U1',reason='SUBORDINATE_DRIFT')
        after=relation_backed_current_effect_candidates(ms,start_state_id='HA',obligation=obligation())
        assert 'U1' not in {x[0] for x in after}
        assert rid in ms.action_outcome_learning.relations
    finally: td.cleanup()


def test_c1_candidate_projection_does_not_invent_feasibility_or_execution_authority():
    td,ms=new_ms()
    try:
        setup(ms); populate(ms)
        rows=relation_backed_current_effect_candidates(ms,start_state_id='HA',obligation=obligation())
        assert rows
        # Projection returns only identity/relation/effect evidence; feasibility remains a separate owner.
        assert all(len(x)==3 for x in rows)
        # Existing learned relations remain non-executable evidence-bound relations.
        for _,rid,_ in rows:
            rel=ms.action_outcome_learning.relations[rid]
            assert rel.execution_authority=='NONE' and rel.truth_authority=='NONE' and rel.semantic_goal_authority=='NONE'
    finally: td.cleanup()


def test_c1_equal_positive_candidates_remain_a_set_not_an_arbitrary_structural_choice():
    td,ms=new_ms()
    try:
        setup(ms)
        # Same state, two actions, equally positive actual effect. C1 should expose both; ranking is downstream.
        for cid in ('U1','U2'):
            for i in range(8): execute_outcome(ms,'HEQ',cid,i,f'HEQ-{cid}',2.0)
        qualify_learned(ms)
        rows=relation_backed_current_effect_candidates(ms,start_state_id='HEQ',obligation=obligation())
        assert tuple(x[0] for x in rows)==('U1','U2')
        assert tuple(x[2] for x in rows)==(2.0,2.0)
    finally: td.cleanup()


def test_c1_no_semantic_parent_child_or_topology_claim_is_created():
    td,ms=new_ms()
    try:
        setup(ms); populate(ms)
        rows=relation_backed_current_effect_candidates(ms,start_state_id='HA',obligation=obligation())
        assert rows
        assert not hasattr(ms,'discover_child_role')
        assert not hasattr(ms,'hierarchy_manager')
        assert not hasattr(ms,'parent_child_topology')
    finally: td.cleanup()
