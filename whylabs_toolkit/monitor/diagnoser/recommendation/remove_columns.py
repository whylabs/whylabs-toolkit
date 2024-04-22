from typing import List

from whylabs_toolkit.monitor.models import Analyzer, TargetLevel

from whylabs_toolkit.monitor.diagnoser.recommendation.recommended_change import RecommendedChange


class RemoveColumns(RecommendedChange):
    name = 'remove_columns'
    summary = 'Remove columns from the analyzer'
    required_info = []
    manual = False

    def _check_can_do(self, analyzer: Analyzer) -> bool:
        if analyzer.targetMatrix.type == TargetLevel.dataset:
            raise ValueError('Cannot remove columns from a dataset level target matrix')
        return super()._check_can_do(analyzer)

    def generate_config(self, analyzer: Analyzer) -> List[Analyzer]:
        self._check_can_do(analyzer)
        to_remove = set(self.columns)
        # remove from includes if possible, otherwise exclude
        remove_includes = set(analyzer.targetMatrix.include).intersection(to_remove)
        analyzer.targetMatrix.include = list(set(analyzer.targetMatrix.include) - to_remove)
        analyzer.targetMatrix.exclude = list(set(analyzer.targetMatrix.exclude) | (to_remove - remove_includes))
        # if nothing's left to target, just remove the analyzer
        if len(analyzer.targetMatrix.include) == 0:
            return []
        return [analyzer]
