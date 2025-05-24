import os
import sys 
import shutil

def get_app_dir():
  if getattr(sys, 'frozen', False):  # Running from PyInstaller .exe
      return os.path.dirname(sys.executable)
  else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

  return os.path.join(base_dir, "datas")

def get_user_data_dir():
  if os.name == 'nt':  # Windows
      appdata = os.getenv('APPDATA')
      user_dir = os.path.join(appdata, "Study Tracker")
  else:
      home = os.path.expanduser("~")
      user_dir = os.path.join(home, ".study_tracker")
  os.makedirs(user_dir, exist_ok=True)
  return user_dir

def initialize_user_data_file(filename):
    user_file = os.path.join(USER_DATA_DIR, filename)
    if not os.path.exists(user_file):
        shutil.copyfile(os.path.join(APP_DIR, filename), user_file)
    return user_file

APP_DIR = get_app_dir()
USER_DATA_DIR = get_user_data_dir()

ICON_PATH = os.path.join(APP_DIR, "assets", "logo_transparent_resized.ico")
SETTINGS_PATH = os.path.join(APP_DIR, "settings.yaml")

DATA_CURRENT_WEEK = initialize_user_data_file("data_current_week.csv")
DATA_WEEKS_LOG = initialize_user_data_file("data_weeks_log.csv")
USER_CONFIG = initialize_user_data_file("user_config.json")