import asyncio
import os
import logging
import sqlite3
import requests
from quotexapi.client import QuotexClient

# Logging config taaki Render logs me live updates dikhein
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurations (Render ke Environment Variables se auto pick karega)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PAIRS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc"]

# 1. AI MEMORY SYSTEM (LOCAL DATABASE)
def init_db():
    conn = sqlite3.connect("ai_memory.db")
    cursor = conn.cursor()
    # Trade history aur unke result ko save karne ke liye table
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
    """AI database se check karega ki ab tak kitne win/loss hue hain"""
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

# 2. PRIVATE TELEGRAM NOTIFICATION SYSTEM
def send_telegram_signal(asset, action, message_type="SIGNAL", extra_info=""):
    if not BOT_TOKEN or not CHAT_ID:
        logging.warning("Telegram Tokens missing! Message nahi bheja ja sakta.")
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
        logging.error(f"Telegram Notification Send Failed: {e}")

# 3. REAL-TIME MARKET ANALYSIS & LEARNING ENGINE
async def analyze_market(client, asset):
    logging.info(f"[{asset}] AI Analysis Engine Shuru Ho Gaya Hai...")
    
    last_candle_close = None
    trade_active = False
    active_trade_info = {}

    async def check_trade_result(current_close):
        """1 minute ke baad check karta hai ki trend continuation trade win hui ya loss"""
        nonlocal trade_active, active_trade_info
        open_price = active_trade_info["open_price"]
        action = active_trade_info["action"]
        
        # Binary Options Logic: Entry price ke upar close = CALL WIN, neeche = PUT WIN
        if action == "CALL":
            result = "WIN" if current_close > open_price else "LOSS"
        else:
            result = "WIN" if current_close < open_price else "LOSS"
            
        save_trade_to_memory(asset, action, open_price, result)
        
        # Memory Database se current performance statistics nikalna
        summary = get_ai_learning_summary()
        feedback_text = f"Asset: {asset}\nAction: {action}\nResult: {result}\n\nTotal AI Memory Stats: {dict(summary)}"
        
        # Telegram par update bhejkar AI khud ko evaluate karega
        send_telegram_signal(asset, action, message_type="MEMORY", extra_info=feedback_text)
        trade_active = False

    # Live market se 1-minute time frame ka price flow loop
    async for candle in client.stream_candles(asset, period=60):
        current_close = candle.get("close")
        current_open = candle.get("open")
        
        if last_candle_close is None:
            last_candle_close = current_close
            continue

        # Agar pichle minute koi signal generated tha, toh sabse pehle uska result check hoga
        if trade_active:
            await check_trade_result(current_close)

        action = None
        # Candlestick Psychology Trend Rider Logic
        # Agar consecutive green candles hain aur market strong up direction me hai
        if current_close > current_open and current_open > last_candle_close:
            action = "CALL"
        # Agar consecutive red candles hain aur market down trend me hai
        elif current_close < current_open and current_open < last_candle_close:
            action = "PUT"

        if action:
            trade_active = True
            active_trade_info = {"open_price": current_close, "action": action}
            
            extra_msg = "💡 Strategy: Trend Rider\n🧠 Status: Feedback loop active (Self-Learning Mode)"
            send_telegram_signal(asset, action, message_type="SIGNAL", extra_info=extra_msg)

        last_candle_close = current_close

# 4. MAIN PROGRAM RUNNER
async def main():
    init_db()
    logging.info("AI Local Memory Database Initialized.")
    
    while True:
        my_ssid = os.environ.get("QUOTEX_SSID")
        if not my_ssid:
            logging.error("QUOTEX_SSID Environment Variable nahi mila! Check Render Settings.")
            await asyncio.sleep(15)
            continue

        try:
            logging.info("Quotex API WebSocket se Connection build kar rahe hain...")
            client = QuotexClient(ssid=my_ssid, is_demo=True)
            await client.connect()
            logging.info("SUCCESS: Quotex Cloud Connection Established!")
            
            # Saare multi-pairs ko ek saath parallelly scan karna bina lag ke
            tasks = [analyze_market(client, asset) for asset in PAIRS]
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logging.error(f"Main Loop Execution Error: {e}. Reconnecting in 10s...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
