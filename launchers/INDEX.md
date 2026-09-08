# Launchers Directory Index

This directory contains executable Windows batch (`.bat`) and VBScript (`.vbs`) launchers to start background servers, dashboards, and mobile/web terminals with one click.

---

## 🚀 Launcher Catalog

| Launcher Name | Target | Description |
| :--- | :--- | :--- |
| [`Launch_Flutter_Terminal.bat`](Launch_Flutter_Terminal.bat) | 📱 Flutter Web App | Starts the background server if not already active and launches the Flutter Terminal at `http://127.0.0.1:8765/app`. |
| [`Launch_Live_Trading_Dashboards.bat`](Launch_Live_Trading_Dashboards.bat) | 🌐 Both HTML Dashboards | Starts background server and opens both `Stock_Growth_and_Selection_Analyzer.html` and `Advance_Technical_Analysis_424_Stocks.html`. |
| [`Start_Technical_Analysis_Terminal.bat`](Start_Technical_Analysis_Terminal.bat) | 📈 Technical Terminal | Starts server and launches `Advance_Technical_Analysis_424_Stocks.html`. |
| [`Start_Live_Price_Server.bat`](Start_Live_Price_Server.bat) | 🖥️ REST API Server | Runs `live_price_server.py` in a visible terminal window on Port 8765. |
| [`Run_Cloud_Market_Engine.bat`](Run_Cloud_Market_Engine.bat) | ⚙️ Full Engine Sync | Executes `backend/cloud_market_engine.py` locally for an immediate full market sync, indicator recalculation, and HTML update. |
| [`Refresh_424_Stock_Prices.bat`](Refresh_424_Stock_Prices.bat) | 🔄 Price Refresher | Quick script to refresh live quotes. |
| [`Run_24x7_Background_Server.vbs`](Run_24x7_Background_Server.vbs) | 🔇 Silent Daemon | Launches `live_price_server.py` silently in the background with zero visible command windows. |
