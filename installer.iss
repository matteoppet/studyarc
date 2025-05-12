; installer.iss
[Setup]
AppName=Study Tracker
AppVersion=1.0
DefaultDirName={pf}\Study Tracker
DefaultGroupName=Study Tracker
OutputDir=output
OutputBaseFilename=StudyTrackerInstaller
Compression=lzma
SolidCompression=yes

DisableDirPage=no
DisableProgramGroupPage=no

[Files]
Source: "installer_source/main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_source/settings.yaml"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_source/data_current_week.csv"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_source/data_weeks_log.csv"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_source/user_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_source/assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs

[Icons]
; Start menu shortcut
Name: "{group}\Study Tracker"; Filename: "{app}\main.exe"
; Desktop shortcut
Name: "{userdesktop}\Study Tracker"; Filename: "{app}\main.exe"
; Uninstall shortcut
Name: "{group}\Uninstall Study Tracker"; Filename: "{uninstallexe}"