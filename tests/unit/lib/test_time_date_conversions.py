import pytest
from datetime import time, datetime
from SimplyTransport.lib.time_date_conversions import (
    convert_joined_date_to_date,
    return_time_difference,
    convert_29_hours_to_24_hours,
)


@pytest.mark.parametrize(
    "start_time, end_time, expected",
    [
        (time(10, 0, 0), time(12, 0, 0), 2),
        (time(10, 0, 0), time(10, 0, 0), 0),
        (time(10, 0, 0), time(22, 0, 0), 12),
        (time(10, 0, 0), time(8, 0, 0), 2),
        (time(23, 0, 0), time(0, 0, 0), 1),
        (time(23, 0, 0), time(1, 0, 0), 2),
        (time(23, 0, 0), time(2, 0, 0), 3),
        (time(23, 0, 0), time(3, 0, 0), 4),
        (time(23, 0, 0), time(4, 0, 0), 5),
    ],
)
def test_return_time_difference(start_time, end_time, expected):
    assert return_time_difference(start_time, end_time) == expected


@pytest.mark.parametrize(
    "date_str, expected_date",
    [
        ("20220101", datetime(2022, 1, 1).date()),
        ("20221231", datetime(2022, 12, 31).date()),
        ("20221015", datetime(2022, 10, 15).date()),
        ("20220909", datetime(2022, 9, 9).date()),
        ("20220808", datetime(2022, 8, 8).date()),
        ("20280707", datetime(2028, 7, 7).date()),
        ("20280606", datetime(2028, 6, 6).date()),
        ("20280505", datetime(2028, 5, 5).date()),
    ],
)
def test_convert_joined_date_to_date(date_str, expected_date):
    assert convert_joined_date_to_date(date_str) == expected_date


@pytest.mark.parametrize(
    "time_29, expected_time",
    [
        ("23:00:00", time(23, 0, 0)),
        ("23:12:12", time(23, 12, 12)),
        ("24:00:00", time(0, 0, 0)),
        ("24:12:12", time(0, 12, 12)),
        ("25:00:00", time(1, 0, 0)),
        ("26:00:00", time(2, 0, 0)),
        ("27:00:00", time(3, 0, 0)),
        ("28:00:00", time(4, 0, 0)),
        ("29:54:54", time(5, 54, 54)),
    ],
)
def test_convert_29_hours_to_24_hours(time_29, expected_time):
    assert convert_29_hours_to_24_hours(time_29) == expected_time
