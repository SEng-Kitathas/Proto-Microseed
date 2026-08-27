from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import (
    Microseed,TernaryCommitment,RelationalCommitment,FeasibilityState,EpistemicStatus,QualificationState,
    project_feasibility,project_epistemic_status,project_qualification_state,project_epistemic_deficit_state,
)
from microseed.development.epistemic import EpistemicDeficitState,EpistemicBearingKind
from microseed.runtime.types import Authority,ResourceMode

checks={}
# Coarse commitment and honest abstention.
checks['yes_no_unknown_exact_commitment_alphabet']={x.value for x in TernaryCommitment}=={'YES','NO','UNKNOWN'}
checks['feasibility_exact_projection']=all([
 project_feasibility(FeasibilityState.FEASIBLE,commitment_id='f1',target_id='F').commitment==TernaryCommitment.YES,
 project_feasibility(FeasibilityState.REFUSED,commitment_id='f2',target_id='F').commitment==TernaryCommitment.NO,
 project_feasibility(FeasibilityState.UNKNOWN,commitment_id='f3',target_id='F').commitment==TernaryCommitment.UNKNOWN])
# Binding/applicability split; NULL is derived only from explicit NO, not uncertainty.
b=RelationalCommitment('b','P',TernaryCommitment.YES,binding=TernaryCommitment.UNKNOWN)
a=RelationalCommitment('a','P',TernaryCommitment.YES,applicability=TernaryCommitment.NO)
checks['binding_unknown_ne_null']=b.gate_unknown and not b.coarse_null and b.abstains()
checks['inapplicable_is_coarse_null_not_fourth_commitment']=a.coarse_null and a.commitment==TernaryCommitment.YES and not a.evaluable
# Native NOT_APPLICABLE maps to withheld commitment plus applicability NO.
na=project_epistemic_status(EpistemicStatus.NOT_APPLICABLE,commitment_id='na',target_id='Q')
checks['native_not_applicable_axis_split']=na.commitment==TernaryCommitment.UNKNOWN and na.applicability==TernaryCommitment.NO
# Conflict/ignorance remain distinct under same UNKNOWN.
ign=RelationalCommitment('i','P',TernaryCommitment.UNKNOWN,reason='IGNORANCE',qualifiers=(('pressure','SEEK_EVIDENCE'),))
con=RelationalCommitment('c','P',TernaryCommitment.UNKNOWN,reason='CONFLICT',qualifiers=(('pressure','DISCRIMINATE_CONFLICT'),))
checks['conflict_vs_ignorance_lossless_sidecar']=ign.commitment==con.commitment and ign.qualifier('pressure')!=con.qualifier('pressure')
# Lifecycle/currentness do not become extra commitment values.
st=project_qualification_state(QualificationState.STALE,commitment_id='s',target_id='C')
checks['stale_is_sidecar_not_commitment']=st.commitment==TernaryCommitment.UNKNOWN and st.qualifier('currentness')=='STALE'
defs=[project_epistemic_deficit_state(x,commitment_id='d'+str(i),target_id='D') for i,x in enumerate(EpistemicDeficitState)]
checks['deficit_lifecycle_preserved_under_unknown']=all(x.commitment==TernaryCommitment.UNKNOWN for x in defs) and {x.qualifier('epistemic_lifecycle') for x in defs}=={x.value for x in EpistemicDeficitState}
# Recursive reference preserves ancestry and grants no implicit authority.
base=RelationalCommitment('base','P',TernaryCommitment.UNKNOWN)
meta=RelationalCommitment('meta','commitment:base:grounded',TernaryCommitment.YES,premise_ids=('base',),qualifiers=(('authority_gain','NONE'),))
checks['recursive_reification_preserves_ancestry_without_authority_gain']=RelationalCommitment.from_serializable(meta.serializable())==meta and meta.qualifier('authority_gain')=='NONE'
# Native orthogonal types preserved; no generic ternarization adapters.
import microseed.development.commitment_adapters as adapters
checks['authority_not_truth_adapter']=not hasattr(adapters,'project_authority') and Authority.EFFECT.value=='EFFECT'
checks['resource_mode_not_truth_adapter']=not hasattr(adapters,'project_resource_mode') and ResourceMode.FEDERATED.value=='FEDERATED'
checks['bearing_kind_not_erased']=not hasattr(adapters,'project_bearing_kind') and EpistemicBearingKind.MODEL_SPACE_CHALLENGE!=EpistemicBearingKind.DISCRIMINATES_LIVE_SET
checks['native_enums_preserved']=('STALE' in {x.value for x in QualificationState} and 'ACTION_LIMITED' in {x.value for x in EpistemicDeficitState} and 'NOT_APPLICABLE' in {x.value for x in EpistemicStatus})
# Truth and universal logic are not promoted by the adapter layer.
checks['no_world_truth_api']=not hasattr(RelationalCommitment,'world_truth') and not hasattr(RelationalCommitment,'settle_truth')
checks['no_universal_kleene_reasoner']=not hasattr(Microseed,'kleene_reason') and not hasattr(Microseed,'truth_table_reason')
# Current milestone/portfolio state.
with tempfile.TemporaryDirectory(prefix='ms1377-replay-') as td:
 ms=Microseed(Path(td));stt=ms.status()
 checks['ms1377_terminal_ms1378_hard_stop']=stt['research_terminal_ms']>=1377 and stt['integration_evidence_through_ms']>=1377 and stt['next_ms']>=1378 and stt.get(f"ms{stt['next_ms']}_started") is False
 checks['global_frontier_returns_to_whole_system_control_loop']=('TRCH_ARCHITECTURAL_COMPRESSION' not in stt['frontier'] and stt['research_terminal_ms']>=1402)

out={'schema':'microseed.maindev-replay.ms1353-1377.v1','checks':checks,'passed':sum(checks.values()),'total':len(checks),'all_pass':all(checks.values())}
Path('MS1353_1377_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
raise SystemExit(0 if out['all_pass'] else 1)
