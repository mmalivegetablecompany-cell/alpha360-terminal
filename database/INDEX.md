# Database Directory Index

This directory holds the persistent JSON databases and market cache files for all 424 Indian equities.

---

## 📊 File Catalog

| File Name | Format | Description |
| :--- | :---: | :--- |
| [`advanced_technicals_424.json`](advanced_technicals_424.json) | JSON (2.6 MB) | Full 360° technical metrics for all 424 equities: EMAs (20, 50), 200 SMA, 14D RSI, MACD, ATR, Bollinger Bands, Pivot levels, 52W High/Low, and Buy Radar signal blueprints. |
| [`html_424_stocks.json`](html_424_stocks.json) | JSON (4.7 MB) | Master combined fundamental compounding and live quotation dataset for all 424 stocks. |
| [`radar_signals_database.json`](radar_signals_database.json) | JSON (19 KB) | Persistent Buy Radar database containing active auto-tracked trades (including restored positions), historical suggestions archive, and completed performance journal. |
| [`market_technicals_cache.json`](market_technicals_cache.json) | JSON (1.2 MB) | Fast lookup cache storing candlestick records and moving averages for quick terminal reloads. |
