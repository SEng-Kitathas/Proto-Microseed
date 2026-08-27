from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

from sklearn.metrics import balanced_accuracy_score

ROOT = Path(__file__).parent
SOURCES = {
    'AFFINE': ROOT / 'MS1545_PASS18_ORDERED_AFFINE_BASELINES.json',
    'LOGISTIC': ROOT / 'MS1545_PASS18_DIRECT_REGULATORY_LINEAR_CLASSIFIER.json',
}


def summarize_source(path: Path) -> dict:
    src = json.loads(path.read_text())
    out = {}
    for channel, channel_data in src['channels'].items():
        model_names = None
        per_model = {}
        class_counts = Counter()
        for seed in channel_data['seeds']:
            details = seed['details']
            if not details:
                continue
            if model_names is None:
                if 'predictions' in details[0]:
                    # affine details: nested effect+stance; logistic: direct label
                    model_names = list(details[0]['predictions'])
                else:
                    raise RuntimeError('unknown detail schema')
            actuals = [str(d['actual']) for d in details]
            class_counts.update(actuals)
            baseline_preds = []
            for d in details:
                bp = d['predictions']['ACTION_MEDIAN']
                if isinstance(bp, dict): bp = bp['stance']
                baseline_preds.append(bp)
            for model in model_names:
                rec = per_model.setdefault(model, {
                    'balanced_accuracy': [],
                    'baseline_error_rows': 0,
                    'baseline_errors_recovered': 0,
                    'baseline_correct_rows': 0,
                    'baseline_correct_broken': 0,
                    'known_rows': 0,
                    'correct_rows': 0,
                })
                preds=[]; ys=[]
                for d, actual, baseline in zip(details, actuals, baseline_preds):
                    p = d['predictions'][model]
                    if isinstance(p, dict): p = p['stance']
                    if p is None:
                        continue
                    preds.append(str(p)); ys.append(actual)
                    rec['known_rows'] += 1
                    rec['correct_rows'] += int(str(p)==actual)
                    if baseline != actual:
                        rec['baseline_error_rows'] += 1
                        rec['baseline_errors_recovered'] += int(str(p)==actual)
                    else:
                        rec['baseline_correct_rows'] += 1
                        rec['baseline_correct_broken'] += int(str(p)!=actual)
                if ys:
                    rec['balanced_accuracy'].append(float(balanced_accuracy_score(ys,preds)))
        channel_out={'class_counts':dict(class_counts),'models':{}}
        for model, rec in per_model.items():
            channel_out['models'][model]={
                'mean_balanced_accuracy': statistics.fmean(rec['balanced_accuracy']) if rec['balanced_accuracy'] else None,
                'baseline_error_recovery_rate': rec['baseline_errors_recovered']/max(rec['baseline_error_rows'],1),
                'baseline_correct_break_rate': rec['baseline_correct_broken']/max(rec['baseline_correct_rows'],1),
                'overall_accuracy': rec['correct_rows']/max(rec['known_rows'],1),
                'known_rows': rec['known_rows'],
                'baseline_error_rows': rec['baseline_error_rows'],
            }
        out[channel]=channel_out
    return out


def main():
    result={name:summarize_source(path) for name,path in SOURCES.items()}
    out={
        'schema':'microseed.ms1545.pass18.antiflattery-metrics.v1',
        'purpose':'attack raw-accuracy denominator; measure class balance and whether richer models repair action-median errors without destroying correct cases',
        'sources':result,
        'nonclaims':['NO_THRESHOLD_AUTHORITY','NO_MAINDEV_MUTATION','NO_MODEL_PROMOTION'],
    }
    path=ROOT/'MS1545_PASS18_ANTIFLATTERY_METRICS.json'
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
