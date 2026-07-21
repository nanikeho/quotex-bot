import time
import asyncio
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from quotexapi.stable_api import Quotex

# ==========================================
# 1. QUOTEX ACCOUNT LOGIN (DEMO ACCOUNT USE KAREIN)
# ==========================================
email = "nanikeho@gmail.com"
password = "78907890@Ho"

# ==========================================
# 2. ALGORITHM MATHEMATICS ENGINE
# ==========================================
def analyze_real_data(asset_name, candles_data):
    """
    Quotex server se aayi real candles par mathematical analysis karta hai.
    """
    # Convert live data to Pandas DataFrame for Math calculation
    df = pd.DataFrame(candles_data)
    df['close'] = df['close'].astype(float)
    
    # Mathematical Indicators using real 'close' prices
    rsi_14 = RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
    ema_9 = EMAIndicator(close=df['close'], window=9).ema_indicator().iloc[-1]
    ema_21 = EMAIndicator(close=df['close'], window=21).ema_indicator().iloc[-1]
    
    current_price = df['close'].iloc[-1]
    
    # Core Mathematical Signal Logic
    prediction = "NEUTRAL"
    
    # Algorithmic Rule 1: Uptrend + Oversold pullback
    if ema_9 > ema_21 and rsi_14 < 35:
        prediction = "CALL (BUY) 🟢"
        reason = f"Uptrend EMA + RSI Oversold ({rsi_14:.1f})"
        
    # Algorithmic Rule 2: Downtrend + Overbought pullback
    elif ema_9 < ema_21 and rsi_14 > 65:
        prediction = "PUT (SELL) 🔴"
        reason = f"Downtrend EMA + RSI Overbought ({rsi_14:.1f})"
        
    # Algorithmic Rule 3: Extreme Mean Reversion (Mathematical Exhaustion)
    elif rsi_14 > 85:
        prediction = "STRONG PUT 🔴"
        reason = f"Extreme Mathematical Overbought ({rsi_14:.1f})"
    elif rsi_14 < 15:
        prediction = "STRONG CALL 🟢"
        reason = f"Extreme Mathematical Oversold ({rsi_14:.1f})"
        
    if prediction != "NEUTRAL":
        print(f"[{time.strftime('%H:%M:%S')}] 🎯 ASSET: {asset_name} | PRICE: {current_price}")
        print(f"⚡ SIGNAL: {prediction} | LOGIC: {reason}")
        print("-" * 50)

# ==========================================
# 3. REAL-TIME DATA FETCH & EXECUTION LOOP
# ==========================================
async def real_time_bot():
    print("🔄 Connecting to Quotex Real-Time Server...")
    client = Quotex(email=email, password=password)
    
    check_connect, message = await client.connect()
    
    if check_connect:
        print("✅ Quotex Server Connected Successfully!\n" + "-"*50)
        
        # 33 OTC Pairs ki list
        otc_pairs = [
            "EURUSD_otc", "GBPUSD_otc", "USDINR_otc", "USDBRL_otc", 
            "AUDCAD_otc", "EURJPY_otc", "GBPJPY_otc" # Add all 33 here
        ]
        
        while True:
            # Har pair ke liye 1-minute time frame (60 seconds) ka real data mangwana
            for pair in otc_pairs:
                try:
                    # Fetching last 30 live candles of 1-minute (60s) timeframe
                    candles = await client.get_candles(pair, 60, offset=0, period=30)
                    
                    if candles:
                        # Pass REAL data to Mathematical Engine
                        analyze_real_data(pair, candles)
                        
                except Exception as e:
                    print(f"Error fetching data for {pair}: {e}")
                    
                await asyncio.sleep(1) # Server par spam na ho isliye chhota delay
                
            print(f"⏳ Waiting for next 1-minute candle close... [{time.strftime('%H:%M:%S')}]")
            await asyncio.sleep(60) # Wait for the next 1-minute candle to form
            
    else:
        print("❌ Connection Failed. Check Email/Password or IP Block.", message)

if __name__ == "__main__":
    asyncio.run(real_time_bot())
