import urllib
import subprocess 
import sys
import os

CURRENT_VERSION = "1.2.1"
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
  subprocess.Popen([installer_path])

  return True