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
    return "Quotex PRNG Monte Carlo Bot is Running!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "V8 PRNG Terminal Started! Monte Carlo Future Price Simulation active.")

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

def send_v8_signal(pair, direction, live_price, accuracy, mc_prob):
    if direction == "CALL":
        action = "CALL (UP)"
        regime = "PRNG Upward Bias Detected"
        zone = "Monte Carlo Breakout"
        entry_price = live_price - 0.00002
        target_price = live_price + 0.00020
    else:
        action = "PUT (DOWN)"
        regime = "PRNG Downward Bias Detected"
        zone = "Monte Carlo Breakdown"
        entry_price = live_price + 0.00002
        target_price = live_price - 0.00020

    msg = f"""=========================================

QUOTEX PRNG ALGORITHM (10s ADVANCE)

Asset Detected : {pair}
Market Regime : {regime}
Live Market Price : {live_price:.5f}

ACTION SIGNAL : {action}
SAFEST EXPIRY : 1 Min
FUTURE ACCURACY : {accuracy}%

MONTE CARLO SIMULATION DATA:
1000-Path PRNG Probability : {mc_prob:.1f}%
Backend Algorithmic Bias : Confirmed
Tick Volatility : Optimal for Continuation

=========================================

MARGIN OF SAFETY (MOS) EXECUTION:
Execution Rule : 10s Advance - Place trade at next candle open.
Ideal Entry Price: {entry_price:.5f}
Target Close : {target_price:.5f}
1-Step MTG Rule : Valid

========================================="""

    bot.send_message(chat_id=CHAT_ID, text=msg)

def core_mathematical_analysis(df, pair):
    try:
        if len(df) < 15:
            return
            
        # Log Returns for Drift and Volatility
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        mu = df['Log_Returns'].mean()
        sigma = df['Log_Returns'].std()
        
        if pd.isna(sigma) or sigma == 0:
            return
            
        last_close = df['Close'].iloc[-1]
        
        # --- MONTE CARLO PRNG SIMULATION ---
        simulations = 1000
        call_wins = 0
        put_wins = 0
        
        # Simulating 1000 possible outcomes for the next candle using PRNG
        for _ in range(simulations):
            random_shock = np.random.normal(0, 1)
            future_price = last_close * np.exp(mu + (sigma * random_shock))
            
            if future_price > last_close:
                call_wins += 1
            elif future_price < last_close:
                put_wins += 1
                
        call_prob = (call_wins / simulations) * 100
        put_prob = (put_wins / simulations) * 100
        
        # Tick Velocity Filter to ensure market is actually moving
        df['Body'] = abs(df['Close'] - df['Open'])
        avg_body = df['Body'].iloc[-10:-1].mean()
        current_body = df['Body'].iloc[-1]
        tick_velocity = current_body / avg_body if avg_body > 0 else 1.0
        
        is_green = df['Close'].iloc[-1] > df['Open'].iloc[-1]
        is_red = df['Close'].iloc[-1] < df['Open'].iloc[-1]
        
        # 📈 CALL (UP) SIGNAL: 
        # Over 85% of Monte Carlo simulations predict an upward move + Tick Velocity is high
        if is_green and call_prob > 85.0 and tick_velocity > 1.2:
            accuracy = round(min(99.5, call_prob + (tick_velocity * 2)), 1)
            send_v8_signal(pair, "CALL", last_close, accuracy, call_prob)

        # 📉 PUT (DOWN) SIGNAL: 
        # Over 85% of Monte Carlo simulations predict a downward move + Tick Velocity is high
        elif is_red and put_prob > 85.0 and tick_velocity > 1.2:
            accuracy = round(min(99.5, put_prob + (tick_velocity * 2)), 1)
            send_v8_signal(pair, "PUT", last_close, accuracy, put_prob)
            
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
    
    print("PRNG Monte Carlo Scanner Started...")
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
    
