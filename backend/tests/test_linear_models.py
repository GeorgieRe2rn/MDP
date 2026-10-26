from datetime import datetime, timedelta, timezone
import json
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.infrastructure.db.models import Base
from app.services.linear_models import fit_linear, train_linear
from app.services.market_pipeline import current_model, load_model, predict_model, specialist


def rows():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [{'id':i, 'at':start+timedelta(days=i), 'x':['PL',float(i%9),None], 'y':2+3*(i%9), 'baseline':2.} for i in range(240)]


def test_ols_recovers_linear_signal_and_roundtrips_without_fitting_test_data():
    model = fit_linear(rows()[:140])
    assert np.allclose(model.predict_counts([['PL',2,None],['unknown',3,None]]),[8,11])
    assert [r[0] for r in model.spec['numeric']]==[1]
    restored = load_model(json.dumps(model.spec),False)
    assert np.allclose(predict_model(restored,[['PL',2,None]],'goals'),[8])
    assert restored.predict_counts([['PL',-99,None]])==[.01]


def test_linear_is_adopted_only_after_temporal_comparison_and_serves_predictions():
    engine=create_engine('sqlite://')
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        report=train_linear(db,'goals','PRE',rows())
        assert report['status']=='adopted'
        assert report['candidate']['mae'] < report['baseline']['mae']
        champion=current_model(db,'goals','PRE')
        assert champion.schema_version=='linear-ols-v1'
        value,meta=specialist(db,'goals','PRE',['PL',2,None],2.)
        assert abs(value-8)<1e-7 and meta['family']=='Regresión lineal + Poisson'
        changed=rows();changed[0]['y']+=1
        assert train_linear(db,'goals','PRE',changed)['status']=='awaiting_fresh_test'
        assert current_model(db,'goals','PRE').id==champion.id


def test_insufficient_evidence_never_activates_a_model():
    engine=create_engine('sqlite://');Base.metadata.create_all(engine)
    with Session(engine) as db:
        assert train_linear(db,'corners','LIVE',rows()[:30])['status']=='awaiting_evidence'
        assert current_model(db,'corners','LIVE') is None
