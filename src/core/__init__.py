import os
import json
import sys
from tkinter import messagebox
import urllib
from core.version import CURRENT_VERSION

DEFAULT_CONFIG = {
  "subjects": {
    "Math": 0,
    "Physics": 0
  },
  "project_folders": {},
  "daily_session_goal": [
    0,45
  ]
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


create_config_file()