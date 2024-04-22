from typing import Optional

from whylabs_toolkit.monitor.models import Analyzer

from whylabs_toolkit.monitor.diagnoser.models import ConditionRecord
from whylabs_toolkit.monitor.diagnoser.recommendation.remove_columns import RemoveColumns


def gen_analyzer(metric='mean', config: Optional[dict] = None,
                 target_matrix: Optional[dict] = None, baseline: Optional[dict] = None):
    target_matrix = {'type': 'column', 'include': ['col1']} if target_matrix is None else target_matrix
    config = {'type': 'fixed', 'metric': metric, 'upper': 1.0} if config is None else config
    if config['type'] != 'fixed':
        config['baseline'] = {'type': 'TrailingWindow', 'size': 7} if baseline is None else baseline
    return Analyzer.parse_obj(
        {
            'id': 'test_analyzer',
            'config': config,
            'targetMatrix': target_matrix,
        })


def test_remove_columns():
    analyzer = gen_analyzer(target_matrix={'type': 'column', 'include': ['col1', 'col2'], 'exclude': ['col3']})
    condition = ConditionRecord(name='fixed_threshold', summary='', columns=['col1', 'col3', 'col4'])
    change = RemoveColumns.from_condition(condition)
    result = change.generate_config(analyzer)
    assert len(result) == 1
    updated = result[0]
    assert updated.targetMatrix.include == ['col2']
    assert updated.targetMatrix.exclude.sort() == ['col3', 'col4'].sort()


def test_remove_columns2():
    analyzer = gen_analyzer(target_matrix={'type': 'column', 'include': ['col1', 'col2'], 'exclude': ['col3']})
    action = RemoveColumns(['col1', 'col2'])
    result = action.generate_config(analyzer)
    assert len(result) == 0
