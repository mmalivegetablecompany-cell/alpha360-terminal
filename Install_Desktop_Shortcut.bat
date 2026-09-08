@echo off
title Install Alpha360 Terminal Desktop Shortcut
echo =====================================================================
echo  Installing Alpha360 Terminal Desktop Shortcut
echo =====================================================================
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\Create_Desktop_Shortcut.ps1"
echo.
echo Done! You can now launch Alpha360 Terminal directly from your Desktop.
pause
