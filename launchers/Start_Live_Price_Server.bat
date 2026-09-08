@echo off
title 424 Stocks Live Price Server (Port 8765)
cd /d "%~dp0.."
echo ======================================================================
echo   🚀 STARTING 424 STOCKS REAL-TIME REST API SERVER (PORT 8765)
echo ======================================================================
echo.
python live_price_server.py
pause
