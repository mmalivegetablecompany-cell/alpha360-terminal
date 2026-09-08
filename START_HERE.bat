@echo off
title 424-Stock Trading Platform - Master Launcher
color 0B
cls

:MENU
echo ==============================================================================
echo   🚀 424-STOCK INSTITUTIONAL TRADING PLATFORM & CROSS-PLATFORM TERMINAL
echo ==============================================================================
echo.
echo   [1] 📱 Launch Flutter Native Web Terminal (Desktop / Web)
echo   [2] 🌐 Launch Both HTML Trading Dashboards (With Live Server Sync)
echo   [3] 📈 Launch Advance Technical Analysis Terminal (424 Stocks Pro 360)
echo   [4] ⚡ Launch Stock Growth & Selection Analyzer (8-Quarter Fundamentals)
echo   [5] ⚙️  Run 24/7 Cloud Market Engine (Manual Full Sync Quotes & Radar)
echo   [6] 🖥️  Start Live Real-Time Price Server (Port 8765)
echo   [7] 🔇 Run Silent Background Server (No Terminal Window)
echo   [8] 📂 Open Excel Models & Workbooks Folder
echo   [9] 📖 View Master Documentation (README.md)
echo   [0] ❌ Exit
echo.
echo ==============================================================================
set /p choice="Please select an option (0-9): "

if "%choice%"=="1" goto FLUTTER
if "%choice%"=="2" goto BOTH_HTML
if "%choice%"=="3" goto TECH_HTML
if "%choice%"=="4" goto FUNDA_HTML
if "%choice%"=="5" goto ENGINE
if "%choice%"=="6" goto SERVER
if "%choice%"=="7" goto SILENT_SERVER
if "%choice%"=="8" goto OPEN_EXCEL
if "%choice%"=="9" goto VIEW_README
if "%choice%"=="0" exit
echo.
echo Invalid option, please try again.
timeout /t 2 >nul
cls
goto MENU

:FLUTTER
cls
echo [STARTING] Launching Flutter Native Web Terminal...
call "%~dp0launchers\Launch_Flutter_Terminal.bat"
goto MENU

:BOTH_HTML
cls
echo [STARTING] Launching Both HTML Trading Dashboards...
call "%~dp0launchers\Launch_Live_Trading_Dashboards.bat"
goto MENU

:TECH_HTML
cls
echo [STARTING] Launching Advance Technical Analysis Terminal...
call "%~dp0launchers\Start_Technical_Analysis_Terminal.bat"
goto MENU

:FUNDA_HTML
cls
echo [STARTING] Launching Stock Growth & Selection Analyzer...
start "" "%~dp0dashboards\Stock_Growth_and_Selection_Analyzer.html"
goto MENU

:ENGINE
cls
echo [STARTING] Running Cloud Market Engine & Radar Evaluator...
call "%~dp0launchers\Run_Cloud_Market_Engine.bat"
goto MENU

:SERVER
cls
echo [STARTING] Launching Live Price Server on Port 8765...
call "%~dp0launchers\Start_Live_Price_Server.bat"
goto MENU

:SILENT_SERVER
cls
echo [STARTING] Starting Silent Background Daemon...
wscript "%~dp0launchers\Run_24x7_Background_Server.vbs"
echo Server running silently in background.
timeout /t 2 >nul
goto MENU

:OPEN_EXCEL
start "" "%~dp0excel_models"
goto MENU

:VIEW_README
start "" "%~dp0README.md"
goto MENU
