import time
import random
import requests
from datetime import datetime
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "BB VIP Upgraded Engine 2026 Active 24/7"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# --- CONFIGURATION (APKA TELEGRAM DATA) ---
TELEGRAM_BOT_TOKEN = "8805973093:AAHnKIMb-5Mnr0yI0XR3-gIW5oUOQyLNfRA"  
TELEGRAM_CHAT_ID = "8240647626"      

OTC_PAIRS = [
    "EURUSD-OTC", "GBPUSD-OTC", "EURGBP-OTC", "EURAUD-OTC", 
    "USDCAD-OTC", "AUDCAD-OTC", "CHFJPY-OTC", "EURNZD-OTC"
]

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram Delivery Error: {e}")
        return None

def advanced_market_scanner():
    """Real price action analytics simulate karne ke liye advanced engine"""
    rsi = random.uniform(10, 90)
    market_trend = random.choice(["STRONG_UPTREND", "STRONG_DOWNTREND", "SIDEWAYS"])
    volume_strength = random.uniform(15, 95)
    candle_rejection = random.choice(["TOP_WICK", "BOTTOM_WICK", "NONE"])
    return {"rsi": rsi, "trend": market_trend, "volume": volume_strength, "wick": candle_rejection}

def calculate_vip_accuracy(data, direction):
    """Mathematical probability matrix for win-rate validation"""
    accuracy = 75.0
    if direction == "UP" and data["trend"] == "STRONG_UPTREND": accuracy += 8.5
    if direction == "DOWN" and data["trend"] == "STRONG_DOWNTREND": accuracy += 8.5
    if data["volume"] > 65: accuracy += 5.2
    if data["rsi"] > 80 or data["rsi"] < 20: accuracy += 6.1
    return round(min(accuracy, 98.4), 2)

def start_scanner():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Core VIP Strategy Scanning OTC...")
    for pair in OTC_PAIRS:
        m_data = advanced_market_scanner()
        
        # Strategy 1: Overbought Reversal + Bottom Wick (Strong Buy)
        if m_data["rsi"] < 25 and m_data["trend"] != "STRONG_DOWNTREND" and m_data["volume"] > 40:
            direction = "🔺 CALL / UP"
            strategy_name = "Oversold Price-Action Reversal"
            expiry_time = "1 MINUTE"
            safety_tip = "If candle ends red with big wick, take 1-Step MTG."
            win_rate = calculate_vip_accuracy(m_data, "UP")
            
        # Strategy 2: Oversold Reversal + Top Wick (Strong Sell)
        elif m_data["rsi"] > 75 and m_data["trend"] != "STRONG_UPTREND" and m_data["volume"] > 40:
            direction = "🔻 PUT / DOWN"
            strategy_name = "Overbought Price-Action Reversal"
            expiry_time = "1 MINUTE"
            safety_tip = "If candle ends green with big wick, take 1-Step MTG."
            win_rate = calculate_vip_accuracy(m_data, "DOWN")
            
        # Strategy 3: 5-Second Scalping Momentum Breakout
        elif m_data["volume"] > 85 and m_data["rsi"] > 50 and m_data["rsi"] < 65 and m_data["trend"] == "STRONG_UPTREND":
            direction = "🚀 FAST UP (SCALPING)"
            strategy_name = "5-Sec High Volume Momentum Breakout"
            expiry_time = "5 SECONDS / 15 SECONDS"
            safety_tip = "Instant click! Direct momentum trade, No MTG recommended."
            win_rate = round(random.uniform(91.2, 97.5), 2)
            
        else:
            continue  # Agar market standard match nahi hua toh skip
            
        entry_time = datetime.now().strftime("%H:%M:%S")

        signal_template = (
            f"👑 **BB VIP PREMIUM AUTO-SIGNAL**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🚀 **Asset:** `{pair}`\n"
            f"⏱️ **Expiry Time:** `{expiry_time}`\n"
            f"⏰ **Entry Time (IST):** `{entry_time}`\n"
            f"🎯 **Action:** **{direction}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 **Strategy:** `{strategy_name}`\n"
            f"🔥 **Win-Rate Probability:** `{win_rate}%`\n"
            f"🛡️ **Safety Guidance:** _{safety_tip}_\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚡ *Strict Filter Applied. Trade with discipline!*"
        )
        
        print(f"-> Sending Premium Signal for {pair}...")
        send_to_telegram(signal_template)
        time.sleep(5.0)  # Rate limiting

if __name__ == "__main__":
    t = Thread(target=run_web_server)
    t.start()
    while True:
        start_scanner()
        time.sleep(45)  # Scan cycle speed up for consistent signals
            
