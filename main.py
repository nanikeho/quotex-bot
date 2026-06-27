import sys
import time
import os
import json
import requests
import pandas as pd
import numpy as np
import ta
import threading
from flask import Flask
import websocket

# Environment Variables
EMAIL = os.environ.get("QUOTEX_EMAIL")
PASSWORD = os.environ.get("QUOTEX_PASSWORD")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

PAIRS = ["EURUSD_OTC", "GBPUSD_OTC", "USDJPY_OTC", "AUDUSD_OTC"]
market_memory = {pair: [] for pair in PAIRS}

app = Flask('')

@app.route('/')
def home():
    return "🚀 Quotex Pure-Engine is Live & Operational 24/7!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send_telegram_signal(pair, pattern_name, direction):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    emoji = "🟩 CALL (UP)" if direction == "UP" else "🟥 PUT (DOWN)"
    message = (
        f"🎯 *QUOTEX PURE SURESHOT SIGNAL* 🎯\n\n"
        f"🌐 *Asset:* `{pair}`\n"
        f"📊 *Strategy:* `{pattern_name}`\n"
        f"📈 *Prediction:* *{emoji}*\n"
        f"⏳ *Timeframe:* `1 MIN`"
    )
    payload = {"chat_id": str(TELEGRAM_CHAT_ID), "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=5)
    except: pass

def detect_sureshot_patterns(df):
    if len(df) < 55: return None, None
    try:
        close_prices = df['close'].astype(float)
        df['ema50'] = ta.trend.ema_indicator(close_prices, window=50)
        df['rsi'] = ta.momentum.rsi(close_prices, window=14)
        
        c1, c2 = df.iloc[-1], df.iloc[-2]
        current_ema, current_rsi = df['ema50'].iloc[-1], df['rsi'].iloc[-1]
        
        # Sureshot Engulfing Reversal
        if c1['close'] > current_ema and c2['close'] < c2['open'] and c1['close'] > c1['open']:
            if 45 < current_rsi < 65 and c1['close'] > c2['open']: 
                return "Pure Bullish Engulfing", "UP"
        if c1['close'] < current_ema and c2['close'] > c2['open'] and c1['close'] < c1['open']:
            if 35 < current_rsi < 55 and c1['close'] < c2['open']: 
                return "Pure Bearish Engulfing", "DOWN"
    except: pass
    return None, None

# --- DIRECT WEBSOCKET CONNECTION TO QUOTEX ---
def on_message(ws, message):
    try:
        data = json.loads(message)
        # Live price incoming stream parser
        if "candle" in data:
            c = data["candle"]
            pair = data["pair"]
            if pair in PAIRS:
                market_memory[pair].append({
                    'time': int(c['time']), 'open': float(c['open']),
                    'high': float(c['high']), 'low': float(c['low']), 'close': float(c['close'])
                })
                if len(market_memory[pair]) > 100: market_memory[pair].pop(0)
                df = pd.DataFrame(market_memory[pair])
                pattern, direction = detect_sureshot_patterns(df)
                if pattern and direction:
                    send_telegram_signal(pair, pattern, direction)
    except: pass

def on_open(ws):
    print("📡 Connected Directly to Quotex Data Pipeline!")
    # Subscribing to live pairs
    for pair in PAIRS:
        ws.send(json.dumps({"action": "subscribe", "pair": pair, "timeframe": 60}))

def start_crypto_stream():
    # Direct secure websocket address without intermediate broken libraries
    ws_url = "wss://ws.quotex.io/socket.io/?EIO=3&transport=websocket"
    ws = websocket.WebSocketApp(ws_url, on_open=on_open, on_message=on_message)
    ws.run_forever()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    print("--- 🧠 STARTING DIRECT QUOTEX PURE STEAM MATRIX ---")
    start_crypto_stream()
