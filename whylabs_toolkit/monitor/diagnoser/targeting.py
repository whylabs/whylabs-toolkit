from typing import List, Union, Set

from whylabs_toolkit.monitor.models import EntitySchema, ColumnMatrix, DatasetMatrix


def expand_target(target: str, schema: EntitySchema) -> List[str]:
    if target == "*":
        return [str(k) for k in schema.columns.keys()]
    col_items = schema.columns.items()
    if target == "group:discrete":
        return [name for (name, c) in col_items if c.discreteness == "discrete"]
    if target == "group:continuous":
        return [name for (name, c) in col_items if c.discreteness == "continuous"]
    if target == "group:input":
        return [name for (name, c) in col_items if c.classifier == "input"]
    if target == "group:output":
        return [name for (name, c) in col_items if c.classifier == "output"]
    return [target]


def targeted_columns(target_matrix: Union[ColumnMatrix, DatasetMatrix], schema: EntitySchema) -> List[str]:
    if target_matrix is None:
        return []
    if isinstance(target_matrix, DatasetMatrix):
        return ["__internal__datasetMetrics"]
    columns: Set[str] = set()
    if target_matrix.include is not None:
        for include in target_matrix.include:
            columns.update(expand_target(include, schema))
    if target_matrix.exclude is not None:
        for exclude in target_matrix.exclude:
            columns = columns - set(expand_target(exclude, schema))
    return list(columns)
