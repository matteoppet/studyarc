import os
import sys 

def get_app_dir():
  if getattr(sys, 'frozen', False):  # Running from PyInstaller .exe
      return os.path.dirname(sys.executable)
  return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()

SETTINGS_PATH = os.path.join(APP_DIR, "settings.yaml")
DATA_CURRENT_WEEK = os.path.join(APP_DIR, "data_current_week.csv")
DATA_WEEKS_LOG = os.path.join(APP_DIR, "data_weeks_log.csv")
USER_CONFIG = os.path.join(APP_DIR, "user_config.json")
ICON_PATH = os.path.join(APP_DIR, "assets", "logo_transparent_resized.ico")