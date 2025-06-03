import urllib
import subprocess 
import sys
import os
import psutil
import time

CURRENT_VERSION = "1.3.0"
REMOTE_URL = "https://raw.githubusercontent.com/matteoppet/studyarc/main/data/version.txt"

def get_remote_version(url):
  with urllib.request.urlopen(url) as response:
    return response.read().decode().strip()

def check_new_version():
  remote_version = get_remote_version(REMOTE_URL)

  if remote_version > CURRENT_VERSION:
    return True
  
def install_new_version():
  remote_version = get_remote_version(REMOTE_URL)

  url = f"https://github.com/matteoppet/studyarc/releases/download/v{remote_version}/setup.exe"
  installer_path = os.path.join(os.getenv("TEMP"), "setup.exe")
  urllib.request.urlretrieve(url, installer_path)

  # Terminate original app process by name
  for proc in psutil.process_iter(['name']):
      if proc.info['name'] == "studyarc.exe":
          proc.terminate()
          proc.wait(timeout=10)

  subprocess.Popen([installer_path], close_fds=True)

  os._exit(0)

  return True