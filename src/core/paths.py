import os
import sys 
import json
from datetime import datetime

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
          "data": {
            "previous_session_date": "",
            "streak": 0,
            "subjects": [
              "Math"
            ]
          },
          "preferences": {
            "style": "xpnative"
          },
          "goals": {
            "daily_session_goal": [
              0,
              1
            ]
          },
          "display_options": {
            "show_metrics_frame": True,
            "show_tables_frame": True,
            "show_charts_frame": True
          },
          "version_info": {
            "auto_update": True
          }
        }
        with open(file=user_file, mode="w") as writef:
          writef.write(json.dumps(data, indent=2))

    return user_file

IS_EXECUTABLE = is_frozen()
USER_DATA_DIR = get_user_data_dir()

if IS_EXECUTABLE: 
  APP_DIR = get_app_dir()

  USER_CONFIG = initialize_user_data_file("user_config.json", "")
  ICON_PATH = os.path.join(APP_DIR, "assets", "logo.ico")
  USER_PATH = os.path.join(APP_DIR, "assets", "user.png")
  DATABASE_PATH = initialize_user_data_file("database.db", "")
else: 
  APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

  USER_CONFIG = os.path.join(APP_DIR, "data", "user_config.json")
  ICON_PATH = os.path.join(APP_DIR, "data", "assets", "logo.ico")
  USER_PATH = os.path.join(APP_DIR, "data", "assets", "user.png")
  DATABASE_PATH = os.path.join(APP_DIR, "data", "database.db")