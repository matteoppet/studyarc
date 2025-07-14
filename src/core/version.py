import urllib.request
import sys
import os

CURRENT_VERSION = "2.2.0"
REMOTE_URL = "https://raw.githubusercontent.com/matteoppet/studyarc/main/data/version.txt"

def get_remote_version(url):
  with urllib.request.urlopen(url) as response:
    return response.read().decode().strip()

def check_new_version():
  remote_version = get_remote_version(REMOTE_URL)

  if remote_version > CURRENT_VERSION:
    return True


def install_new_version(root_window):
  import win32process
  import subprocess

  remote_version = get_remote_version(REMOTE_URL)
  url = f"https://github.com/matteoppet/studyarc/releases/download/v{remote_version}/setup.exe"
  installer_path = os.path.join(os.getenv("TEMP"), "setup.exe")
  batch_path = os.path.join(os.getenv("TEMP"), "update.bat")

  try:
    urllib.request.urlretrieve(url, installer_path)
  except urllib.error.URLError as e:
     print("Error downloading installer")
  
  with open(batch_path, "w") as f:
        f.write("""@echo off
set EXE=studyarc.exe

echo Waiting for %EXE% to close...
:wait
tasklist | find /i "%EXE%" >nul
if not errorlevel 1 (
    timeout /t 1 >nul
    goto wait
)

echo Ensuring file locks are released...
timeout /t 5 >nul

echo Starting installer...
powershell -Command "Start-Process '%TEMP%\setup.exe' -ArgumentList '/VERYSILENT /FORCECLOSEAPPLICATIONS' -Verb RunAs -Wait"
echo Installer finished.
rem Close the batch script's console window
exit /b
""")

  subprocess.Popen(
    ["cmd.exe", "/c", batch_path],
    creationflags=win32process.CREATE_NO_WINDOW 
  )
  root_window.destroy()
  sys.exit()