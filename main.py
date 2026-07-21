import time
import asyncio
import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from quotexapi.stable_api import Quotex

# ==========================================
# 1. TELEGRAM & QUOTEX CONFIGURATION
# ==========================================
# ⚠️ HAMESHA DEMO ACCOUNT KA EMAIL/PASSWORD USE KAREIN!
QUOTEX_EMAIL = "YOUR_QUOTEX_DEMO_EMAIL@gmail.com"
QUOTEX_PASSWORD = "YOUR_QUOTEX_PASSWORD"

# Aapki Telegram Details
TELEGRAM_BOT_TOKEN = "8805973093:AAHnKIMb-5Mnr0yI0XR3-gIW5oUOQyLNfRA"
TELEGRAM_CHAT_ID = "8240647626"

# ==========================================
# 2. TELEGRAM ALERT FUNCTION
# ==========================================
def send_telegram_alert(asset, prediction, reason, current_price):
    """
    Generate hone wale signal ko Telegram par bhejta hai.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    text = (
        f"🤖 **QUOTEX REAL-TIME MATH ENGINE**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Asset**: `{asset.upper()}`\n"
        f"💰 **Live Price**: `{current_price}`\n"
        f"⚡ **Signal Order**: *{prediction}*\n"
        f"🧠 **Math Logic**: `{reason}`\n"
        f"⏰ **Time**: `{time.strftime('%H:%M:%S')} IST`\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=5)
    except Exception as e:
        print(f"❌ Telegram Push Error: {e}")

# ==========================================
# 3. ALGORITHM MATHEMATICS ENGINE
# ==========================================
def analyze_real_data(asset_name, candles_data):
    """
    Quotex server se aayi real candles par mathematical analysis karta hai.
    """
    df = pd.DataFrame(candles_data)
    df['close'] = df['close'].astype(float)
    
    # Technical Indicators (Math)
    rsi_14 = RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
    ema_9 = EMAIndicator(close=df['close'], window=9).ema_indicator().iloc[-1]
    ema_21 = EMAIndicator(close=df['close'], window=21).ema_indicator().iloc[-1]
    
    current_price = df['close'].iloc[-1]
    prediction = "NEUTRAL"
    reason = ""
    
    # 📈 Algorithmic Rule 1: Uptrend Pullback
    if ema_9 > ema_21 and rsi_14 < 35:
        prediction = "CALL 🟢"
        reason = f"Uptrend EMA + RSI Oversold ({rsi_14:.1f})"
        
    # 📉 Algorithmic Rule 2: Downtrend Pullback
    elif ema_9 < ema_21 and rsi_14 > 65:
        prediction = "PUT 🔴"
        reason = f"Downtrend EMA + RSI Overbought ({rsi_14:.1f})"
        
    # ⚠️ Algorithmic Rule 3: Extreme Overbought (Mean Reversion)
    elif rsi_14 > 85:
        prediction = "STRONG PUT 🔴"
        reason = f"Extreme Math Overbought ({rsi_14:.1f})"
        
    # ⚠️ Algorithmic Rule 4: Extreme Oversold (Mean Reversion)
    elif rsi_14 < 15:
        prediction = "STRONG CALL 🟢"
        reason = f"Extreme Math Oversold ({rsi_14:.1f})"
        
    # Agar rule match hua toh terminal par print karega aur Telegram par bhejega
    if prediction != "NEUTRAL":
        print(f"[{time.strftime('%H:%M:%S')}] 🎯 SIGNAL GENERATED: {asset_name} -> {prediction}")
        send_telegram_alert(asset_name, prediction, reason, current_price)

# ==========================================
# 4. REAL-TIME DATA FETCH & EXECUTION LOOP
# ==========================================
async def real_time_bot():
    print("🔄 Connecting to Quotex Real-Time Server...")
    # Quotex me login kar raha hai
    client = Quotex(email=QUOTEX_EMAIL, password=QUOTEX_PASSWORD)
    
    check_connect, message = await client.connect()
    
    if check_connect:
        print("✅ Quotex Server Connected Successfully!\n" + "-"*50)
        
        # 33 OTC Pairs (Aap isme aur pairs add kar sakte hain)
        otc_pairs = [
            "EURUSD_otc", "GBPUSD_otc", "USDINR_otc", "USDBRL_otc", 
            "AUDCAD_otc", "EURJPY_otc", "GBPJPY_otc", "USDCHF_otc",
            "NZDUSD_otc", "AUDUSD_otc"
        ]
        
        while True:
            # Har pair ki 1-minute candle ka data nikalna
            for pair in otc_pairs:
                try:
                    candles = await client.get_candles(pair, 60, offset=0, period=30)
                    if candles:
                        analyze_real_data(pair, candles)
                except Exception as e:
                    pass
                    
                await asyncio.sleep(1) # IP block hone se bachane ke liye chhota delay
                
            print(f"⏳ Waiting for next 1-minute candle close... [{time.strftime('%H:%M:%S')}]")
            await asyncio.sleep(60) # 1 Minute wait (Next candle ke liye)
            
    else:
        print("❌ Connection Failed. Email/Password check karein ya IP Cloudflare se block hai.", message)

# Bot Run Command
if __name__ == "__main__":
    asyncio.run(real_time_bot())
