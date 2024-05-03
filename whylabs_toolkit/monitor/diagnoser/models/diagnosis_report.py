import pandas as pd
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from whylabs_toolkit.monitor.models import (
    Analyzer,
    Monitor,
    Segment,
    TargetLevel,
    FixedThresholdsConfig,
    ConjunctionConfig,
    DisjunctionConfig,
    GlobalAction,
)

from whylabs_toolkit.monitor.diagnoser.helpers.describe import (
    describe_truncated_table,
    filter_by_index,
    describe_truncated_list,
)
from whylabs_toolkit.monitor.diagnoser.helpers.utils import segment_as_readable_text


class SegmentReport(BaseModel):
    batchCount: int
    segment: Segment
    totalAnomalies: int
    totalFailures: int
    totalColumns: int


class NamedCount(BaseModel):
    name: str
    count: int

    def to_tuple(self) -> Tuple[str, int]:
        return self.name, self.count


class ConditionRecord(BaseModel):
    columns: Optional[List[str]]  # not present for some conditions like stale analysis
    info: Optional[Dict]
    summary: str
    name: str


class QualityIssueRecord(BaseModel):
    name: str
    description: str
    detectors: List[str]


class ProfileSummary(BaseModel):
    minRowName: str
    minRowCount: int
    maxRowName: str
    maxRowCount: int

    def describe(self) -> str:
        count_desc = (
            str(self.minRowCount)
            if self.minRowCount == self.maxRowCount
            else f"{self.minRowCount} - {self.maxRowCount}"
        )
        return f"Diagnostic interval rollup contains {count_desc} rows for the diagnosed columns.\n"


class BatchesSummary(BaseModel):
    minBatchName: str
    minBatchCount: int
    maxBatchName: str
    maxBatchCount: int

    def describe(self) -> str:
        count_desc = (
            str(self.minBatchCount)
            if self.minBatchCount == self.maxBatchCount
            else f"{self.minBatchCount} - {self.maxBatchCount}"
        )
        return f"Diagnostic interval contains {count_desc} batches.\n"


class ResultRecord(BaseModel):
    diagnosedColumnCount: int
    batchCount: int

    def describe(self) -> str:
        return f"Found non-failed results for {self.diagnosedColumnCount} columns and {self.batchCount} batches."


class FailureRecord(BaseModel):
    totalFailuresCount: int
    maxFailuresCount: int
    meanFailuresCount: int
    byColumnCount: List[NamedCount]
    byTypeCount: List[NamedCount]

    def describe(self) -> str:
        failures = pd.DataFrame([c.to_tuple() for c in self.byColumnCount])
        failure_types = [t.name for t in self.byTypeCount]
        if len(failures) == 0:
            return "No failures were detected."
        return (
            f"Found {self.totalFailuresCount} failed results, with up to {self.maxFailuresCount} "
            f"failures per column and {self.meanFailuresCount} failures on average.\n"
            f"Failure types are {describe_truncated_list(failure_types)}\n"
            f"Columns with failures are: \n{describe_truncated_table(failures)}\n"
        )


class AnomalyRecord(BaseModel):
    totalAnomalyCount: int
    maxAnomalyCount: int
    meanAnomalyCount: int
    batchCount: int
    byColumnCount: List[NamedCount]
    byColumnBatchCount: List[NamedCount]

    def describe(self) -> str:
        counts = pd.Series([c.to_tuple() for c in self.byColumnCount])
        max_count = int(self.maxAnomalyCount)
        max_pct = max_count * 100 / self.batchCount
        mean_count = float(self.meanAnomalyCount)
        mean_pct = mean_count * 100 / self.batchCount
        return (
            f"Found {self.totalAnomalyCount} anomalies in {len(self.byColumnCount)} columns, with up to "
            f"{max_pct:.1f}% ({max_count}) batches having anomalies per column and "
            f"{mean_pct:.1f}% ({mean_count:.1f}) on average.\n"
            f"Columns with anomalies are:\n{describe_truncated_table(counts)}\n"
        )


class AnalysisResultsSummary(BaseModel):
    results: ResultRecord
    failures: FailureRecord
    anomalies: AnomalyRecord

    def describe(self) -> str:
        return (
            f"Analysis results summary:\n"
            f"{self.results.describe()}\n"
            f"{self.anomalies.describe()}\n"
            f"{self.failures.describe()}\n"
        )


class DiagnosticDataSummary(BaseModel):
    diagnosticSegment: Segment
    diagnosticProfile: Optional[ProfileSummary]
    diagnosticBatches: Optional[BatchesSummary]
    analysisResults: Optional[AnalysisResultsSummary]
    targetedColumnCount: int

    def describe(self) -> str:
        return "\n".join(
            [
                f'Diagnostic segment is "{segment_as_readable_text(self.diagnosticSegment.tags)}".',
                self.diagnosticBatches.describe() if self.diagnosticBatches is not None else "",
                self.diagnosticProfile.describe() if self.diagnosticProfile is not None else "",
                self.analysisResults.describe() if self.analysisResults is not None else "",
            ]
        )


class AnalyzerDiagnosisReport(BaseModel):
    orgId: str
    datasetId: str
    analyzerId: str
    interval: str
    expectedBatchCount: int
    diagnosticData: DiagnosticDataSummary
    qualityIssues: List[QualityIssueRecord]
    conditions: List[ConditionRecord]

    def describe(self) -> str:
        text = "\n".join([self.diagnosticData.describe(), self.describe_quality_issues(), self.describe_conditions()])
        return text

    def describe_quality_issues(self) -> str:
        if len(self.qualityIssues) == 0:
            return "No issues impacting diagnosis quality were detected"
        text = "Conditions that may impact diagnosis quality include:\n"
        for issue in self.qualityIssues:
            text += f"\t* {issue.name}: {issue.description} - detectors {issue.detectors}\n"
        return text

    def describe_conditions(self) -> str:
        if len(self.conditions) == 0:
            return "No conditions related to noise were detected."
        condition_cols: List[str] = []
        text = "Conditions that may contribute to noise include:\n"
        for condition in self.conditions:
            text += f"\t* Condition {condition.name} ({condition.summary})"
            if condition.columns is not None:
                condition_cols += condition.columns
                col_text = describe_truncated_list(condition.columns, 10)
                text += f" for {len(condition.columns)} columns: {col_text}"
            text += "\n"

        cols = pd.Series(condition_cols).unique()
        if len(cols) > 0:
            text += f"\nAnomalies for columns with these conditions:\n"
            by_col_count = (
                self.diagnosticData.analysisResults.anomalies.byColumnCount
                if (self.diagnosticData.analysisResults is not None)
                else []
            )
            count_tuples = [c.to_tuple() for c in by_col_count]
            idx, values = zip(*count_tuples)
            count_by_col = pd.Series(values, idx)
            cols_with_count = filter_by_index(cols.tolist(), count_by_col).sort_values(ascending=False)
            cols_with_count.rename("anomalies")
            text += describe_truncated_table(cols_with_count)
            text += f"\nAccounting for {cols_with_count.sum()} anomalies out of " f"{count_by_col.sum()}\n"

        return text


class MonitorDiagnosisReport(AnalyzerDiagnosisReport):
    monitor: Optional[Monitor]  # sometimes there isn't one, e.g. it's been deleted
    analyzer: Optional[Analyzer]
    analyzedColumnCount: int

    def describe(self) -> str:
        text = "\n".join([self.describe_monitor(), self.describe_analyzer(), super().describe()])
        return text

    def describe_monitor(self) -> str:
        if self.monitor is None:
            return "Monitor has been deleted.\n"
        text = (
            f'Diagnosis is for monitor "{self.monitor.displayName if self.monitor.displayName else self.monitor.id}" '
            f"[{self.monitor.id}] in {self.datasetId} {self.orgId}, over interval {self.interval}.\n"
        )
        if len(self.monitor.actions) > 0:
            text += f"Monitor has {len(self.monitor.actions)} notification actions "
            text += f"{[a.target for a in self.monitor.actions if isinstance(a, GlobalAction)]}.\n"
        return text

    def describe_analyzer(self) -> str:
        if self.analyzer is None:
            return "No analyzer found.\n"
        if isinstance(self.analyzer.config, ConjunctionConfig) or isinstance(self.analyzer.config, DisjunctionConfig):
            return f"\nAnalyzer is a composite {self.analyzer.config.type}."
        baseline = (
            "no baseline"
            if (isinstance(self.analyzer.config, FixedThresholdsConfig) or self.analyzer.config.baseline is None)
            else f"{self.analyzer.config.baseline.type} baseline"
        )
        targeting_desc = ""
        if self.analyzer is None:
            return ""
        metric = self.analyzer.config.metric
        if self.analyzer.targetMatrix is not None and self.analyzer.targetMatrix.type == TargetLevel.column:
            targeting_desc = (
                f'\nAnalyzer "{self.analyzer.id}" targets {self.diagnosticData.targetedColumnCount} '
                f"columns and ran on {self.analyzedColumnCount} columns in the diagnosed segment.\n"
            )
        text = f"Analyzer is {self.analyzer.config.type} configuration for {metric} metric with {baseline}."
        text += targeting_desc
        text += "\n"
        return text


class MonitorDiagnosisReportList(BaseModel):
    __root__: List[MonitorDiagnosisReport]
