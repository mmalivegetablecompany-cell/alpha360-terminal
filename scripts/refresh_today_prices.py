"""
Unified Price & Market Intelligence Synchronizer
Delegates to backend/cloud_market_engine.py to guarantee 100% synchronous price
updates across both HTML dashboards, radar databases, news, and corporate orders.
"""

import os
import sys
import subprocess

sys.stdout.reconfigure(encoding="utf-8")

def refresh_prices():
    print("=" * 70)
    print("🚀 INITIATING UNIFIED 424 STOCK MARKET REFRESH & SYNCHRONIZATION")
    print("=" * 70)
    
    script_path = os.path.join(os.path.dirname(__file__), "backend", "cloud_market_engine.py")
    if not os.path.exists(script_path):
        script_path = "backend/cloud_market_engine.py"
        
    subprocess.run([sys.executable, script_path], check=True)
    print("\n✅ All 424 stocks, radar signals, news, and dashboards fully refreshed!")

if __name__ == "__main__":
    refresh_prices()
