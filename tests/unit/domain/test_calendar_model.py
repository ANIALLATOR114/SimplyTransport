from SimplyTransport.domain.calendar.model import CalendarModel
from SimplyTransport.domain.calendar_dates.model import CalendarDateModel

from datetime import date

def test_calendar_model_returns_true_if_active():
    """Test that the CalendarModel returns True if the calendar is active on the given date"""
    calendar = CalendarModel(
        id="1",
        monday=1,
        tuesday=1,
        wednesday=1,
        thursday=1,
        friday=1,
        saturday=1,
        sunday=1,
        start_date=date(2021, 1, 1),
        end_date=date(2021, 12, 31),
        dataset="test",
    )
    assert calendar.true_if_active(date(2021, 1, 1)) is True
    assert calendar.true_if_active(date(2021, 12, 31)) is True
    assert calendar.true_if_active(date(2021, 6, 30)) is True
    assert calendar.true_if_active(date(2020, 1, 2)) is False
    assert calendar.true_if_active(date(2022, 1, 2)) is False


def test_calendar_model_returns_true_if_in_exceptions():
    """Test that the CalendarModel returns True if the calendar is active on the given date"""
    calendar = CalendarModel(
        id="1",
        monday=1,
        tuesday=1,
        wednesday=1,
        thursday=1,
        friday=1,
        saturday=1,
        sunday=1,
        start_date=date(2021, 1, 1),
        end_date=date(2021, 12, 31),
        dataset="test",
    )
    assert calendar.in_exceptions([]) is False
    assert calendar.in_exceptions(
        [
            CalendarDateModel(
                service_id="1",
                date=date(2021, 1, 1),
                exception_type=1,
                dataset="test",
            )
        ]
    ) is True
    assert calendar.in_exceptions(
        [
            CalendarDateModel(
                service_id="different_id",
                date=date(2021, 1, 1),
                exception_type=1,
                dataset="test",
            )
        ]
    ) is False