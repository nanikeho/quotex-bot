import time
import asyncio
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
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
        f"🤖 **QUOTEX HIGH-ACCURACY ALGO**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Asset**: `{asset.upper()}`\n"
        f"💰 **Live Price**: `{current_price}`\n"
        f"⚡ **Action**: *{prediction}*\n"
        f"🧠 **Math Logic**: `{reason}`\n"
        f"⏰ **Time**: `{time.strftime('%H:%M:%S')} IST`\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=5)
    except Exception as e:
        print(f"❌ Telegram Push Error: {e}")

# ==========================================
# 3. HIGH-ACCURACY MATHEMATICS ENGINE (BB + RSI)
# ==========================================
def analyze_real_data(asset_name, candles_data):
    """
    Quotex server se aayi real candles par Bollinger Band aur RSI analysis.
    """
    df = pd.DataFrame(candles_data)
    df['close'] = df['close'].astype(float)
    
    # Mathematical Indicators
    rsi_14 = RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
    
    # Bollinger Bands (Window 20, Std Dev 2)
    bb = BollingerBands(close=df['close'], window=20, window_dev=2)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]
    
    current_price = df['close'].iloc[-1]
    prediction = "NEUTRAL"
    reason = ""
    
    # 📉 PUT Logic: Price upper band ke bahar hai + RSI Overbought hai
    if current_price > bb_upper and rsi_14 > 70:
        prediction = "PUT (SELL) 🔴"
        reason = f"BB Upper Breakout + RSI ({rsi_14:.1f})"
        
    # 📈 CALL Logic: Price lower band ke bahar hai + RSI Oversold hai
    elif current_price < bb_lower and rsi_14 < 30:
        prediction = "CALL (BUY) 🟢"
        reason = f"BB Lower Breakout + RSI ({rsi_14:.1f})"
        
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
        
        # OTC Pairs ki List (Aap aur bhi add kar sakte hain)
        otc_pairs = [
            "EURUSD_otc", "GBPUSD_otc", "USDINR_otc", "USDBRL_otc", 
            "AUDCAD_otc", "EURJPY_otc", "GBPJPY_otc"
        ]
        
        while True:
            # Har pair ki 1-minute candle ka data nikalna
            for pair in otc_pairs:
                try:
                    candles = await client.get_candles(pair, 60, offset=0, period=30)
                    if candles:
                        analyze_real_data(pair, candles)
                except Exception as e:
                    # Agar kisi pair me error aaye toh skip kar dega
                    pass
                    
                await asyncio.sleep(1) # API ko spam hone se bachane ke liye 1 sec delay
                
            print(f"⏳ Scanning active... waiting for exact math setup. [{time.strftime('%H:%M:%S')}]")
            await asyncio.sleep(60) # 1 Minute wait (Next candle close hone tak)
            
    else:
        print("❌ Connection Failed. Email/Password check karein ya IP block hai.", message)

# ==========================================
# 5. STARTUP COMMAND
# ==========================================
if __name__ == "__main__":
    # 🛠️ TELEGRAM CONNECTION TEST (Script run hote hi test message aayega)
    print("📲 Sending Test Message to Telegram...")
    send_telegram_alert("TEST_ASSET", "TEST 🟢", "Checking Connection", 1.0500)
    
    # Asli bot shuru karein
    asyncio.run(real_time_bot())
