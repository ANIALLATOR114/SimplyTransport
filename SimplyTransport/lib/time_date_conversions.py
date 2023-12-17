from datetime import datetime
import json


def convert_29_hours_to_24_hours(time: str) -> datetime.time:
    """Converts a time in 29 hours format to 24 hours format"""
    hours_str, minutes_str, seconds_str = time.split(":")
    if int(hours_str) > 23:
        hours_str = str(int(hours_str) - 24)
    if len(hours_str) == 1:
        hours_str = f"0{hours_str}"

    fixed_arrival_time = f"{hours_str}:{minutes_str}:{seconds_str}"
    return datetime.strptime(fixed_arrival_time, "%H:%M:%S").time()


def convert_joined_date_to_date(date: str) -> datetime.date:
    return datetime.strptime(date, "%Y%m%d").date()


class DateTimeEncoderForJson(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%H:%M:%S %d-%m-%Y')
        return super().default(obj)