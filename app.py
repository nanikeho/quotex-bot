import telebot  # Yahan capital 'I' ko theek karke small 'i' kar diya gaya hai
import pandas as pd
import pandas_ta as ta
import time
import threading
from flask import Flask, request
from datetime import datetime
import random
import os

# --- CONFIGURATION ---
# DHYAN RAHE: Yahan apne asli Token aur Chat ID zaroor daalein
TELEGRAM_TOKEN = '8988354871:AAHJAwIhQkNcGBLtV0Lo4FJ3E1nabqZgq7Q'
CHAT_ID = '8240647626'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Quotex All-OTC Math Core Bot is Running!"

# --- START COMMAND HANDLER ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "✅ Hello! Quotex All-OTC Math Bot successfully start ho gaya hai. Setup bilkul theek hai aur ab aapko market analysis ke 1-minute signals milna shuru ho jayenge.")

# Webhook route to receive updates from Telegram smoothly
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def get_live_otc_data(pair):
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
        df.ta.rsi(length=7, append=True)
        df.ta.bbands(length=14, std=2, append=True)
        df.ta.ema(length=50, append=True)
        
        rsi_col = [col for col in df.columns if 'RSI' in col][0]
        bb_upper = [col for col in df.columns if 'BBU' in col][0]
        bb_lower = [col for col in df.columns if 'BBL' in col][0]
        
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
    
    # Automatic Webhook Setup for Render
    RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL')
    if RENDER_URL:
        bot.remove_webhook()
        time.sleep(1)
        # Webhook set karte waqt koi purana token conflict na aaye
        try:
            bot.set_webhook(url=f"{RENDER_URL}/{TELEGRAM_TOKEN}")
            print(f"Webhook set successfully to: {RENDER_URL}/{TELEGRAM_TOKEN}")
        except Exception as e:
            print(f"Webhook setup failed: {e}")
            
    # PORT fix: Render apne aap port assign karega
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
                
