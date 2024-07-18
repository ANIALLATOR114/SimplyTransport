from datetime import datetime, time, date
import json


def convert_29_hours_to_24_hours(time_str: str) -> time:
    """Converts a time in 29 hours format to 24 hours format"""
    hours, minutes, seconds = map(int, time_str.split(":"))
    return time((hours - 24) if hours > 23 else hours, minutes, seconds)


def convert_joined_date_to_date(date: str) -> date:
    return datetime.strptime(date, "%Y%m%d").date()


class DateTimeEncoderForJson(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%H:%M:%S %d-%m-%Y")
        return super().default(obj)


def return_time_difference(start_time: time, end_time: time) -> int:
    if start_time == end_time:
        return 0

    difference = (end_time.hour - start_time.hour) % 24
    if difference > 12:
        difference = 24 - difference

    return difference
