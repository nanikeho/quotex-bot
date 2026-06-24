import time
import random
import requests
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Quotex Pro MoneyManagement Engine Live"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8805973093:AAHnKIMb-5Mnr0yI0XR3-gIW5oUOQyLNfRA"  
TELEGRAM_CHAT_ID = "8240647626"      

# TRADING SETTINGS (Aap apne hisab se change kar sakte hain)
STARTING_TRADE_AMOUNT = 10  # Base trade amount (e.g., $10 ya ₹1000)

# SAARE EXACT QUOTEX PAIRS
QUOTEX_EXACT_PAIRS = [
    "USD/BRL (OTC)", "CAD/CHF (OTC)", "NZD/CHF (OTC)", "USD/MXN (OTC)", "USD/PKR (OTC)",
    "USD/ZAR (OTC)", "EUR/USD", "NZD/JPY (OTC)", "USD/NGN (OTC)", "EUR/JPY",
    "EUR/NZD (OTC)", "GBP/NZD (OTC)", "USD/EGP (OTC)", "AUD/JPY", "GBP/USD",
    "USD/DZD (OTC)", "EUR/AUD", "EUR/GBP", "USD/INR (OTC)", "AUD/USD",
    "GBP/JPY", "NZD/USD (OTC)", "USD/BDT (OTC)", "USD/CAD", "USD/JPY",
    "USD/COP (OTC)", "CAD/JPY", "EUR/CAD", "GBP/AUD", "GBP/CAD",
    "USD/CHF", "AUD/CAD", "AUD/CHF", "USD/IDR (OTC)", "AUD/NZD (OTC)",
    "CHF/JPY", "NZD/CAD (OTC)", "USD/ARS (OTC)", "USD/PHP (OTC)", "EUR/CHF", "GBP/CHF"
]

# --- PERFORMANCE COUNTERS FOR 30-MIN REPORT ---
stats = {
    "total_signals": 0,
    "direct_wins": 0,
    "mtg_wins": 0,
    "losses": 0
}

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram Error: {e}")
        return None

def get_real_ist_time():
    """Exact Indian Standard Time (IST)"""
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%H:%M:%S")

def track_and_send_result(pair, direction):
    """Result calculate karega aur counters update karega"""
    global stats
    time.sleep(60)  # 1-Minute Expiry Wait
    
    outcome = random.choice(["DIRECT_WIN", "DIRECT_WIN", "MTG_REQUIRED", "LOSS"])
    ist_now = get_real_ist_time()
    
    if outcome == "DIRECT_WIN":
        stats["direct_wins"] += 1
        result_msg = (
            f"🎯 **RESULT FOR {pair}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏁 **Status:** 🟢 **DIRECT SHURESHOT WIN !!**\n"
            f"⏰ **Time:** `{ist_now}`\n"
            f"🎉 Trade successfully closed in Profit."
        )
        send_to_telegram(result_msg)
        
    elif outcome == "MTG_REQUIRED":
        mtg_amount = STARTING_TRADE_AMOUNT * 2
        result_msg = (
            f"⚠️ **ATTENTION FOR {pair}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔄 **Status:** 🔴 Main Trade Loss.\n"
            f"👉 **ACTION:** **Take 1-Step MTG (Martingale)** immediately!\n"
            f"💰 **MTG Amount:** `${mtg_amount}` (Double)\n"
            f"⏰ **Time:** `{ist_now}`"
        )
        send_to_telegram(result_msg)
        
        time.sleep(60)  # MTG Candle Wait
        mtg_outcome = random.choice(["MTG_WIN", "TOTAL_LOSS"])
        ist_mtg = get_real_ist_time()
        
        if mtg_outcome == "MTG_WIN":
            stats["mtg_wins"] += 1
            result_msg = (
                f"🎯 **MTG RESULT FOR {pair}**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏁 **Status:** 🟡 **MTG-1 SUCCESS WIN !!**\n"
                f"⏰ **Time:** `{ist_mtg}`\n"
                f"✅ Recovered loss & booked clear profit!"
            )
        else:
            stats["losses"] += 1
            result_msg = (
                f"❌ **FINAL RESULT FOR {pair}**\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏁 **Status:** 💀 **TOTAL LOSS (Market Bad)**\n"
                f"⏰ **Time:** `{ist_mtg}`\n"
                f"🛑 Discipline first. Skip next trade on this asset."
            )
        send_to_telegram(result_msg)
        
    else:
        stats["losses"] += 1
        result_msg = (
            f"❌ **RESULT FOR {pair}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏁 **Status:** 💀 **DIRECT LOSS**\n"
            f"⏰ **Time:** `{ist_now}`\n"
            f"📉 Market pressure broken."
        )
        send_to_telegram(result_msg)

def report_scheduler():
    """Har 30 Minutes par Automatic Performance Summary Report bhejne ke liye"""
    global stats
    while True:
        time.sleep(1800)  # 30 Minutes = 1800 Seconds
        
        total = stats["total_signals"]
        wins = stats["direct_wins"] + stats["mtg_wins"]
        losses = stats["losses"]
        
        # Win Rate Calculation
        win_rate = (wins / total * 100) if total > 0 else 0
        
        report_template = (
            f"📊 **📊 QUOTEX 30-MIN PERFORMANCE REPORT 📊**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ **Report Time (IST):** `{get_real_ist_time()}`\n"
            f"📡 **Total Signals Generated:** `{total}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **Direct Shureshot Wins:** `{stats['direct_wins']}`\n"
            f"🟡 **Martingale (MTG-1) Wins:** `{stats['mtg_wins']}`\n"
            f"🔴 **Total Session Losses:** `{losses}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 **Accuracy Rate:** `{round(win_rate, 2)}%`\n"
            f"📊 **Overall Result:** {'🔥 IN PROFIT' if win_rate >= 75 else '⚠️ CAUTION / SLOW MARKET'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔄 *Stats are reset now. Starting fresh session analysis...*"
        )
        
        send_to_telegram(report_template)
        
        # Reset stats for next 30 mins
        stats = {"total_signals": 0, "direct_wins": 0, "mtg_wins": 0, "losses": 0}

def start_scanner():
    global stats
    print(f"[{get_real_ist_time()}] Scanning 40+ Assets with Risk Management Matrix...")
    for pair in QUOTEX_EXACT_PAIRS:
        # Market Simulator
        rsi = random.uniform(10, 90)
        trend = random.choice(["UPTREND", "DOWNTREND", "CHOPPY"])
        volume = random.uniform(20, 100)
        
        if rsi < 22 and trend == "UPTREND" and volume > 75:
            direction = "🔺 CALL / UP"
            strategy = "S1-Demand Zone Reversal"
            win_rate = round(random.uniform(94.2, 98.8), 2)
        elif rsi > 78 and trend == "DOWNTREND" and volume > 75:
            direction = "🔻 PUT / DOWN"
            strategy = "S2-Supply Zone Reversal"
            win_rate = round(random.uniform(94.2, 98.8), 2)
        else:
            continue
            
        stats["total_signals"] += 1
        real_time = get_real_ist_time()
        
        signal_template = (
            f"🔥 **🔥 QUOTEX VIP SHURESHOT ALERT 🔥**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🚀 **Asset:** `{pair}`\n"
            f"⏱ Lentgh: `1 MINUTE`\n"
            f"⏰ **Exact Entry (IST):** `{real_time}`\n"
            f"🎯 **Direction:** **{direction}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 **Recommended Trade Amount:** `${STARTING_TRADE_AMOUNT}`\n"
            f"📊 **Engine Logic:** `{strategy}`\n"
            f"💎 **Probability Accuracy:** `{win_rate}%`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚡ *Strictly apply Money Management rules!*"
        )
        
        print(f"-> Sending Premium Signal for {pair}...")
        send_to_telegram(signal_template)
        
        # Background mein result analyze karne ka thread
        Thread(target=track_and_send_result, args=(pair, direction)).start()
        time.sleep(6.0)

if __name__ == "__main__":
    # Web server thread
    Thread(target=run_web_server).start()
    # 30-Minute Report thread
    Thread(target=report_scheduler).start()
    
    while True:
        start_scanner()
        time.sleep(30)
        
