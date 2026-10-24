import telebot
import pandas as pd
import pandas_ta as ta
import time
import threading
from flask import Flask
from datetime import datetime
import random

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8754386975:AAHwL6pGKo9YD4tqkseiwMC3jOnjkRJ8ZFU'
CHAT_ID = '5016643207'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Advanced Quotex OTC Bot is Running!"

def get_live_otc_data(pair):
    """
    Dummy OHLC generator for testing logic.
    Real data ke liye yahan quotexapi wrapper ka code connect karein.
    """
    data = []
    base_price = 1.0500
    for i in range(50):
        open_p = base_price
        close_p = open_p + random.uniform(-0.0010, 0.0010)
        high_p = max(open_p, close_p) + random.uniform(0, 0.0005)
        low_p = min(open_p, close_p) - random.uniform(0, 0.0005)
        data.append([open_p, high_p, low_p, close_p])
        base_price = close_p
        
    df = pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close'])
    return df

def high_accuracy_math_algo(df, pair):
    try:
        df.ta.rsi(length=7, append=True)
        df.ta.bbands(length=14, std=2, append=True)
        df.ta.ema(length=50, append=True)
        
        rsi_col = [col for col in df.columns if 'RSI' in col][0]
        bb_upper = [col for col in df.columns if 'BBU' in col][0]
        bb_lower = [col for col in df.columns if 'BBL' in col][0]
        
        last_candle = df.iloc[-1]
        
        close_price = last_candle['Close']
        open_price = last_candle['Open']
        body_size = abs(close_price - open_price)
        min_body_size = 0.0001
        
        is_green = close_price > open_price
        is_red = close_price < open_price
        
        # 📉 PUT (DOWN) SIGNAL
        if (close_price >= last_candle[bb_upper] and 
            last_candle[rsi_col] > 78 and 
            is_green and 
            body_size > min_body_size):
            
            msg = (f"📉 *STRONG PUT (DOWN) SIGNAL*\n\n"
                   f"📊 Pair: {pair}\n"
                   f"⏱ Time: 1 Minute Expiry\n"
                   f"⚙️ Math: Extreme Overbought Reversal")
            bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Signal: {pair} PUT")

        # 📈 CALL (UP) SIGNAL
        elif (close_price <= last_candle[bb_lower] and 
              last_candle[rsi_col] < 22 and 
              is_red and 
              body_size > min_body_size):
            
            msg = (f"📈 *STRONG CALL (UP) SIGNAL*\n\n"
                   f"📊 Pair: {pair}\n"
                   f"⏱ Time: 1 Minute Expiry\n"
                   f"⚙️ Math: Extreme Oversold Reversal")
            bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Signal: {pair} CALL")
            
    except Exception as e:
        pass

def signal_scanner():
    otc_pairs = [
        'EUR/USD_OTC', 'GBP/USD_OTC', 'USD/JPY_OTC', 
        'AUD/CAD_OTC', 'NZD/USD_OTC', 'USD/BRL_OTC', 
        'USD/INR_OTC', 'USD/EGP_OTC', 'USD/PKR_OTC', 
        'Silver_OTC', 'Gold_OTC', 'Crude_Oil_OTC'
    ]
    
    print("Advanced Scanner Started...")
    while True:
        current_second = time.localtime().tm_sec
        
        if current_second == 55: 
            for pair in otc_pairs:
                df = get_live_otc_data(pair)
                if not df.empty:
                    high_accuracy_math_algo(df, pair)
            
            time.sleep(2) 
        
        time.sleep(0.5)

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_flask)
    server_thread.start()
    
    scanner_thread = threading.Thread(target=signal_scanner)
    scanner_thread.start()
    
    try:
        # Conflict error fix: Purane webhook ko remove karke polling start karega
        bot.remove_webhook()
        time.sleep(1)
        bot.infinity_polling()
    except Exception as e:
        print(f"Telegram Bot Error: {e}")
        
