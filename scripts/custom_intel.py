import sys, os, json, time, re, math, random
import numpy as np
import pandas as pd
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")

from part2_metadata import load_new_stocks_catalog
from fetch_helper import fetch_screener_data, fetch_yf_data
from process_stock import prepare_12_quarter_series, get_effective_prices_for_dates, ANN_DATES
from financials_engine import build_quarters_history, compute_fundamental_metrics
from technicals_engine import compute_technicals_from_df
from forecast_engine import build_forecast_profile
from mood_engine import assign_market_mood

# Specific custom news/catalysts for high quality intelligence
CUSTOM_INTEL = {
    "ZENTEC": {
        "pos_news": "Undisputed market leader in indigenous combat training simulators and Counter-Unmanned Aerial Vehicle (anti-drone) systems; >70% ROCE, zero debt, and soaring defence export book.",
        "neg_news": "Lumpy quarterly order booking and high customer concentration with Ministry of Defence.",
        "consensus": "Strong Buy / Consensus Top Pick",
        "tailwinds": "Modern warfare emphasis on anti-drone protection, border surveillance indigenization, and export incentives under Raksha Mantri mandates.",
        "default_price": 1820.0
    },
    "POWERINDIA": {
        "pos_news": "Undisputed technology monopoly in High-Voltage Direct Current (HVDC) transmission links; multi-billion dollar grid order book for green energy corridors.",
        "neg_news": "Trading at elevated valuation multiples; execution depends on Power Grid project milestone clearances.",
        "consensus": "Strong Buy / Consensus Top Pick",
        "tailwinds": "National transmission mission to evacuate 500 GW renewable power by 2030; grid modernization capex.",
        "default_price": 31750.0
    },
    "APOLLO": {
        "pos_news": "Critical electronic systems, telemetry, missile guidance, and underwater warfare hardware with soaring Ministry of Defence order inflows.",
        "neg_news": "Milestone-linked government payment cycles and high working capital intensity.",
        "consensus": "Strong Buy / High Momentum",
        "tailwinds": "Defence Acquisition Council approvals, Make in India indigenization mandates, and missile systems export ramp-up.",
        "default_price": 388.0
    },
    "TDPOWERSYS": {
        "pos_news": "Zero-debt AC generator specialist with >50% domestic market share; massive global export demand for steam, gas, and hydro generators driven by global data centers.",
        "neg_news": "Raw material copper price spikes and global industrial capex cycle timing.",
        "consensus": "Strong Buy / Consensus Top Pick",
        "tailwinds": "Global AI data center captive power backup requirements and worldwide decarbonized gas turbine investments.",
        "default_price": 435.0
    },
    "UNOMINDA": {
        "pos_news": "Premier Tier-1 auto component leader supplying smart LED lighting, alloy wheels, acoustic systems, and high-voltage EV powertrain components across OEM leaders.",
        "neg_news": "Higher capex for new EV joint ventures temporarily moderating free cash flow yields.",
        "consensus": "Overweight / Structural Winner",
        "tailwinds": "Vehicle premiumization (sunroofs, smart cockpits, alloy wheels) increasing content-per-vehicle by 3x across Indian passenger cars.",
        "default_price": 995.0
    },
    "RKFORGE": {
        "pos_news": "Global precision forging leader; establishing India's largest forged train wheel manufacturing facility for Indian Railways and scaling EV component exports.",
        "neg_news": "North American Class-8 truck build rate cyclicality and European automotive demand softness.",
        "consensus": "Strong Buy / Consensus Top Pick",
        "tailwinds": "Import substitution of forged train wheels by Ministry of Railways and global automotive supply chain friendshoring.",
        "default_price": 860.0
    },
    "GPIL": {
        "pos_news": "High-ROCE Chhattisgarh miner, producing high-grade iron pellets and sponge iron with 100% captive power and zero net debt.",
        "neg_news": "Cyclical iron ore pellet pricing and international steel demand variations.",
        "consensus": "Strong Buy / Deep Value Multi-bagger",
        "tailwinds": "Government focus on high-grade pellet domestic blending and massive infrastructure steel demand.",
        "default_price": 185.0
    },
    "HEROMOTOCO": {
        "pos_news": "World's largest 2-wheeler maker (35% ROCE, 3.5% Dividend Yield, 19x P/E) + strategic ~38% ownership in Ather Energy driving EV transformation.",
        "neg_news": "Intense competition in entry-level 100cc rural commuter segment and EV transition adoption pace.",
        "consensus": "Overweight / Long-term Compounder",
        "tailwinds": "Rural income revival from favorable monsoons, festive vehicle demand, and urban premiumization (Harley-Davidson 440, Xtreme).",
        "default_price": 5300.0
    }
}

print("Loaded custom intel dictionary.")
