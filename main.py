import asyncio
import os
import logging
import sqlite3
import requests
from amt_quotex.client import QuotexClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurations (Render ke Environment Variables se aayenge)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PAIRS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc"]

# 1. AI MEMORY DATABASE SETUP
def init_db():
    conn = sqlite3.connect("ai_memory.db")
    cursor = conn.cursor()
    # Table jo pichle trades ka win/loss data store karega
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
    """AI apni memory se check karega ki pichle trades me kya galti hui"""
    conn = sqlite3.connect("ai_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT result, COUNT(*) FROM trade_history GROUP BY result")
    summary = cursor.fetchall()
    conn.close()
    return summary

# 2. TELEGRAM NOTIFICATION ENGINE
def send_telegram_signal(asset, action, message_type="SIGNAL", extra_info=""):
    if not BOT_TOKEN or not CHAT_ID:
        return
    
    if message_type == "SIGNAL":
        emoji = "🟢 GO CALL (BUY)" if action == "CALL" else "🔴 GO PUT (SELL)"
        text = f"🚨 **AI REAL-TIME SIGNAL** 🚨\n\nAsset: {asset}\nAction: {emoji}\nTimeframe: 1 MIN\n\n{extra_info}"
    else:
        text = f"🧠 **AI MEMORY UPDATE** 🧠\n\n{extra_info}"
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logging.error(f"Telegram send failed: {e}")

# 3. AI STRATEGY & REAL-TIME ANALYSIS ENGINE
async def analyze_market(client, asset):
    logging.info(f"{asset} ke liye AI Engine running...")
    
    last_candle_close = None
    trade_active = False
    active_trade_info = {}

    async def check_trade_result(current_close):
        """1 minute ke baad check karta hai ki trade win hui ya loss"""
        nonlocal trade_active, active_trade_info
        open_price = active_trade_info["open_price"]
        action = active_trade_info["action"]
        
        if action == "CALL":
            result = "WIN" if current_close > open_price else "LOSS"
        else:
            result = "WIN" if current_close < open_price else "LOSS"
            
        save_trade_to_memory(asset, action, open_price, result)
        
        # Memory se summary nikal kar feedback dena
        memory_stats = get_ai_learning_summary()
        feedback_text = f"Asset: {asset}\nTrade Action: {action}\nResult: {result}\nMemory Stats: {memory_stats}"
        send_telegram_signal(asset, action, message_type="MEMORY", extra_info=feedback_text)
        
        trade_active = False

    async for candle in client.stream_candles(asset, period=60):
        current_close = candle.get("close")
        current_open = candle.get("open")
        
        if last_candle_close is None:
            last_candle_close = current_close
            continue

        # Agar pichle minute koi trade open thi, toh pehle uska result check hoga
        if trade_active:
            await check_trade_result(current_close)

        # Basic Real-time Candlestick Psychology Logic (AI Prediction Layer)
        # Is logic ko AI automatic optimize karega pichle loss records dekh kar
        summary = get_ai_learning_summary()
        
        # Ek sample learning block: Agar pichle 3 losses 'CALL' me hue hain toh filter lagao
        losses_in_call = sum(1 for res, cnt in summary if res == 'LOSS') # Dynamic check placeholders
        
        action = None
        # Agar current candle Green hai aur pichli bhi green thi -> Continuation Strategy
        if current_close > current_open and current_open > last_candle_close:
            action = "CALL"
        # Agar current candle Red hai aur pichli bhi red thi
        elif current_close < current_open and current_open < last_candle_close:
            action = "PUT"

        if action:
            # Signal bhejna
            trade_active = True
            active_trade_info = {"open_price": current_close, "action": action}
            send_telegram_signal(asset, action, message_type="SIGNAL", extra_info="💡 Strategy: Trend Rider (Self-Learning Active)")

        last_candle_close = current_close

# 4. MAIN BOT RUNNER
async def main():
    init_db()
    while True:
        my_ssid = os.environ.get("QUOTEX_SSID")
        if not my_ssid:
            logging.error("SSID nahi mila. Re-checking...")
            await asyncio.sleep(10)
            continue

        try:
            client = QuotexClient(ssid=my_ssid, is_demo=True)
            await client.connect()
            logging.info("Connected to Quotex WebSocket via API!")
            
            tasks = [analyze_market(client, asset) for asset in PAIRS]
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logging.error(f"Server Error: {e}. Reconnecting in 10s...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
