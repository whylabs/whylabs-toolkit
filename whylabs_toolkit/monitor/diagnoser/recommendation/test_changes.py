from whylabs_toolkit.monitor.diagnoser.models import ConditionRecord
from whylabs_toolkit.monitor.diagnoser.recommendation.recommended_change import RecommendedChange


def test_from_condition():
    info = {'k1': 3}
    condition = ConditionRecord(name="fixed_threshold_mismatch", summary='a mismatch', columns=['col1', 'col3', 'col4'], info=info)
    change = RecommendedChange.from_condition(condition)
    assert change.columns == condition.columns
    assert change.info == condition.info


def test_merge_changes():
    change1 = RecommendedChange(columns=['c1', 'c2'], info={'f1': 1, 'f2': 2})
    change2 = RecommendedChange(columns=['c1', 'c3'], info={'f1': 0, 'f3': 3})
    merged = change1.merge(change2)
    assert change1.columns == ['c1', 'c2']
    assert change2.columns == ['c1', 'c3']
    assert set(merged.columns) == {'c1', 'c2', 'c3'}
    assert merged.info == {'f1': 0, 'f2': 2, 'f3': 3}

