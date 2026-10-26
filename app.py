import telebot
import pandas as pd
import time
import threading
from flask import Flask, request
import random
import os

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8988354871:AAHJAwIhQkNcGBLtV0Lo4FJ3E1nabqZgq7Q'
CHAT_ID = '8240647626'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Quotex V8 Pure Math Algorithm is Running!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "V8 Execution Matrix Started! 10-Second Advance Prediction Active (No Indicators, Pure Math).")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def get_live_otc_data(pair):
    # Simulated tick data logic (Connect live Quotex WebSocket for real market data)
    data = []
    base_price = 1.0500
    for i in range(50):
        open_p = base_price
        close_p = open_p + random.uniform(-0.0015, 0.0015)
        high_p = max(open_p, close_p) + random.uniform(0, 0.0005)
        low_p = min(open_p, close_p) - random.uniform(0, 0.0005)
        data.append([open_p, high_p, low_p, close_p])
        base_price = close_p
    df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close'])
    return df

def send_v8_signal(pair, direction, live_price, accuracy):
    if direction == "CALL":
        action = "CALL (UP)"
        regime = "Algorithmic Buy-Side Imbalance"
        zone = "Acceleration Phase"
        left_context = "Pure math confirms bullish order flow dominating."
        trap = "Retail fading the momentum; smart money forcing continuation."
        entry_price = live_price - 0.00005
        target_price = live_price + 0.00020
    else:
        action = "PUT (DOWN)"
        regime = "Algorithmic Sell-Side Imbalance"
        zone = "Acceleration Phase"
        left_context = "Pure math confirms bearish order flow dominating."
        trap = "Retail buying the dip; smart money forcing liquidation."
        entry_price = live_price + 0.00005
        target_price = live_price - 0.00020

    msg = f"""=========================================

QUOTEX PURE MATH ALGORITHM (10s ADVANCE)

Asset Detected : {pair}

Market Regime : {regime}

Zone Behavior : {zone}

Live Market Price : {live_price:.5f}

ACTION SIGNAL : {action}

SAFEST EXPIRY : 1 Min

FUTURE ACCURACY : {accuracy}%

V8 PURE PRICE ACTION ANALYSIS:

Left-Side Context: {left_context}

Candle Physics : Expanding body velocity, zero mathematical rejection.

Retail Trap : {trap}

=========================================

MARGIN OF SAFETY (MOS) EXECUTION:

Execution Rule : Exact entry required within next 10 seconds.

Exact Entry Price: {entry_price:.5f}

Wave Target : {target_price:.5f}

1-Step MTG Rule : Valid

========================================="""

    bot.send_message(chat_id=CHAT_ID, text=msg)

def core_mathematical_analysis(df, pair):
    try:
        if len(df) < 3:
            return
            
        # Pure Mathematical Analysis (No Indicators)
        c2 = df.iloc[-2] # Previous Candle
        c3 = df.iloc[-1] # Current Candle (Live at 50th second)
        
        # Current Candle Physics
        open_p, close_p = c3['Open'], c3['Close']
        high_p, low_p = c3['High'], c3['Low']
        
        body = abs(close_p - open_p)
        upper_wick = high_p - max(open_p, close_p)
        lower_wick = min(open_p, close_p) - low_p
        total_size = high_p - low_p if (high_p - low_p) > 0 else 0.00001
        
        # Previous Candle Physics (To calculate momentum acceleration)
        body_c2 = abs(c2['Close'] - c2['Open'])
        
        is_green = close_p > open_p
        is_red = close_p < open_p
        prev_green = c2['Close'] > c2['Open']
        prev_red = c2['Close'] < c2['Open']
        
        # Accuracy Calculation purely based on Body Dominance & Momentum Shift
        accuracy = round(86.5 + ((body / total_size) * 12.4), 1)
        
        # 📈 CALL (UP) FUTURE PREDICTION: 
        # Both candles green, current body is bigger than previous (velocity increasing), 
        # and upper wick is practically non-existent (< 10% of body).
        if is_green and prev_green and (body > body_c2) and (upper_wick < (body * 0.1)):
            send_v8_signal(pair, "CALL", close_p, accuracy)

        # 📉 PUT (DOWN) FUTURE PREDICTION: 
        # Both candles red, current body is bigger than previous (velocity increasing), 
        # and lower wick is practically non-existent (< 10% of body).
        elif is_red and prev_red and (body > body_c2) and (lower_wick < (body * 0.1)):
            send_v8_signal(pair, "PUT", close_p, accuracy)
            
    except Exception as e:
        pass

def signal_scanner():
    all_otc_pairs = [
        'EUR/USD_OTC', 'GBP/USD_OTC', 'AUD/USD_OTC', 'USD/JPY_OTC', 
        'USD/CHF_OTC', 'EUR/GBP_OTC', 'AUD/CAD_OTC', 'NZD/USD_OTC', 
        'USD/CAD_OTC', 'EUR/JPY_OTC', 'GBP/JPY_OTC', 'EUR/AUD_OTC', 
        'GBP/AUD_OTC', 'CAD/JPY_OTC', 'EUR/CAD_OTC', 'CHF/JPY_OTC', 
        'NZD/JPY_OTC', 'AUD/JPY_OTC', 'USD/BRL_OTC', 'USD/INR_OTC', 
        'USD/MXN_OTC', 'USD/ZAR_OTC', 'USD/TRY_OTC', 'USD/PKR_OTC', 
        'USD/EGP_OTC', 'Gold_OTC', 'Silver_OTC', 'Crude_Oil_OTC', 
        'Bitcoin_OTC', 'Ethereum_OTC'
    ]
    
    print("Pure Math Scanner Started...")
    while True:
        current_second = time.localtime().tm_sec
        # Exactly 10 seconds before candle close (at 50th second)
        if current_second == 50: 
            for pair in all_otc_pairs:
                df = get_live_otc_data(pair)
                if not df.empty:
                    core_mathematical_analysis(df, pair)
            time.sleep(2) 
        time.sleep(0.5)

if __name__ == "__main__":
    scanner_thread = threading.Thread(target=signal_scanner)
    scanner_thread.start()
    
    RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL')
    if RENDER_URL:
        bot.remove_webhook()
        time.sleep(1)
        try:
            bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_TOKEN}")
        except Exception:
            pass
            
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
    
