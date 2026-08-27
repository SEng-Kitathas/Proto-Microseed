from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

from sklearn.linear_model import LogisticRegression

from research.habitat_r2_exact import ACTIONS
from research.run_ms1537_pass10_r2_projection_quarry import VALUES
from research.run_ms1545_pass18_ordered_affine_baselines import rows, median_by_action, stance_from_effect

ACTION_INDEX = {action: idx for idx, action in enumerate(ACTIONS)}


def encode(row: dict, mode: str, mean_x: float, scale_x: float) -> list[float]:
    x = (float(row['pre_value']) - mean_x) / scale_x
    action = str(row['action'])
    onehot = [1.0 if action == a else 0.0 for a in ACTIONS]
    if mode == 'STATE_ONLY':
        return [x]
    if mode == 'ACTION_PLUS_STATE_SHARED':
        return [x, *onehot]
    if mode == 'ACTION_PLUS_STATE_INTERACTION':
        return [*onehot, *(x * bit for bit in onehot)]
    raise ValueError(mode)


class FixedClassifier:
    def __init__(self, label: str): self.label = label
    def predict(self, rows): return [self.label for _ in rows]


def fit_classifier(train: list[dict], mode: str):
    labels = [str(r['actual_stance']) for r in train]
    uniq = sorted(set(labels))
    mean_x = statistics.fmean(float(r['pre_value']) for r in train)
    var = statistics.fmean((float(r['pre_value']) - mean_x) ** 2 for r in train)
    scale_x = math.sqrt(var) if var > 1e-12 else 1.0
    if len(uniq) == 1:
        return FixedClassifier(uniq[0]), mean_x, scale_x
    X = [encode(r, mode, mean_x, scale_x) for r in train]
    clf = LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs')
    clf.fit(X, labels)
    return clf, mean_x, scale_x


def eval_seed(seed: int, channel: str) -> dict:
    samples = rows(seed, channel)
    cut = max(1, int(len(samples) * 0.70))
    train = samples[:cut]
    validation = samples[cut:]

    action_medians = median_by_action(train)
    modes = ('STATE_ONLY', 'ACTION_PLUS_STATE_SHARED', 'ACTION_PLUS_STATE_INTERACTION')
    fitted = {mode: fit_classifier(train, mode) for mode in modes}

    stats = {'ACTION_MEDIAN': 0, **{m: 0 for m in modes}}
    details = []
    for row in validation:
        actual = str(row['actual_stance'])
        action = str(row['action'])
        med = action_medians.get(action)
        action_pred = None if med is None else stance_from_effect(channel, float(row['pre_value']), med)
        stats['ACTION_MEDIAN'] += int(action_pred == actual)
        preds = {'ACTION_MEDIAN': action_pred}
        for mode in modes:
            clf, mean_x, scale_x = fitted[mode]
            X = [encode(row, mode, mean_x, scale_x)]
            pred = str(clf.predict(X)[0])
            stats[mode] += int(pred == actual)
            preds[mode] = pred
        details.append({'tick': int(row['tick']), 'action': action, 'pre_value': float(row['pre_value']), 'actual': actual, 'predictions': preds})

    n = max(len(validation), 1)
    acc = {name: stats[name] / n for name in stats}
    return {
        'seed': seed,
        'train_rows': len(train),
        'validation_rows': len(validation),
        'accuracy': acc,
        'lift_over_action_median': {name: acc[name] - acc['ACTION_MEDIAN'] for name in acc},
        'lift_over_state_only': {name: acc[name] - acc['STATE_ONLY'] for name in acc},
        'details': details,
    }


def summarize(seed_rows: list[dict]) -> dict:
    names = tuple(seed_rows[0]['accuracy'])
    return {
        name: {
            'mean_accuracy': statistics.fmean(r['accuracy'][name] for r in seed_rows),
            'mean_lift_over_action_median': statistics.fmean(r['lift_over_action_median'][name] for r in seed_rows),
            'mean_lift_over_state_only': statistics.fmean(r['lift_over_state_only'][name] for r in seed_rows),
            'positive_lift_over_action_median_seeds': sum(r['lift_over_action_median'][name] > 0 for r in seed_rows),
            'positive_lift_over_state_only_seeds': sum(r['lift_over_state_only'][name] > 0 for r in seed_rows),
        }
        for name in names
    }


def main() -> None:
    channels = {}
    for channel in VALUES:
        seed_rows = [eval_seed(seed, channel) for seed in range(100, 112)]
        channels[channel] = {'seeds': seed_rows, 'summary': summarize(seed_rows)}

    candidate = 'ACTION_PLUS_STATE_INTERACTION'
    out = {
        'schema': 'microseed.ms1545.pass18.direct-regulatory-linear-classifier.v1',
        'discriminator': 'CAN_STANDARD_REGULARIZED_LINEAR_CLASSIFICATION_USE_ORDERED_CURRENT_VALUE_PLUS_ACTION_TO_CLOSE_SINGLE_LIFETIME_DECISION_RELEVANT_SAMPLE_EFFICIENCY',
        'data_boundary': 'ONE_R2_LIFETIME_PRE_DRIFT__NOISY_OBSERVED_CURRENT_CHANNEL_VALUE_PLUS_ACTION__TARGET_IS_EXISTING_REGULATORY_CONSEQUENCE_STANCE_FROM_ACTUAL_OBSERVED_OUTCOME',
        'split': 'FIRST_70_PERCENT_TRAIN__LAST_30_PERCENT_VALIDATION',
        'model': 'sklearn LogisticRegression(C=1.0, solver=lbfgs, max_iter=1000); fixed, no hyperparameter sweep',
        'feature_sets': {
            'STATE_ONLY': 'standardized current scalar only',
            'ACTION_PLUS_STATE_SHARED': 'standardized current scalar + action one-hot; shared scalar coefficient',
            'ACTION_PLUS_STATE_INTERACTION': 'action one-hot + action-specific scalar interactions; linear decision surfaces',
        },
        'channels': channels,
        'candidate_for_discriminator': candidate,
        'nonclaims': [
            'NO_MAINDEV_MUTATION', 'NO_NEW_PRIMITIVE', 'NO_WHOLE_ORGANISM_CREDIT',
            'NO_LOGISTIC_REGRESSION_ARCHITECTURE_PROPOSAL', 'NO_HYPERPARAMETER_TUNING',
            'NO_LINEAR_SEPARABILITY_LAW', 'NO_HIDDEN_STATE',
        ],
    }
    path = Path(__file__).with_name('MS1545_PASS18_DIRECT_REGULATORY_LINEAR_CLASSIFIER.json')
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'channels': {c: channels[c]['summary'] for c in VALUES}}, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
