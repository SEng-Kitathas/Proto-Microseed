from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from microseed import Microseed
from microseed.runtime.types import QueryObligation, CapabilityContract
from research.run_ms1536_habitat_r2_whole_organism import register_current_surfaces, collect_pre_drift_random_training, seed_training

ROOT=Path(__file__).parents[1]


def sha(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # Live behavioral surface: derive one current effect-witness packet from actual current code.
    with tempfile.TemporaryDirectory(prefix='ms1551-gap-audit-') as td:
        ms=Microseed(Path(td));register_current_surfaces(ms);seed_training(ms,collect_pre_drift_random_training(1551))
        result=ms.derive_multi_value_action_licenses(('ENERGY','THERMAL','INTEGRITY'))
        effect_keys=sorted({k for row in result.get('effect_witnesses',{}).values() for k in row})

    entity_src=(ROOT/'microseed/runtime/entity.py').read_text()
    types_src=(ROOT/'microseed/runtime/types.py').read_text()
    witness_occurrences=(entity_src+types_src).count('witness_predicate')
    q_fields=list(QueryObligation.__dataclass_fields__)
    c_fields=list(CapabilityContract.__dataclass_fields__)
    uncertainty_markers=('uncertainty','variance','std','sigma','confidence','credible','effect_low','effect_high','reliability')
    effect_has_uncertainty=any(any(marker in key.lower() for marker in uncertainty_markers) for key in effect_keys)
    query_has_use_sufficiency=any(any(marker in field.lower() for marker in ('assurance','risk','reliab','uncertainty','tolerance')) for field in q_fields)

    out={
      'schema':'microseed.ms1551.pass24.use-sufficiency-gap-audit.v1',
      'discriminator':'DOES_LIVE_MICROSEED_ALREADY_HAVE_AN_OWNER_FOR_QUERY_RELATIVE_CONSEQUENCE_EVIDENCE_SUFFICIENCY_OR_WOULD_PROMOTING_PASS22_REQUIRE_A_NEW_DISTINCTION',
      'live_code':{
        'QueryObligation_fields':q_fields,
        'CapabilityContract_fields':c_fields,
        'derived_effect_witness_keys':effect_keys,
        'effect_witness_has_explicit_uncertainty_or_reliability':effect_has_uncertainty,
        'query_obligation_has_explicit_use_sufficiency_dimension':query_has_use_sufficiency,
        'witness_predicate_literal_occurrences_in_types_plus_entity':witness_occurrences,
        'file_sha256':{
          'microseed/runtime/types.py':sha(ROOT/'microseed/runtime/types.py'),
          'microseed/development/discovery.py':sha(ROOT/'microseed/development/discovery.py'),
          'microseed/development/action_licensing.py':sha(ROOT/'microseed/development/action_licensing.py'),
          'microseed/runtime/entity.py':sha(ROOT/'microseed/runtime/entity.py'),
        },
      },
      'evidence_reconciliation':{
        'pass21':'some control-relevant effects, especially REST, are not sign-identifiable within one R2 regime under current learner-visible noise/opportunity',
        'pass22':'one supplied interval scheme reduced false-green licenses in one bounded assay while preserving some action',
        'pass23':'that exact interval scheme did not provide a uniform advantage across all drift regimes; estimator/threshold mechanism not promoted',
        'witness_predicate_lineage':'historically earned for exact witness-for-query-obligation correspondence, not for statistical assurance or risk tolerance; do not repurpose silently',
      },
      'surviving_candidate_law':'CURRENT_EFFECT_EVIDENCE != EFFECT_EVIDENCE_SUFFICIENT_FOR_THIS_CONSEQUENTIAL_USE',
      'disposition':'NARROWED_SURVIVED_DISTINCTION_PRESSURE__NO_CURRENT_OWNER__SPECIFIC_ESTIMATOR_AND_USE_CONTRACT_UNRESOLVED__NO_MAINDEV_MUTATION',
      'primitive_earned':False,
      'main_dev_mutation':'NONE',
      'nonclaims':['NO_CONFIDENCE_INTERVAL_STANDARD','NO_RISK_TOLERANCE_FIELD_EARNED','NO_PAL_ARCHITECTURE_IMPORT','NO_WITNESS_PREDICATE_REPURPOSING','NO_WHOLE_ORGANISM_CREDIT'],
    }
    p=Path(__file__).with_name('MS1551_PASS24_USE_SUFFICIENCY_GAP_AUDIT.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
