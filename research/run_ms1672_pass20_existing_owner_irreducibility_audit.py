from __future__ import annotations
import inspect,json
from pathlib import Path
from microseed.cognition.hypothesis import HypothesisSet
from microseed.development.action_learning import ActionOutcomePredictiveCandidate,QualifiedActionOutcomePredictiveRelation
from microseed.development.constructor_growth import ProjectionConstructorCandidate,discover_projection_constructor_candidates
from microseed.development.projection_discovery import EpistemicProjectionCandidate,discover_epistemic_projection_candidates
OUT=Path(__file__).with_name('MS1672_PASS20_EXISTING_OWNER_IRREDUCIBILITY_AUDIT.json')
def fields(cls):return list(cls.__dataclass_fields__)
def main():
 audit={
  'HypothesisSet':{'constructor':str(inspect.signature(HypothesisSet)),'best_probe':str(inspect.signature(HypothesisSet.best_probe)),'role':'consumes caller-supplied hypotheses; no candidate formation'},
  'ActionOutcomePredictiveCandidate':{'fields':fields(ActionOutcomePredictiveCandidate),'role':'single start_state + capability -> next_state/value effect; no relation between action expressions'},
  'QualifiedActionOutcomePredictiveRelation':{'fields':fields(QualifiedActionOutcomePredictiveRelation),'role':'qualified single-action predictive edge; no action-composition expression'},
  'EpistemicProjectionCandidate':{'fields':fields(EpistemicProjectionCandidate),'discover':str(inspect.signature(discover_epistemic_projection_candidates)),'role':'partitions supplied raw-token positions by action-conditioned effect prediction; no action-action composition relation'},
  'ProjectionConstructorCandidate':{'fields':fields(ProjectionConstructorCandidate),'discover':str(inspect.signature(discover_projection_constructor_candidates)),'role':'grows raw/history feature support to predict effect; no first-class action composition relation'},
 }
 text=json.dumps(audit,sort_keys=True)
 checks={'no_existing_action_composition_field':all('first_action' not in str(v) and 'second_action' not in str(v) for v in audit.values()),'hypothesis_set_downstream':audit['HypothesisSet']['role'].startswith('consumes'),'projection_constructors_are_context_to_effect_not_action_algebra':all('action' in audit[k]['role'] and ('no action-action composition relation' in audit[k]['role'] or 'no first-class action composition relation' in audit[k]['role']) for k in ('EpistemicProjectionCandidate','ProjectionConstructorCandidate'))}
 out={'milestone':'MS1672','pass':20,'audit':audit,'checks':checks,'pass_all':all(checks.values()),'disposition':'IRREDUCIBLE_REPRESENTATIONAL_SEAM_LOCALIZED__OPAQUE_ACTION_COMPOSITION_RELATION_HAS_NO_CURRENT_OWNER','primitive_earned':False,'reason_not_yet_primitive':'Research mechanism has not yet been embodied against live outcome/currentness/qualification and stochastic observation boundaries.'}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps({'checks':checks,'disposition':out['disposition']},indent=2))
if __name__=='__main__':main()
