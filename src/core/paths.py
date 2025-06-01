import os
import sys 
import shutil
import json

def is_frozen():
  return getattr(sys, 'frozen', False)

def get_app_dir():
  if is_frozen():
    return os.path.dirname(sys.executable)
  else:
    return os.path.dirname(os.path.abspath(__file__))
  
def get_user_data_dir():
  if os.name == 'nt':  # Windows
      appdata = os.getenv('APPDATA')
      user_dir = os.path.join(appdata, "StudyArc")
  else:
      home = os.path.expanduser("~")
      user_dir = os.path.join(home, ".studyarc")
  os.makedirs(user_dir, exist_ok=True)
  return user_dir

def initialize_user_data_file(filename, headers):
    user_file = os.path.join(USER_DATA_DIR, filename)
    if not os.path.exists(user_file):

      if filename != "user_config.json":
        with open(file=user_file, mode="w") as writef:
          writef.write(headers)
      else:
        data = {
          "last_day": "2025 5 31",
          "session_goal": [
            0,
            45
          ],
          "style": "xpnative",
          "theme": "Light",
          "font": "@Microsoft JhengHei",
          "subjects": [
            "Math",
            "Physics"
          ],
          "filename_gif": "default.gif"
        }
        with open(file=user_file, mode="w") as writef:
          writef.write(json.dumps(data, indent=2))

    return user_file
  
IS_EXECUTABLE = is_frozen()
USER_DATA_DIR = get_user_data_dir()

if IS_EXECUTABLE: 
  APP_DIR = get_app_dir()

  DATA_CURRENT_WEEK = initialize_user_data_file("data_current_week.csv", "Day,Time,Description")
  DATA_WEEKS_LOG = initialize_user_data_file("data_weeks_log.csv", "Week number,Total Time,Summary")
  USER_CONFIG = initialize_user_data_file("user_config.json", "")
  SETTINGS_PATH = os.path.join(APP_DIR, "settings.yaml")
  ICON_PATH = os.path.join(APP_DIR, "assets", "logo.ico")
  GIFS_PATH = os.path.join(APP_DIR, "assets", "gifs")
else: 
  APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

  DATA_CURRENT_WEEK = os.path.join(APP_DIR, "data", "data_current_week.csv")
  DATA_WEEKS_LOG = os.path.join(APP_DIR, "data", "data_weeks_log.csv")
  USER_CONFIG = os.path.join(APP_DIR, "data", "user_config.json")
  SETTINGS_PATH = os.path.join(APP_DIR, "data", "settings.yaml")
  ICON_PATH = os.path.join(APP_DIR, "data", "assets", "logo.ico")
  GIFS_PATH = os.path.join(APP_DIR, "data", "assets", "gifs")