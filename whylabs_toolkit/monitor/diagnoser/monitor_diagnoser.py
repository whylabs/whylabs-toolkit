import os

import pandas as pd
from typing import Tuple, List, Optional, Dict

from pydantic import ValidationError
from whylabs_client.model.analyzer_segment_columns_diagnostic_request import AnalyzerSegmentColumnsDiagnosticRequest
from whylabs_client.model.analyzer_segment_columns_diagnostic_response import AnalyzerSegmentColumnsDiagnosticResponse
from whylabs_client.model.analyzer_segments_diagnostic_request import AnalyzerSegmentsDiagnosticRequest
from whylabs_client.model.analyzer_segments_diagnostic_response import AnalyzerSegmentsDiagnosticResponse
from whylabs_client.model.analyzers_diagnostic_response import AnalyzersDiagnosticResponse
from whylabs_client.model.diagnosis_request import DiagnosisRequest
from whylabs_client.model.diagnostic_interval_request import DiagnosticIntervalRequest
from whylabs_client.model.diagnostic_interval_response import DiagnosticIntervalResponse
from whylabs_client.model.analyzers_diagnostic_request import AnalyzersDiagnosticRequest
from whylabs_client.model.segment import Segment as WhyLabsSegment
from whylabs_client.model.segment_tag import SegmentTag as WhyLabsSegmentTag
from whylabs_toolkit.helpers.utils import get_monitor_api, get_models_api, get_monitor_diagnostics_api
from whylabs_toolkit.monitor.models import TimeRange, Monitor, Segment, Analyzer, EntitySchema
from whylabs_toolkit.utils.granularity import Granularity

from whylabs_toolkit.monitor.diagnoser.helpers.utils import get_monitor_diagnostics_api, segment_as_readable_text
from whylabs_toolkit.helpers.monitor_helpers import time_period_to_granularity
from whylabs_toolkit.monitor.diagnoser.constants import DEFAULT_BATCHES
from whylabs_toolkit.monitor.diagnoser.models import (
    NoisyMonitorStats,
    FailedMonitorStats,
    FailedSegmentStats,
    NoisySegmentStats,
    NoisyColumnStats,
    MonitorDiagnosisReport,
)
from whylabs_toolkit.monitor.diagnoser.targeting import targeted_columns


def to_mapped_dict(obj: object) -> object:
    """
    Convert a WhyLabs Client class instance into a JSON dictionary with keys mapped to the API schema. For example,
    the pythonized 'org_id' attribute becomes 'orgId'.
    :param obj:
    :return: dict
    """
    if hasattr(obj, "to_dict") and hasattr(obj, "attribute_map"):
        return {obj.attribute_map[k]: to_mapped_dict(getattr(obj, k)) for k, _ in obj.to_dict().items()}
    if isinstance(obj, list):
        return [to_mapped_dict(i) for i in obj]
    return obj


class MonitorDiagnoser:
    def __init__(self, org_id: str, dataset_id: str):
        self.org_id: str = org_id
        self.dataset_id: str = dataset_id
        self.desired_batches: int = DEFAULT_BATCHES
        self.granularity: Optional[Granularity] = None
        self._diagnostics_api = get_monitor_diagnostics_api()
        self._monitor_api = get_monitor_api()
        self._models_api = get_models_api()
        self._diagnostics_api = get_monitor_diagnostics_api()
        self._monitor_configs: Optional[List[Monitor]] = None
        self._noisy_monitors: Optional[List[NoisyMonitorStats]] = None
        self._failed_monitors: Optional[List[FailedMonitorStats]] = None
        self._noisy_segments: Optional[List[NoisySegmentStats]] = None
        self._failed_segments: Optional[List[FailedSegmentStats]] = None
        self._noisy_columns: Optional[List[NoisyColumnStats]] = None
        self._diagnostic_interval: Optional[str] = None
        self._monitor_id: Optional[str] = None
        self._diagnostic_segment: Optional[Segment] = None
        self._analyzer: Optional[Analyzer] = None
        self._diagnosed_columns: Optional[List[str]] = None
        self._diagnosis: Optional[MonitorDiagnosisReport] = None
        self.schema: Optional[EntitySchema] = None

    @property
    def noisy_monitors(self) -> List[NoisyMonitorStats]:
        if self._noisy_monitors is None:
            raise Exception('Run "detect_noisy_monitors" first to get the noisy monitors.')
        return self._noisy_monitors

    @property
    def noisy_monitors_with_actions(self) -> List[NoisyMonitorStats]:
        return [m for m in self.noisy_monitors if m.action_count > 0]

    @property
    def noisy_monitors_without_actions(self) -> List[NoisyMonitorStats]:
        return [m for m in self.noisy_monitors if m.action_count == 0]

    @property
    def failed_monitors(self) -> List[FailedMonitorStats]:
        if self._failed_monitors is None:
            raise Exception('Run "detect_noisy_monitors" first to get the failed monitors.')
        return self._failed_monitors

    @property
    def noisy_segments(self) -> List[NoisySegmentStats]:
        if self._noisy_segments is None:
            raise Exception('Run "detect_noisy_segments" first to get the noisy monitors.')
        return self._noisy_segments

    @property
    def failed_segments(self) -> List[FailedSegmentStats]:
        if self._failed_segments is None:
            raise Exception('Run "detect_noisy_segments" first to get the failed monitors.')
        return self._failed_segments

    @property
    def noisy_columns(self) -> List[NoisyColumnStats]:
        if self._noisy_columns is None:
            raise Exception('Run "detect_noisy_columns" first to get the noisy columns.')
        return self._noisy_columns

    @property
    def monitor_configs(self) -> List[Monitor]:
        if self._monitor_configs is None:
            config = self._monitor_api.get_monitor_config_v3(self.org_id, self.dataset_id)
            self._monitor_configs = []
            for m in config.get("monitors", []):
                try:
                    self._monitor_configs.append(Monitor.parse_obj(m))
                except ValidationError:
                    pass  # skipping monitors with validation problems
        return self._monitor_configs

    @property
    def diagnostic_interval(self) -> str:
        if self._diagnostic_interval is None:
            raise Exception('Set a diagnostic interval first, e.g. by running "choose_dataset_batches"')
        return self._diagnostic_interval

    @diagnostic_interval.setter
    def diagnostic_interval(self, interval: str) -> None:
        self._diagnostic_interval = interval

    @property
    def diagnostic_segment(self) -> Segment:
        if self._diagnostic_segment is None:
            raise Exception('Set the "diagnostic_segment" property first, e.g. by running "detect_noisy_segments"')
        return self._diagnostic_segment

    @diagnostic_segment.setter
    def diagnostic_segment(self, segment: Segment) -> None:
        if self._diagnostic_segment != segment:
            self._diagnostic_segment = segment
            self._noisy_columns = None
            self._diagnosis = None

    @property
    def monitor_id_to_diagnose(self) -> str:
        if self._monitor_id is None:
            raise Exception('Set the "monitor_id" property first, e.g. by running "detect_noisy_monitors"')
        return self._monitor_id

    @monitor_id_to_diagnose.setter
    def monitor_id_to_diagnose(self, monitor_id: str) -> None:
        if self._monitor_id != monitor_id:
            self._monitor_id = monitor_id
            # Reset anything specific to the monitor
            self._analyzer = None
            self._noisy_segments = None
            self._failed_segments = None
            self._noisy_columns = None
            self._diagnosis = None
            self._diagnostic_segment = None

    @property
    def monitor_to_diagnose(self) -> Optional[Monitor]:
        return next((m for m in self.monitor_configs if m.id == self._monitor_id), None)

    def targeted_columns(self) -> List[str]:
        if self.schema is None:
            self.schema = self._models_api.get_entity_schema(self.org_id, self.dataset_id)
        return targeted_columns(self.analyzer_to_diagnose.targetMatrix, self.schema)

    @property
    def analyzer_to_diagnose(self) -> Analyzer:
        if self._analyzer is None:
            analyzer_id = self.get_analyzer_id_for_monitor()
            resp = self._monitor_api.get_analyzer(self.org_id, self.dataset_id, analyzer_id)
            self._analyzer = Analyzer.parse_obj(resp)
        return self._analyzer

    def choose_dataset_batches(self) -> Tuple[TimeRange, Granularity, str]:
        """
        Based on the dataset's batch frequency, lineage (start/end) and the desired number of batches,
        recommends a diagnostic interval for the dataset.
        :return: tuple of lineage, granularity, interval
        """
        # get recommended diagnostic interval and the dataset's batch frequency
        resp: DiagnosticIntervalResponse = self._diagnostics_api.recommend_diagnostic_interval(
            self.org_id, DiagnosticIntervalRequest(dataset_id=self.dataset_id, batches=self.desired_batches)
        )
        time_period = resp.time_period
        self._diagnostic_interval = resp.interval
        if resp.start_timestamp is None or resp.end_timestamp is None:
            raise Exception("No existing batch data")

        lineage = TimeRange(start=resp.start_timestamp, end=resp.end_timestamp)
        self.granularity = time_period_to_granularity(time_period)

        return lineage, self.granularity, resp.interval

    def detect_noisy_monitors(self) -> List[NoisyMonitorStats]:
        """
        Detects noisy monitors for the dataset. The summary statistics are returned and made available in the
        noisy_monitors property.
        :return: List of noisy monitor statistics, ordered with the noisiest first
        """

        def merge_monitor_actions(item: Dict, mon_acts: List[Dict]) -> Dict:
            monitor_action = next((m for m in mon_acts if m["analyzer_id"] == item["analyzer_id"]), None)
            if monitor_action:
                item.update(monitor_action)
            else:
                item["action_count"] = 0
                item["action_targets"] = []
            return item

        if self._diagnostic_interval is None:
            self.choose_dataset_batches()
        resp: AnalyzersDiagnosticResponse = self._diagnostics_api.detect_noisy_analyzers(
            self.org_id, AnalyzersDiagnosticRequest(dataset_id=self.dataset_id, interval=self._diagnostic_interval)
        )
        monitor_actions = [
            {
                "monitor_id": m.id,
                "analyzer_id": m.analyzerIds[0] if len(m.analyzerIds) > 0 else None,
                "action_count": len(m.actions),
                "action_targets": [a.target for a in m.actions if a.type == "global"],
            }
            for m in self.monitor_configs
        ]
        self._noisy_monitors = [
            NoisyMonitorStats.parse_obj(merge_monitor_actions(item.to_dict(), monitor_actions))
            for item in resp.noisy_analyzers
        ]
        self._failed_monitors = [
            FailedMonitorStats.parse_obj(merge_monitor_actions(item.to_dict(), monitor_actions))
            for item in resp.failed_analyzers
        ]
        if len(self._noisy_monitors) == 0:
            raise Exception("No noisy monitors found")
        if self._monitor_id is None:
            self._monitor_id = self._noisy_monitors[0].monitor_id
        return self._noisy_monitors

    def get_analyzer_id_for_monitor(self) -> str:
        analyzer_id: Optional[str] = next(
            (m.analyzerIds[0] for m in self.monitor_configs if m.id == self.monitor_id_to_diagnose), None
        )
        if analyzer_id is None:
            raise Exception(f"No analyzer found for monitor {self.monitor_id_to_diagnose}")
        return analyzer_id

    def detect_noisy_segments(self) -> List[NoisySegmentStats]:
        analyzer_id = self.get_analyzer_id_for_monitor()
        resp: AnalyzerSegmentsDiagnosticResponse = self._diagnostics_api.detect_noisy_segments(
            self.org_id,
            AnalyzerSegmentsDiagnosticRequest(
                dataset_id=self.dataset_id, analyzer_id=analyzer_id, interval=self._diagnostic_interval
            ),
        )
        self._noisy_segments = [NoisySegmentStats.parse_obj(n.to_dict()) for n in resp.noisy_segments]
        self._failed_segments = [FailedSegmentStats.parse_obj(n.to_dict()) for n in resp.failed_segments]
        self.diagnostic_segment = self._noisy_segments[0].segment
        return self._noisy_segments

    def detect_noisy_columns(self) -> List[NoisyColumnStats]:
        analyzer_id = self.get_analyzer_id_for_monitor()
        resp: AnalyzerSegmentColumnsDiagnosticResponse = self._diagnostics_api.detect_noisy_columns(
            self.org_id,
            AnalyzerSegmentColumnsDiagnosticRequest(
                dataset_id=self.dataset_id,
                analyzer_id=analyzer_id,
                interval=self._diagnostic_interval,
                segment=WhyLabsSegment(tags=[WhyLabsSegmentTag(t.key, t.value) for t in self.diagnostic_segment.tags]),
            ),
        )
        self._noisy_columns = [NoisyColumnStats.parse_obj(n.to_dict()) for n in resp.noisy_columns]
        return self._noisy_columns

    def describe_segments(self) -> str:
        with_anomalies = [s for s in self.noisy_segments if s.total_anomalies > 0]
        with_failures = [s for s in self.failed_segments if s.total_failed > 0]
        text = (
            f"{len(with_anomalies)} of {len(self.noisy_segments)} analyzed segments have anomalies "
            f"and {len(with_failures)} have failures\n\n"
        )
        if len(with_anomalies):
            text += "Segments with anomalies:\n"
            text += pd.DataFrame.from_records(with_anomalies).to_markdown()
            text += "\n"
        if len(with_failures):
            text += "Segments with failures:\n"
            text += pd.DataFrame.from_records(with_failures).to_markdown()
            text += "\n"
        noisiest = segment_as_readable_text(self.noisy_segments[0].segment.tags)
        text += f"Noisiest segment selected for diagnosis: {noisiest}\n"
        return text

    def describe_columns(self) -> str:
        cols = self.noisy_columns
        text = f"Analysis ran on {len(cols)} columns in the diagnosed segment.\n"
        text += pd.DataFrame.from_records(cols).to_markdown()
        return text

    def diagnose(self, columns: Optional[List[str]] = None) -> MonitorDiagnosisReport:
        if self._diagnostic_interval is None:
            self.choose_dataset_batches()
        if self._monitor_id is None:
            self.detect_noisy_monitors()
        if self._diagnostic_segment is None:
            self.detect_noisy_segments()
        if columns is None:
            if self._noisy_columns is None:
                self.detect_noisy_columns()
            self._diagnosed_columns = [c.column for c in self.noisy_columns[:100]]
        else:
            self._diagnosed_columns = columns[:100]
        use_local_server = os.environ.get("USE_LOCAL_SERVER", False)
        if use_local_server:
            # Call the server function directly if configured to do so (for testing)
            try:
                from smart_config.server.server import DiagnosisRequest as DiagnoserDiagnosisRequest
                from smart_config.server.diagnosis.analyzer_diagnoser import AnalyzerDiagnoser

                if use_local_server == "library":
                    # Call server code directly
                    analyzer_diagnoser = AnalyzerDiagnoser(
                        self.org_id,
                        self.dataset_id,
                        self.get_analyzer_id_for_monitor(),
                        self.diagnostic_interval,
                        os.environ["WHYLABS_API_KEY"],
                    )
                    analyzer_diagnoser.assemble_data([t for t in self.diagnostic_segment.tags], self._diagnosed_columns)
                    analyzer_diagnoser.run_detectors()
                    report = analyzer_diagnoser.summarize_diagnosis()
                    report_dict = report.dict()
                else:
                    # Call local instance of server
                    from smart_config.server.service.diagnosis_service import DiagnosisService

                    diagnosis_service = DiagnosisService(
                        options={
                            "headers": {
                                "Accept": "application/json",
                                "Content-Type": "application/json",
                                "X-API-KEY": os.environ["WHYLABS_API_KEY"],
                            }
                        }
                    )
                    report_dict = diagnosis_service.diagnose_sync(
                        DiagnoserDiagnosisRequest(
                            orgId=self.org_id,
                            datasetId=self.dataset_id,
                            analyzerId=self.get_analyzer_id_for_monitor(),
                            interval=self.diagnostic_interval,
                            columns=self._diagnosed_columns,
                            segment=self.diagnostic_segment,
                        )
                    )
            except ImportError:
                raise Exception("USE_LOCAL_SERVER is set but server library is not available.")
        else:
            # Call the diagnosis API via whyLabs client
            response = self._diagnostics_api.diagnose_analyzer_sync(
                self.org_id,
                DiagnosisRequest(
                    dataset_id=self.dataset_id,
                    analyzer_id=self.get_analyzer_id_for_monitor(),
                    interval=self.diagnostic_interval,
                    columns=self._diagnosed_columns,
                    segment=WhyLabsSegment(
                        tags=[WhyLabsSegmentTag(t.key, t.value) for t in self.diagnostic_segment.tags]
                    ),
                ),
            )

            report_dict = to_mapped_dict(response)

        self._diagnosis = MonitorDiagnosisReport(
            **report_dict,
            analyzer=self.analyzer_to_diagnose,
            monitor=self.monitor_to_diagnose,
            analyzedColumnCount=len(self.noisy_columns),
        )
        return self._diagnosis
