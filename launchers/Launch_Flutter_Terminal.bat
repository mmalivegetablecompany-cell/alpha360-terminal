@echo off
title 424 Stocks Flutter Native Web Terminal Launcher
cd /d "%~dp0.."
echo ======================================================================
echo   🚀 424 STOCKS FLUTTER TRADING TERMINAL (PRO DESKTOP & WEB)
echo ======================================================================
echo.

:: 1. Check if Live Quote Server on Port 8765 is running
netstat -ano | findstr :8765 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [OK] Live Server is already running on http://127.0.0.1:8765
) else (
    echo [STARTING] Starting background Live Server on Port 8765...
    start /min "424 Stocks Live Server" cmd /k "python live_price_server.py"
    timeout /t 3 /nobreak >nul
)

:: 2. Launch Flutter App in browser
echo.
echo [LAUNCHING] Opening Flutter Native Terminal at http://127.0.0.1:8765/app ...
start "" "http://127.0.0.1:8765/app"

echo.
echo ======================================================================
echo   ✅ Flutter Web Terminal Successfully Launched!
echo   • URL: http://127.0.0.1:8765/app
echo   • Features: 424 Stocks, ⚡ Buy Radar, Real-Time News, Order Filings
echo ======================================================================
echo.
