@echo off
REM Step 1: Run PyInstaller
cd builds\pyinstaller
pyinstaller main.spec

REM Step 2: Return to project root
cd ../..

REM Step 3: Delete previous Inno Setup output directory
rmdir /s /q builds\inno\output

Rem Step 4: Open Inno Setup Compiler for manual build
iscc builds\inno\installer.iss