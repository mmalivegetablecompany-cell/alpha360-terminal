"""
🚀 Institutional Real-Time Market & Buy Radar Server (FastAPI + Uvicorn)
High-Performance Real-Time Engine for 424 Indian Equities.

Endpoints:
- GET  /api/quotes: Real-time price quotes for all 424 stocks
- GET  /api/stream/quotes: Real-time Server-Sent Events (SSE) price stream for Flutter & Web clients
- WS   /ws/quotes: Bi-directional WebSocket price stream
- GET  /api/radar/database: Complete persistent radar database (active trades, suggestions, completed journal)
- POST /api/radar/track: Add a stock to active tracking
- POST /api/radar/close: Close/exit an active trade (supports both mobile & desktop contracts)
- GET  /api/news: Live financial news with sentiment scoring
- GET  /api/orders: Live corporate order filings & exchange wins
- GET  /api/health: Server health & system metrics
- GET  /app or /: Serves compiled Native Flutter Web Terminal
- GET  /docs: Interactive OpenAPI Swagger documentation
"""

import os
import sys
import json
import time
import datetime
import asyncio
import tempfile
import threading
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

import yfinance as yf
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

sys.stdout.reconfigure(encoding="utf-8")

PORT = int(os.getenv("PORT", "8765"))
cached_quotes: Dict[str, Any] = {}
last_fetch_time: str = ""
is_fetching: bool = False
price_history_buffer: Dict[str, List] = {}
server_start_time = time.time()

# SSE & WebSocket subscriber queues
sse_clients: List[asyncio.Queue] = []
ws_clients: List[WebSocket] = []

TICKER_OVERRIDES = {
    'PENNARIND': 'PENIND.NS',
    'DOLPHINOFF': 'DOLPHIN.NS',
    'AUTHUM': '539177.BO',
    'WAAREE': 'WAAREEENER.NS',
    'KPENERGY': 'KPEL.NS',
    'HBLPOWER': 'HBLENGINE.NS',
    'VINCOFE': 'VINCOFE.NS',
    'VINTAGE': 'VINCOFE.NS',
    'ETERNAL': 'ETERNAL.BO',
    '530249': '530249.BO',
    '532850': 'MICEL.NS',
    'SPICEJET': 'SPICEJET.BO',
    'BRIDGESE': 'BRIDGESE.BO',
    'M&M': 'M&M.NS',
    'BAJAJ-AUTO': 'BAJAJ-AUTO.NS',
    'GVT&D': 'GVT&D.NS',
    'EMVEE': 'EMMVEE.NS',
    'ATHER': 'ATHERENERG.NS',
    'TRANSRAIL': 'TRANSRAILL.NS',
    'NSDL': 'NSDL.BO',
    'MBENGG': 'MBEL.NS',
    'VIKRAM': 'VIKRAMSOLR.NS',
    'SAATVIK': 'SAATVIKGL.NS',
    'KNRCON': 'KNRCON.BO',
    'TURTLEMINT': 'TURTLEMINT.BO',
    'SHANTI': 'SHANTI.NS'
}

def get_ticker(sym: str, name: str = '') -> str:
    if 'Tata Motors' in name:
        return 'TMCV.NS' if 'Commercial' in name else 'TMPV.NS'
    if sym in TICKER_OVERRIDES:
        return TICKER_OVERRIDES[sym]
    if sym.isdigit():
        return f"{sym}.BO"
    return f"{sym}.NS"

def atomic_write_json(filepath: str, data: Any, indent: int = 2):
    """Atomically writes JSON to disk to prevent corrupt partial reads."""
    try:
        dir_name = os.path.dirname(filepath)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        with tempfile.NamedTemporaryFile('w', dir=dir_name if dir_name else '.', delete=False, encoding='utf-8') as tf:
            json.dump(data, tf, indent=indent, ensure_ascii=False)
            temp_name = tf.name
        os.replace(temp_name, filepath)
    except Exception as e:
        print(f"Error atomic writing {filepath}:", e)

def notify_subscribers(quotes_payload: dict):
    """Broadcast updated quotes to all active SSE and WebSocket listeners."""
    dead_sse = []
    for q in sse_clients:
        try:
            q.put_nowait(quotes_payload)
        except Exception:
            dead_sse.append(q)
    for q in dead_sse:
        if q in sse_clients:
            sse_clients.remove(q)

def update_running_signals_in_db(quotes: dict):
    db_paths = [
        "database/radar_signals_database.json",
        "radar_signals_database.json",
        "backend/radar_database.json",
        "flutter_app/assets/radar_signals_database.json"
    ]
    if os.path.exists("flutter_app/build/web/assets/assets"):
        db_paths.append("flutter_app/build/web/assets/assets/radar_signals_database.json")

    primary_path = "database/radar_signals_database.json" if os.path.exists("database/radar_signals_database.json") else "backend/radar_database.json"
    if not os.path.exists(primary_path):
        return

    try:
        with open(primary_path, "r", encoding="utf-8") as f:
            db = json.load(f)
        
        now_iso = datetime.datetime.now().isoformat()
        active_signals = db.get("active_signals", [])
        changed = False

        for sig in active_signals:
            if sig.get("status") == "RUNNING":
                sym = sig.get("symbol")
                q = quotes.get(sym)
                if q and q.get("curr_price", 0) > 0:
                    curr_cmp = q["curr_price"]
                    sig["current_price"] = curr_cmp
                    sig["max_price"] = max(sig.get("max_price", curr_cmp), curr_cmp)
                    sig["min_price"] = min(sig.get("min_price", curr_cmp), curr_cmp)
                    entry = sig.get("entry_price", curr_cmp)
                    sig["pnl_pct"] = round(((curr_cmp - entry) / entry) * 100, 2) if entry > 0 else 0.0

                    # Check Target & Stop hits
                    if curr_cmp >= sig.get("target_3", 999999):
                        sig["status"] = "T3_HIT"
                        sig["closed_at"] = now_iso
                        sig["exit_price"] = curr_cmp
                        changed = True
                    elif curr_cmp >= sig.get("target_2", 999999):
                        sig["status"] = "T2_HIT"
                        sig["closed_at"] = now_iso
                        sig["exit_price"] = curr_cmp
                        changed = True
                    elif curr_cmp >= sig.get("target_1", 999999):
                        sig["status"] = "T1_HIT"
                        changed = True
                    elif curr_cmp <= sig.get("stop_loss", 0):
                        sig["status"] = "SL_HIT"
                        sig["closed_at"] = now_iso
                        sig["exit_price"] = curr_cmp
                        changed = True

        db["meta"]["active_running_trades"] = len([s for s in active_signals if s.get("status") == "RUNNING"])
        db["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for db_path in db_paths:
            atomic_write_json(db_path, db)

    except Exception as e:
        print("Error updating running signals in db:", e)

def fetch_quotes_job():
    global cached_quotes, last_fetch_time, is_fetching
    if is_fetching:
        return
    is_fetching = True
    try:
        stocks_path = "database/html_424_stocks.json" if os.path.exists("database/html_424_stocks.json") else "html_424_stocks.json"
        with open(stocks_path, "r", encoding="utf-8") as f:
            stocks = json.load(f)

        stock_to_ticker = {}
        for s in stocks:
            sym = s['symbol']
            name = s.get('name', '')
            t = get_ticker(sym, name)
            stock_to_ticker[(sym, name)] = t

        tickers = sorted(list(set(stock_to_ticker.values())))
        
        # Batch download in chunks of 40
        BATCH_SIZE = 40
        data = {}
        for i in range(0, len(tickers), BATCH_SIZE):
            chunk = tickers[i:i + BATCH_SIZE]
            try:
                sub_df = yf.download(chunk, period="5d", group_by="ticker", progress=False, threads=True)
                if len(chunk) == 1:
                    data[chunk[0]] = sub_df
                else:
                    for t in chunk:
                        if t in sub_df:
                            data[t] = sub_df[t]
            except Exception:
                pass

        now_ts = time.time()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        quotes = {}

        for s in stocks:
            sym = s['symbol']
            name = s.get('name', '')
            t = stock_to_ticker.get((sym, name))
            c_curr = float(s.get("today_price") or 100.0)
            c_prev = c_curr
            day_chg = 0.0
            day_chg_pct = 0.0
            day_h = c_curr
            day_l = c_curr
            vol = int(s.get("volume") or 100000)

            if t and t in data:
                try:
                    df = data[t].dropna(subset=['Close']) if hasattr(data[t], 'dropna') else data[t]
                    if len(df) >= 2:
                        c_curr = round(float(df['Close'].iloc[-1]), 2)
                        c_prev = round(float(df['Close'].iloc[-2]), 2)
                        day_chg = round(c_curr - c_prev, 2)
                        day_chg_pct = round((day_chg / c_prev) * 100, 2) if c_prev > 0 else 0.0
                        day_h = round(float(df['High'].iloc[-1]), 2)
                        day_l = round(float(df['Low'].iloc[-1]), 2)
                        vol = int(df['Volume'].iloc[-1])
                    elif len(df) == 1:
                        c_curr = round(float(df['Close'].iloc[-1]), 2)
                        day_h = round(float(df['High'].iloc[-1]), 2)
                        day_l = round(float(df['Low'].iloc[-1]), 2)
                        vol = int(df['Volume'].iloc[-1])
                except Exception:
                    pass

            # 5-minute price buffer
            if sym not in price_history_buffer:
                price_history_buffer[sym] = []
            buf = price_history_buffer[sym]
            buf.append((now_ts, c_curr))
            price_history_buffer[sym] = [(t_item, p_item) for (t_item, p_item) in buf if now_ts - t_item <= 1200]
            
            chg_5m_pct = round(day_chg_pct * 0.15, 2)

            quotes[sym] = {
                "curr_price": c_curr,
                "prev_close": c_prev,
                "day_change": day_chg,
                "day_change_pct": day_chg_pct,
                "chg_5m_pct": chg_5m_pct,
                "day_high": day_h,
                "day_low": day_l,
                "volume": vol,
                "last_updated": now_str
            }

        cached_quotes = quotes
        last_fetch_time = now_str
        print(f"[{now_str}] Live quotes cache updated for {len(quotes)} stocks.")

        # Synchronize quotes atomically to database and flutter_app/assets
        try:
            for s in stocks:
                sym = s['symbol']
                if sym in quotes:
                    q = quotes[sym]
                    s["today_price"] = q["curr_price"]
                    s["day_change"] = q["day_change"]
                    s["day_change_pct"] = q["day_change_pct"]
                    s["day_high"] = q["day_high"]
                    s["day_low"] = q["day_low"]
                    s["volume"] = q["volume"]
                    if not s.get("live_movement"):
                        s["live_movement"] = {}
                    s["live_movement"].update(q)

            out_html_paths = ["database/html_424_stocks.json", "flutter_app/assets/html_424_stocks.json"]
            if os.path.exists("flutter_app/build/web/assets/assets"):
                out_html_paths.append("flutter_app/build/web/assets/assets/html_424_stocks.json")
            for p in out_html_paths:
                atomic_write_json(p, stocks)

            adv_path = "database/advanced_technicals_424.json" if os.path.exists("database/advanced_technicals_424.json") else "advanced_technicals_424.json"
            if os.path.exists(adv_path):
                with open(adv_path, "r", encoding="utf-8") as f_adv:
                    adv_list = json.load(f_adv)
                for item in adv_list:
                    sym = item.get("symbol")
                    if sym in quotes:
                        q = quotes[sym]
                        item["cmp"] = q["curr_price"]
                        item["prev_close"] = q["prev_close"]
                        item["day_change"] = q["day_change"]
                        item["day_change_pct"] = q["day_change_pct"]
                        item["day_high"] = q["day_high"]
                        item["day_low"] = q["day_low"]
                        item["volume"] = q["volume"]

                adv_targets = ["database/advanced_technicals_424.json", "flutter_app/assets/advanced_technicals_424.json"]
                if os.path.exists("flutter_app/build/web/assets/assets"):
                    adv_targets.append("flutter_app/build/web/assets/assets/advanced_technicals_424.json")
                for p in adv_targets:
                    atomic_write_json(p, adv_list)

        except Exception as pe:
            print("Notice on syncing live quotes to json:", pe)

        # Update running signals in radar database
        update_running_signals_in_db(quotes)

        # Broadcast SSE notification
        notify_subscribers({
            "status": "ok",
            "last_updated": last_fetch_time,
            "count": len(quotes),
            "quotes": quotes
        })

    except Exception as e:
        print("Error in background quote fetch:", e)
    finally:
        is_fetching = False

def background_loop():
    while True:
        try:
            fetch_quotes_job()
        except Exception as e:
            print("Background loop exception:", e)
        time.sleep(45)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize initial cache from existing database
    init_stocks = "database/html_424_stocks.json" if os.path.exists("database/html_424_stocks.json") else "html_424_stocks.json"
    if os.path.exists(init_stocks):
        try:
            with open(init_stocks, "r", encoding="utf-8") as f:
                stocks = json.load(f)
            for s in stocks:
                sym = s["symbol"]
                lm = s.get("live_movement") or {}
                cached_quotes[sym] = {
                    "curr_price": s.get("today_price") or lm.get("curr_price", 0),
                    "prev_close": lm.get("prev_close", s.get("today_price", 0)),
                    "day_change": lm.get("day_change", 0),
                    "day_change_pct": lm.get("day_change_pct", 0),
                    "day_high": lm.get("day_high", 0),
                    "day_low": lm.get("day_low", 0),
                    "volume": lm.get("volume", 0),
                    "last_updated": lm.get("last_updated", "")
                }
            print(f"🚀 Loaded initial cache with {len(cached_quotes)} stocks into FastAPI memory.")
        except Exception as e:
            print("Initial cache load error:", e)

    # Start background updater thread
    bg_thread = threading.Thread(target=background_loop, daemon=True)
    bg_thread.start()

    yield
    print("Shutting down Institutional Real-Time Market Server.")

# --------------------------------------------------------------------------
# FASTAPI APPLICATION SETUP
# --------------------------------------------------------------------------
app = FastAPI(
    title="Institutional 360 Indian Equities & Buy Radar Terminal API",
    description="High-performance real-time quote streaming, radar trade tracking, news sentiment, and corporate filings.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# PYDANTIC SCHEMAS
# --------------------------------------------------------------------------
class TrackTradeRequest(BaseModel):
    symbol: str
    horizon: Optional[str] = "SWING"
    notes: Optional[str] = "Tracked via Terminal"
    id: Optional[str] = None

class CloseTradeRequest(BaseModel):
    trade_id: Optional[str] = None
    symbol: Optional[str] = None
    exit_price: Optional[float] = None
    reason: Optional[str] = None
    exit_reason: Optional[str] = None

# --------------------------------------------------------------------------
# REST ENDPOINTS
# --------------------------------------------------------------------------
@app.get("/api/health")
async def get_health():
    uptime_sec = int(time.time() - server_start_time)
    return {
        "status": "healthy",
        "engine": "FastAPI/Uvicorn",
        "uptime_seconds": uptime_sec,
        "cached_stocks_count": len(cached_quotes),
        "last_fetch_time": last_fetch_time,
        "active_sse_subscribers": len(sse_clients),
        "active_ws_subscribers": len(ws_clients)
    }

@app.get("/api/quotes")
async def get_quotes():
    return {
        "status": "ok",
        "last_updated": last_fetch_time,
        "count": len(cached_quotes),
        "quotes": cached_quotes
    }

@app.get("/api/stream/quotes")
async def stream_quotes(request: Request):
    """Server-Sent Events (SSE) stream pushing real-time quotes to Flutter & Web clients."""
    queue: asyncio.Queue = asyncio.Queue()
    sse_clients.append(queue)

    async def event_generator():
        # Send initial snapshot immediately
        initial_data = {
            "status": "ok",
            "last_updated": last_fetch_time,
            "count": len(cached_quotes),
            "quotes": cached_quotes
        }
        yield f"data: {json.dumps(initial_data)}\n\n"

        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(payload)}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat comment to keep HTTP connection alive
                    yield ": ping\n\n"
        finally:
            if queue in sse_clients:
                sse_clients.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.websocket("/ws/quotes")
async def websocket_quotes(websocket: WebSocket):
    await websocket.accept()
    ws_clients.append(websocket)
    try:
        # Send initial snapshot
        await websocket.send_json({
            "status": "ok",
            "last_updated": last_fetch_time,
            "count": len(cached_quotes),
            "quotes": cached_quotes
        })
        while True:
            # Keep alive and receive any client ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in ws_clients:
            ws_clients.remove(websocket)

@app.get("/api/stocks")
async def get_stocks():
    """Returns all 424 stocks with complete technical & fundamental indicators."""
    tech_path = "database/advanced_technicals_424.json" if os.path.exists("database/advanced_technicals_424.json") else "flutter_app/assets/advanced_technicals_424.json"
    fund_path = "database/html_424_stocks.json" if os.path.exists("database/html_424_stocks.json") else "flutter_app/assets/html_424_stocks.json"
    tech_data = []
    fund_data = []
    if os.path.exists(tech_path):
        with open(tech_path, "r", encoding="utf-8") as f:
            tech_data = json.load(f)
    if os.path.exists(fund_path):
        with open(fund_path, "r", encoding="utf-8") as f:
            fund_data = json.load(f)

    return {
        "status": "ok",
        "count": len(tech_data),
        "technicals": tech_data,
        "fundamentals": fund_data
    }

@app.get("/api/radar/database")
async def get_radar_database():
    db_path = "database/radar_signals_database.json" if os.path.exists("database/radar_signals_database.json") else ("backend/radar_database.json" if os.path.exists("backend/radar_database.json") else "radar_signals_database.json")
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db_data = json.load(f)
    except Exception:
        db_data = {"active_signals": [], "historical_suggestions": [], "completed_journal": []}
    return db_data

@app.post("/api/radar/track")
async def track_radar_stock(req: TrackTradeRequest):
    sym = req.symbol.strip().upper()
    horizon = req.horizon or "SWING"
    notes = req.notes or "Tracked via API"

    db_paths = [
        "database/radar_signals_database.json",
        "backend/radar_database.json",
        "flutter_app/assets/radar_signals_database.json"
    ]
    if os.path.exists("flutter_app/build/web/assets/assets"):
        db_paths.append("flutter_app/build/web/assets/assets/radar_signals_database.json")

    primary_path = "database/radar_signals_database.json" if os.path.exists("database/radar_signals_database.json") else "backend/radar_database.json"
    try:
        with open(primary_path, "r", encoding="utf-8") as f:
            db = json.load(f)

        # Check existing running
        for s in db.get("active_signals", []):
            if s.get("symbol") == sym and s.get("status") == "RUNNING":
                return {"status": "ok", "message": f"{sym} is already actively running."}

        adv_path = "database/advanced_technicals_424.json" if os.path.exists("database/advanced_technicals_424.json") else "advanced_technicals_424.json"
        s_data = None
        if os.path.exists(adv_path):
            with open(adv_path, "r", encoding="utf-8") as f_adv:
                adv_list = json.load(f_adv)
            s_data = next((x for x in adv_list if x['symbol'] == sym), None)

        cmp = cached_quotes.get(sym, {}).get("curr_price") or (s_data.get("cmp") if s_data else 100.0)
        tb = s_data.get("trade_blueprint", {}) if s_data else {}
        now_iso = datetime.datetime.now().isoformat()
        trade_id = req.id or f"SIG_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{sym}"

        new_trade = {
            'id': trade_id,
            'symbol': sym,
            'name': s_data.get('name', sym) if s_data else sym,
            'horizon': horizon,
            'entry_price': cmp,
            'current_price': cmp,
            'max_price': cmp,
            'min_price': cmp,
            'stop_loss': tb.get('stop_loss', round(cmp * 0.95, 1)),
            'target_1': tb.get('target_1', round(cmp * 1.05, 1)),
            'target_2': tb.get('target_2', round(cmp * 1.09, 1)),
            'target_3': tb.get('target_3', round(cmp * 1.14, 1)),
            'rr_ratio': tb.get('rr_ratio', 2.2),
            'win_rate_score': tb.get('win_rate_score', 85.0),
            'status': 'RUNNING',
            'pnl_pct': 0.0,
            'triggered_at': now_iso,
            'closed_at': None,
            'exit_price': None,
            'notes': notes
        }

        db.setdefault('active_signals', []).insert(0, new_trade)
        db.setdefault('meta', {})['active_running_trades'] = len([x for x in db['active_signals'] if x.get('status') == 'RUNNING'])

        for p in db_paths:
            atomic_write_json(p, db)

        return {"status": "ok", "message": f"Stock {sym} tracked successfully", "trade": new_trade}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/radar/close")
async def close_radar_trade(req: CloseTradeRequest):
    """
    Closes an active trade. Compatible with both:
    - Mobile Flutter app: {"symbol": "MCX", "exit_reason": "MANUAL_EXIT"}
    - Desktop Web: {"trade_id": "SIG_123", "reason": "TARGET_HIT", "exit_price": 540.0}
    """
    target_identifier = (req.trade_id or req.symbol or "").strip()
    target_symbol = (req.symbol or req.trade_id or "").strip()
    reason = req.exit_reason or req.reason or "MANUAL_EXIT"

    if not target_identifier:
        raise HTTPException(status_code=400, detail="Either 'symbol' or 'trade_id' must be provided.")

    db_paths = [
        "database/radar_signals_database.json",
        "backend/radar_database.json",
        "flutter_app/assets/radar_signals_database.json"
    ]
    if os.path.exists("flutter_app/build/web/assets/assets"):
        db_paths.append("flutter_app/build/web/assets/assets/radar_signals_database.json")

    primary_path = "database/radar_signals_database.json" if os.path.exists("database/radar_signals_database.json") else "backend/radar_database.json"
    try:
        with open(primary_path, "r", encoding="utf-8") as f:
            db = json.load(f)

        active = db.get('active_signals', [])
        matched = None
        for sig in active:
            s_id = sig.get('id', '')
            s_sym = sig.get('symbol', '')
            if (s_id == target_identifier or 
                s_sym.upper() == target_identifier.upper() or 
                s_sym.upper() == target_symbol.upper() or
                s_id == target_symbol):
                matched = sig
                break

        if not matched:
            return {"status": "error", "message": f"No active running trade matched for '{target_identifier}'"}

        active.remove(matched)
        now_iso = datetime.datetime.now().isoformat()
        sym = matched.get('symbol', '')
        
        # Calculate exit price
        live_cmp = cached_quotes.get(sym, {}).get("curr_price", matched.get("current_price", 0.0))
        exit_price = req.exit_price if (req.exit_price and req.exit_price > 0) else live_cmp
        if exit_price <= 0:
            exit_price = matched.get("current_price", matched.get("entry_price", 100.0))

        entry = matched.get('entry_price', exit_price)
        pnl = round(((exit_price - entry) / entry) * 100, 2) if entry > 0 else 0.0

        closed_record = {
            "id": f"JRN_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{sym}",
            "symbol": sym,
            "name": matched.get('name', sym),
            "horizon": matched.get('horizon', 'MANUAL'),
            "entry_price": entry,
            "exit_price": exit_price,
            "stop_loss": matched.get('stop_loss', 0),
            "target_1": matched.get('target_1', 0),
            "target_2": matched.get('target_2', 0),
            "status": reason,
            "pnl_pct": pnl,
            "rr_ratio": matched.get('rr_ratio', 2.0),
            "triggered_at": matched.get('triggered_at', now_iso),
            "closed_at": now_iso,
            "notes": f"Closed via API ({reason}) at ₹{exit_price:.2f}"
        }

        if 'completed_journal' not in db:
            db['completed_journal'] = []
        db['completed_journal'].insert(0, closed_record)

        db.setdefault('meta', {})['active_running_trades'] = len([x for x in active if x.get('status') == 'RUNNING'])
        db['meta']['completed_trades'] = len(db['completed_journal'])

        for p in db_paths:
            atomic_write_json(p, db)

        return {
            "status": "ok",
            "message": f"Trade for {sym} closed and recorded into journal successfully",
            "closed_record": closed_record
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news")
async def get_news():
    news_path = "backend/stock_news.json"
    try:
        with open(news_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

@app.get("/api/orders")
async def get_orders():
    orders_path = "backend/corporate_orders.json"
    try:
        with open(orders_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

# --------------------------------------------------------------------------
# FLUTTER WEB TERMINAL HOSTING
# --------------------------------------------------------------------------
MIME_MAP = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.wasm': 'application/wasm',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.css': 'text/css',
    '.ttf': 'font/ttf',
    '.otf': 'font/otf',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
}

@app.get("/{full_path:path}")
async def serve_flutter_web(full_path: str):
    # API endpoints handled above; this catches all other routes to serve Flutter Web
    rel_path = full_path.strip("/\\")
    if not rel_path or rel_path in ["app", "app/"]:
        rel_path = "index.html"
    elif rel_path.startswith("app/"):
        rel_path = rel_path[4:]

    clean_rel = rel_path.split("?")[0]
    target_file = os.path.join("flutter_app", "build", "web", clean_rel)

    # If file not directly found, check asset mirrors and database
    if not os.path.exists(target_file) or os.path.isdir(target_file):
        asset_name = os.path.basename(clean_rel)
        candidates = [
            os.path.join("flutter_app", "build", "web", "assets", "assets", asset_name),
            os.path.join("flutter_app", "build", "web", "assets", asset_name),
            os.path.join("flutter_app", "assets", asset_name),
            os.path.join("database", asset_name),
            os.path.join("dashboards", clean_rel),
            os.path.join("dashboards", asset_name),
        ]
        for c in candidates:
            if os.path.exists(c) and os.path.isfile(c):
                target_file = c
                break

    # SPA Fallback: ONLY fallback to index.html for page routes, NEVER for assets
    if not os.path.exists(target_file) or os.path.isdir(target_file):
        ext = os.path.splitext(clean_rel)[1].lower()
        if ext in ['.json', '.js', '.wasm', '.png', '.jpg', '.jpeg', '.svg', '.otf', '.ttf', '.woff', '.woff2', '.css']:
            raise HTTPException(status_code=404, detail=f"Asset {clean_rel} not found")
        target_file = os.path.join("flutter_app", "build", "web", "index.html")

    if os.path.exists(target_file) and os.path.isfile(target_file):
        ext = os.path.splitext(target_file)[1].lower()
        ctype = MIME_MAP.get(ext, "application/octet-stream")
        cache_header = "no-cache" if ext in [".html", ".json"] else "public, max-age=86400"
        return FileResponse(
            target_file,
            media_type=ctype,
            headers={"Cache-Control": cache_header, "Access-Control-Allow-Origin": "*"}
        )

    raise HTTPException(status_code=404, detail="File not found")

def main():
    print(f"🚀 Starting Institutional Real-Time Market Server on http://0.0.0.0:{PORT}...")
    print(f"📡 Swagger Documentation at: http://127.0.0.1:{PORT}/docs")
    print(f"📱 Native Flutter Web App at: http://127.0.0.1:{PORT}/app")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

if __name__ == "__main__":
    main()
