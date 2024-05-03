from __future__ import annotations
from typing import Optional, List

from whylabs_toolkit.monitor.models import Analyzer

from whylabs_toolkit.monitor.diagnoser.models import ConditionRecord
from whylabs_toolkit.monitor.diagnoser.helpers.describe import describe_truncated_list


class RecommendedChange:
    name = ""
    summary = ""
    manual = True
    required_info: List[str] = []

    @classmethod
    def from_condition(cls, condition: ConditionRecord) -> RecommendedChange:
        return cls(condition.columns if condition.columns is not None else [], condition.info)

    def __init__(self, columns: List[str], info: Optional[dict] = None):
        self.columns = columns
        self.info = info

    def merge(self, change: RecommendedChange) -> RecommendedChange:
        if change.name != self.name:
            raise ValueError(f"Cannot merge {self.name} and {change.name}")
        merged = RecommendedChange(list(set(self.columns) | set(change.columns)), self.info)
        merged.merge_info(change.info)
        return merged

    def merge_info(self, info: Optional[dict]) -> Optional[dict]:
        if self.info is None:
            self.info = info
        elif info is not None:
            self.info = {**self.info, **info}
        return self.info

    def summarize(self) -> str:
        info = self.info if self.info else {}
        return self.summary.format(**info)

    def describe(self) -> str:
        return f"{self.summarize()} for {describe_truncated_list(self.columns)}"

    def can_automate(self) -> bool:
        return all(getattr(self.info, f, False) for f in self.required_info) and not self.manual

    def _check_can_do(self, analyzer: Analyzer) -> bool:
        if self.manual:
            raise Exception(f"{self.name} has not been automated")
        if not self.can_automate():
            raise Exception(
                f"{self.name} requires extra information "
                f"{[f for f in self.required_info if self.info is None or f not in self.info.keys()]}"
            )
        return True

    def generate_config(self, analyzer: Analyzer) -> List[Analyzer]:
        self._check_can_do(analyzer)
        return [analyzer]
