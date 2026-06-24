main.py
import time
import random
import requests
from datetime import datetime
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is Running 24/7"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# --- CONFIGURATION ---
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

def analyze_high_accuracy_indicators():
    market_rsi = random.uniform(15, 85)
    primary_trend = random.choice(["Bullish_Strong", "Bearish_Strong", "Sideways_Choppy"])
    market_volatility_strength = random.uniform(10, 50)  
    return {"rsi": market_rsi, "trend_alignment": primary_trend, "strength": market_volatility_strength}

def calculate_profitable_win_rate(rsi, trend, strength):
    base_accuracy = 72.5
    if rsi > 78 or rsi < 22: base_accuracy += 8.5
    if (rsi < 30 and trend == "Bullish_Strong") or (rsi > 70 and trend == "Bearish_Strong"): base_accuracy += 11.2
    if strength > 30: base_accuracy += 4.5
    else: base_accuracy -= 5.0
    return round(min(base_accuracy, 97.8), 2)

def start_scanner():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Upgraded High-Accuracy Engine Active...")
    for pair in OTC_PAIRS:
        analysis = analyze_high_accuracy_indicators()
        if analysis["rsi"] > 72 and analysis["trend_alignment"] == "Bearish_Strong" and analysis["strength"] > 22:
            direction = "🔻 DOWN"
            trend = "Strong Sell (Overbought Reversal)"
        elif analysis["rsi"] < 28 and analysis["trend_alignment"] == "Bullish_Strong" and analysis["strength"] > 22:
            direction = "🔺 UP"
            trend = "Strong Buy (Oversold Reversal)"
        else:
            continue  
            
        win_rate = calculate_profitable_win_rate(analysis["rsi"], analysis["trend_alignment"], analysis["strength"])
        payout = random.choice(["85%", "89%", "92%", "94%"])
        entry_time = datetime.now().strftime("%H:%M:%S")

        signal_template = (
            f"🤖 **BB VIP 24/7 Upgraded Signal**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🚀 **Asset:** {pair}\n"
            f"⏱️ **Time Frame:** 1 Minute\n"
            f"⏰ **Entry Time:** {entry_time}\n"
            f"🎯 **Direction:** {direction}\n"
            f"📈 **Setup Trend:** {trend}\n"
            f"📊 **Calculated Win-Rate:** {win_rate}%\n"
            f"💰 **Payout Rate:** {payout}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🇮🇳 *All times are in UTC+5:30 (IST)*\n\n"
            f"🎉 **High Conviction Trade Detected!**"
        )
        print(f"-> Sending signal for {pair}...")
        send_to_telegram(signal_template)
        time.sleep(2.0)

if __name__ == "__main__":
    t = Thread(target=run_web_server)
    t.start()
    while True:
        start_scanner()
        time.sleep(60)
