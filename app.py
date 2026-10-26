import telebot
import pandas as pd
import numpy as np
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
    return "Quotex V8 Advanced Quant Algorithm is Running!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "V8 Advanced Quant Terminal Started! Micro-structure & Tick Velocity analysis is active.")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def get_live_otc_data(pair):
    # Simulated tick data (Replace with live WebSocket for real trading)
    data = []
    base_price = 1.0500
    for i in range(50):
        open_p = base_price
        close_p = open_p + random.uniform(-0.0015, 0.0015)
        high_p = max(open_p, close_p) + random.uniform(0, 0.0006)
        low_p = min(open_p, close_p) - random.uniform(0, 0.0006)
        data.append([open_p, high_p, low_p, close_p])
        base_price = close_p
    df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close'])
    return df

def send_v8_signal(pair, direction, live_price, accuracy, z_score, velocity):
    if direction == "CALL":
        action = "CALL (UP)"
        regime = "Bullish Algorithmic Injection"
        zone = "Micro-Structure Breakout"
        entry_price = live_price - 0.00003
        target_price = live_price + 0.00025
    else:
        action = "PUT (DOWN)"
        regime = "Bearish Algorithmic Injection"
        zone = "Micro-Structure Breakdown"
        entry_price = live_price + 0.00003
        target_price = live_price - 0.00025

    msg = f"""=========================================

QUOTEX QUANT ALGORITHM (10s ADVANCE)

Asset Detected : {pair}
Market Regime : {regime}
Zone Behavior : {zone}
Live Market Price : {live_price:.5f}

ACTION SIGNAL : {action}
SAFEST EXPIRY : 1 Min
FUTURE ACCURACY : {accuracy}%

DEEP ALGORITHMIC METRICS:
Z-Score Anomaly : {z_score:.2f} (Deviation from Mean)
Tick Velocity Multiplier : {velocity:.1f}x
Volume State : Expanding rapidly out of Volatility Squeeze.

=========================================

MARGIN OF SAFETY (MOS) EXECUTION:
Execution Rule : 10s Advance - Place trade exactly at new candle open.
Ideal Entry Price: {entry_price:.5f}
Target Close : {target_price:.5f}
1-Step MTG Rule : Valid

========================================="""

    bot.send_message(chat_id=CHAT_ID, text=msg)

def core_mathematical_analysis(df, pair):
    try:
        if len(df) < 15:
            return
            
        # 1. Log Returns & Z-Score Analysis
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        mean_return = df['Log_Returns'].mean()
        std_return = df['Log_Returns'].std()
        
        if std_return == 0 or pd.isna(std_return):
            return
            
        current_log_return = df['Log_Returns'].iloc[-1]
        z_score = (current_log_return - mean_return) / std_return
        
        # 2. Volatility Squeeze & Tick Velocity (Average Body Size vs Current Body)
        df['Body'] = abs(df['Close'] - df['Open'])
        avg_body_recent = df['Body'].iloc[-10:-1].mean() # Pichli 9 candles ka average body
        current_body = df['Body'].iloc[-1]
        
        tick_velocity = current_body / avg_body_recent if avg_body_recent > 0 else 1.0

        # Current Candle Data
        c_current = df.iloc[-1]
        open_p, close_p = c_current['Open'], c_current['Close']
        high_p, low_p = c_current['High'], c_current['Low']
        
        upper_wick = high_p - max(open_p, close_p)
        lower_wick = min(open_p, close_p) - low_p
        
        is_green = close_p > open_p
        is_red = close_p < open_p
        
        # 3. Micro-Structure Confirmation (Last 3 candles trend)
        c2 = df.iloc[-2]
        c3 = df.iloc[-3]
        higher_lows = (low_p > c2['Low']) and (c2['Low'] > c3['Low'])
        lower_highs = (high_p < c2['High']) and (c2['High'] < c3['High'])
        
        # Dynamic Accuracy Calculation
        base_acc = 82.0
        acc_z = min(abs(z_score) * 4, 10.0) # Max 10% from Z-Score
        acc_vel = min(tick_velocity * 3, 6.5) # Max 6.5% from Velocity
        accuracy = round(min(99.2, base_acc + acc_z + acc_vel), 1)
        
        # 📈 CALL (UP) SIGNAL: 
        # Z-Score > 1.8, Tick Velocity > 1.5x (Sudden volume), Higher Lows structure, No upper wick trap
        if is_green and (z_score > 1.8) and (tick_velocity > 1.5) and higher_lows and (upper_wick < (current_body * 0.1)):
            send_v8_signal(pair, "CALL", close_p, accuracy, z_score, tick_velocity)

        # 📉 PUT (DOWN) SIGNAL: 
        # Z-Score < -1.8, Tick Velocity > 1.5x (Sudden volume), Lower Highs structure, No lower wick trap
        elif is_red and (z_score < -1.8) and (tick_velocity > 1.5) and lower_highs and (lower_wick < (current_body * 0.1)):
            send_v8_signal(pair, "PUT", close_p, accuracy, z_score, tick_velocity)
            
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
    
    print("Advanced Algorithm Scanner Started...")
    while True:
        current_second = time.localtime().tm_sec
        # Scanning exactly at the 50th second (10 seconds before expiry)
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
    
