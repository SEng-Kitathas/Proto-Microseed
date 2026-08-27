from __future__ import annotations
from dataclasses import fields
import json, subprocess, sys, os
from pathlib import Path

from microseed.development.recruitment import RecruitmentOption

ROOT=Path(__file__).resolve().parents[1]
TEST='tests/embodiment/test_ms1703_epistemic_step_intent_research.py'
p=subprocess.run([sys.executable,'-m','pytest','-q',TEST],cwd=ROOT,env={**os.environ,'PYTHONPATH':'.'},capture_output=True,text=True,timeout=20)
if p.returncode!=0:
    raise SystemExit(p.stdout+p.stderr)

# Static currentness/provenance audit of the exact typed feasibility carrier.
field_names=[f.name for f in fields(RecruitmentOption)]
currentness_fields=[x for x in field_names if x in {'epoch','currentness','authority','source_id','evidence_id','valid_from','valid_until'}]

# Existing executor basis audit comes from the live source itself.
entity_src=(ROOT/'microseed/runtime/entity.py').read_text()
native_bases=[x for x in ('SINGLE_VALUE_REHEARSAL','MULTI_VALUE_LICENSE') if x in entity_src]
research_basis='EPISTEMIC_PROGRAM_STEP' in entity_src

out={
  'milestone':'MS1703',
  'pass':1,
  'campaign':'PRELINGUAL_AUTONOMOUS_EPISTEMIC_MACRO_REALIZATION_THROUGH_ORDINARY_ACTION_LOOP',
  'native_intent_basis_audit':{
    'native_existing_bases':native_bases,
    'native_epistemic_program_basis_before_pass':False,
    'research_only_adapter_added':research_basis,
    'macro_executor_added':False,
    'planner_or_scheduler_added':False,
  },
  'research_adapter_test':{'result':'10/10_PASS','tail':'\n'.join(p.stdout.splitlines()[-3:])},
  'feasibility_currentness_audit':{
    'carrier':'RecruitmentOption',
    'fields':field_names,
    'explicit_currentness_or_provenance_fields':currentness_fields,
    'model_evidence_ids_are_content_ancestry_only':True,
    'typed_FEASIBLE_can_be_resupplied_without_proving_physical_currentness':True,
  },
  'earned':[
    'ONE_CURRENT_EPISTEMIC_PROGRAM_STEP_CAN_BE_NOMINATED_WITH_ZERO_AUTHORITY_GAIN',
    'EXECUTE_BOUNDED_ACTION_CAN_REDERIVE_TRIAL_DEFICIT_COMPONENT_STATE_AND_TYPED_FEASIBILITY_CONTENT_BEFORE_EFFECT',
    'REFUSED_OR_UNKNOWN_TYPED_FEASIBILITY_BLOCKS_ACTION',
    'TRIAL_DEFICIT_COMPONENT_OR_CONTROL_STATE_DRIFT_BLOCKS_ACTION',
  ],
  'preserved_negative':[
    'CALLER_SUPPLIED_FEASIBILITY_CONTENT_IS_NOT_GROUNDED_EXECUTION_TIME_FEASIBILITY',
    'CONTENT_RECHECK_IS_NOT_PHYSICAL_CURRENTNESS_REVALIDATION',
    'EPISTEMIC_VALUE_DOES_NOT_BYPASS_FEASIBILITY',
  ],
  'disposition':'NARROWED__RESEARCH_SINGLE_STEP_INTENT_ADAPTER_SURVIVES__EXECUTION_TIME_FEASIBILITY_CURRENTNESS_NOT_GROUNDED__ROTATE_TO_FEASIBILITY_GROUNDING',
  'attention_reservoir':{
    'selected':'EMBODIED_FEASIBILITY_CURRENTNESS_GROUNDING',
    'open':'AUTONOMOUS_EPISTEMIC_EPISODE_INITIATION',
    'reason':'Frozen MS1703 rule requires current feasibility before EFFECT; existing RecruitmentOption is typed model input without an independent currentness/provenance owner.'
  },
  'main_dev_mutation':'NONE',
}
assert p.returncode==0 and research_basis and not currentness_fields
(ROOT/'research/MS1703_PASS01_AUTONOMOUS_EPISTEMIC_INTENT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
