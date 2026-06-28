import asyncio
import os
import logging
import sqlite3
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurations
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PAIRS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc"]

# ---------------------------------------------------------
# RENDER PORT BINDING FIX (Web Server Mock Topology)
# ---------------------------------------------------------
class MockServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Quotex AI Bot Engine is Running Safely!")

def start_health_server():
    """Render ke Port Scan Timeout error ko bypass karne ke liye background web server"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), MockServer)
    logging.info(f"Health check server initiated on port: {port}")
    server.serve_forever()

# ---------------------------------------------------------
# DATABASE ENGINE (AI MEMORY SYSTEM)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("ai_memory.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT,
            action TEXT,
            price REAL,
            result TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_trade_to_memory(asset, action, price, result):
    conn = sqlite3.connect("ai_memory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trade_history (asset, action, price, result) VALUES (?, ?, ?, ?)", 
                   (asset, action, price, result))
    conn.commit()
    conn.close()

def get_ai_learning_summary():
    conn = sqlite3.connect("ai_memory.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT result, COUNT(*) FROM trade_history GROUP BY result")
        summary = cursor.fetchall()
        return summary
    except Exception as e:
        logging.error(f"Database error: {e}")
        return []
    finally:
        conn.close()

# ---------------------------------------------------------
# TELEGRAM SIGNAL SYSTEM
# ---------------------------------------------------------
def send_telegram_signal(asset, action, message_type="SIGNAL", extra_info=""):
    if not BOT_TOKEN or not CHAT_ID:
        logging.warning("Telegram settings missing. Notification bypassed.")
        return
    if message_type == "SIGNAL":
        emoji = "🟢 GO CALL (BUY)" if action == "CALL" else "🔴 GO PUT (SELL)"
        text = f"🚨 **AI REAL-TIME SIGNAL** 🚨\n\nAsset: {asset}\nAction: {emoji}\nTimeframe: 1 MIN\n\n{extra_info}"
    else:
        text = f"🧠 **AI MEMORY LOOP UPDATE** 🧠\n\n{extra_info}"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Telegram transmission failed: {e}")

# ---------------------------------------------------------
# ROBUST DATA FETCHING LOOP & MARKET ANALYSIS
# ---------------------------------------------------------
async def fetch_and_analyze(asset, state, ssid):
    """Direct HTTP REST pipeline configuration to bypass Cloudflare socket shields"""
    # Custom headers matching a clean browser footprint
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": f"ssid={ssid}",
        "Origin": "https://qxbroker.com"
    }
    
    # Dynamic alternative API data route nodes
    url = f"https://qxbroker.com/api/v1/candles?asset={asset}&period=60&limit=2"
    
    try:
        # Running inside loop execution thread
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            candles = response.json()
            if len(candles) < 2:
                return
                
            # Formatting index structures based on time-series responses
            pichli_candle = candles[0]
            current_candle = candles[1]
            
            candle_open = float(current_candle.get("open", 0))
            candle_close = float(current_candle.get("close", 0))
            last_close = float(pichli_candle.get("close", 0))
            
            if state["last_close"].get(asset) is None:
                state["last_close"][asset] = candle_close
                return

            # Check previous active trade evaluation results
            if state["trade_active"].get(asset):
                open_price = state["active_trade"][asset]["open_price"]
                action = state["active_trade"][asset]["action"]
                
                result = "WIN" if (action == "CALL" and candle_close > open_price) or (action == "PUT" and candle_close < open_price) else "LOSS"
                save_trade_to_memory(asset, action, open_price, result)
                
                summary = get_ai_learning_summary()
                feedback = f"Asset: {asset}\nAction: {action}\nResult: {result}\n\nMorphing AI Memory: {dict(summary)}"
                send_telegram_signal(asset, action, message_type="MEMORY", extra_info=feedback)
                state["trade_active"][asset] = False

            # Core Price Action Candlestick Trajectory Analysis
            action = None
            if candle_close > candle_open and candle_open > last_close:
                action = "CALL"
            elif candle_close < candle_open and candle_open < last_close:
                action = "PUT"

            if action:
                state["trade_active"][asset] = True
                state["active_trade"][asset] = {"open_price": candle_close, "action": action}
                extra_msg = f"💡 Strategy: Trend Rider\n📈 Current Close: {candle_close}\n🧠 Status: Cloud Stream Framework Secured"
                send_telegram_signal(asset, action, message_type="SIGNAL", extra_info=extra_msg)

            state["last_close"][asset] = candle_close
            
        elif response.status_code == 401:
            logging.error(f"[{asset}] Unauthorized Access. Please verify your QUOTEX_SSID value.")
        else:
            logging.warning(f"[{asset}] Alternative node response status code: {response.status_code}")
            
    except Exception as e:
        logging.error(f"Internal Pipeline scanning error for {asset}: {e}")

# ---------------------------------------------------------
# BOT CORE ORCHESTRATION PROCESS
# ---------------------------------------------------------
async def bot_core_loop():
    init_db()
    logging.info("Direct AI Core Memory Initialized.")
    
    state = {"last_close": {}, "trade_active": {}, "active_trade": {}}
    
    # Initialize basic state variables
    for asset in PAIRS:
        state["trade_active"][asset] = False

    while True:
        my_ssid = os.environ.get("QUOTEX_SSID")
        if not my_ssid:
            logging.error("QUOTEX_SSID variable mapping missing inside Render environment configuration.")
            await asyncio.sleep(20)
            continue
            
        # Parallel chunk asynchronous pooling execution across target profiles
        tasks = [fetch_and_analyze(asset, state, my_ssid) for asset in PAIRS]
        await asyncio.gather(*tasks)
        
        # Poll synchronization sequence tracking intervals precisely every 60 seconds
        await asyncio.sleep(60)

if __name__ == "__main__":
    # Start the port server thread to satisfy Render's health checkers
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()
    
    # Run core orchestration framework
    asyncio.run(bot_core_loop())
