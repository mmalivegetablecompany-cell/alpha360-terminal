# 🛰️ Alpha360 Terminal — 24/7 Cloud & Installation Guide

This guide covers everything you need to run **Alpha360 Terminal** on your **Android phone**, your **Windows PC**, and keep it streaming live data **24/7 in the cloud** completely free.

---

## 📱 1. Android Phone Installation (APK)

Your release APK is pre-built, signed, and ready to install:
- **File location**: `Alpha360_Terminal.apk` (in the project root: `d:\New folder (5)\Alpha360_Terminal.apk`)
- **Size**: ~23.8 MB
- **Package**: `com.alpha360.terminal`
- **Icon**: High-resolution Institutional Neon Emerald Candlestick & Gold Chevron Emblem
- **Permissions**: Internet access, network state monitoring, cleartext HTTP enabled for local LAN.

### How to Install on your Phone:
1. **Transfer the APK** to your phone via:
   - USB cable (copy to `Downloads` folder on phone)
   - Send to yourself on WhatsApp / Telegram / Google Drive / Email
2. On your phone, tap `Alpha360_Terminal.apk` to install.
3. If prompted with *"For security, your phone is not allowed to install unknown apps"*, tap **Settings** and toggle **Allow from this source**.
4. Tap **Install** and then **Open**!

### Connecting your Phone to Live Data:
- **Out of the box (Offline Mode)**: The APK is bundled with the complete database of 424 stocks, technical signals, radar trades, and company financials. It works immediately even with zero internet or server running!
- **Home Wi-Fi Mode (Instant Live Streaming)**:
  1. Make sure your PC and phone are on the same Wi-Fi network.
  2. Launch `Alpha360_Terminal.exe` on your PC.
  3. Find your PC's IP address (run `ipconfig` in cmd, e.g., `192.168.1.15`).
  4. On your phone app, tap the **Gateway / Network plug icon** in the top-right app bar.
  5. Enter `http://192.168.1.15:8765` and tap **Test Connection**.
  6. Tap **Save Gateway**. Your phone is now streaming real-time live quotes directly from your PC!
- **24/7 Worldwide Mode (Cloud)**: See Section 3 below.

---

## 💻 2. Windows Desktop App (.exe)

Your native Windows desktop app has been compiled with the custom multi-resolution icon and standalone window runner:
- **File location**: `d:\New folder (5)\Alpha360_Terminal.exe`
- **Desktop Shortcut**: Already placed on your Windows Desktop at `C:\Users\HITS\Desktop\Alpha360 Terminal.lnk`
- **Resolution**: Launches into a dedicated 1440x900 native workstation window without address bar or browser tabs.

### How to Run:
1. Double-click the **Alpha360 Terminal** shortcut on your desktop, or run `Alpha360_Terminal.exe`.
2. The launcher automatically verifies if the background real-time data engine is active. If not, it boots it silently in the background.
3. It opens the institutional terminal window running the Flutter interface at 120 FPS.
4. If you ever move the folder or reinstall shortcuts, simply double-click `Install_Desktop_Shortcut.bat`.

---

## ☁️ 3. 24/7 Cloud Server Setup (GitHub & Render/Railway)

To keep your terminal updating **24 hours a day, 7 days a week** without needing your PC on:

### Part A: GitHub Actions (Autonomous 24/7 Market Engine)
GitHub Actions will run autonomously on GitHub's cloud servers every 15 minutes during Indian market hours (9:15 AM to 3:45 PM IST) and at market close (4:15 PM IST).

#### Steps to Setup:
1. **Initialize Git & Push to GitHub**:
   Open PowerShell in `d:\New folder (5)`:
   ```bash
   git init
   git add .
   git commit -m "Alpha360 Terminal Initial Release"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/alpha360-terminal.git
   git push -u origin main
   ```
2. **Enable Workflow Write Permissions (Crucial Step)**:
   - Open your repository on [GitHub.com](https://github.com).
   - Click **Settings** (top tab of repo).
   - In the left sidebar, click **Actions** -> **General**.
   - Scroll down to **Workflow permissions**.
   - Select **"Read and write permissions"**.
   - Check the box for **"Allow GitHub Actions to approve pull request..."** (optional).
   - Click **Save**.
3. **Verify Execution**:
   - Go to the **Actions** tab on your GitHub repository.
   - You will see **"24/7 Autonomous Market Engine & Signal Tracker"**.
   - You can click **Run workflow** -> **Run workflow** to test it anytime!
   - Every 15 minutes during market hours, GitHub will fetch live quotes for all 424 stocks, recalculate technicals, evaluate buy radar signals, and commit the fresh JSON data back to your repository.

---

### Part B: 24/7 Live Price Server on the Cloud (Free Tier)
To have a persistent API URL (e.g. `https://alpha360-api.onrender.com`) that your Android phone can stream from anywhere in the world on 5G/4G:

#### Deploying to Render.com (100% Free):
1. Sign up for free at [Render.com](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository (`alpha360-terminal`).
4. Render automatically reads our `render.yaml` and `Dockerfile`:
   - **Environment**: Docker or Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python live_price_server.py`
   - **Plan**: Free
5. Click **Deploy Web Service**.
6. Render will generate a free live public URL, for example:
   `https://alpha360-market-server.onrender.com`

#### Connecting your Android Phone & Windows App to the Cloud URL:
1. Open **Alpha360 Terminal** on your phone or desktop.
2. Tap the **Network Gateway** icon (top right).
3. Paste your Render URL: `https://alpha360-market-server.onrender.com`
4. Tap **Test Connection** (it will show latency in ms).
5. Tap **Save Gateway**.
6. **Done!** Your Android phone and Windows desktop terminal now stream institutional quotes, buy radar alerts, and company news 24/7 wherever you are in the world!

---

## 🛠️ Summary of Key Files

| File | Description |
|---|---|
| `Alpha360_Terminal.apk` | Release installable Android APK (23.8 MB) |
| `Alpha360_Terminal.exe` | Native Windows desktop app with embedded icon |
| `Install_Desktop_Shortcut.bat` | 1-click installer to add shortcut to Windows Desktop |
| `.github/workflows/market_24x7_cron.yml` | GitHub Actions 24/7 automated market hours cron job |
| `backend/cloud_market_engine.py` | Autonomous multi-threaded market engine |
| `live_price_server.py` | FastAPI real-time streaming server (SSE + WebSockets) |
| `Dockerfile` | Docker container specification for cloud hosting |
| `render.yaml` | 1-click cloud deployment configuration |
| `requirements.txt` | Python cloud dependencies |
