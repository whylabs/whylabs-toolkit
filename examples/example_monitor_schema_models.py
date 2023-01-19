# type: ignore

"""Console script for monitor_schema."""
# flake8: noqa
import json
import uuid
from typing import Dict

from whylabs_toolkit.monitor_schema.models import (
    Analyzer,
    AnomalyFilter,
    BaselineType,
    Cadence,
    ColumnDataType,
    ColumnDiscreteness,
    ColumnMatrix,
    ColumnSchema,
    DatasetMatrix,
    DigestMode,
    Document,
    DriftConfig,
    EntitySchema,
    EveryAnomalyMode,
    FixedCadenceSchedule,
    GlobalAction,
    Granularity,
    Monitor,
    Segment,
    SendEmail,
    SlackWebhook,
    StddevConfig,
    TargetLevel,
    TrailingWindowBaseline,
)


def main() -> Dict:
    """Generates schema and example document JSON."""
    schema_str = Document.schema_json(indent=2)
    schema = json.loads(schema_str)
    schema['$id'] = "https://gitlab.com/whylabs/core/montor-schema/-/blob/main/schema/schema.json"
    schema['$version'] = "1.0"

    f1_score_analyzer = Analyzer(
        id='drift-analyzer',
        schedule=FixedCadenceSchedule(type='fixed', cadence=Cadence.daily),
        targetMatrix=DatasetMatrix(
            type=TargetLevel.dataset,
            segments=[Segment(tags=[])],
        ),
        dataReadinessDuration="PT19H",
        backfillGracePeriodDuration="P7D",
        config=StddevConfig(
            type="stddev",
            metric='classification.f1',
            factor=5,
            baseline=TrailingWindowBaseline(type=BaselineType.TrailingWindow, size=14),
        ),
    )

    hist_drift_analyzer = Analyzer(
        id='numerical_drift-analyzer',
        schedule=FixedCadenceSchedule(type='fixed', cadence=Cadence.daily),
        targetMatrix=ColumnMatrix(
            type=TargetLevel.column,
            include=['group:continuous'],
            segments=[Segment(tags=[])],
        ),
        config=DriftConfig(
            type='drift',
            metric='histogram',
            algorithm='hellinger',
            threshold=0.5,
            baseline=TrailingWindowBaseline(type=BaselineType.TrailingWindow, size=14),
        ),
    )
    freqitems_drift_analyzer = Analyzer(
        id='frequent_items_drift-analyzer',
        schedule=FixedCadenceSchedule(type='fixed', cadence=Cadence.daily),
        targetMatrix=ColumnMatrix(
            type=TargetLevel.column,
            include=['group:discrete'],
            segments=[Segment(tags=[])],
        ),
        config=DriftConfig(
            type='drift',
            metric='frequent_items',
            algorithm='hellinger',
            threshold=0.5,
            baseline=TrailingWindowBaseline(type=BaselineType.TrailingWindow, size=14),
        ),
    )
    document = Document(
        id=uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
        orgId='org-1',
        schemaVersion=1,
        datasetId='model-1',
        granularity=Granularity.daily,
        entitySchema=EntitySchema(
            columns={
                'annual_inc': ColumnSchema(
                    discreteness=ColumnDiscreteness.discrete, dataType=ColumnDataType.integral, classifier='input'
                ),
                'prediction': ColumnSchema(
                    discreteness=ColumnDiscreteness.discrete, dataType=ColumnDataType.integral, classifier='output'
                ),
            },
        ),
        analyzers=[hist_drift_analyzer, freqitems_drift_analyzer, f1_score_analyzer],
        monitors=[
            Monitor(
                id='drift-monitor-1',
                analyzerIds=[hist_drift_analyzer.id, freqitems_drift_analyzer.id],
                schedule=FixedCadenceSchedule(type='fixed', cadence='daily'),
                severity=4,
                mode=DigestMode(
                    type='DIGEST',
                    filter=AnomalyFilter(minAlertCount=20),
                ),
                actions=[
                    GlobalAction(type='global', target='action-xyz'),
                    SendEmail(type='email', target='demo@whylabs.ai'),
                    SlackWebhook(type='slack', target='https://demo.com'),
                ],
            ),
            Monitor(
                id='drift-monitor-important-features-2',
                analyzerIds=[hist_drift_analyzer.id, freqitems_drift_analyzer.id],
                schedule=FixedCadenceSchedule(type='fixed', cadence='daily'),
                severity=2,
                mode=EveryAnomalyMode(
                    type='EVERY_ANOMALY',
                    filter=AnomalyFilter(minWeight=0.5, minRankByWeight=10, excludeColumns=['very_noisy']),
                ),
                actions=[
                    GlobalAction(type='global', target='action-xyz'),
                    SendEmail(type='email', target='demo@whylabs.ai'),
                    SlackWebhook(type='slack', target='https://demo.com'),
                ],
            ),
            Monitor(
                id='f1-monitor-1',
                analyzerIds=[f1_score_analyzer.id],
                schedule=FixedCadenceSchedule(type='fixed', cadence='daily'),
                severity=2,
                mode=EveryAnomalyMode(type='EVERY_ANOMALY'),
                actions=[
                    GlobalAction(type='global', target='action-xyz'),
                    SendEmail(type='email', target='demo@whylabs.ai'),
                ],
            ),
        ],
    )
    doc_json = document.json(indent=2, exclude_none=True)
    return doc_json

if __name__ == "__main__":
    print(main())