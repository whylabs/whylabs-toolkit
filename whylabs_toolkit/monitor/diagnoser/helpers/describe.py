from typing import List, Union

import pandas as pd


def describe_truncated_list(vals: List[str], num: int = 10) -> str:
    if len(vals) <= num:
        return str(vals)
    return f"{vals[0:num]} and {len(vals) - num} more"


def describe_truncated_table(df: Union[pd.DataFrame, pd.Series], num: int = 10) -> str:
    if len(df) <= num:
        table = df.to_markdown()
        return str(table) if table is not None else "No data to display."
    return f"{df[0:num].to_markdown()}\n and {len(df) - num} more"


def filter_by_index(items: Union[pd.Index, list], ref: pd.Series) -> pd.Series:
    """
    Filters the reference by items in its index. Appends 0 values for any
    items not in the ref index.

    Example use... ref is anomalies by column, items are columns in a condition.
    """
    index = items if isinstance(items, pd.Index) else pd.Index(items)
    diff = index.difference(ref.index)
    if len(diff) == 0:
        return ref.loc[index].sort_index()
    expanded_ref = pd.concat([ref, pd.Series([0] * len(diff), index=diff)])
    return expanded_ref.loc[index].sort_index()
