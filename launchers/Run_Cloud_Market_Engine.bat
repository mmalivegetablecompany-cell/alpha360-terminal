@echo off
title 424 Stocks Cloud Market Engine (Manual Run)
cd /d "%~dp0.."
echo ======================================================================
echo   🚀 RUNNING 424 STOCKS CLOUD MARKET ENGINE & SYNCHRONIZER
echo ======================================================================
echo.
echo Fetching latest market quotes, updating technicals, evaluating radar,
echo scraping corporate orders, and synchronizing HTML terminals...
echo.

python backend\cloud_market_engine.py

echo.
echo ======================================================================
echo   ✅ Engine Execution Completed!
echo ======================================================================
pause
