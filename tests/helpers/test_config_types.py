from whylabs_toolkit.container.config_types import DatasetCadence, DatasetUploadCadenceGranularity


def test_container_config_parsing() -> None:
    """
    Our python container depends on these types staying the way they are. This is
    the easiest way to make sure we don't accidentally break the downstream container.
    """
    daily = DatasetCadence("DAILY")
    assert daily == DatasetCadence.DAILY

    hourly = DatasetCadence("HOURLY")
    assert hourly == DatasetCadence.HOURLY

    daily_granularity = DatasetUploadCadenceGranularity("D")
    assert daily_granularity == DatasetUploadCadenceGranularity.DAY

    hour_granularity = DatasetUploadCadenceGranularity("H")
    assert hour_granularity == DatasetUploadCadenceGranularity.HOUR

    minute_granularity = DatasetUploadCadenceGranularity("M")
    assert minute_granularity == DatasetUploadCadenceGranularity.MINUTE
