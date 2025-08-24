import os
import json
import sys
from tkinter import messagebox
import urllib
from core.version import CURRENT_VERSION

DEFAULT_CONFIG = {
  "themes": {},
  "streaks": {},
  "daily_session_goal": {}
}

if getattr(sys, "frozen", False): # from compiled exe
  CONFIG_DIR = os.path.expanduser("~/.studyarc")
  CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
  DATABASE_FILE = os.path.join(CONFIG_DIR, "database.db")
else: # from script
  CONFIG_DIR = os.path.expanduser("../database")
  CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
  DATABASE_FILE = os.path.join(CONFIG_DIR, "database.db")

def create_config_file():
  if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
  if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
      json.dump(DEFAULT_CONFIG, f, indent=4)

def get_latest_version():
  url = 'https://raw.githubusercontent.com/matteoppet/studyarc/main/frontend/latest_version.txt'

  try:
    with urllib.request.urlopen(url) as response:
      return response.read().decode('utf-8').strip()
  except:
    return None

def check_for_update(root_window):
  latest = get_latest_version()

  if latest and latest != CURRENT_VERSION:
    root_window.withdraw()
    if messagebox.showinfo("Update Available",
               f"A new version ({latest}) is available.\n\nDownload latest version through:\n\nhttps://sourceforge.net/projects/studyarc/"):
      root_window.deiconify()

def update_base_config_file(new_user_id):
  with open(CONFIG_FILE, "r") as config_read:
    data = json.load(config_read)

  data["streaks"][new_user_id] = {"current_streak": 0}
  data["daily_session_goal"][new_user_id] = [0,45]
  data["themes"][new_user_id] = "light"

  with open(CONFIG_FILE, "w") as config_write:
    config_write.write(json.dumps(data, indent=2))

create_config_file()