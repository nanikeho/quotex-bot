import asyncio
import os
import logging
import sqlite3
import json
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PAIRS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc"]

# 1. DATABASE SYSTEM
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

# 2. TELEGRAM SYSTEM
def send_telegram_signal(asset, action, message_type="SIGNAL", extra_info=""):
    if not BOT_TOKEN or not CHAT_ID:
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
        logging.error(f"Telegram failed: {e}")

# 3. ANALYSIS & DATA PROCESSING
async def process_candle_data(asset, candle_open, candle_close, state):
    if state["last_close"].get(asset) is None:
        state["last_close"][asset] = candle_close
        return

    last_close = state["last_close"][asset]

    # Active trade result check
    if state["trade_active"].get(asset):
        open_price = state["active_trade"][asset]["open_price"]
        action = state["active_trade"][asset]["action"]
        
        result = "WIN" if (action == "CALL" and candle_close > open_price) or (action == "PUT" and candle_close < open_price) else "LOSS"
        save_trade_to_memory(asset, action, open_price, result)
        
        summary = get_ai_learning_summary()
        feedback = f"Asset: {asset}\nAction: {action}\nResult: {result}\n\nMorphing AI Memory: {dict(summary)}"
        send_telegram_signal(asset, action, message_type="MEMORY", extra_info=feedback)
        state["trade_active"][asset] = False

    # Strategy logic
    action = None
    if candle_close > candle_open and candle_open > last_close:
        action = "CALL"
    elif candle_close < candle_open and candle_open < last_close:
        action = "PUT"

    if action:
        state["trade_active"][asset] = True
        state["active_trade"][asset] = {"open_price": candle_close, "action": action}
        extra_msg = "💡 Strategy: Trend Rider\n🧠 Status: Direct Cloud Streaming Active"
        send_telegram_signal(asset, action, message_type="SIGNAL", extra_info=extra_msg)

    state["last_close"][asset] = candle_close

# 4. DIRECT WEBSOCKET CONNECTION RUNNER
async def main():
    init_db()
    logging.info("Direct AI Core Memory Initialized.")
    
    state = {"last_close": {}, "trade_active": {}, "active_trade": {}}
    
    # Quotex WebSocket Server URL
    uri = "wss://ws.qatx.com/connect" 
    
    while True:
        my_ssid = os.environ.get("QUOTEX_SSID")
        if not my_ssid:
            logging.error("QUOTEX_SSID nahi mila!")
            await asyncio.sleep(15)
            continue
            
        try:
            import websockets
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Cookie": f"ssid={my_ssid}"
            }
            
            logging.info("Connecting to Quotex Cloud Server via Direct Secure WebSocket...")
            async with websockets.connect(uri, extra_headers=headers) as websocket:
                logging.info("SUCCESS: Connected to Quotex Core Network directly!")
                
                # Market assets subscribe karne ke liye request packets bhejte hain
                for asset in PAIRS:
                    sub_msg = {"action": "subscribe", "asset": asset, "period": 60}
                    await websocket.send(json.dumps(sub_msg))
                    state["trade_active"][asset] = False
                
                # Live streaming data collection loop
                async for message in websocket:
                    data = json.loads(message)
                    # Jab live candle update data receive ho
                    if "candle" in data or ("action" in data and data["action"] == "candle"):
                        candle = data.get("candle", data)
                        asset = candle.get("asset")
                        if asset in PAIRS:
                            await process_candle_data(asset, candle.get("open"), candle.get("close"), state)
                            
        except Exception as e:
            logging.error(f"Network Pipe Connection Error: {e}. Reconnecting in 10s...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
    
