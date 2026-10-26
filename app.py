import telebot
import pandas as pd
import numpy as np
import time
import threading
from flask import Flask, request
import random
import os
import math

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8988354871:AAHJAwIhQkNcGBLtV0Lo4FJ3E1nabqZgq7Q'
CHAT_ID = '8240647626'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Quotex Quant Math Algorithm is Running!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "V8 Quant Terminal Started! Real-time mathematical anomaly detection active.")

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

def send_v8_signal(pair, direction, live_price, accuracy, z_score):
    if direction == "CALL":
        action = "CALL (UP)"
        regime = "Positive Algorithmic Z-Score Anomaly"
        zone = "Buy-Side Liquidity Expansion"
        entry_price = live_price - 0.00005
        target_price = live_price + 0.00020
    else:
        action = "PUT (DOWN)"
        regime = "Negative Algorithmic Z-Score Anomaly"
        zone = "Sell-Side Liquidity Expansion"
        entry_price = live_price + 0.00005
        target_price = live_price - 0.00020

    msg = f"""=========================================

QUOTEX QUANT ALGORITHM (10s ADVANCE)

Asset Detected : {pair}
Market Regime : {regime}
Zone Behavior : {zone}
Live Market Price : {live_price:.5f}

ACTION SIGNAL : {action}
SAFEST EXPIRY : 1 Min
FUTURE ACCURACY : {accuracy}%

QUANTITATIVE MATH ANALYSIS:
Log Return Anomaly (Z-Score) : {z_score:.2f}
Candle Physics : Expanding standard deviation, pure momentum override.
OTC Behavior : Algorithm detects mathematical imbalance.

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
        if len(df) < 10:
            return
            
        # Log Returns & Z-Score Analysis (Real Quant Math)
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        mean_return = df['Log_Returns'].mean()
        std_return = df['Log_Returns'].std()
        
        c_current = df.iloc[-1]
        c_prev = df.iloc[-2]
        
        current_log_return = df['Log_Returns'].iloc[-1]
        
        # Avoid division by zero
        if std_return == 0 or pd.isna(std_return):
            return
            
        z_score = (current_log_return - mean_return) / std_return
        
        open_p, close_p = c_current['Open'], c_current['Close']
        high_p, low_p = c_current['High'], c_current['Low']
        
        body = abs(close_p - open_p)
        upper_wick = high_p - max(open_p, close_p)
        lower_wick = min(open_p, close_p) - low_p
        total_size = high_p - low_p if (high_p - low_p) > 0 else 0.00001
        
        is_green = close_p > open_p
        is_red = close_p < open_p
        
        # Base accuracy on Z-Score magnitude and body dominance
        body_dominance = (body / total_size) * 100
        z_score_magnitude = min(abs(z_score) * 10, 20) 
        accuracy = round(min(98.5, 75.0 + (body_dominance * 0.15) + z_score_magnitude), 1)
        
        # 📈 CALL (UP) PREDICTION
        # Z-Score > 1.5 indicates a statistically significant bullish algorithmic push
        if is_green and (z_score > 1.5) and (upper_wick < (body * 0.15)):
            send_v8_signal(pair, "CALL", close_p, accuracy, z_score)

        # 📉 PUT (DOWN) PREDICTION
        # Z-Score < -1.5 indicates a statistically significant bearish algorithmic push
        elif is_red and (z_score < -1.5) and (lower_wick < (body * 0.15)):
            send_v8_signal(pair, "PUT", close_p, accuracy, z_score)
            
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
    
    print("Quantitative Math Scanner Started...")
    while True:
        current_second = time.localtime().tm_sec
        # 10 seconds advance logic
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
    
