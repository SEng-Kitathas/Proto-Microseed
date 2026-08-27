from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent; P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_3.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_2.json'; BASE=json.loads(P.read_text())
def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v2.2':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 t=p.get('relational_commitment_policy',{})
 if t.get('commitment_values')!=['YES','NO','UNKNOWN']:e.append('TERNARY_COMMITMENT')
 if t.get('binding_values')!=['YES','NO','UNKNOWN']:e.append('TERNARY_BINDING')
 if t.get('applicability_values')!=['YES','NO','UNKNOWN']:e.append('TERNARY_APPLICABILITY')
 for k in ('binding_applicability_orthogonal','unknown_is_explicit_abstention','null_is_derived_only_from_explicit_binding_or_applicability_no','unknown_gate_is_not_null','sidecar_must_preserve_behaviorally_relevant_distinctions','recursive_reference_preserves_ancestry','graded_evidence_may_remain_continuous','native_lifecycle_enums_preserved','authority_remains_orthogonal','resource_mode_remains_orthogonal','bearing_kind_remains_typed','qualification_currentness_lifecycle_not_ternarized_wholesale','epistemic_deficit_lifecycle_preserved_under_unknown'):
  if t.get(k) is not True:e.append('TRCH:'+k)
 if t.get('recursive_reference_grants_authority')!='NONE':e.append('REIFICATION_AUTH')
 if t.get('general_truth_logic')!='NOT_INTEGRATED':e.append('TRUTH_LOGIC')
 if t.get('general_symbolic_reasoner')!='NOT_INTEGRATED':e.append('SYMBOLIC')
 a=p.get('architectural_interrupt_policy',{})
 expected={'single_bound_null_sidecar':'REJECTED_AS_TOO_COARSE','strong_kleene_universal_composition':'NOT_INTEGRATED','authority_as_truth':'FORBIDDEN','recency_as_truth':'FORBIDDEN','cycle_implies_invalid':'FORBIDDEN','premise_support_loss_implies_null':'FORBIDDEN','reification_implies_metacognition':'FORBIDDEN','truth_authority':'NONE','bulk_native_enum_replacement':'FORBIDDEN_UNTIL_DIFFERENTIAL_LOSSLESS_REPLACEMENT_EVIDENCE'}
 for k,v in expected.items():
  if a.get(k)!=v:e.append('INTERRUPT:'+k)
 if a.get('hypothesis_status')!='OARR_NARROWED_SURVIVED__INTEGRATED_AS_COMMON_PRIMITIVE_PLUS_ADAPTERS_ONLY':e.append('STATUS')
 for k in BASE.get('refinements_from_ms1353_1377',{}):
  if p.get('refinements_from_ms1353_1377',{}).get(k) is not True:e.append('DROP:'+k)
 ci=p.get('current_integration',{})
 if ci.get('research_terminal_ms')!=1377 or ci.get('integration_terminal_ms')!=1377:e.append('TERMINAL')
 if ci.get('ms1378_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1377-BOUNDED-DELIBERATION-TO-ACTION-OUTCOME-CLOSURE__TRCH-CONSTRAINED-WHOLE-SYSTEM-PRELINGUAL-CONTROL-LOOP':e.append('FRONTIER')
 if p.get('language_policy',{}).get('active_phase')!='PRELINGUAL':e.append('LANGUAGE_PHASE')
 return not e,e

def setpath(x,path,val):
 cur=x; parts=path.split('.')
 for k in parts[:-1]:cur=cur[k]
 cur[parts[-1]]=val

def main():
 p=json.loads(P.read_text()); ok,errs=validate(p); muts=[]
 specs=[
 ('drop_unknown','relational_commitment_policy.commitment_values',['YES','NO']),('fourth','relational_commitment_policy.commitment_values',['YES','NO','UNKNOWN','BOTH']),
 ('collapse_binding','relational_commitment_policy.binding_values',['BOUND','NULL']),('collapse_app','relational_commitment_policy.applicability_values',['APPLICABLE','INAPPLICABLE']),
 ('reification_auth','relational_commitment_policy.recursive_reference_grants_authority','TRUTH'),('truth_logic','relational_commitment_policy.general_truth_logic','STRONG_KLEENE'),
 ('symbolic','relational_commitment_policy.general_symbolic_reasoner','INTEGRATED'),('bulk','architectural_interrupt_policy.bulk_native_enum_replacement','ALLOWED'),
 ('authority_truth','architectural_interrupt_policy.authority_as_truth','ALLOWED'),('recency_truth','architectural_interrupt_policy.recency_as_truth','ALLOWED'),
 ('cycle','architectural_interrupt_policy.cycle_implies_invalid','REQUIRED'),('support_null','architectural_interrupt_policy.premise_support_loss_implies_null','REQUIRED'),
 ('meta','architectural_interrupt_policy.reification_implies_metacognition','REQUIRED'),('kleene','architectural_interrupt_policy.strong_kleene_universal_composition','INTEGRATED'),
 ('start','current_integration.ms1378_started',True),('terminal','current_integration.research_terminal_ms',1378),('frontier','current_integration.selected_frontier','GENERAL_SYMBOLIC_PLANNER'),
 ('language','language_policy.active_phase','LINGUISTIC')]
 for n,path,val in specs:
  x=copy.deepcopy(p);setpath(x,path,val);muts.append((n,x))
 for k in ('binding_applicability_orthogonal','unknown_is_explicit_abstention','null_is_derived_only_from_explicit_binding_or_applicability_no','unknown_gate_is_not_null','sidecar_must_preserve_behaviorally_relevant_distinctions','recursive_reference_preserves_ancestry','graded_evidence_may_remain_continuous','native_lifecycle_enums_preserved','authority_remains_orthogonal','resource_mode_remains_orthogonal','bearing_kind_remains_typed','qualification_currentness_lifecycle_not_ternarized_wholesale','epistemic_deficit_lifecycle_preserved_under_unknown'):
  x=copy.deepcopy(p);x['relational_commitment_policy'][k]=False;muts.append(('drop_'+k,x))
 for k in BASE['refinements_from_ms1353_1377']:
  x=copy.deepcopy(p);x['refinements_from_ms1353_1377'][k]=False;muts.append(('drop_refinement_'+k,x))
 # additional attractive-but-forbidden donor mutations
 extras=[('single_null','architectural_interrupt_policy.single_bound_null_sidecar','INTEGRATED'),('truth_auth','architectural_interrupt_policy.truth_authority','INTERNAL'),('hypothesis_overpromote','architectural_interrupt_policy.hypothesis_status','UNIVERSAL_COGNITIVE_SUBSTRATE_PROVED')]
 for n,path,val in extras:
  x=copy.deepcopy(p);setpath(x,path,val);muts.append((n,x))
 escaped=[n for n,x in muts if validate(x)[0]]
 out={'schema':'microseed.maindev-operating-profile-validation.v2.3','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(muts),'hostile_mutants_rejected':len(muts)-len(escaped),'escaped':escaped,'all_pass':ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_3_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
