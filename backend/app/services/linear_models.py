"""OLS count specialists; training-only preprocessing and chronological evaluation."""
import json
import math
import numpy as np
from sklearn.linear_model import LinearRegression

SCHEMA = 'linear-ols-v1'


def matrix(xs, spec):
    result = []
    for x in xs:
        row = [float(str(x[0]) == league) for league in spec['leagues']]
        for i, median, scale in spec['numeric']:
            value = x[i]
            value = float(value) if isinstance(value, (int, float)) and math.isfinite(value) else median
            row.append((value - median) / scale)
        result.append(row)
    return np.asarray(result, dtype=float)


class LinearCountModel:
    def __init__(self, spec):
        self.spec = spec

    def predict_counts(self, xs):
        raw = matrix(xs, self.spec) @ np.asarray(self.spec['coefficients']) + self.spec['intercept']
        # OLS can produce negative counts. This bound is an explicit model rule.
        return np.maximum(.01, raw).tolist()


def fit_linear(rows):
    xs = [r['x'] for r in rows]
    spec = {'family': 'linear_ols', 'leagues': sorted({str(x[0]) for x in xs}), 'numeric': []}
    for i in range(1, len(xs[0])):
        observed = [float(x[i]) for x in xs if isinstance(x[i], (int, float)) and math.isfinite(x[i])]
        if not observed:
            continue  # Never invent a feature with no observed training values.
        spec['numeric'].append([i, float(np.median(observed)), max(float(np.std(observed)), 1.)])
    model = LinearRegression().fit(matrix(xs, spec), [r['y'] for r in rows])
    spec.update(coefficients=model.coef_.tolist(), intercept=float(model.intercept_))
    return LinearCountModel(spec)


def train_linear(db, market, phase, rows):
    from app.services.market_pipeline import temporal_split, fingerprint, blend, score, current_model, load_model, predict_model, MIN_SAMPLES
    from app.infrastructure.db.models import MarketLearner
    from app.etl.calendar import utcnow, kickoff_iso, parse_iso
    signature = fingerprint([(r['id'], r['y'], r['x'], r['baseline']) for r in rows])
    previous = db.query(MarketLearner).filter_by(schema_version=SCHEMA, market=market, phase=phase, dataset_digest=signature).first()
    if previous:
        return previous.report
    report = {'family': 'Regresión lineal OLS', 'schema': SCHEMA, 'samples': len(rows), 'minimum': MIN_SAMPLES, 'market': market, 'phase': phase, 'status': 'awaiting_evidence'}
    blob = None
    adopted = False
    split = temporal_split(rows)
    if split:
        train, validation, test = split
        model = fit_linear(train)
        vp = model.predict_counts([r['x'] for r in validation])
        weight = min([0, .25, .5, .75, 1], key=lambda w: score(validation, [blend(r['baseline'], p, w) for r, p in zip(validation, vp)], market)['log_loss'])
        tp = model.predict_counts([r['x'] for r in test])
        candidate = score(test, [blend(r['baseline'], p, weight) for r, p in zip(test, tp)], market)
        baseline = score(test, [r['baseline'] for r in test], market)
        champion = current_model(db, market, phase)
        champion_score = baseline
        if champion:
            cp = predict_model(load_model(champion.model_json, False), [r['x'] for r in test], market)
            champion_score = score(test, [blend(r['baseline'], p, champion.report['weight']) for r, p in zip(test, cp)], market)
        # Each family gets its own fixed chronological benchmark; later revisions need fresh tests.
        previous_tests = [r for r in db.query(MarketLearner).filter(MarketLearner.schema_version == SCHEMA, MarketLearner.market == market, MarketLearner.phase == phase).all() if r.report.get('status') in ('adopted', 'not_improved') and r.report.get('test_end')]
        fresh = not previous_tests or min(r['at'] for r in test) > max(parse_iso(r.report['test_end']) for r in previous_tests)
        if champion and champion.report.get("train_end") and parse_iso(champion.report["train_end"]) >= min(r["at"] for r in test):
            fresh = False
        adopted = fresh and weight > 0 and candidate['log_loss'] < min(baseline['log_loss'], champion_score['log_loss']) - .002
        report.update(status='adopted' if adopted else 'not_improved' if fresh else 'awaiting_fresh_test', weight=weight, candidate=candidate, baseline=baseline, champion=champion_score, train_matches=len(train), validation_matches=len(validation), test_matches=len(test), train_end=kickoff_iso(max(r['at'] for r in train)), validation_start=kickoff_iso(min(r['at'] for r in validation)), test_start=kickoff_iso(min(r['at'] for r in test)), test_end=kickoff_iso(max(r['at'] for r in test)), coefficients=model.spec, negative_policy='clip_to_0.01')
        blob = json.dumps(model.spec, allow_nan=False)
    db.add(MarketLearner(schema_version=SCHEMA, market=market, phase=phase, created_at=utcnow(), dataset_digest=signature, adopted=adopted, model_json=blob, report=report))
    db.commit()
    return report


def linear_status(db, market, phase):
    from app.infrastructure.db.models import MarketLearner
    row = db.query(MarketLearner).filter_by(schema_version=SCHEMA, market=market, phase=phase).order_by(MarketLearner.id.desc()).first()
    return row.report if row else {'status': 'pending', 'samples': 0}

