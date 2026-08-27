from __future__ import annotations

import json
import statistics
from pathlib import Path

from sklearn.metrics import balanced_accuracy_score
from sklearn.tree import DecisionTreeClassifier

from research.habitat_r2_exact import ACTIONS
from research.run_ms1537_pass10_r2_projection_quarry import VALUES
from research.run_ms1545_pass18_ordered_affine_baselines import rows, median_by_action, stance_from_effect

MAX_DEPTH = 2
MIN_SAMPLES_LEAF = 3


def fit_action_trees(train: list[dict]) -> dict[str, object]:
    result = {}
    for action in ACTIONS:
        subset = [r for r in train if str(r['action']) == action]
        if len(subset) < MIN_SAMPLES_LEAF * 2:
            continue
        labels = [str(r['actual_stance']) for r in subset]
        if len(set(labels)) == 1:
            result[action] = labels[0]
            continue
        clf = DecisionTreeClassifier(
            max_depth=MAX_DEPTH,
            min_samples_leaf=MIN_SAMPLES_LEAF,
            random_state=0,
            criterion='gini',
        )
        clf.fit([[float(r['pre_value'])] for r in subset], labels)
        result[action] = clf
    return result


def tree_predict(model, pre_value: float) -> str | None:
    if model is None:
        return None
    if isinstance(model, str):
        return model
    return str(model.predict([[pre_value]])[0])


def evaluate(seed: int, channel: str) -> dict:
    samples = rows(seed, channel)
    cut = max(1, int(len(samples) * .70))
    train, validation = samples[:cut], samples[cut:]
    medians = median_by_action(train)
    trees = fit_action_trees(train)

    actuals=[]; median_preds=[]; tree_preds=[]
    details=[]
    for row in validation:
        action=str(row['action']); x=float(row['pre_value']); actual=str(row['actual_stance'])
        med=medians.get(action)
        mp=None if med is None else stance_from_effect(channel,x,med)
        tp=tree_predict(trees.get(action),x)
        actuals.append(actual);median_preds.append(mp);tree_preds.append(tp)
        details.append({'tick':int(row['tick']),'action':action,'pre_value':x,'actual':actual,'ACTION_MEDIAN':mp,'ORDERED_THRESHOLD':tp})

    known=[i for i,p in enumerate(tree_preds) if p is not None]
    tree_actual=[actuals[i] for i in known];tree_known=[tree_preds[i] for i in known]
    median_correct=sum(p==y for p,y in zip(median_preds,actuals))
    tree_correct=sum(tree_preds[i]==actuals[i] for i in known)
    baseline_error=[i for i,(p,y) in enumerate(zip(median_preds,actuals)) if p!=y]
    baseline_correct=[i for i,(p,y) in enumerate(zip(median_preds,actuals)) if p==y]
    recovered=sum(tree_preds[i]==actuals[i] for i in baseline_error if tree_preds[i] is not None)
    broken=sum(tree_preds[i]!=actuals[i] for i in baseline_correct if tree_preds[i] is not None)

    return {
        'seed':seed,'train_rows':len(train),'validation_rows':len(validation),
        'tree_action_count':len(trees),
        'action_median_accuracy':median_correct/max(len(actuals),1),
        'ordered_threshold_coverage':len(known)/max(len(actuals),1),
        'ordered_threshold_accuracy_all_rows':tree_correct/max(len(actuals),1),
        'ordered_threshold_accuracy_when_available':tree_correct/max(len(known),1),
        'ordered_threshold_balanced_accuracy_when_available':float(balanced_accuracy_score(tree_actual,tree_known)) if tree_actual else None,
        'lift_over_action_median_all_rows':(tree_correct-median_correct)/max(len(actuals),1),
        'baseline_error_recovery_rate':recovered/max(len(baseline_error),1),
        'baseline_correct_break_rate':broken/max(len(baseline_correct),1),
        'details':details,
    }


def main():
    channels={}
    for ch in VALUES:
        rs=[evaluate(seed,ch) for seed in range(100,112)]
        channels[ch]={
            'seeds':rs,
            'summary':{
                'mean_action_median_accuracy':statistics.fmean(r['action_median_accuracy'] for r in rs),
                'mean_ordered_threshold_coverage':statistics.fmean(r['ordered_threshold_coverage'] for r in rs),
                'mean_ordered_threshold_accuracy_all_rows':statistics.fmean(r['ordered_threshold_accuracy_all_rows'] for r in rs),
                'mean_ordered_threshold_accuracy_when_available':statistics.fmean(r['ordered_threshold_accuracy_when_available'] for r in rs),
                'mean_balanced_accuracy_when_available':statistics.fmean(r['ordered_threshold_balanced_accuracy_when_available'] for r in rs if r['ordered_threshold_balanced_accuracy_when_available'] is not None),
                'mean_lift_over_action_median_all_rows':statistics.fmean(r['lift_over_action_median_all_rows'] for r in rs),
                'positive_lift_seed_count':sum(r['lift_over_action_median_all_rows']>0 for r in rs),
                'mean_baseline_error_recovery_rate':statistics.fmean(r['baseline_error_recovery_rate'] for r in rs),
                'mean_baseline_correct_break_rate':statistics.fmean(r['baseline_correct_break_rate'] for r in rs),
            },
        }
    out={
        'schema':'microseed.ms1546.pass19.ordered-threshold-grammar.v1',
        'discriminator':'DOES_A_MINIMAL_ORDERED_COMPARISON_GRAMMAR_MATERIALLY_IMPROVE_SINGLE_LIFETIME_R2_REGULATORY_CONSEQUENCE_GENERALIZATION_OVER_ACTION_ONLY_RECURRENCE',
        'data_boundary':'ONE_R2_LIFETIME_PRE_DRIFT__OBSERVED_CURRENT_CHANNEL_SCALAR_PLUS_ACTION__ACTUAL_OBSERVED_REGULATORY_CONSEQUENCE_STANCE',
        'grammar':'ONE_PER_ACTION_SHALLOW_ORDERED_TREE__MAX_DEPTH_2__MIN_LEAF_3__NO_CROSS_CHANNEL_FEATURES',
        'interpretation_boundary':'TREE_IS_BORING_COMPARATOR_ONLY; MECHANISM_UNDER_TEST_IS_ORDERED_THRESHOLD_ATOM',
        'channels':channels,
        'nonclaims':['NO_MAINDEV_MUTATION','NO_NEW_PRIMITIVE_EARNED','NO_TREE_ARCHITECTURE_PROPOSAL','NO_DEPTH_SWEEP','NO_HYPERPARAMETER_TUNING','NO_WHOLE_ORGANISM_CREDIT'],
    }
    p=Path(__file__).with_name('MS1546_PASS19_ORDERED_THRESHOLD_GRAMMAR.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({c:channels[c]['summary'] for c in VALUES},indent=2,sort_keys=True))
if __name__=='__main__':main()
