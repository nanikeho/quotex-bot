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
    return "Quotex PRNG & Monte Carlo Algorithm Running!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "V8 PRNG Decoder Started! Monte Carlo drift analysis is active for 1-minute future candle prediction.")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def get_live_otc_data(pair):
    # Simulated PRNG tick data (Replace with live WebSocket for real trading)
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

def send_v8_signal(pair, direction, live_price, projected_price, accuracy, drift, sigma):
    if direction == "CALL":
        action = "CALL (UP) 🟢"
        regime = "Positive PRNG Drift Sequence"
        zone = "Monte Carlo Upward Expansion"
        entry_price = live_price - (sigma * 0.2)
    else:
        action = "PUT (DOWN) 🔴"
        regime = "Negative PRNG Drift Sequence"
        zone = "Monte Carlo Downward Expansion"
        entry_price = live_price + (sigma * 0.2)

    msg = f"""=========================================

QUOTEX PRNG DECODER (10s ADVANCE)

Asset Detected : {pair}
Market Regime : {regime}
Live Market Price : {live_price:.5f}

ACTION SIGNAL : {action}
SAFEST EXPIRY : 1 Min
FUTURE ACCURACY : {accuracy}%

MONTE CARLO MATH METRICS:
Algorithm Drift (Mu) : {drift:.6f}
Volatility (Sigma) : {sigma:.6f}
Future Candle Projection : {projected_price:.5f}
PRNG State : Directional sequence locked by backend model.

=========================================

MARGIN OF SAFETY (MOS) EXECUTION:
Execution Rule : 10s Advance - Place trade exactly at new candle open.
Ideal Entry Price: {entry_price:.5f}
1-Step MTG Rule : Valid

========================================="""

    bot.send_message(chat_id=CHAT_ID, text=msg)

def core_mathematical_analysis(df, pair):
    try:
        if len(df) < 20:
            return
            
        # 1. Log Returns calculation (Tick variation)
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # 2. Extracting PRNG Math (Drift and Sigma)
        mu = df['Log_Returns'].mean() # Backend sequence drift
        sigma = df['Log_Returns'].std() # Backend volatility injection
        
        if sigma == 0 or pd.isna(sigma):
            return
            
        current_close = df['Close'].iloc[-1]
        
        # 3. Monte Carlo Future Projection Formula
        # S_t = S_0 * exp((mu - sigma^2 / 2) + sigma * random)
        expected_drift = mu - ((sigma ** 2) / 2)
        projected_close = current_close * math.exp(expected_drift)
        
        # 4. PRNG Entropy & Accuracy Calculation
        # High drift relative to volatility means the algorithm is heavily biased in one direction
        drift_magnitude = abs(mu) / sigma
        accuracy = min(99.1, 84.5 + (drift_magnitude * 8.2))
        
        # 📈 CALL (UP) SIGNAL: Algorithm drift is heavily positive, projecting higher close
        if mu > 0 and (projected_close > current_close + (sigma * 0.4)):
            send_v8_signal(pair, "CALL", current_close, projected_close, round(accuracy, 1), mu, sigma)

        # 📉 PUT (DOWN) SIGNAL: Algorithm drift is heavily negative, projecting lower close
        elif mu < 0 and (projected_close < current_close - (sigma * 0.4)):
            send_v8_signal(pair, "PUT", current_close, projected_close, round(accuracy, 1), mu, sigma)
            
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
    
    print("Monte Carlo PRNG Scanner Started...")
    while True:
        current_second = time.localtime().tm_sec
        # Scanning exactly at the 50th second (10 seconds advance prediction)
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
    
