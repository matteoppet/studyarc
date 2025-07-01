from datetime import date, timedelta
import sys
import os

def resource_path(relative_path):
  try:
    base_path = sys._MEIPASS
  except AttributeError:
    base_path = os.path.abspath(".")
  return os.path.join(base_path, relative_path)


def time_to_seconds(hours, minutes):
  return hours * 3600 + minutes * 60

def seconds_to_time(seconds):
  result_hours = seconds // 3600
  result_minutes = (seconds % 3600) // 60
  result_seconds = seconds % 60
  return [result_hours, result_minutes, result_seconds]

def get_current_week_dates(target_date: date = None) -> tuple[date, date]:
  if target_date is None:
      today = date.today()
  else:
    today = target_date

  days_since_monday = today.weekday()
  monday_of_week = today - timedelta(days=days_since_monday)

  days_until_sunday = 6 - today.weekday()
  sunday_of_week = today + timedelta(days=days_until_sunday)

  return monday_of_week, sunday_of_week