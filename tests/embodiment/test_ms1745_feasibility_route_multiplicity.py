from microseed import Authority, CapabilityContract, QualificationState
from microseed.development.epistemic_action import derive_current_grounded_feasibility_surface
from microseed.runtime.types import FeasibilityState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture


def _add_route(m, fid, target, state, calls):
    m.register_capability(CapabilityContract(
        fid, f'feas-{target}', {'target_capability_id':target}, {}, (), (),
        Authority.DERIVED_READ_ONLY, ('MS1745',), 'CURRENT', {}, dependencies=(target,),
        query_obligation_id='QF-'+fid, qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda _fid=fid, _state=state, **_: calls.append(_fid) or {'feasibility':_state,'reason':'ROUTE'},
        operational_scope_id='S',
    ))


def _by_target(options): return {x.capability_id:x for x in options}


def test_two_current_routes_agree_without_independence_or_truth_gain():
    td,m,effect_calls,world,trial,dc=fixture(); route_calls=[]
    try:
        _add_route(m,'FEAS-A-2','A','FEASIBLE',route_calls)
        options,basis=derive_current_grounded_feasibility_surface(capabilities=m.capabilities,operational_scope_id='S')
        assert _by_target(options)['A'].feasibility == FeasibilityState.FEASIBLE
        assert basis['A']['reason']=='ROUTE_AGREEMENT_WITHOUT_INDEPENDENCE_GAIN'
        assert basis['A']['evidence_independence_authority']==basis['A']['truth_authority']=='NONE'
        assert basis['A']['route_ids']==('FEAS-A','FEAS-A-2')
        assert route_calls==['FEAS-A-2'] and effect_calls==[]
    finally: td.cleanup()


def test_route_disagreement_projects_unknown_not_pick_first_or_vote():
    td,m,effect_calls,world,trial,dc=fixture(); route_calls=[]
    try:
        _add_route(m,'FEAS-A-2','A','REFUSED',route_calls)
        options,basis=derive_current_grounded_feasibility_surface(capabilities=m.capabilities,operational_scope_id='S')
        assert _by_target(options)['A'].feasibility == FeasibilityState.UNKNOWN
        assert basis['A']['reason']=='CURRENT_FEASIBILITY_ROUTE_DISAGREEMENT'
        assert basis['A']['route_results']==(('FEAS-A','FEASIBLE'),('FEAS-A-2','REFUSED'))
        assert effect_calls==[]
    finally: td.cleanup()


def test_single_route_retains_existing_bounded_feasibility_semantics():
    td,m,effect_calls,world,trial,dc=fixture()
    try:
        world['A']='REFUSED'
        options,basis=derive_current_grounded_feasibility_surface(capabilities=m.capabilities,operational_scope_id='S')
        assert _by_target(options)['A'].feasibility == FeasibilityState.REFUSED
        assert basis['A']['reason']=='SINGLE_CURRENT_ROUTE'
        assert effect_calls==[]
    finally: td.cleanup()


def test_no_current_route_means_no_option_not_fabricated_unknown_route():
    td,m,effect_calls,world,trial,dc=fixture()
    try:
        m.capabilities.contracts['FEAS-A'].currentness='STALE'
        options,basis=derive_current_grounded_feasibility_surface(capabilities=m.capabilities,operational_scope_id='S')
        assert 'A' not in _by_target(options)
        assert 'A' not in basis
        assert effect_calls==[]
    finally: td.cleanup()
