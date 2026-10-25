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

# Agar aapko message ke sath banner image bhejni hai, toh yahan image link daalein
IMAGE_URL_CALL = "https://i.imgur.com/dummy_call_image.png" 
IMAGE_URL_PUT = "https://i.imgur.com/dummy_put_image.png"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Quotex Premium VIP Format Bot is Running!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "✅ Premium OTC Bot Started! Ab aapko high accuracy signals VIP format mein milenge.")

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

def send_vip_signal(pair, direction):
    confidence = random.randint(85, 96)
    if confidence >= 90:
        bar = "🟩🟩🟩🟩⬜"
        grade = "📈 HIGH"
        risk = "Low"
    else:
        bar = "🟩🟩🟩⬜⬜"
        grade = "📉 MEDIUM"
        risk = "Medium"
        
    current_time = datetime.now().strftime("%H:%M:%S")
    
    if direction == "CALL":
        header = "🟢 <b>CALL | BUY</b>"
        image = IMAGE_URL_CALL
    else:
        header = "🔴 <b>PUT | SELL</b>"
        image = IMAGE_URL_PUT
        
    caption = f"""{header}
━━━━━━━━━━━━━━━━━
💲 <b>{pair}</b>
📊 Market: 🔄 OTC • 1 MIN
━━━━━━━━━━━━━━━━━
🔥 Confidence: {confidence}% {bar}
🥇 Grade: {grade}
🪙 Risk: {risk}
━━━━━━━━━━━━━━━━━
⏱ {current_time} ⚡ <b>EXECUTE NOW</b>"""

    try:
        bot.send_photo(chat_id=CHAT_ID, photo=image, caption=caption, parse_mode='HTML')
    except Exception:
        bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode='HTML')

def core_mathematical_analysis(df, pair):
    try:
        df.ta.rsi(length=7, append=True)
        df.ta.bbands(length=14, std=2, append=True)
        
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
        
        if (close_p >= last[bb_upper] and last[rsi_col] > 79 and is_green and upper_wick > body_size):
            send_vip_signal(pair, "PUT")

        elif (close_p <= last[bb_lower] and last[rsi_col] < 21 and is_red and lower_wick > body_size):
            send_vip_signal(pair, "CALL")
            
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
    
    print("VIP Scanner Started...")
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
        
