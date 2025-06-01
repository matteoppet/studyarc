from PIL import Image, ImageTk
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