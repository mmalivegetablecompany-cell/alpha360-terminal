@echo off
:: Batch script to install Visual Studio CMake component for pure Flutter C++ Windows builds
:: Run as Administrator
echo =====================================================================
echo  Visual Studio C++ CMake Component Installer (for Flutter Windows)
echo =====================================================================
echo Requesting administrator privileges...
powershell -Command "Start-Process -FilePath '%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\setup.exe' -ArgumentList 'modify --installPath \"%ProgramFiles%\Microsoft Visual Studio\2022\Community\" --add Microsoft.VisualStudio.Component.VC.CMake.Project --passive --norestart' -Verb RunAs -Wait"
echo.
echo Component installation requested. Once finished, run 'flutter doctor' to verify.
pause
