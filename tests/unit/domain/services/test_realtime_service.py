from datetime import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from SimplyTransport.domain.realtime.enums import ScheduleRealtionship
from SimplyTransport.domain.realtime.realtime_schedule.model import RealTimeScheduleModel
from SimplyTransport.domain.schedule.model import StaticScheduleModel
from SimplyTransport.domain.services.realtime_service import RealTimeService
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
async def test_get_realtime_schedules_matches_per_stop_stop_time():
    static = StaticScheduleModel(
        stop_time=StopTimeModel(arrival_time=time.fromisoformat("12:00:00"), stop_sequence=1),
        route=AsyncMock(short_name="4"),
        calendar=AsyncMock(),
        stop=AsyncMock(id="S1"),
        trip=AsyncMock(id="T1", dataset="TFI"),
    )
    rt_trip = SimpleNamespace(
        trip_id="T1",
        route_id="R1",
        schedule_relationship=ScheduleRealtionship.SCHEDULED,
    )
    rt_st = SimpleNamespace(
        trip_id="T1",
        stop_id="S1",
        stop_sequence=1,
        arrival_delay=60,
        departure_delay=60,
        schedule_relationship=ScheduleRealtionship.SCHEDULED,
    )
    repo = AsyncMock()
    repo.load_recent_rt_overlay_for_schedules = AsyncMock(
        return_value=({"T1": rt_trip}, {("T1", "S1", 1): rt_st})
    )
    svc = RealTimeService(
        rt_stop_repository=AsyncMock(),
        rt_trip_repository=AsyncMock(),
        rt_vehicle_repository=AsyncMock(),
        realtime_schedule_repository=repo,
    )

    out = await svc.get_realtime_schedules_for_static_schedules([static])

    assert len(out) == 1
    assert out[0].rt_stop_time is rt_st
    assert out[0].rt_trip is rt_trip
    assert out[0].is_trip_removed is False
    assert out[0].delay_in_seconds == 60


@pytest.mark.asyncio
async def test_get_realtime_schedules_trip_removed_without_stop_time_row():
    static = StaticScheduleModel(
        stop_time=StopTimeModel(arrival_time=time.fromisoformat("12:10:00"), stop_sequence=1),
        route=AsyncMock(),
        calendar=AsyncMock(),
        stop=AsyncMock(id="S1"),
        trip=AsyncMock(id="T1", dataset="TFI"),
    )
    rt_trip = SimpleNamespace(
        trip_id="T1",
        route_id="R1",
        schedule_relationship=ScheduleRealtionship.CANCELED,
    )
    repo = AsyncMock()
    repo.load_recent_rt_overlay_for_schedules = AsyncMock(return_value=({"T1": rt_trip}, {}))
    svc = RealTimeService(
        rt_stop_repository=AsyncMock(),
        rt_trip_repository=AsyncMock(),
        rt_vehicle_repository=AsyncMock(),
        realtime_schedule_repository=repo,
    )

    out = await svc.get_realtime_schedules_for_static_schedules([static])

    assert len(out) == 1
    assert out[0].is_trip_removed is True
    assert out[0].rt_stop_time is None
    assert out[0].rt_trip is rt_trip
