import time
import os
import requests
import pandas as pd
import numpy as np
from quotexapi.stable_api import QuotexAPI

# ==================== CONFIGURATION (RENDER COMPATIBLE) ====================
# Yeh lines Render par aapke save kiye hue variables ko automatically utha lengi
EMAIL = os.environ.get("QUOTEX_EMAIL")
PASSWORD = os.environ.get("QUOTEX_PASSWORD")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

ASSET = "EURUSD"
TIMEFRAME = 60  # 60 seconds = 1 Minute
# ===========================================================================

# Memory Storage for Candles
candle_memory = []

def send_telegram_signal(pattern_name, direction):
    """Telegram par alert bhejne ka function"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    emoji = "🟩 CALL (UP)" if direction == "UP" else "🟥 PUT (DOWN)"
    
    message = (
        f"🚨 *QUOTEX LIVE PATTERN DETECTED* 🚨\n\n"
        f"🌐 *Asset:* {ASSET}\n"
        f"⏰ *Timeframe:* 1-Min\n"
        f"📊 *Pattern:* `{pattern_name}`\n"
        f"📈 *Signal:* *{emoji}*\n\n"
        f"⚠️ *Risk Warning:* Pattern formation ke baad next candle par confirmation zaroori hai."
    )
    
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
        print(f"[+] Signal Sent to Telegram: {pattern_name} -> {direction}")
    except Exception as e:
        print(f"[-] Telegram Error: {e}")

def detect_chart_patterns(df):
    """
    Live chart patterns ko memory (dataframe) se analyze aur detect karne ka engine
    """
    if len(df) < 5:
        return None, None

    # Latest aur pichli candles ka data nikalte hain
    c1 = df.iloc[-1]  # Jo candle abhi abhi close hui hai
    c2 = df.iloc[-2]  # Usse pehle wali candle
    
    # Candle Bodies and Size Calculation
    c1_body = abs(c1['close'] - c1['open'])
    c2_body = abs(c2['close'] - c2['open'])
    
    c1_green = c1['close'] > c1['open']
    c1_red = c1['close'] < c1['open']
    c2_green = c2['close'] > c2['open']
    c2_red = c2['close'] < c2['open']

    # --- 1. BULLISH ENGULFING PATTERN ---
    if c2_red and c1_green and c1['close'] > c2['open'] and c1['open'] < c2['close']:
        return "Bullish Engulfing", "UP"

    # --- 2. BEARISH ENGULFING PATTERN ---
    if c2_green and c1_red and c1['close'] < c2['open'] and c1['open'] > c2['close']:
        return "Bearish Engulfing", "DOWN"

    # --- 3. HAMMER PATTERN ---
    c1_total_size = c1['high'] - c1['low']
    lower_wick = min(c1['open'], c1['close']) - c1['low']
    upper_wick = c1['high'] - max(c1['open'], c1['close'])
    
    if c1_total_size > 0 and lower_wick > (2 * c1_body) and upper_wick < (0.2 * c1_total_size):
        return "Hammer (Bullish Reversal)", "UP"

    # --- 4. SHOOTING STAR PATTERN ---
    if c1_total_size > 0 and upper_wick > (2 * c1_body) and lower_wick < (0.2 * c1_total_size):
        return "Shooting Star (Bearish Reversal)", "DOWN"

    return None, None

# ==================== MAIN EXECUTION ====================
if not EMAIL or not PASSWORD or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("[-] CRITICAL ERROR: Environment Variables missing on Render!")
    exit(1)

api = QuotexAPI(email=EMAIL, password=PASSWORD)
print("[*] Connecting to Quotex via Cloud Server...")
check, reason = api.connect()

if check:
    print("[+] Connected Successfully!")
    api.change_balance("PRACTICE")
    api.start_candles_stream(ASSET, size=TIMEFRAME)
    print(f"[*] Started 1-Minute Live Stream for {ASSET}. Monitoring patterns...")
    
    last_candle_time = 0

    while True:
        try:
            # Reconnect Logic if connection drops
            if not api.check_connect():
                print("[-] Disconnected! Retrying connection...")
                api.connect()
                api.start_candles_stream(ASSET, size=TIMEFRAME)
                time.sleep(5)
                continue

            candles = api.get_candles(ASSET)
            if candles:
                latest_candle = candles[-1]
                
                # Check karein agar naya 1-minute candle close hua hai
                if latest_candle['time'] > last_candle_time:
                    last_candle_time = latest_candle['time']
                    
                    # Live data ko clean format mein memory list mein append karein
                    candle_memory.append({
                        'time': latest_candle['time'],
                        'open': float(latest_candle['open']),
                        'high': float(latest_candle['high']),
                        'low': float(latest_candle['low']),
                        'close': float(latest_candle['close'])
                    })
                    
                    # Memory Optimization: Sirf aakhri 100 candles ka data rakhein
                    if len(candle_memory) > 100:
                        candle_memory.pop(0)
                    
                    # List ko Dataframe mein convert karein analysis ke liye
                    df = pd.DataFrame(candle_memory)
                    
                    print(f"\n[+] Memory Updated. Total Candles in Memory: {len(df)}")
                    
                    # PATTERN DETECTION ENGINE TRIGGER
                    pattern, direction = detect_chart_patterns(df)
                    
                    if pattern and direction:
                        print(f"[🔥] MATCH FOUND: {pattern} -> Direction: {direction}")
                        send_telegram_signal(pattern, direction)
                    else:
                        print("[.] Monitoring... No strong pattern matched on this candle.")

        except Exception as e:
            print(f"[-] Runtime Error: {e}")
            time.sleep(5)
            
        time.sleep(1) # Check every second
else:
    print(f"[-] Connection Failed: {reason}")
    
