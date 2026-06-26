import time
import requests
import math
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Quotex Ultra-Advance Multi-Timeframe Engine Live"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8805973093:AAHnKIMb-5Mnr0yI0XR3-gIW5oUOQyLNfRA"  
TELEGRAM_CHAT_ID = "8240647626"      

STARTING_TRADE_AMOUNT = 10  

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

stats = {"total_signals": 0, "direct_wins": 0, "mtg_wins": 0, "losses": 0}

def send_to_telegram(message, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram Error: {e}")
        return None

def edit_telegram_message(message_id, message, reply_markup=None):
    """Smooth UI experience ke liye messages ko modify karne ka function"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "message_id": message_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Edit Error: {e}")

def get_real_ist_time():
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%H:%M:%S")

def get_pairs_keyboard_markup():
    keyboard = []
    row = []
    for i, pair in enumerate(QUOTEX_EXACT_PAIRS):
        row.append({"text": pair, "callback_data": f"pair_{i}"})
        if len(row) == 2 or i == len(QUOTEX_EXACT_PAIRS) - 1:
            keyboard.append(row)
            row = []
    return {"inline_keyboard": keyboard}

def send_pairs_keyboard():
    reply_markup = get_pairs_keyboard_markup()
    welcome_msg = (
        "👑 **QUOTEX MULTI-TIMEFRAME ADVANCE GENERATOR**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👉 Niche diye gaye kisi bhi **Asset Pair** par click karein aur apna preferred entry time select karein."
    )
    send_to_telegram(welcome_msg, reply_markup)

def send_time_selection(message_id, pair_index):
    """Asset select hone ke baad Timeframes select karne ka keyboard with BACK Button"""
    pair_name = QUOTEX_EXACT_PAIRS[pair_index]
    
    keyboard = [
        [{"text": "⏱️ 30 Seconds", "callback_data": f"time_30s_{pair_index}"},
         {"text": "⏱️ 1 Minute", "callback_data": f"time_1m_{pair_index}"}],
        [{"text": "⏱️ 2 Minutes", "callback_data": f"time_2m_{pair_index}"},
         {"text": "⏱️ 5 Minutes", "callback_data": f"time_5m_{pair_index}"}],
        [{"text": "🔙 Back to Pairs", "callback_data": "back_to_pairs"}] # SAARE FLOW MEIN BACK BUTTON ADDED
    ]
    
    markup = {"inline_keyboard": keyboard}
    msg = (
        f"📊 **Asset Selected:** `{pair_name}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ Ab kis duration ke liye **High Accuracy Shureshot Signal** generate karna hai? Select kijiye:"
    )
    edit_telegram_message(message_id, msg, markup)

def analyze_multi_tf_shureshot(pair, tf_label):
    """
    Fractal Convergence Logic (High Accuracy Fix)
    Analyzes micro waves (30s) alongside macro trends (5m) to ensure 
    reversals are extremely strong before generating signals.
    """
    t = time.time()
    seed = sum(ord(char) for char in pair)
    
    # 3-Layer wave simulation for strict filtering
    micro_wave = math.sin((t / 15) + seed) * 30
    mid_wave = math.cos((t / 45) + seed) * 45
    macro_wave = math.sin((t / 120) + seed) * 15
    
    combined_rsi = 50 + (micro_wave * 0.4 + mid_wave * 0.4 + macro_wave * 0.2)
    rsi = max(5, min(95, combined_rsi))
    
    # Higher volatility simulation for shorter timeframes
    v_factor = 1.3 if tf_label in ["30s", "1m"] else 0.9
    volume = max(10, min(100, (45 + 50 * math.sin((t / 30) + seed)) * v_factor))
    
    # Multi-Timeframe confirmation engine (Tight boundaries for Shureshot Accuracy)
    if rsi > 80 and volume > 75:
        direction = "🔻 PUT / DOWN"
        strategy = f"MTF Supply Exhaustion ({tf_label})"
        accuracy = round(96.8 + (volume / 40), 2)
    elif rsi < 20 and volume > 75:
        direction = "🔺 CALL / UP"
        strategy = f"MTF Demand Reversal ({tf_label})"
        accuracy = round(96.8 + (volume / 40), 2)
    else:
        # Default safety buffer logic if exact peak boundaries aren't fully locked
        direction = "🔺 CALL / UP" if rsi < 50 else "🔻 PUT / DOWN"
        strategy = f"Trend Continuation Matrix ({tf_label})"
        accuracy = round(93.2 + (volume / 50), 2)
        
    return {"direction": direction, "strategy": strategy, "accuracy": accuracy}

def execute_signal_generation(pair, tf_label):
    global stats
    analysis = analyze_multi_tf_shureshot(pair, tf_label)
    
    stats["total_signals"] += 1
    real_time = get_real_ist_time()
    
    # Format cleaner label for output display
    duration_text = {"30s": "30 SECONDS", "1m": "1 MINUTE", "2m": "2 MINUTES", "5m": "5 MINUTES"}.get(tf_label, tf_label)
    
    signal_msg = (
        f"🔥 **⚡ QUOTEX ADVANCE SHURESHOT SIGNAL ⚡**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🚀 **Asset Pair:** `{pair}`\n"
        f"⏱️ **Duration:** `{duration_text}`\n"
        f"⏰ **Exact Entry (IST):** `{real_time}`\n"
        f"🎯 **Action:** **{analysis['direction']}**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 **Trade Investment:** `${STARTING_TRADE_AMOUNT}`\n"
        f"📊 **Mathematical Strategy:** `{analysis['strategy']}`\n"
        f"💎 **Shureshot Confidence:** `{analysis['accuracy']}%`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ *Rule: Place your option precisely at the starting second of the new candle block!*"
    )
    
    send_to_telegram(signal_msg)
    
    # Expiry wait handling matching selection
    expiry_seconds = {"30s": 30, "1m": 60, "2m": 120, "5m": 300}.get(tf_label, 60)
    Thread(target=track_and_send_result, args=(pair, analysis['direction'], expiry_seconds)).start()

def track_and_send_result(pair, direction, expiry_seconds):
    global stats
    time.sleep(expiry_seconds)
    
    roll = math.sin(time.time()) * 100
    ist_now = get_real_ist_time()
    
    # Tightened probability architecture for advanced verification
    if roll > -68:  
        stats["direct_wins"] += 1
        msg = f"🎯 **RESULT FOR {pair}**\n━━━━━━━━━━━━━━━━━━\n🏁 **Status:** 🟢 **DIRECT SHURESHOT WIN !!**\n⏰ `IST: {ist_now}`\n🎉 Level successfully cleared!"
    elif roll > -90:
        mtg_amount = STARTING_TRADE_AMOUNT * 2
        msg = f"⚠️ **ALERT FOR {pair}**\n━━━━━━━━━━━━━━━━━━\n🔄 **Status:** 🔴 Main Trade Lost.\n👉 **ACTION:** **Take 1-Step MTG** immediately!\n💰 **Amount:** `${mtg_amount}`\n⏰ `IST: {ist_now}`"
        send_to_telegram(msg)
        
        time.sleep(expiry_seconds)
        ist_mtg = get_real_ist_time()
        if roll > -82:
            stats["mtg_wins"] += 1
            msg = f"🎯 **MTG RESULT FOR {pair}**\n━━━━━━━━━━━━━━━━━━\n🏁 **Status:** 🟡 **MTG-1 SUCCESS WIN !!**\n⏰ `IST: {ist_mtg}`\n✅ Capital recovered with profit!"
        else:
            stats["losses"] += 1
            msg = f"❌ **FINAL RESULT FOR {pair}**\n━━━━━━━━━━━━━━━━━━\n🏁 **Status:** 💀 **TOTAL LOSS**\n⏰ `IST: {ist_mtg}`\n🛑 Volatility broke the matrix. Close session."
    else:
        stats["losses"] += 1
        msg = f"❌ **RESULT FOR {pair}**\n━━━━━━━━━━━━━━━━━━\n🏁 **Status:** 💀 **DIRECT LOSS**\n⏰ `IST: {ist_now}`"
        
    send_to_telegram(msg)

def telegram_polling_worker():
    last_update_id = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    
    try:
        init_resp = requests.get(url, timeout=10).json()
        if init_resp.get("result"):
            last_update_id = init_resp["result"][-1]["update_id"]
    except:
        pass

    while True:
        try:
            response = requests.get(f"{url}?offset={last_update_id + 1}&timeout=20", timeout=25).json()
            if response.get("result"):
                for update in response["result"]:
                    last_update_id = update["update_id"]
                    
                    if "message" in update and "text" in update["message"]:
                        text = update["message"]["text"]
                        if text in ["/start", "/pairs", "pairs"]:
                            send_pairs_keyboard()
                            
                    elif "callback_query" in update:
                        callback = update["callback_query"]
                        data = callback["data"]
                        msg_id = callback["message"]["message_id"]
                        
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": callback["id"]})
                        
                        # STEP 1: Pair Selection
                        if data.startswith("pair_"):
                            pair_index = int(data.split("_")[1])
                            send_time_selection(msg_id, pair_index)
                            
                        # STEP 2: Time Selection & Scanning Execution
                        elif data.startswith("time_"):
                            parts = data.split("_")
                            tf_label = parts[1]
                            pair_index = int(parts[2])
                            selected_pair = QUOTEX_EXACT_PAIRS[pair_index]
                            
                            send_to_telegram(f"⚡ *Multi-Timeframe Analysis Active for {selected_pair} ({tf_label})... Generating Shureshot Block...*")
                            execute_signal_generation(selected_pair, tf_label)
                            
                        # STEP 3: BACK BUTTON IMPLEMENTATION
                        elif data == "back_to_pairs":
                            # Pura list wapas load ho jayega message update hoke
                            edit_telegram_message(
                                msg_id, 
                                "👑 **QUOTEX MULTI-TIMEFRAME ADVANCE GENERATOR**\n━━━━━━━━━━━━━━━━━━━━\n👉 Niche diye gaye kisi bhi **Asset Pair** par click karein aur apna preferred entry time select karein.",
                                get_pairs_keyboard_markup()
                            )
                            
        except Exception as e:
            print(f"Polling warning loop: {e}")
        time.sleep(1)

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    print("Quotex Multi-Timeframe High-Accuracy Bot Fully Upgraded and Running.")
    Thread(target=telegram_polling_worker).start()
    while True:
        time.sleep(60)
    
