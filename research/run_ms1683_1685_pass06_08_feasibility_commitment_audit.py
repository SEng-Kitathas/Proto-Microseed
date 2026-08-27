from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority, CapabilityContract, FeasibilityState, Microseed, QualificationState, RecruitmentOption
from microseed.development.commitment_adapters import project_feasibility, project_qualification_state
from microseed.runtime.commitment import RelationalCommitment,TernaryCommitment,conjoin_required_commitments
from microseed.development.action_closure import BoundedActionIntent

def cap(cid):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1683',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:None)

def run():
    td=tempfile.TemporaryDirectory(prefix='ms1683-')
    try:
        m=Microseed(Path(td.name));m.register_capability(cap('A'));m.register_capability(cap('B'))
        opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE,resource_tags=('ra',)),RecruitmentOption('B',FeasibilityState.FEASIBLE,resource_tags=('rb',)))
        rp=m.nominate_recruitment(opts,('A','B'),operational_scope_id=None,assistance_ancestry=('SUPPLIED_RECRUITMENT_TOPOLOGY',))
        composed=m.compose_recruitment(rp.proposal_id)
        assert composed['status']=='COMPOSED_EPHEMERAL' and composed['plan']==['A','B'] and composed['composition_authority']=='NONE'
        refused=False
        try:m.nominate_recruitment((RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.REFUSED)),('A','B'),assistance_ancestry=('SUPPLIED_RECRUITMENT_TOPOLOGY',))
        except ValueError as e: refused='RECRUITMENT_NOT_FEASIBLE:B:REFUSED' in str(e)
        conflict=False
        try:m.nominate_recruitment((RecruitmentOption('A',FeasibilityState.FEASIBLE,resource_tags=('same',)),RecruitmentOption('B',FeasibilityState.FEASIBLE,resource_tags=('same',))),('A','B'),assistance_ancestry=('SUPPLIED_RECRUITMENT_TOPOLOGY',))
        except ValueError as e: conflict='RECRUITMENT_RESOURCE_CONFLICT' in str(e)
        assert refused and conflict
        discrimination=RelationalCommitment('DISC','macro:AB',TernaryCommitment.YES,reason='DISCRIMINATES_LIVE_SET',qualifiers=(('authority_gain','NONE'),))
        feas=project_feasibility(FeasibilityState.FEASIBLE,commitment_id='FEAS',target_id='macro:AB')
        qa=project_qualification_state(QualificationState.SHADOW_QUALIFIED,commitment_id='QA',target_id='cap:A')
        qb=project_qualification_state(QualificationState.SHADOW_QUALIFIED,commitment_id='QB',target_id='cap:B')
        joint=conjoin_required_commitments((discrimination,feas,qa,qb),commitment_id='JOINT',target_id='macro:AB',reason_prefix='EPISTEMIC_PROGRAM')
        assert joint.licenses_yes() and joint.qualifier('authority_gain')=='NONE'
        basis_kinds=set()
        # Current executor recognizes only these native basis kinds in entity.py; BoundedActionIntent default exposes one of them.
        basis_kinds.add(BoundedActionIntent.__dataclass_fields__['basis_kind'].default)
        src=Path('microseed/runtime/entity.py').read_text()
        if 'MULTI_VALUE_LICENSE' in src:basis_kinds.add('MULTI_VALUE_LICENSE')
        assert 'EPISTEMIC_PROGRAM_PROBE' not in basis_kinds and 'EPISTEMIC_PROGRAM_PROBE' not in src
        out={
          'MS1683_pass06':{'recruitment_plan':composed['plan'],'composition_authority':composed['composition_authority'],'refused_component_rejected':refused,'resource_conflict_rejected':conflict,'disposition':'EXISTING_RECRUITMENT_ENFORCES_CALLER_SUPPLIED_TYPED_FEASIBILITY_AND_RESOURCE_CONFLICTS__DOES_NOT_GRANT_EFFECT_AUTHORITY'},
          'MS1684_pass07':{'joint_epistemic_feasibility_commitment':joint.serializable(),'disposition':'EXISTING_TERNARY_COMMITMENT_ALGEBRA_CAN_CONJOIN_DISCRIMINATION_FEASIBILITY_AND_CURRENT_QUALIFICATION_WITH_ZERO_AUTHORITY_GAIN'},
          'MS1685_pass08':{'recognized_action_intent_basis_kinds':sorted(basis_kinds),'disposition':'NO_EXISTING_ACTION_INTENT_BRIDGE_CONSUMES_EPISTEMIC_PROGRAM_COMMITMENT__EXECUTION_REMAINS_BLOCKED_WITHOUT_NEW_NARROW_WIRING','assistance_debt':'FEASIBILITY_STATE_REMAINS_CALLER_SUPPLIED_AT_THIS_BOUNDARY'},
        }
        Path(__file__).with_name('MS1683_1685_PASS06_08_FEASIBILITY_COMMITMENT_AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True))
        print(json.dumps(out,indent=2,sort_keys=True))
    finally:td.cleanup()
if __name__=='__main__':run()
