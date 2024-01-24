from unittest.mock import AsyncMock

from datetime import time

from SimplyTransport.domain.realtime.realtime_schedule.model import RealTimeScheduleModel
from SimplyTransport.domain.realtime.stop_time.model import RTStopTimeModel
from SimplyTransport.domain.realtime.trip.model import RTTripModel
from SimplyTransport.domain.schedule.model import StaticScheduleModel
from SimplyTransport.domain.services.realtime_service import RealTimeService
import pytest

from SimplyTransport.domain.stop_times.model import StopTimeModel


@pytest.mark.asyncio
async def test_apply_custom_23_00_sorting_should_return_sorted_list_no_change_normal_times():
    # Arrange
    mock_schedule_data = [
        RealTimeScheduleModel(
            static_schedule=StaticScheduleModel(
                stop_time=StopTimeModel(arrival_time=time.fromisoformat("23:00:00")),
                route=AsyncMock(),
                calendar=AsyncMock(),
                stop=AsyncMock(),
                trip=AsyncMock(),
            )
        ),
        RealTimeScheduleModel(
            static_schedule=StaticScheduleModel(
                stop_time=StopTimeModel(arrival_time=time.fromisoformat("00:00:00")),
                route=AsyncMock(),
                calendar=AsyncMock(),
                stop=AsyncMock(),
                trip=AsyncMock(),
            )
        ),
        RealTimeScheduleModel(
            static_schedule=StaticScheduleModel(
                stop_time=StopTimeModel(arrival_time=time.fromisoformat("01:00:00")),
                route=AsyncMock(),
                calendar=AsyncMock(),
                stop=AsyncMock(),
                trip=AsyncMock(),
            )
        ),
    ]

    real_time_service = RealTimeService(
        rt_stop_repository=AsyncMock(),
        rt_trip_repository=AsyncMock(),
        rt_vehicle_repository=AsyncMock(),
        realtime_schedule_repository=AsyncMock(),
    )

    # Act
    result = await real_time_service.apply_custom_23_00_sorting(mock_schedule_data)

    # Assert
    assert len(result) == len(mock_schedule_data)
    assert result[0] == mock_schedule_data[0]
    assert result[1] == mock_schedule_data[1]
    assert result[2] == mock_schedule_data[2]


@pytest.mark.asyncio
async def test_apply_custom_23_00_sorting_should_return_sorted_list_backwards():
    # Arrange
    mock_schedule_data = [
        RealTimeScheduleModel(
            static_schedule=StaticScheduleModel(
                stop_time=StopTimeModel(arrival_time=time.fromisoformat("01:00:00")),
                route=AsyncMock(),
                calendar=AsyncMock(),
                stop=AsyncMock(),
                trip=AsyncMock(),
            )
        ),
        RealTimeScheduleModel(
            static_schedule=StaticScheduleModel(
                stop_time=StopTimeModel(arrival_time=time.fromisoformat("00:00:00")),
                route=AsyncMock(),
                calendar=AsyncMock(),
                stop=AsyncMock(),
                trip=AsyncMock(),
            )
        ),
        RealTimeScheduleModel(
            static_schedule=StaticScheduleModel(
                stop_time=StopTimeModel(arrival_time=time.fromisoformat("23:00:00")),
                route=AsyncMock(),
                calendar=AsyncMock(),
                stop=AsyncMock(),
                trip=AsyncMock(),
            )
        ),
    ]

    real_time_service = RealTimeService(
        rt_stop_repository=AsyncMock(),
        rt_trip_repository=AsyncMock(),
        rt_vehicle_repository=AsyncMock(),
        realtime_schedule_repository=AsyncMock(),
    )

    # Act
    result = await real_time_service.apply_custom_23_00_sorting(mock_schedule_data)

    # Assert
    assert len(result) == len(mock_schedule_data)
    assert result[0] == mock_schedule_data[2]
    assert result[1] == mock_schedule_data[1]
    assert result[2] == mock_schedule_data[0]


@pytest.mark.asyncio
async def test_parse_most_recent_realtime_update_returns_most_recent_updates():
    # Arrange
    inputs = [
        (RTStopTimeModel(stop_sequence=1, trip_id="trip1"), RTTripModel(trip_id="trip1")),
        (RTStopTimeModel(stop_sequence=2, trip_id="trip1"), RTTripModel(trip_id="trip1")),
        (RTStopTimeModel(stop_sequence=1, trip_id="trip2"), RTTripModel(trip_id="trip2")),
    ]

    real_time_service = RealTimeService(
        rt_stop_repository=AsyncMock(),
        rt_trip_repository=AsyncMock(),
        rt_vehicle_repository=AsyncMock(),
        realtime_schedule_repository=AsyncMock(),
    )

    # Act
    result = real_time_service.parse_most_recent_realtime_update(inputs)

    # Assert
    expected_results = [
        (RTStopTimeModel(stop_sequence=2, trip_id="trip1"), RTTripModel(trip_id="trip1")),
        (RTStopTimeModel(stop_sequence=1, trip_id="trip2"), RTTripModel(trip_id="trip2")),
    ]
    assert len(result) == len(expected_results)
    assert result[0] == inputs[1]
    assert result[1] == inputs[2]


@pytest.mark.asyncio
async def test_parse_most_recent_realtime_update_returns_empty_list_with_no_input():
    # Arrange
    real_time_service = RealTimeService(
        rt_stop_repository=AsyncMock(),
        rt_trip_repository=AsyncMock(),
        rt_vehicle_repository=AsyncMock(),
        realtime_schedule_repository=AsyncMock(),
    )

    # Act
    result = real_time_service.parse_most_recent_realtime_update([])

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_parse_most_recent_realtime_update_is_order_independent():
    # Arrange
    inputs = [
        (RTStopTimeModel(stop_sequence=2, trip_id="trip1"), RTTripModel(trip_id="trip1")),
        (RTStopTimeModel(stop_sequence=1, trip_id="trip1"), RTTripModel(trip_id="trip1")),
        (RTStopTimeModel(stop_sequence=1, trip_id="trip2"), RTTripModel(trip_id="trip2")),
    ]

    real_time_service = RealTimeService(
        rt_stop_repository=AsyncMock(),
        rt_trip_repository=AsyncMock(),
        rt_vehicle_repository=AsyncMock(),
        realtime_schedule_repository=AsyncMock(),
    )

    # Act
    result = real_time_service.parse_most_recent_realtime_update(inputs)

    # Assert
    expected_results = [
        (RTStopTimeModel(stop_sequence=2, trip_id="trip1"), RTTripModel(trip_id="trip1")),
        (RTStopTimeModel(stop_sequence=1, trip_id="trip2"), RTTripModel(trip_id="trip2")),
    ]
    assert len(result) == len(expected_results)
    assert result[0] == inputs[0]
    assert result[1] == inputs[2]
