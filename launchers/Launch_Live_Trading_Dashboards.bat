@echo off
title 424 Stocks Live Trading Dashboards Launcher
cd /d "%~dp0.."
echo ======================================================================
echo   🚀 INDIAN EQUITIES & ADVANCED TECHNICAL TERMINAL (PRO 360)
echo ======================================================================
echo.

:: 1. Check if Live Quote Server on Port 8765 is running
netstat -ano | findstr :8765 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [OK] Live Market Quote Server is already active on http://127.0.0.1:8765
) else (
    echo [STARTING] Starting background Live Quote Server on Port 8765...
    start /min "424 Stocks Live Server" cmd /k "python live_price_server.py"
    timeout /t 3 /nobreak >nul
)

:: 2. Launch both Dashboards in user browser
echo.
echo [LAUNCHING] Opening Indian Equities Watchlist Dashboard...
start "" "%~dp0..\dashboards\Stock_Growth_and_Selection_Analyzer.html"

timeout /t 1 /nobreak >nul
echo [LAUNCHING] Opening 424 Stocks Advanced Technical Terminal...
start "" "%~dp0..\dashboards\Advance_Technical_Analysis_424_Stocks.html"

echo.
echo ======================================================================
echo   ✅ Both Dashboards Successfully Launched with Live Server Sync!
echo   • Real-Time Market Ticker Stream: Active (Port 8765)
echo   • Auto-Refresh Cycle: 15-30 seconds
echo   • Live Quotation Feeds: NSE & BSE
echo ======================================================================
echo.
