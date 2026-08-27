from __future__ import annotations
from pathlib import Path
import json,tempfile,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))

from microseed import Microseed,Authority,CapabilityContract,QualificationState,RecruitmentTopologyContract,FeasibilityState
from microseed.development.recruitment import RecruitmentOption


def cap(cid,deps=()):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1003-1027-REPLAY',),'CURRENT',{},dependencies=tuple(deps),qualification=QualificationState.SHADOW_QUALIFIED)


def topo(ms,tid='T'):
    t=RecruitmentTopologyContract(
        topology_id=tid,purpose='opaque-topology',relations=(('A','B'),),capability_epochs=(('A',ms.capabilities.epochs['A']),('B',ms.capabilities.epochs['B'])),
        signature_sha256='',authority=Authority.DERIVED_READ_ONLY,lineage=('MS1003-1027',),currentness='CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('HSP_EXTERNAL_TOPOLOGY_QUALIFICATION',),invariants=('NO_SEMANTIC_ROLE_AUTHORITY','NO_IDENTITY_AUTHORITY'),hazards=('PAIRWISE_LANGUAGE',),
    );t.signature_sha256=t.computed_signature_sha256();return t


def build(ms,order=('A','B')):
    for cid in order: ms.register_capability(cap(cid))
    ms.register_recruitment_topology(topo(ms))


def main():
    with tempfile.TemporaryDirectory(prefix='ms1003-1027-replay-a-') as a, tempfile.TemporaryDirectory(prefix='ms1003-1027-replay-b-') as b:
        m1=Microseed(Path(a));build(m1,('A','B'))
        p=m1.nominate_recruitment((RecruitmentOption('A',FeasibilityState.FEASIBLE,resource_tags=('a',)),RecruitmentOption('B',FeasibilityState.FEASIBLE,resource_tags=('b',))),('A','B'),topology_id='T')
        current_before=m1.recruitment_status(p.proposal_id)
        m1.register_capability(cap('X'),topology_dependencies=(('T',0),));m1.register_capability(cap('Y',deps=('X',)))
        m1.change_capability_dependency('A',reason='STRUCTURAL_CONSTITUENT_DRIFT')
        after=m1.recruitment_status(p.proposal_id)
        states={k:v.qualification.value for k,v in m1.capabilities.contracts.items() if k in {'A','X','Y'}}
        topo_current=m1.topologies.is_current('T')
        snapshot=m1.topologies.snapshot()['T']

        # Same terminal topology bytes, different developmental path order.
        m2=Microseed(Path(b));build(m2,('B','A'))
        same_terminal=(m2.topologies.snapshot()['T']['contract']['relations']==snapshot['contract']['relations'])
        biography_relation=m1.compare_biography(m2.biography.export())
        status=m1.status()
        checks={
            'qualified_topology_was_current':current_before['status']=='CURRENT',
            'constituent_drift_stales_topology':not topo_current,
            'bound_recruitment_unknown_after_topology_drift':after['status']=='UNKNOWN_INCOMPLETE',
            'topology_bound_capability_stales':states.get('X')=='STALE',
            'second_order_topology_dependent_stales':states.get('Y')=='STALE',
            'historical_topology_retained':snapshot['contract']['relations']==[['A','B']] or snapshot['contract']['relations']==(('A','B'),),
            'topology_no_semantic_role_authority':snapshot['contract']['semantic_role_authority']=='NONE',
            'topology_no_identity_authority':snapshot['contract']['identity_authority']=='NONE',
            'same_terminal_topology_possible':same_terminal,
            'same_terminal_topology_not_same_biography':biography_relation!='SAME_BIOGRAPHY_STATE',
            'identity_still_unqualified':status['identity_claim']=='NOT_QUALIFIED' and status['topology_identity_authority']=='NONE',
            'pairwise_constructor_not_promoted':not hasattr(m1,'discover_recruitment_topology') and 'RESEARCH_MECHANISM_NOT_ENTITY_AUTHORITY' in status['topology_constructor'],
            'prelingual_hard_stop':status['language']=='DEFERRED_PRELINGUAL_COGNITION_ACTIVE' and status['next_ms']>=1203 and status.get(f"ms{status['next_ms']}_started") is False,
            'selected_cross_family_frontier':status['research_terminal_ms']>=1252 and status['frontier'].startswith('ATTN-MS'),
        }
        out={'schema':'microseed.ms1003-1027-maindev-replay.v0.9','checks':checks,'all_pass':all(checks.values()),'recruitment_before':current_before,'recruitment_after':after,'capability_states_after_constituent_drift':states,'topology_snapshot_after_drift':snapshot,'same_terminal_topology':same_terminal,'biography_relation':biography_relation,'status':status}
        print(json.dumps(out,indent=2,sort_keys=True))
        raise SystemExit(0 if out['all_pass'] else 1)

if __name__=='__main__': main()
