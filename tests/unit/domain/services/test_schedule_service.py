from datetime import date, time
from unittest.mock import AsyncMock

import pytest
from SimplyTransport.domain.enums import DayOfWeek
from SimplyTransport.domain.schedule.model import StaticScheduleModel
from SimplyTransport.domain.services.schedule_service import ScheduleService
from SimplyTransport.domain.stop_times.model import StopTimeModel


@pytest.mark.asyncio
async def test_get_schedule_on_stop_for_day_should_call_repository():
    # Arrange
    schedule_repository = AsyncMock()
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    stop_id = "stop_id"
    day = DayOfWeek.MONDAY

    # Act
    await schedule_service.get_schedule_on_stop_for_day(stop_id=stop_id, day=day)

    # Assert
    schedule_repository.get_static_schedules.assert_called_once_with(stop_id=stop_id, day=day)


@pytest.mark.asyncio
async def test_get_schedule_on_stop_for_day_should_have_equal_static_schedules():
    # Arrange
    mock_schedule_data = [AsyncMock(), AsyncMock()]
    schedule_repository = AsyncMock()
    schedule_repository.get_static_schedules.return_value = mock_schedule_data
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    stop_id = "stop_id"
    day = DayOfWeek.MONDAY

    # Act
    result = await schedule_service.get_schedule_on_stop_for_day(stop_id=stop_id, day=day)

    # Assert
    schedule_repository.get_static_schedules.assert_called_once_with(stop_id=stop_id, day=day)
    assert len(result) == len(mock_schedule_data)


@pytest.mark.asyncio
async def test_get_schedule_on_stop_for_day_between_times_should_call_repository():
    # Arrange
    schedule_repository = AsyncMock()
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    stop_id = "stop_id"
    day = DayOfWeek.MONDAY
    start_time = time(hour=10, minute=0, second=0)
    end_time = time(hour=11, minute=0, second=0)

    # Act
    await schedule_service.get_schedule_on_stop_for_day_between_times(
        stop_id=stop_id, day=day, start_time=start_time, end_time=end_time
    )

    # Assert
    schedule_repository.get_static_schedules.assert_called_once_with(
        stop_id=stop_id, day=day, start_time=start_time, end_time=end_time
    )


@pytest.mark.asyncio
async def test_get_schedule_on_stop_for_day_between_times_should_have_equal_static_schedules():
    # Arrange
    mock_schedule_data = [AsyncMock(), AsyncMock()]
    schedule_repository = AsyncMock()
    schedule_repository.get_static_schedules.return_value = mock_schedule_data
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    stop_id = "stop_id"
    day = DayOfWeek.MONDAY
    start_time = time(hour=10, minute=0, second=0)
    end_time = time(hour=11, minute=0, second=0)

    # Act
    result = await schedule_service.get_schedule_on_stop_for_day_between_times(
        stop_id=stop_id, day=day, start_time=start_time, end_time=end_time
    )

    # Assert
    schedule_repository.get_static_schedules.assert_called_once_with(
        stop_id=stop_id, day=day, start_time=start_time, end_time=end_time
    )
    assert len(result) == len(mock_schedule_data)


@pytest.mark.asyncio
async def test_apply_custom_23_00_sorting_should_return_sorted_list_reverse():
    # Arrange
    mock_schedule_data = [
        StaticScheduleModel(
            stop_time=StopTimeModel(arrival_time=time.fromisoformat("01:01:01")),
            route=AsyncMock(),
            calendar=AsyncMock(),
            stop=AsyncMock(),
            trip=AsyncMock(),
        ),
        StaticScheduleModel(
            stop_time=StopTimeModel(arrival_time=time.fromisoformat("23:00:00")),
            route=AsyncMock(),
            calendar=AsyncMock(),
            stop=AsyncMock(),
            trip=AsyncMock(),
        ),
    ]
    schedule_repository = AsyncMock()
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    # Act
    result = await schedule_service.apply_custom_23_00_sorting(mock_schedule_data)

    # Assert
    assert len(result) == len(mock_schedule_data)
    assert result[0] == mock_schedule_data[1]
    assert result[1] == mock_schedule_data[0]


@pytest.mark.asyncio
async def test_apply_custom_23_00_sorting_should_return_sorted_list_no_change():
    # Arrange
    mock_schedule_data = [
        StaticScheduleModel(
            stop_time=StopTimeModel(arrival_time=time.fromisoformat("23:00:00")),
            route=AsyncMock(),
            calendar=AsyncMock(),
            stop=AsyncMock(),
            trip=AsyncMock(),
        ),
        StaticScheduleModel(
            stop_time=StopTimeModel(arrival_time=time.fromisoformat("01:01:01")),
            route=AsyncMock(),
            calendar=AsyncMock(),
            stop=AsyncMock(),
            trip=AsyncMock(),
        ),
    ]
    schedule_repository = AsyncMock()
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    # Act
    result = await schedule_service.apply_custom_23_00_sorting(mock_schedule_data)

    # Assert
    assert len(result) == len(mock_schedule_data)
    assert result[0] == mock_schedule_data[0]
    assert result[1] == mock_schedule_data[1]


@pytest.mark.asyncio
async def test_apply_custom_23_00_sorting_should_return_sorted_list_no_change_normal_times():
    # Arrange
    mock_schedule_data = [
        StaticScheduleModel(
            stop_time=StopTimeModel(arrival_time=time.fromisoformat("21:00:00")),
            route=AsyncMock(),
            calendar=AsyncMock(),
            stop=AsyncMock(),
            trip=AsyncMock(),
        ),
        StaticScheduleModel(
            stop_time=StopTimeModel(arrival_time=time.fromisoformat("21:01:01")),
            route=AsyncMock(),
            calendar=AsyncMock(),
            stop=AsyncMock(),
            trip=AsyncMock(),
        ),
    ]
    schedule_repository = AsyncMock()
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    # Act
    result = await schedule_service.apply_custom_23_00_sorting(mock_schedule_data)

    # Assert
    assert len(result) == len(mock_schedule_data)
    assert result[0] == mock_schedule_data[0]
    assert result[1] == mock_schedule_data[1]


@pytest.mark.asyncio
async def test_remove_exceptions_and_inactive_calendars_should_call_repository():
    # Arrange
    schedule_repository = AsyncMock()
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )

    mock_calendar1 = AsyncMock()
    mock_calendar1.service_id = "service1"
    mock_calendar2 = AsyncMock()
    mock_calendar2.service_id = "service2"

    mock_schedule1 = AsyncMock(spec=StaticScheduleModel)
    mock_schedule1.calendar = mock_calendar1
    mock_schedule2 = AsyncMock(spec=StaticScheduleModel)
    mock_schedule2.calendar = mock_calendar2
    mock_schedule_data: list[StaticScheduleModel] = [mock_schedule1, mock_schedule2]

    # Act
    await schedule_service.remove_exceptions_and_inactive_calendars(mock_schedule_data)

    # Assert
    calendar_date_repository.get_removed_exceptions_on_date.assert_called_once_with(date=date.today())


@pytest.mark.asyncio
async def test_get_by_trip_id_calls_repository():
    # Arrange
    schedule_repository = AsyncMock()
    calendar_date_repository = AsyncMock()
    schedule_service = ScheduleService(
        schedule_repository=schedule_repository,
        calendar_date_repository=calendar_date_repository,
    )
    trip_id = "trip_id"

    # Act
    await schedule_service.get_by_trip_id(trip_id=trip_id)

    # Assert
    schedule_repository.get_by_trip_id.assert_called_once_with(trip_id=trip_id)
