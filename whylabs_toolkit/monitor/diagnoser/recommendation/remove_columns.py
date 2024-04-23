from typing import List, Union

from whylabs_toolkit.monitor.models import Analyzer, TargetLevel, ColumnMatrix, DatasetMatrix

from whylabs_toolkit.monitor.diagnoser.recommendation.recommended_change import RecommendedChange
from whylabs_toolkit.monitor.models.analyzer import ColumnGroups


class RemoveColumns(RecommendedChange):
    name = "remove_columns"
    summary = "Remove columns from the analyzer"
    required_info: List[str] = []
    manual = False

    def _check_can_do(self, analyzer: Analyzer) -> bool:
        if analyzer.targetMatrix.type == TargetLevel.dataset:
            raise ValueError("Cannot remove columns from a dataset level target matrix")
        return super()._check_can_do(analyzer)

    def generate_config(self, analyzer: Analyzer) -> List[Analyzer]:
        self._check_can_do(analyzer)
        if isinstance(analyzer.targetMatrix, DatasetMatrix):
            return [analyzer]
        target_matrix: ColumnMatrix = analyzer.targetMatrix
        include: List[str] = analyzer.targetMatrix.include if analyzer.targetMatrix.include is not None else []
        exclude: List[Union[ColumnGroups, str]] = (
            analyzer.targetMatrix.exclude if analyzer.targetMatrix.exclude is not None else []
        )
        to_remove = set(self.columns)
        # remove from includes if possible, otherwise exclude
        remove_includes = set(include).intersection(to_remove)
        new_includes = list(set(include) - to_remove)
        analyzer.targetMatrix.include = new_includes
        new_excludes = list(set(exclude).union(to_remove - remove_includes))
        analyzer.targetMatrix.exclude = new_excludes
        # if nothing's left to target, just remove the analyzer
        if len(analyzer.targetMatrix.include) == 0:
            return []
        return [analyzer]
