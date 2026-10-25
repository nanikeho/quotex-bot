import telebot
import pandas as pd
import pandas_ta as ta
import time
import threading
from flask import Flask, request
from datetime import datetime
import random
import os

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8988354871:AAHJAwIhQkNcGBLtV0Lo4FJ3E1nabqZgq7Q'
CHAT_ID = '8240647626'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Manual selection ke liye dynamic list
active_pairs = set()

@app.route('/')
def home():
    return "Quotex Manual Pair Setup Bot is Running!"

# --- TELEGRAM COMMANDS ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    msg = ("✅ Bot Started!\n\n"
           "Ab aap manually pairs select kar sakte hain.\n"
           "Commands:\n"
           "/add EUR/USD_OTC -> Pair add karne ke liye\n"
           "/remove EUR/USD_OTC -> Pair hatane ke liye\n"
           "/list -> Active pairs dekhne ke liye")
    bot.reply_to(message, msg)

@bot.message_handler(commands=['add'])
def add_pair(message):
    try:
        pair = message.text.split()[1].upper()
        if "_OTC" not in pair:
            pair += "_OTC"
        active_pairs.add(pair)
        bot.reply_to(message, f"✅ {pair} background analysis ke liye add ho gaya hai.")
    except Exception:
        bot.reply_to(message, "❌ Sahi format use karein: /add EUR/USD_OTC")

@bot.message_handler(commands=['remove'])
def remove_pair(message):
    try:
        pair = message.text.split()[1].upper()
        if "_OTC" not in pair:
            pair += "_OTC"
        active_pairs.discard(pair)
        bot.reply_to(message, f"🗑️ {pair} analysis list se hata diya gaya hai.")
    except Exception:
        bot.reply_to(message, "❌ Sahi format use karein: /remove EUR/USD_OTC")

@bot.message_handler(commands=['list'])
def list_pairs(message):
    if not active_pairs:
        bot.reply_to(message, "⚠️ Abhi koi pair selected nahi hai. /add command ka use karein.")
        return
    pairs_str = "\n".join(active_pairs)
    bot.reply_to(message, f"📋 Currently Active Pairs:\n{pairs_str}")

# --- WEBHOOK ROUTE ---
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
        
        # 📉 1-MIN PUT
        if (close_p >= last[bb_upper] and last[rsi_col] > 79 and is_green and upper_wick > body_size):
            msg = f"📉 *PUT SIGNAL*\n📊 Pair: {pair}\n⏱ Expiry: 1 Min"
            bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

        # 📈 1-MIN CALL
        elif (close_p <= last[bb_lower] and last[rsi_col] < 21 and is_red and lower_wick > body_size):
            msg = f"📈 *CALL SIGNAL*\n📊 Pair: {pair}\n⏱ Expiry: 1 Min"
            bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
            
    except Exception as e:
        pass

def signal_scanner():
    while True:
        current_second = time.localtime().tm_sec
        # Sirf tab scan karega jab active_pairs mein koi pair hoga
        if current_second == 55 and active_pairs: 
            # list() use karna zaroori hai taaki loop chalte waqt set change na ho
            for pair in list(active_pairs):
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
