import sys, os, json, time, re, math
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def parse_num(val_str):
    if not val_str or val_str == '-' or val_str == '':
        return 0.0
    val_str = str(val_str).replace(',', '').replace('%', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

def fetch_screener_data(slug):
    if not slug:
        return None
    for mode in ["consolidated/", ""]:
        url = f"https://www.screener.in/company/{slug}/{mode}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=4)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                sec = soup.find('section', id='quarters')
                if sec:
                    tbl = sec.find('table')
                    if tbl:
                        headers = [th.get_text(strip=True) for th in tbl.find('thead').find_all('th')][1:]
                        rows = {}
                        for tr in tbl.find('tbody').find_all('tr'):
                            cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                            if cells:
                                name = cells[0].replace('+', '').strip()
                                rows[name] = [parse_num(c) for c in cells[1:]]
                        return {"headers": headers, "rows": rows}
        except Exception:
            pass
    return None

def fetch_yf_data(ticker_str):
    if not ticker_str:
        return None
    try:
        t = yf.Ticker(ticker_str)
        hist = t.history(period="1y")
        curr_p = None
        try:
            curr_p = float(t.fast_info['lastPrice'])
        except:
            if not hist.empty:
                curr_p = float(hist['Close'].iloc[-1])
        return {"hist": hist, "curr_price": curr_p, "info": {}}
    except Exception:
        return None
