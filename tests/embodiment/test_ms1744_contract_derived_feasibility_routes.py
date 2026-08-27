from microseed import Authority, CapabilityContract, QualificationState
from microseed.development.epistemic_action import derive_current_epistemic_feasibility_routes
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture


def _routes(m):
    return derive_current_epistemic_feasibility_routes(
        capabilities=m.capabilities,
        operational_scope_id='S',
    )


def test_current_contracts_enumerate_existing_feasibility_routes_without_supplied_route_list():
    td,m,calls,world,trial,dc=fixture()
    try:
        rows=_routes(m)
        assert [(target,fid,ob.obligation_id) for target,fid,ob in rows] == [
            ('A','FEAS-A','QF-A'),('B','FEAS-B','QF-B')
        ]
        assert calls == []
    finally: td.cleanup()


def test_bogus_caller_route_has_no_control_over_contract_derived_surface():
    td,m,calls,world,trial,dc=fixture()
    try:
        # No caller route is accepted by the derivation API at all.
        rows=_routes(m)
        assert all(fid != 'FEAS-BOGUS' for _,fid,_ in rows)
        assert calls == []
    finally: td.cleanup()


def test_multiple_current_routes_for_same_target_are_preserved_not_pick_first():
    td,m,calls,world,trial,dc=fixture()
    try:
        m.register_capability(CapabilityContract(
            'FEAS-A-2','feasibility-A-2',{'target_capability_id':'A'},{},(),(),
            Authority.DERIVED_READ_ONLY,('MS1744',),'CURRENT',{},dependencies=('A',),
            query_obligation_id='QF-A-2',qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {'feasibility':'FEASIBLE','reason':'SECOND_ROUTE'},operational_scope_id='S',
        ))
        rows=_routes(m)
        a=[(target,fid,ob.obligation_id) for target,fid,ob in rows if target=='A']
        assert a == [('A','FEAS-A','QF-A'),('A','FEAS-A-2','QF-A-2')]
        assert calls == []
    finally: td.cleanup()


def test_wrong_scope_or_stale_route_cannot_enter_surface():
    td,m,calls,world,trial,dc=fixture()
    try:
        m.register_capability(CapabilityContract(
            'FEAS-A-WRONG-SCOPE','wrong-scope',{'target_capability_id':'A'},{},(),(),
            Authority.DERIVED_READ_ONLY,('MS1744',),'CURRENT',{},dependencies=('A',),
            query_obligation_id='QF-A-X',qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {'feasibility':'FEASIBLE'},operational_scope_id='OTHER',
        ))
        m.capabilities.contracts['FEAS-B'].currentness='STALE'
        rows=_routes(m)
        ids=[fid for _,fid,_ in rows]
        assert 'FEAS-A-WRONG-SCOPE' not in ids
        assert 'FEAS-B' not in ids
        assert ids == ['FEAS-A']
        assert calls == []
    finally: td.cleanup()
