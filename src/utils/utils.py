def get_time_from_seconds(seconds: int) -> tuple[int, int, int]:
  seconds = int(seconds)
  hours, remainder = divmod(int(seconds), 3600)
  minutes, seconds = divmod(remainder, 60)

  return hours, minutes, seconds


def get_seconds_from_time(hours: int, minutes: int, seconds: int) -> int:
  return hours * 3600 + minutes * 60 + seconds


def format_time(hours: int, minutes: int, seconds: int) -> str:
  return f"{hours}h {minutes}m {seconds}s"


def resource_path(relative_path: str) -> str:
    import sys
    import os

    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
