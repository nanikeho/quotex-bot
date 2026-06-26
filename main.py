import time
import os
import requests
import pandas as pd
import numpy as np
import urllib3
from quotexapi.stable_api import QuotexAPI

# Network SSL Warnings ko bypass karne ke liye
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== CONFIGURATION ====================
# NOTE: Security ke liye apne PC par chalaate waqt hi direct values likhein.
EMAIL = os.environ.get("QUOTEX_EMAIL", "nanikeho@gmail.com")
PASSWORD = os.environ.get("QUOTEX_PASSWORD", "78907890@Ho")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8805973093:AAHnKIMb-5Mnr0yI0XR3-gIW5oUOQyLNfRA")

# Agar aapki Chat ID channel ki hai aur usme minus (-) sign hai, toh exact minus ke sath likhein (e.g., "-1008240647626")
# Agar normal person ya setup testing hai toh simple ID string format mein:
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8240647626")

ASSET = "EURUSD_OTC"  # Quotex Algorithm OTC Market
TIMEFRAME = 60        # 1-Min Candle Structure

candle_memory = []
# =======================================================

def send_telegram_signal(pattern_name, direction):
    """Direct IP Bypass Gateway ke sath Telegram alert trigger"""
    # Hugging Face ya host blocks se bachne ke liye direct Telegram IP routing
    url = f"https://149.154.167.220/bot{TELEGRAM_TOKEN}/sendMessage"
    
    emoji = "🟩 CALL (UP) ⬆️" if direction == "UP" else "🟥 PUT (DOWN) ⬇️"
    
    message = (
        f"🎯 *QUOTEX OTC ALGO PREDICTION* 🎯\n\n"
        f"🌐 *Asset/Pair:* `{ASSET}`\n"
        f"⏳ *Timeframe:* 1-Minute OTC Stream\n"
        f"📊 *Trigger Pattern:* `{pattern_name}`\n\n"
        f"🚀 *NEXT CANDLE PREDICTION:* *{emoji}*\n"
        f"⏰ *Expiry Time:* `1 MINUTE`\n\n"
        f"✅ *Status:* Algorithmic Flow Tracking Confirmed!"
    )
    
    payload = {
        "chat_id": str(TELEGRAM_CHAT_ID), 
        "text": message, 
        "parse_mode": "Markdown"
    }
    headers = {
        "Host": "api.telegram.org", 
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            print(f"🚀 [SIGNAL SENT] {ASSET} -> {pattern_name} ({direction})")
        else:
            # Fallback agar direct IP ko koi issue ho
            normal_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(normal_url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Telegram Delivery Error: {e}")

def detect_chart_patterns(df):
    """OTC Data points calculation matrix"""
    if len(df) < 5:
        return None, None
        
    c1 = df.iloc[-1]  # Current Closed Candle
    c2 = df.iloc[-2]  # Previous Candle
    
    c1_body = abs(c1['close'] - c1['open'])
    c1_green = c1['close'] > c1['open']
    c1_red = c1['close'] < c1['open']
    c2_green = c2['close'] > c2['open']
    c2_red = c2['close'] < c2['open']

    # 1. OTC Trend Continuation (Engulfing Breakout)
    if c2_red and c1_green and c1['close'] > c2['open'] and c1['open'] < c2['close']:
        return "OTC Bullish Engulfing", "UP"
    if c2_green and c1_red and c1['close'] < c2['open'] and c1['open'] > c2['close']:
        return "OTC Bearish Engulfing", "DOWN"
        
    # 2. OTC Algorithmic Reversal (Wick Rejection)
    c1_total_size = c1['high'] - c1['low']
    lower_wick = min(c1['open'], c1['close']) - c1['low']
    upper_wick = c1['high'] - max(c1['open'], c1['close'])
    
    if c1_total_size > 0 and lower_wick > (2 * c1_body) and upper_wick < (0.2 * c1_total_size):
        return "OTC Hammer (Price Action Reversal)", "UP"
    if c1_total_size > 0 and upper_wick > (2 * c1_body) and lower_wick < (0.2 * c1_total_size):
        return "OTC Shooting Star (Price Action Reversal)", "DOWN"
        
    return None, None

if __name__ == "__main__":
    print("--- INITIALIZING REAL-TIME QUOTEX ENGINE ---")
    
    if not EMAIL or not PASSWORD:
        print("❌ Error: Quotex credentials missing in setup environment.")
        exit(1)

    api = QuotexAPI(email=EMAIL, password=PASSWORD)
    check, reason = api.connect()

    if check:
        print(f"✅ Account Connected Successfully for {EMAIL}!")
        api.change_balance("PRACTICE")
        api.start_candles_stream(ASSET, size=TIMEFRAME)
        last_candle_time = 0
        
        print(f"📡 System Active! Tracking {ASSET} for Next Candle Predictions...\n")
        
        while True:
            try:
                if not api.check_connect():
                    print("⚠️ Connection lost, re-authenticating...")
                    api.connect()
                    api.start_candles_stream(ASSET, size=TIMEFRAME)
                    time.sleep(5)
                    continue
                    
                candles = api.get_candles(ASSET)
                if candles:
                    latest_candle = candles[-1]
                    
                    # Naye minute ki complete candle tick capture frame
                    if latest_candle['time'] > last_candle_time:
                        last_candle_time = latest_candle['time']
                        
                        candle_memory.append({
                            'time': latest_candle['time'],
                            'open': float(latest_candle['open']),
                            'high': float(latest_candle['high']),
                            'low': float(latest_candle['low']),
                            'close': float(latest_candle['close'])
                        })
                        
                        if len(candle_memory) > 100:
                            candle_memory.pop(0)
                            
                        df = pd.DataFrame(candle_memory)
                        pattern, direction = detect_chart_patterns(df)
                        
                        if pattern and direction:
                            send_telegram_signal(pattern, direction)
                            
            except Exception as e:
                print(f"⚠️ Loop Exception Alert: {e}")
                time.sleep(2)
            time.sleep(1)
    else:
        print(f"❌ Initialization Failed! Reason: {reason}")
    
