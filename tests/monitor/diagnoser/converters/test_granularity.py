from whylabs_toolkit.monitor.diagnoser.converters.granularity import calculate_num_batches


def test_calculate_num_batches_hourly():
    assert calculate_num_batches('2022-01-01T00:00:00Z/2022-01-01T03:30:00Z', 'hourly') == 3
    assert calculate_num_batches('2022-01-01T00:00:00Z/2022-01-03T01:00:00Z', 'hourly') == 49
    assert calculate_num_batches('2022-01-01T00:00:00Z/2022-01-02T00:00:00Z', 'hourly') == 24
    assert calculate_num_batches('2022-11-19T00:00:00.000Z/2022-12-19T00:00:00.000Z', 'hourly') == 720
    assert calculate_num_batches('2022-11-19T00:00:00.000Z/2023-12-19T00:00:00.000Z', 'hourly') == 9480


def test_calculate_num_batches_daily():
    assert calculate_num_batches('2022-01-01T00:00:00Z/2022-01-02T00:00:00Z', 'daily') == 1
    assert calculate_num_batches('2022-01-01T00:00:00Z/2022-01-09T00:00:00Z', 'daily') == 8
    assert calculate_num_batches('2022-11-19T00:00:00.000Z/2022-12-19T00:00:00.000Z', 'daily') == 30
    assert calculate_num_batches('2022-11-19T00:00:00.000Z/2023-12-19T00:00:00.000Z', 'daily') == 395


def test_calculate_num_batches_weekly():
    assert calculate_num_batches('2022-01-01T00:00:00Z/2022-01-02T00:00:00Z', 'weekly') == 0
    assert calculate_num_batches('2022-01-01T00:00:00Z/2022-01-09T00:00:00Z', 'weekly') == 1
    assert calculate_num_batches('2022-11-19T00:00:00.000Z/2022-12-19T00:00:00.000Z', 'weekly') == 4
    assert calculate_num_batches('2022-11-19T00:00:00.000Z/2023-12-19T00:00:00.000Z', 'weekly') == 56


def test_calculate_num_batches_monthly():
    assert calculate_num_batches('2022-01-01T00:00:00Z/2022-02-02T00:00:00Z', 'monthly') == 1
    assert calculate_num_batches('2022-01-01T00:00:00Z/2023-02-02T00:00:00Z', 'monthly') == 13


def test_calculate_num_batches_duration():
    assert calculate_num_batches('2022-01-01T00:00:00Z/P3D', 'daily') == 3
    assert calculate_num_batches('2022-01-01T00:00:00Z/P1W', 'daily') == 7
    assert calculate_num_batches('2022-01-01T00:00:00Z/P1D', 'hourly') == 24


def test_calculate_num_batches_format():
    assert calculate_num_batches('2022-01-01T00:00/2022-01-02T00:00', 'daily') == 1
    assert calculate_num_batches('2022-01-01/2022-01-02', 'daily') == 1
    assert calculate_num_batches('2022-01-01/P1D', 'daily') == 1
