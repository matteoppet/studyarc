import os
import sys 
import shutil

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

  
IS_EXECUTABLE = is_frozen()
USER_DATA_DIR = get_user_data_dir()

if IS_EXECUTABLE: 
  APP_DIR = get_app_dir()

  DATA_CURRENT_WEEK = initialize_user_data_file("data_current_week.csv")
  DATA_WEEKS_LOG = initialize_user_data_file("data_weeks_log.csv")
  USER_CONFIG = initialize_user_data_file("user_config.json")
  SETTINGS_PATH = os.path.join(APP_DIR, "settings.yaml")
  ICON_PATH = os.path.join(APP_DIR, "assets", "logo_transparent_resized.ico")
  GIFS_PATH = os.path.join(APP_DIR, "assets", "gifs")
else: 
  APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

  DATA_CURRENT_WEEK = os.path.join(APP_DIR, "data", "data_current_week.csv")
  DATA_WEEKS_LOG = os.path.join(APP_DIR, "data", "data_weeks_log.csv")
  USER_CONFIG = os.path.join(APP_DIR, "data", "user_config.json")
  SETTINGS_PATH = os.path.join(APP_DIR, "data", "settings.yaml")
  ICON_PATH = os.path.join(APP_DIR, "data", "assets", "logo_transparent_resized.ico")
  GIFS_PATH = os.path.join(APP_DIR, "data", "assets", "gifs")
