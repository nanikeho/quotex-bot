import telebot
import pandas as pd
import pandas_ta as ta
import time
import threading
from flask import Flask, request
from datetime import datetime
import random

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8754386975:AAHwL6pGKo9YD4tqkseiwMC3jOnjkRJ8ZFU'
CHAT_ID = '5016643207'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Quotex All-OTC Math Core Bot is Running!"

# Webhook route to prevent 409 Conflict Error
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def get_live_otc_data(pair):
    """
    Dummy OHLC generator for math analysis simulation.
    Real data ke liye yahan quotexapi WebSocket wrapper connect karein.
    """
    data = []
    base_price = 1.0500
    for i in range(50):
        open_p = base_price
        close_p = open_p + random.uniform(-0.0010, 0.0010)
        high_p = max(open_p, close_p) + random.uniform(0, 0.0006)
        low_p = min(open_p, close_p) - random.uniform(0, 0.0006)
        data.append([open_p, high_p, low_p, close_p])
        base_price = close_p
        
    df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close'])
    return df

def core_mathematical_analysis(df, pair):
    try:
        # Core Mathematics Indicators for 1-Min Expiry
        df.ta.rsi(length=7, append=True)
        df.ta.bbands(length=14, std=2, append=True)
        df.ta.ema(length=50, append=True)
        
        rsi_col = [col for col in df.columns if 'RSI' in col][0]
        bb_upper = [col for col in df.columns if 'BBU' in col][0]
        bb_lower = [col for col in df.columns if 'BBL' in col][0]
        ema_col = [col for col in df.columns if 'EMA' in col][0]
        
        last = df.iloc[-1]
        
        close_p = last['Close']
        open_p = last['Open']
        high_p = last['High']
        low_p = last['Low']
        
        body_size = abs(close_p - open_p)
        upper_wick = high_p - max(close_p, open_p)
        lower_wick = min(close_p, open_p) - low_p
        
        is_green = close_p > open_p
        is_red = close_p < open_p
        
        # 📉 1-MIN PUT (DOWN) MATH SIGNAL
        # Math condition: Price upper Bollinger Band ko cross kare, RSI extreme overbought ho, aur rejection wick ho.
        if (close_p >= last[bb_upper] and 
            last[rsi_col] > 79 and 
            is_green and 
            upper_wick > body_size):
            
            msg = (f"📉 *1-MIN PUT (DOWN) SIGNAL*\n\n"
                   f"📊 Pair: {pair}\n"
                   f"⏱ Expiry: 1 Minute\n"
                   f"⚙️ Math Core: BB Upper Breach + RSI Overbought + Wick Rejection")
            bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

        # 📈 1-MIN CALL (UP) MATH SIGNAL
        # Math condition: Price lower Bollinger Band ko cross kare, RSI extreme oversold ho, aur lower rejection wick ho.
        elif (close_p <= last[bb_lower] and 
              last[rsi_col] < 21 and 
              is_red and 
              lower_wick > body_size):
            
            msg = (f"📈 *1-MIN CALL (UP) SIGNAL*\n\n"
                   f"📊 Pair: {pair}\n"
                   f"⏱ Expiry: 1 Minute\n"
                   f"⚙️ Math Core: BB Lower Breach + RSI Oversold + Wick Rejection")
            bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
            
    except Exception as e:
        pass

def signal_scanner():
    # Quotex ke sabhi major aur popular OTC pairs ki complete list (No manual selection needed)
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
    
    print("All-OTC Core Math Scanner Started...")
    while True:
        current_second = time.localtime().tm_sec
        # Har 1-minute ki candle close hone se 5 second pehle (55th second) sabhi pairs scan honge
        if current_second == 55: 
            for pair in all_otc_pairs:
                df = get_live_otc_data(pair)
                if not df.empty:
                    core_mathematical_analysis(df, pair)
            time.sleep(2) 
        time.sleep(0.5)

if __name__ == "__main__":
    scanner_thread = threading.Thread(target=signal_scanner)
    scanner_thread.start()
    
    app.run(host="0.0.0.0", port=8080)
    
