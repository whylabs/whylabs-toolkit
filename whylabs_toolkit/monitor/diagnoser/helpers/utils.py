import os
from typing import List, Optional

from whylabs_client.api.monitor_diagnostics_api import MonitorDiagnosticsApi

from whylabs_toolkit.helpers.client import create_client
from whylabs_toolkit.helpers.config import Config
from whylabs_toolkit.monitor.models import SegmentTag


def get_monitor_diagnostics_api(config: Config = Config()) -> MonitorDiagnosticsApi:
    """
    Get the monitor diagnostics API, which is used to interact with the WhyLabs Monitor Diagnostics service
    to diagnose noisy monitors.
    :param config:
    :return:
    """
    return MonitorDiagnosticsApi(api_client=create_client(config=config))


def env_setup(
    org_id: str, dataset_id: str, api_key: Optional[str] = None, whylabs_endpoint: Optional[str] = None
) -> None:
    """
    Set environment variables to work with both whylabs-toolkit and whylogs. Will pick up the API
    key from the environment if not provided as a parameter.
    :param org_id:
    :param dataset_id:
    :param api_key:
    :param whylabs_endpoint:
    :return:
    """
    os.environ["WHYLABS_API_KEY"] = api_key if api_key else os.environ["WHYLABS_API_KEY"]
    if not os.environ["WHYLABS_API_KEY"]:
        raise Exception("Please provide an API key")
    os.environ["WHYLABS_DEFAULT_ORG_ID"] = org_id
    os.environ["ORG_ID"] = org_id
    os.environ["WHYLABS_DEFAULT_DATASET_ID"] = dataset_id
    if whylabs_endpoint:
        os.environ["WHYLABS_API_ENDPOINT"] = whylabs_endpoint
        os.environ["WHYLABS_HOST"] = whylabs_endpoint


def segment_to_text(segment: List[SegmentTag]) -> str:
    if segment is None or len(segment) == 0:
        return ""
    text = ""
    for tag in segment:
        if len(text) > 0:
            text += "&"
        text += f"{tag.key}={tag.value}"
    return text


def segment_as_readable_text(segment: List[SegmentTag]) -> str:
    text = segment_to_text(segment)
    return "overall" if text == "" else text


def text_to_segment(text: str) -> List[SegmentTag]:
    if text == "":
        return []
    tags = []
    parts = text.split("&")
    for part in parts:
        [key, value] = part.split("=", 2)
        tags.append(SegmentTag(key=key, value=value))
    return tags
