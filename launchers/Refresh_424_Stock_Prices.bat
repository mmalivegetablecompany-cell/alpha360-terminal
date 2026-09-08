@echo off
title 424 Stocks Price Refresher
cd /d "%~dp0.."
echo ======================================================================
echo   🔄 REFRESHING 424 STOCKS LIVE QUOTES
echo ======================================================================
python scripts\refresh_today_prices.py
pause
