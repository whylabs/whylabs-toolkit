"""Common utilities."""
from typing import Any, Dict

from pydantic import Field, constr


def anyOf_to_oneOf(schema: Dict[str, Any], field_name: str) -> None:
    """Turn anyOf in JSON schema to oneOf.

    onfOf is much stricter and pyDantic doesn't produce this tag. We hijack the JSON schema object to
    set this correctly.

    See: https://github.com/samuelcolvin/pydantic/issues/656
    """
    cfg = schema["properties"].get(field_name)
    if cfg is None:
        return
    if cfg.get("anyOf") is None:
        return
    cfg["oneOf"] = cfg["anyOf"]
    del cfg["anyOf"]


COLUMN_NAME_TYPE = constr(max_length=1000)
METRIC_NAME_STR = constr(max_length=50)


def duration_field(description: str, title: str) -> Any:
    """Duration of a field."""
    return Field(
        None,
        title=title,
        description=description,
        example="PT1H, P1D",
        regex="^P(?!$)(\\d+M)?(\\d+W)?(\\d+D)?(T(?=\\d+[HM])(\\d+H)?(\\d+M)?)?$",
    )
