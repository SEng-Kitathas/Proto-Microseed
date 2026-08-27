from __future__ import annotations
import inspect,json
from pathlib import Path
from microseed.runtime.types import CapabilityContract,RecruitmentTopologyContract,OperationalCoordinationContract,OperationalCounterpartyContract
from microseed.development.capability_admission import CapabilityCandidate
from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation

def main():
    cap_methods=[x for x in ('signature_payload','computed_signature_sha256') if hasattr(CapabilityContract,x)]
    neighbors={k:[x for x in ('signature_payload','computed_signature_sha256') if hasattr(v,x)] for k,v in {'topology':RecruitmentTopologyContract,'coordination':OperationalCoordinationContract,'counterparty':OperationalCounterpartyContract}.items()}
    out={'pass':'MS1641_PASS14','capability_contract_content_signature_methods':cap_methods,'neighbor_contract_signature_patterns':neighbors,'capability_candidate_has_digest':hasattr(CapabilityCandidate,'digest'),'qualified_relation_premise_fields':[x for x in QualifiedActionOutcomePredictiveRelation.__dataclass_fields__ if x.startswith('evidence_premise')],
         'finding':'CONTENT_BOUND_SIGNATURE_PATTERN_EXISTS_ACROSS_NEIGHBOR_CONTRACTS_AND_CAPABILITY_CANDIDATES_BUT_NOT_ON_ADMITTED_CAPABILITY_CONTRACT_OR_ACTION_RELATION_PREMISE_REFERENCE',
         'irreducible_gap':'historical premise needs immutable content identity in addition to runtime epoch; otherwise restart aliasing survives',
         'candidate_delta':'add stable CapabilityContract signature payload/digest + carry premise signature beside premise epoch through existing action-learning ancestry path',
         'nonclaim':'does not ground or qualify the premise; only prevents identity aliasing','authority':'RESEARCH_ONLY','next':'IMPLEMENT_RESEARCH_ONLY_GENERIC_PREMISE_SIGNATURE_CARRIER_AND_ATTACK_RESTART_ALIAS'}
    Path('research/MS1641_PASS14_CONTENT_SIGNATURE_QUARRY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
