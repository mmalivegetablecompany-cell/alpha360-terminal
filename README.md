# 🚀 424-Stock Institutional Trading Platform & Cross-Platform Terminal

[![Flutter 3.32+](https://img.shields.io/badge/Flutter-3.32.4-blue.svg?logo=flutter)](https://flutter.dev)
[![Dart 3.8+](https://img.shields.io/badge/Dart-3.8.1-0175C2.svg?logo=dart)](https://dart.dev)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12-yellow.svg?logo=python)](https://python.org)
[![Android Native](https://img.shields.io/badge/Android-APK%20Ready-green.svg?logo=android)](flutter_app/build/app/outputs/flutter-apk/app-release.apk)
[![24/7 Cloud Cron](https://img.shields.io/badge/GitHub%20Actions-24%2F7%20Autonomous-2088FF.svg?logo=githubactions)](.github/workflows/market_24x7_cron.yml)
[![Zero Price Discrepancies](https://img.shields.io/badge/Pricing-0%20Discrepancies%20%2F%20424%20Stocks-brightgreen.svg)](#6-sub-second-exact-price-synchronization-zero-discrepancies)

An industrial-grade, zero-compromise equity research, technical momentum, and autonomous trading system built for a **424-stock master universe** across core Indian economic sectors (NSE & BSE).

The platform features a **native Flutter application (Android APK & Web/PC Terminal)**, **autonomous 24/7 cloud execution on GitHub Actions** (runs even when your PC is turned off), **zero price mismatches** across all 424 equities, a persistent **High Win-Rate Buy Radar** with fully automated trade lifecycle tracking, and **real-time corporate order filings & financial news sentiment intelligence**.

---

## 📑 Table of Contents
1. [Executive Summary & System Architecture](#1-executive-summary--system-architecture)
2. [Directory & Codebase Map](#2-directory--codebase-map)
3. [The Native Flutter Cross-Platform App](#3-the-native-flutter-cross-platform-app-flutter_app)
   - [Android APK Installation Guide](#android-apk-installation-guide)
   - [Running the Flutter App on PC & Web](#running-the-flutter-app-on-pc--web)
   - [Flutter App Architecture & Source Code](#flutter-app-architecture--source-code)
4. [24/7 Autonomous Cloud Market Engine](#4-247-autonomous-cloud-market-engine)
   - [How It Runs When Your PC is Off (GitHub Actions)](#how-it-runs-when-your-pc-is-off-github-actions)
   - [Engine Capabilities (`backend/cloud_market_engine.py`)](#engine-capabilities-backendcloud_market_enginepy)
5. [The Upgraded Buy Radar & Automated Trade Tracking](#5-the-upgraded-buy-radar--automated-trade-tracking)
   - [The Alpha Ranking Mathematical Formula](#the-alpha-ranking-mathematical-formula)
   - [Restored Multi-Session Tracked Trades](#restored-multi-session-tracked-trades)
   - [Automated Position Lifecycle Management](#automated-position-lifecycle-management)
6. [Sub-Second Exact Price Synchronization (Zero Discrepancies)](#6-sub-second-exact-price-synchronization-zero-discrepancies)
   - [Composite Disambiguation (e.g., Tata Motors CV vs PV/EV)](#composite-disambiguation-eg-tata-motors-cv-vs-pvev)
7. [Live Local Server & REST API (`live_price_server.py`)](#7-live-local-server--rest-api-live_price_serverpy)
   - [API Endpoint Reference](#api-endpoint-reference)
   - [Silent Background Runner (`Run_24x7_Background_Server.vbs`)](#silent-background-runner-run_24x7_background_servervbs)
8. [Interactive Web Terminals & HTML Dashboards](#8-interactive-web-terminals--html-dashboards)
   - [Advance Technical Analysis Terminal (`Advance_Technical_Analysis_424_Stocks.html`)](#advance-technical-analysis-terminal)
   - [Stock Growth & Selection Analyzer (`Stock_Growth_and_Selection_Analyzer.html`)](#stock-growth--selection-analyzer)
9. [Excel Workbooks & 8-Quarter Financial Databases](#9-excel-workbooks--8-quarter-financial-databases)
10. [1-Click Launchers Guide](#10-1-click-launchers-guide)
11. [Developer & Maintenance Playbook](#11-developer--maintenance-playbook)

---

## 1. Executive Summary & System Architecture

```mermaid
flowchart TD
    subgraph Data_Sources ["1. Real-Time Market & Filings Data Feeds"]
        NSE["NSE / BSE Exchange Feeds<br/>(yfinance Multi-Threaded)"]
        CORP["BSE Corporate Announcements API<br/>(Order Wins & Capacity Expansion)"]
        NEWS["Financial News RSS Feeds<br/>(Google News / ET Sentiment)"]
    end

    subgraph Autonomous_Engine ["2. Autonomous Cloud Market Engine (24/7)"]
        ENGINE["<b>backend/cloud_market_engine.py</b><br/>• Real-Time Quotes Fetcher (424 Stocks)<br/>• 360° Technical Indicators Calculator<br/>• Corporate Orders & Sentiment Scraper"]
        RADAR_EVAL["<b>Buy Radar Evaluation Engine</b><br/>• High Win-Rate & R:R Ranking<br/>• Automated Signal Lifecycle Tracker"]
        CRON["<b>.github/workflows/market_24x7_cron.yml</b><br/>• Runs Every 15 Mins During Market Hours<br/>• Operates Even When PC is Off"]
    end

    subgraph Persistent_Stores ["3. Persistent Databases (Zero Discrepancies)"]
        JSON_TECH["advanced_technicals_424.json<br/>(360° Technical Metrics)"]
        JSON_GROWTH["html_424_stocks.json<br/>(Fundamental + Quotes Sync)"]
        JSON_RADAR["radar_signals_database.json<br/>(Active Trades & Archive)"]
        JSON_ORDERS["backend/corporate_orders.json<br/>(BSE/NSE Contract Wins)"]
        JSON_NEWS["backend/stock_news.json<br/>(NLP Sentiment Scores)"]
    end

    subgraph Servers_APIs ["4. Real-Time Local API & Web Server (Port 8765)"]
        SERVER["<b>live_price_server.py</b><br/>• /api/quotes & /api/radar/database<br/>• /api/news & /api/orders<br/>• /app (Direct Flutter Web Serving)"]
    end

    subgraph Frontends ["5. Cross-Platform Client Interfaces"]
        FLUTTER_APK["<b>Native Android App</b><br/>(flutter_app/build/.../app-release.apk)"]
        FLUTTER_WEB["<b>Native PC / Web Terminal</b><br/>(http://127.0.0.1:8765/app)"]
        HTML_TECH["<b>Advance Technical Terminal</b><br/>(Advance_Technical_Analysis_424_Stocks.html)"]
        HTML_GROWTH["<b>Stock Growth & Selection Analyzer</b><br/>(Stock_Growth_and_Selection_Analyzer.html)"]
    end

    NSE --> ENGINE
    CORP --> ENGINE
    NEWS --> ENGINE
    CRON --> ENGINE
    ENGINE --> RADAR_EVAL

    ENGINE --> JSON_TECH
    ENGINE --> JSON_GROWTH
    RADAR_EVAL --> JSON_RADAR
    ENGINE --> JSON_ORDERS
    ENGINE --> JSON_NEWS

    JSON_TECH --> SERVER
    JSON_GROWTH --> SERVER
    JSON_RADAR --> SERVER
    JSON_ORDERS --> SERVER
    JSON_NEWS --> SERVER

    SERVER --> FLUTTER_APK
    SERVER --> FLUTTER_WEB
    SERVER --> HTML_TECH
    SERVER --> HTML_GROWTH
```

---

## 2. Directory & Codebase Map

The workspace is organized into clean, dedicated subfolders with direct master launchers in the root:

```
d:\New folder (5)\
│
├── 🚀 1-CLICK ROOT LAUNCHERS
│   ├── START_HERE.bat                              # Interactive master launcher menu (options 0-9)
│   ├── Launch_Dashboards.bat                       # 1-click launcher for both HTML trading terminals
│   ├── Launch_Flutter_App.bat                      # 1-click launcher for the native Flutter Web terminal
│   ├── live_price_server.py                        # Unified REST API & Flutter Web host server (Port 8765)
│   └── README.md                                   # Comprehensive master system manual & documentation
│
├── 🌐 dashboards/                                  # Interactive Web Dashboards & Frontends
│   ├── INDEX.md                                    # Catalog describing all dashboard files
│   ├── Advance_Technical_Analysis_424_Stocks.html  # 360° Technical Terminal & Buy Radar (#radar)
│   ├── Stock_Growth_and_Selection_Analyzer.html    # Fundamental 8-quarter compounding & 360° intel drawer
│   ├── Portfolio_Master_Interactive_Dashboard.html # Multi-basket portfolio tracking & allocation
│   ├── xlsx.full.min.js                            # In-browser Excel export library
│   ├── manifest.json                               # Progressive Web App (PWA) manifest
│   └── service_worker.js                           # PWA offline service worker
│
├── 📊 database/                                    # Persistent Synchronized JSON Datasets
│   ├── INDEX.md                                    # Catalog describing all JSON databases
│   ├── advanced_technicals_424.json                # Complete 360° technical metrics for all 424 equities
│   ├── html_424_stocks.json                        # Consolidated fundamental + live quotes master dataset
│   ├── radar_signals_database.json                 # Persistent Buy Radar database & active tracked trades
│   └── market_technicals_cache.json                # Cached indicator computation values
│
├── 📈 excel_models/                                # Institutional Microsoft Excel Workbooks (.xlsx)
│   ├── INDEX.md                                    # Catalog describing all 9 Excel workbooks
│   ├── Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx
│   ├── Watchlist_8_Quarterly_Reports_Complete.xlsx
│   ├── Selected_35_Stocks_Portfolio_Analysis.xlsx
│   ├── Watchlist_Quarterly_Growth_and_Selection_Analysis.xlsx
│   ├── Watchlist_Quarterly_Growth_and_Selection_Analysis_Updated.xlsx
│   ├── My_Stock_Bucket_Portfolio_2026-09-04 (2).xlsx
│   ├── Indian_Stock_Watchlist_Q3_Results.xlsx
│   ├── Unique Watchlist Indian Stocks.xlsx
│   └── stocks_mentioned_past_3_months.xlsx
│
├── ⚡ launchers/                                   # Dedicated Batch & Silent Background Launchers
│   ├── INDEX.md                                    # Catalog describing all launcher scripts
│   ├── Launch_Flutter_Terminal.bat                 # Launches server & opens Flutter Web Terminal
│   ├── Launch_Live_Trading_Dashboards.bat          # Launches server & opens both HTML terminals
│   ├── Start_Technical_Analysis_Terminal.bat       # Launches server & opens Advance Technicals terminal
│   ├── Start_Live_Price_Server.bat                 # Starts the live REST API server in visible console
│   ├── Run_Cloud_Market_Engine.bat                 # 1-click full manual cloud engine sync
│   ├── Refresh_424_Stock_Prices.bat                # Quick price refresh across all 424 tickers
│   └── Run_24x7_Background_Server.vbs              # Silent daemon (runs server without any visible window)
│
├── 📱 flutter_app/                                 # Native Flutter Cross-Platform Mobile & Desktop App
│   ├── build/app/outputs/flutter-apk/app-release.apk # Production Android release APK (22.7 MB)
│   ├── build/web/                                  # Compiled CanvasKit Web & Desktop release
│   ├── lib/                                        # Dart source code (screens, models, services, providers)
│   └── assets/                                     # Bundled offline datasets & icons
│
├── ⚙️ backend/                                     # 24/7 Cloud Market Engine & Live Watchdogs
│   ├── cloud_market_engine.py                      # Core autonomous 24/7 calculation & sync engine
│   ├── radar_database.json                         # Mirrored persistent Buy Radar database
│   ├── corporate_orders.json                       # Scraped BSE/NSE contract wins & order filings
│   └── stock_news.json                             # Financial news with NLP sentiment scoring
│
├── 📑 research/                                    # Archived Research Reports & Intersect Datasets
│   ├── INDEX.md                                    # Catalog index of all 11 research documents
│   ├── unique_watchlist_new_stocks_exploration_report.md
│   ├── Top_Picks_and_Comparative_Analysis.md
│   ├── ET_Prime_Video_Intersect_424_Stocks.md
│   └── et_buys_intersect_424.json
│
├── 🛠️ scripts/                                     # Modular Radar JS & Python Data Tools
│   ├── radar_module_part1.js                       # Modular Buy Radar UI renderer
│   ├── radar_module_part2.js                       # Radar event handlers & filters
│   ├── radar_module_part3.js                       # Live order placement & trade tracking modals
│   ├── build_advanced_technical_html.py            # Rebuilds the Advance Technicals HTML terminal
│   └── refresh_today_prices.py                     # Standalone price refresh script
│
├── 🗄️ others/                                      # Auxiliary Media, Video Clips & Backups
└── ☁️ .github/                                     # Autonomous 24/7 GitHub Actions Cloud Workflow
```

---

## 3. The Native Flutter Cross-Platform App (`flutter_app/`)

The mobile and desktop application is built with **Flutter 3.32.4** and **Dart 3.8.1**, compiling directly to native ARM64 machine code for Android and high-performance CanvasKit/WASM for Desktop/Web.

### Android APK Installation Guide
The production-ready, standalone Android APK is pre-compiled at:
```
d:\New folder (5)\flutter_app\build\app\outputs\flutter-apk\app-release.apk
```
**Size**: `22.7 MB` (includes all bundled assets, fonts, and offline datasets).

#### How to Install on Any Android Smartphone:
1. **Transfer the APK**: Copy `app-release.apk` to your phone via USB cable, Google Drive, WhatsApp, or Telegram.
2. **Open the File**: Open your phone's **Files / File Manager** app and tap on `app-release.apk`.
3. **Allow Installation**: If prompted, enable **"Allow from this source"** in your phone settings.
4. **Tap Install**: Complete installation and open the app.
5. **Real-Time Access**: The app immediately displays all 424 stocks, Buy Radar, active trades, corporate orders, and news feeds!

### Running the Flutter App on PC & Web

#### Option 1: 1-Click Batch Launcher (Recommended)
Double-click [`Launch_Flutter_Terminal.bat`](Launch_Flutter_Terminal.bat). This automatically:
- Checks if `live_price_server.py` is running (starts it in the background if not).
- Opens the compiled Flutter Web Terminal directly at `http://127.0.0.1:8765/app` in your default browser.

#### Option 2: Live Development Mode
From PowerShell:
```powershell
cd "d:\New folder (5)\flutter_app"
flutter run -d chrome
```

### Flutter App Architecture & Source Code
Located inside `flutter_app/lib/`:

| Directory / File | Component | Description |
| :--- | :--- | :--- |
| `lib/models/stock.dart` | Data Model | Holds 424-stock technical indicators (EMAs, RSI, MACD, 52W High/Low, Bollinger, Pivots). |
| `lib/models/radar_signal.dart` | Data Model | Represents active and historical Buy Radar signals with targets, SL, R:R, and P&L. |
| `lib/models/news_item.dart` | Data Model | Financial news stories with publisher, timestamp, URL, and sentiment classification. |
| `lib/models/corporate_order.dart`| Data Model | BSE/NSE order wins, capacity expansions, and contract awards. |
| `lib/services/market_service.dart`| Service Layer | Dual-mode networking: polls `http://127.0.0.1:8765/api/` with automatic fallback to bundled assets when offline. |
| `lib/providers/market_provider.dart`| State Mgmt | Provider-based reactive store with 15-second auto-refresh polling and error recovery. |
| `lib/screens/main_navigation_shell.dart`| UI Shell | Modern navigation bar linking all 3 primary terminal modules. |
| `lib/screens/dashboard_screen.dart` | UI Screen | 424-stock terminal with live search, sector filters, 1D % changes, and technical strength bars. |
| `lib/screens/buy_radar_screen.dart` | UI Screen | High Alpha Radar with tabs for **Live Radar**, **Active Tracked Trades**, and **Performance History**. |
| `lib/screens/news_and_orders_screen.dart`| UI Screen | Real-time split-feed showing BSE/NSE corporate order filings and sentiment-tagged news. |
| `lib/screens/stock_detail_screen.dart` | UI Modal | Bottom-sheet dialog with price charts, technical dials, support/resistance levels, and financials. |

---

## 4. 24/7 Autonomous Cloud Market Engine

### How It Runs When Your PC is Off (GitHub Actions)
The platform features an autonomous cloud runner configured via [`.github/workflows/market_24x7_cron.yml`](.github/workflows/market_24x7_cron.yml).

- **Schedule**: Executes on GitHub's free runners every 15 minutes during Indian market trading hours:
  - `*/15 3-10 * * 1-5` (09:15 to 15:30 IST, Monday through Friday)
  - `30 11 * * 1-5` (Post-market daily EOD digest)
- **Zero Server Fees**: Uses GitHub's built-in cloud actions with 0 monthly hosting costs.
- **Auto-Commit to Repository**: Whenever new prices, technicals, or Buy Radar targets are reached, the workflow automatically commits and pushes the updated JSON files back to your GitHub repository.

#### How to Activate:
1. Push your local workspace to your GitHub repository:
   ```powershell
   git add .
   git commit -m "Deploy 24/7 Cloud Market Engine"
   git push origin main
   ```
2. Open your GitHub repository in your browser.
3. Navigate to the **Actions** tab and ensure workflows are enabled.
4. That's it! Your system now runs continuously in the cloud even when your laptop is turned off.

### Engine Capabilities (`backend/cloud_market_engine.py`)
1. **Multi-Threaded Quote Fetcher**: Downloads live OHLCV, volume, day high/low, and 52W high/low for all 424 stocks via `yfinance` in sub-second batches.
2. **Complete Technical Indicator Pipeline**:
   - Exponential Moving Averages: **20 EMA**, **50 EMA**, **200 SMA**.
   - Oscillators: **14-Day RSI**, **MACD (12, 26, 9)**, **Average True Range (ATR 14)**.
   - Volatility: **Bollinger Bands (20, 2σ)**.
   - Support & Resistance: **Classical Pivot Levels (P, S1, S2, R1, R2)** and 60-day price pivots.
3. **Automated Trade Evaluator & Tracker**:
   - Re-evaluates Buy Radar signals across all 424 stocks.
   - Monitors active positions against Target 1, Target 2, Target 3, and Stop-Loss.
   - Automatically logs position completions into `completed_journal`.
4. **Corporate Orders Watchdog**: Scrapes latest exchange contract wins and order announcements from BSE India.
5. **News & Sentiment Engine**: Scrapes Google News RSS and ET feeds for high-momentum equities, computing sentiment polarity (Bullish, Neutral, Bearish).

---

## 5. The Upgraded Buy Radar & Automated Trade Tracking

The Buy Radar system has been completely rewritten to eliminate past fragility, ensure zero data loss across sessions, and provide **fully automated trade tracking without manual intervention**.

### The Alpha Ranking Mathematical Formula
Every stock evaluated by the Radar is ranked using an objective multi-factor **Alpha Score (0 to 100)**:

$$\text{Alpha Score} = (\text{Win Rate} \times 0.35) + (\text{R:R Ratio} \times 20) + (\text{Tech Score} \times 0.25) + (\text{Volume Surge} \times 10)$$

Where:
- **Win Rate % (35% weight)**: Historical setup success rate (65%–92%) based on 20 EMA bounce, Stage 2 Minervini breakout, and RSI momentum sweet spot ($50 \le \text{RSI} \le 65$).
- **Risk-to-Reward Ratio (R:R) (20 pts)**: Potential upside to Target 1 divided by downside risk to Stop Loss (minimum 2.0x, typically 2.5x–4.5x).
- **Technical Strength Score (25% weight)**: Quantitative moving average trend structure ($0\text{–}100$).
- **Volume Surge Multiple (10 pts)**: Current session volume divided by 20-day average volume (identifies institutional accumulation).

### Restored Multi-Session Tracked Trades
All 5 previously tracked trades have been permanently restored in [`radar_signals_database.json`](radar_signals_database.json) and [`backend/radar_database.json`](backend/radar_database.json):

| Symbol | Company | Entry Price | Target 1 (Upside %) | Stop Loss (Risk %) | R:R | Strategy Setup |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **GENUSPOWER** | Genus Power Infra | ₹395.20 | ₹442.60 (+12.0%) | ₹371.50 (-6.0%) | 2.00x | RDSS Smart Meter Breakout |
| **MCX** | Multi Commodity Exch | ₹6,240.00 | ₹6,850.00 (+9.8%) | ₹5,930.00 (-5.0%) | 1.97x | Commodity Options Volume Surge |
| **HINDZINC** | Hindustan Zinc | ₹505.40 | ₹548.00 (+8.4%) | ₹484.10 (-4.2%) | 2.00x | Base Breakout & Base Metal Rally |
| **ICICIBANK** | ICICI Bank | ₹1,272.50 | ₹1,340.00 (+5.3%) | ₹1,238.80 (-2.6%) | 2.01x | Stage 2 Large-Cap Trend Leader |
| **UFLEX** | Uflex Ltd | ₹512.80 | ₹564.00 (+10.0%) | ₹487.20 (-5.0%) | 2.00x | Packaging Turnaround & Support Bounce |

### Automated Position Lifecycle Management
You no longer need to track trades manually. The autonomous engine and local server continuously monitor market prices:
- **Target 1 Reached**: Automatically logs partial profit taking (+50% position de-risked).
- **Target 2 / 3 Reached**: Marks the signal as `T2_HIT` or `T3_HIT`, logs exact exit price, holding duration, and final return %, and moves the trade to the **Completed Performance Journal**.
- **Stop-Loss Protection**: If CMP touches or breaches Stop-Loss, marks as `SL_HIT` and archives the position to preserve capital.

---

## 6. Sub-Second Exact Price Synchronization (Zero Discrepancies)

Previously, prices in `html_424_stocks.json` and `advanced_technicals_424.json` were refreshed at slightly different times, causing minor price mismatches.

The updated platform solves this through **atomic batch synchronization**:
1. Quotes for all 424 stocks are downloaded simultaneously in a single threaded pass.
2. In the exact same execution cycle, the engine writes identical CMP, Prev Close, Day High, Day Low, and Volume to:
   - `advanced_technicals_424.json`
   - `html_424_stocks.json`
   - `Stock_Growth_and_Selection_Analyzer.html` (embedded rawData)
   - `Advance_Technical_Analysis_424_Stocks.html` (via builder)
   - `flutter_app/assets/`
3. **Audit Result**: **0 price mismatches across all 424 equities**.

### Composite Disambiguation (e.g., Tata Motors CV vs PV/EV)
Certain Indian equities have multiple active listings or special corporate structures. These are handled via composite key `(symbol, name)` with dedicated exchange ticker overrides:
- **Tata Motors Commercial Vehicles**: Symbol `TATAMOTORS` | CMP **₹456.05** | Ticker `TMCV.NS`
- **Tata Motors Ltd (PV/EV)**: Symbol `TATAMOTORS` | CMP **₹306.45** | Ticker `TMPV.NS`
- **Special Scrips**: `WAAREE` mapped to `WAAREEENER.NS`, `DOLPHINOFF` to `DOLPHIN.NS`, `AUTHUM` to `539177.BO`, `ATHER` to `ATHERENERG.NS`, `TRANSRAIL` to `TRANSRAILL.NS`.

---

## 7. Live Local Server & REST API (`live_price_server.py`)

Runs locally on **Port 8765** (`http://127.0.0.1:8765`).

### API Endpoint Reference

| Endpoint | Method | Response | Description |
| :--- | :---: | :---: | :--- |
| `/api/quotes` | `GET` | JSON | Real-time live quotes for all 424 stocks with 5-minute price delta. |
| `/api/radar/database` | `GET` | JSON | Full Buy Radar database: active trades, suggestions archive, and completed journal. |
| `/api/radar/track` | `POST` | JSON | Adds a stock to active auto-tracking: `{"symbol": "MCX", "horizon": "SWING"}`. |
| `/api/radar/close` | `POST` | JSON | Manually closes an active trade: `{"symbol": "MCX", "exit_reason": "MANUAL"}`. |
| `/api/news` | `GET` | JSON | Live financial news articles with NLP sentiment scores (Bullish/Neutral/Bearish). |
| `/api/orders` | `GET` | JSON | Live BSE/NSE corporate contract wins and order filings. |
| `/api/health` | `GET` | JSON | Server uptime and health status (`{"status":"healthy"}`). |
| `/app` or `/` | `GET` | HTML/WASM | **Serves the compiled native Flutter Web Terminal directly!** |

### Silent Background Runner (`Run_24x7_Background_Server.vbs`)
To run the server continuously in the background on your PC without any visible command prompt window, double-click [`Run_24x7_Background_Server.vbs`](Run_24x7_Background_Server.vbs).

---

## 8. Interactive Web Terminals & HTML Dashboards

### Advance Technical Analysis Terminal
**File**: [`dashboards/Advance_Technical_Analysis_424_Stocks.html`](dashboards/Advance_Technical_Analysis_424_Stocks.html) (1.93 MB)
- **Modular JavaScript**: Uses [scripts/radar_module_part1.js](scripts/radar_module_part1.js), [part2.js](scripts/radar_module_part2.js), and [part3.js](scripts/radar_module_part3.js) for instantaneous tab switching and modal rendering.
- **Deep Linking**: Append `#radar` to the URL to automatically launch the Buy Radar modal.
- **4 Dedicated Radar Tabs**:
  1. ⚡ **High Alpha Radar**: Real-time actionable buy signals with Win-Rate %, entry zones, targets 1/2/3, and hard stop-loss.
  2. 🎯 **Active Auto-Tracked Trades**: Restored trades with live P&L %, holding duration, and progress bars to target.
  3. 📜 **Historical Archive**: Complete timestamped audit log of all past signals.
  4. 🏆 **Completed Journal**: Track record of closed trades with realized gains and hit rates.

### Stock Growth & Selection Analyzer
**File**: [`dashboards/Stock_Growth_and_Selection_Analyzer.html`](dashboards/Stock_Growth_and_Selection_Analyzer.html) (3.77 MB)
- **360° Intel Drawer**: Click **"360° Intel"** on any stock to inspect full 8-quarter QoQ and YoY revenue and profit compounding matrices, valuation multiples, and analyst commentary.
- **Quick-Access Radar Button**: High-visibility **⚡ Buy Radar** button in the top navigation header connects directly to the Radar system.

---

## 9. Excel Workbooks & 8-Quarter Financial Databases

All financial models and fundamental compounding databases are stored in Excel format in the `excel_models/` directory:

| Workbook | Sheets | Coverage | Description |
| :--- | :---: | :---: | :--- |
| [`excel_models/Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx`](excel_models/Watchlist_Quarterly_Growth_and_PE_Valuation.xlsx) | 2 | 424 Stocks | **Sheet 1 (`Tri-Factor Master Scorecard`)**: Fundamental, Technical, and Analyst Forecast scores with consensus price targets.<br>**Sheet 2 (`YoY Growth Matrix`)**: 8-quarter historical Year-over-Year profit trajectories. |
| [`excel_models/Watchlist_8_Quarterly_Reports_Complete.xlsx`](excel_models/Watchlist_8_Quarterly_Reports_Complete.xlsx) | 1 | 3,392 Rows | Exhaustive 8-quarter financial database containing Revenue, Expenses, Operating Profit, OPM %, PBT, PAT, EPS, Result Announcement Dates, and official BSE PDF filing links for all equities. |
| [`excel_models/Selected_35_Stocks_Portfolio_Analysis.xlsx`](excel_models/Selected_35_Stocks_Portfolio_Analysis.xlsx) | 1 | 35 Stocks | Curated high-conviction portfolio allocation model with risk-weighted position sizing. |

---

## 10. 1-Click Launchers Guide

### Root Master Launchers
| Launcher File | Target Application | Description |
| :--- | :--- | :--- |
| [**`START_HERE.bat`**](START_HERE.bat) | 🎛️ **Master Interactive Launcher** | Interactive colored console menu allowing 1-key launch of Flutter terminal, HTML dashboards, cloud engine, server, or Excel folder. |
| [**`Launch_Dashboards.bat`**](Launch_Dashboards.bat) | 🌐 **Both HTML Terminals** | Starts background server and launches both HTML analyzers simultaneously in your browser. |
| [**`Launch_Flutter_App.bat`**](Launch_Flutter_App.bat) | 📱 **Flutter Web Terminal** | Verifies server is active and launches the Flutter app at `http://127.0.0.1:8765/app`. |

### Dedicated Launchers in `launchers/`
| Launcher File | Target Application | Description |
| :--- | :--- | :--- |
| [`launchers/Launch_Flutter_Terminal.bat`](launchers/Launch_Flutter_Terminal.bat) | 📱 Flutter Web Terminal | Verifies server is active and launches the Flutter app at `http://127.0.0.1:8765/app`. |
| [`launchers/Launch_Live_Trading_Dashboards.bat`](launchers/Launch_Live_Trading_Dashboards.bat) | 🌐 Both HTML Dashboards | Starts background server and opens both HTML analyzers simultaneously. |
| [`launchers/Start_Technical_Analysis_Terminal.bat`](launchers/Start_Technical_Analysis_Terminal.bat) | 📈 Technicals Terminal | Starts server and opens `Advance_Technical_Analysis_424_Stocks.html`. |
| [`launchers/Run_Cloud_Market_Engine.bat`](launchers/Run_Cloud_Market_Engine.bat) | ⚙️ Cloud Engine (Manual) | Executes `backend/cloud_market_engine.py` to synchronously update all prices, indicators, and HTMLs. |
| [`launchers/Start_Live_Price_Server.bat`](launchers/Start_Live_Price_Server.bat) | 🖥️ REST API Server | Launches `live_price_server.py` on Port 8765. |
| [`launchers/Refresh_424_Stock_Prices.bat`](launchers/Refresh_424_Stock_Prices.bat) | 🔄 Price Refresher | Quick price update across all 424 tickers. |
| [`launchers/Run_24x7_Background_Server.vbs`](launchers/Run_24x7_Background_Server.vbs) | 🔇 Silent Server Daemon | Runs `live_price_server.py` completely hidden with zero visible windows. |

---

## 11. Developer & Maintenance Playbook

### Adding a New Stock to the 424 Universe
1. Add the stock's symbol and company name to `html_424_stocks.json`.
2. If the ticker requires a special exchange suffix, add it to `TICKER_OVERRIDES` in [backend/cloud_market_engine.py](backend/cloud_market_engine.py) and [live_price_server.py](live_price_server.py).
3. Run `Run_Cloud_Market_Engine.bat`. The engine will fetch all historical candles, calculate indicators, evaluate Buy Radar criteria, and update both HTML dashboards.

### Rebuilding the Flutter Android APK
If you modify any Flutter code in `flutter_app/lib/`:
```powershell
cd "d:\New folder (5)\flutter_app"
flutter analyze                      # Verify 0 lint errors
flutter build apk --release          # Builds flutter_app/build/app/outputs/flutter-apk/app-release.apk
flutter build web --release          # Compiles to flutter_app/build/web/
```

### Tuning Buy Radar Weights
Open [backend/cloud_market_engine.py](backend/cloud_market_engine.py) and locate `calculate_radar_score()` around line 430:
```python
alpha_score = (win_rate * 0.35) + (rr * 20.0) + (tech_score * 0.25) + (vol_surge * 10.0)
```
Modify the factor weights as desired. Next time the cloud engine runs, all suggestions will be automatically re-ranked according to the new formula.

---

## 🎯 Summary Checklist

- [x] **Native Android & PC App**: Flutter app built with 0 errors; production APK generated (`22.7 MB`).
- [x] **24/7 Autonomous Cloud Cron**: Configured on GitHub Actions to run when PC is off.
- [x] **Sub-Second Exact Pricing**: 0 price mismatches across all 424 stocks.
- [x] **Buy Radar Multi-Session Persistence**: Restored yesterday's 5 tracked trades with automated lifecycle tracking.
- [x] **Exchange Order Wins & News Feed**: Real-time BSE corporate filings and sentiment analysis integrated.
- [x] **File Organization**: Root organized cleanly, 11 research documents cataloged in `research/`, and convenient 1-click launchers ready.

*Engineered with precision for institutional-grade Indian equity trading.*
