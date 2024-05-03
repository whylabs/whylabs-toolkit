from __future__ import annotations
from typing import List, NamedTuple, Optional
import pandas as pd
from whylabs_client.api.monitor_api import MonitorApi
from whylabs_toolkit.helpers.utils import get_monitor_api
from whylabs_toolkit.monitor.models import Analyzer, Monitor

from whylabs_toolkit.monitor.diagnoser.recommendation.recommended_change import RecommendedChange
from whylabs_toolkit.monitor.diagnoser.recommendation.manual_change import ManualChange
from whylabs_toolkit.monitor.diagnoser.recommendation.remove_columns import RemoveColumns
from whylabs_toolkit.monitor.diagnoser.models.diagnosis_report import (
    MonitorDiagnosisReport,
    ConditionRecord,
)


class ChangeResults(NamedTuple):
    succeeded: List[RecommendedChange]
    failed: List[RecommendedChange]
    errors: List[str]
    manual: List[RecommendedChange]

    def describe(self) -> str:
        description = ""
        if len(self.succeeded):
            description += "Successfully made the following changes:\n"
            description += "\n\t".join(["\t* " + c.describe() for c in self.succeeded]) + "\n"
        if len(self.failed):
            description += "Failed to make the following changes:\n"
            description += "\n\t".join(["\t* " + c.describe() for c in self.failed])
            description += "\nErrors:\n"
            description += "\n\t".join(["\t* " + e for e in self.errors]) + "\n"
        if len(self.manual):
            description += "The following changes require manual intervention:\n"
            description += "\n\t".join(["\t* " + c.describe() for c in self.manual]) + "\n"
        return description


class ChangeRecommender:

    _condition_order = [
        # specific conditions unlikely to be rectified by other actions
        "changing_discrete",
        "changing_continuous",
        "few_unique",
        "many_unique",
        "very_few_unique",
        "late_upload_mismatch",
        "narrow_threshold_band",
        "small_nonnull_batches",
        # most general conditions
        "stale_analysis",
        "low_drift_threshold",
        "fixed_threshold_mismatch",
        "stddev_insufficient_baseline",
        "missing_baseline_batches",
        "fixed_baseline_mismatch",
    ]

    def __init__(self, report: MonitorDiagnosisReport):
        self._min_anomaly_count = 0
        self.report = report
        self.org_id = report.orgId
        self.dataset_id = report.datasetId
        self.analyzer = report.analyzer
        self.monitor = report.monitor
        self._monitor_api = None  # lazy

    @property
    def monitor_api(self) -> MonitorApi:
        if self._monitor_api is None:
            self._monitor_api = get_monitor_api()
        return self._monitor_api

    def _sort_conditions(self, conditions: List[ConditionRecord]) -> List[ConditionRecord]:
        return sorted(conditions, key=lambda c: self._condition_order.index(c.name))

    @staticmethod
    def _best_change_for_condition(condition: ConditionRecord) -> RecommendedChange:
        if condition.columns is None:
            raise ValueError("Condition must have columns to recommend a change")
        if condition.name in ["changing_discrete", "changing_continuous"]:
            return RemoveColumns(columns=condition.columns, info=condition.info)
        info = condition.info if condition.info else {}
        info["condition"] = condition.name
        info["summary"] = condition.summary
        return ManualChange(columns=condition.columns, info=info)

    @property
    def min_anomaly_count(self) -> int:
        return self._min_anomaly_count

    @min_anomaly_count.setter
    def min_anomaly_count(self, count: int) -> int:
        self._min_anomaly_count = count
        return self._min_anomaly_count

    def recommend(self) -> List[RecommendedChange]:
        by_col_count = (
            self.report.diagnosticData.analysisResults.anomalies.byColumnCount
            if (self.report.diagnosticData.analysisResults is not None)
            else []
        )
        count_tuples = [c.to_tuple() for c in by_col_count]
        cols, counts = zip(*count_tuples)
        anom_count = pd.Series(counts, index=cols)
        cols_to_address = anom_count[anom_count >= self.min_anomaly_count]
        changes = []
        # find the best actions for the cols that pass min anomaly criteria
        for c in self._sort_conditions(self.report.conditions):
            c.columns = list(cols_to_address.filter(items=c.columns if c.columns else []).index)
            if len(c.columns) > 0:
                changes.append(self._best_change_for_condition(c))
        return changes

    def _update_analyzer(self, updated: Analyzer) -> None:
        self.monitor_api.put_analyzer(
            org_id=self.org_id,
            dataset_id=self.dataset_id,
            analyzer_id=updated.id,
            body=updated.dict(exclude_none=True),
        )

    def _delete_monitor(self) -> None:
        if self.monitor is not None and self.analyzer is not None:
            analyzer: Analyzer = self.analyzer
            self.monitor_api.delete_monitor(org_id=self.org_id, dataset_id=self.dataset_id, monitor_id=self.monitor.id)
        self.monitor_api.delete_analyzer(org_id=self.org_id, dataset_id=self.dataset_id, analyzer_id=analyzer.id)

    def _add_new_monitor(self, new_analyzer: Analyzer) -> None:
        new_monitor = (
            Monitor(**self.monitor.dict(), id=new_analyzer.id) if self.monitor else Monitor(id=new_analyzer.id)
        )
        self.monitor_api.put_monitor(
            org_id=self.org_id,
            dataset_id=self.dataset_id,
            monitor_id=new_analyzer.id,  # use same id as the analyzer
            body=new_monitor.json(exclude_none=True),
        )
        self.monitor_api.put_analyzer(
            org_id=self.org_id,
            dataset_id=self.dataset_id,
            analyzer_id=new_analyzer.id,
            body=new_analyzer.json(exclude_none=True),
        )

    def make_changes(self, changes: Optional[List[RecommendedChange]] = None) -> ChangeResults:
        changes = self.recommend() if changes is None else changes
        succeeded: List[RecommendedChange] = []
        failed: List[RecommendedChange] = []
        errors: List[str] = []
        for c in changes:
            if c.can_automate() and self.analyzer:
                try:
                    changed_analyzers = c.generate_config(self.analyzer)
                    if next((a.id for a in changed_analyzers), None) is None:
                        # Delete existing analyzer/monitor as there's nothing useful left in it
                        self._delete_monitor()
                    # update existing or create new monitor(s)
                    for changed in changed_analyzers:
                        if changed.id == self.analyzer.id:
                            self._update_analyzer(changed)
                        else:
                            self._add_new_monitor(changed)
                    succeeded.append(c)
                except Exception as e:
                    failed.append(c)
                    errors.append(f"{c.name} failed with {e}")
        return ChangeResults(succeeded, failed, errors, [c for c in changes if not c.can_automate()])
