@echo off
title 424 Stocks Advanced Technical Terminal Launcher
cd /d "%~dp0.."
echo ======================================================================
echo   🚀 424 STOCKS ADVANCED TECHNICAL ANALYSIS TERMINAL (PRO 360°)
echo ======================================================================
echo.

:: Check if port 8765 is already listening
netstat -ano | findstr :8765 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [OK] Live Quote Server is already active on http://127.0.0.1:8765
) else (
    echo [STARTING] Starting background Live Quote Server on Port 8765...
    start /min "424 Stocks Live Server" cmd /k "python live_price_server.py"
    timeout /t 2 /nobreak >nul
)

echo.
echo [LAUNCHING] Opening Advance_Technical_Analysis_424_Stocks.html in your browser...
start "" "%~dp0..\dashboards\Advance_Technical_Analysis_424_Stocks.html"

echo.
echo ======================================================================
echo   ✅ Terminal Successfully Launched!
echo ======================================================================
echo.
