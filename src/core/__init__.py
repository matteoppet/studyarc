import os
import json
import sys

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


create_config_file()