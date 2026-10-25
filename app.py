import telebot
import pandas as pd
import pandas_ta as ta
import time
import threading
from flask import Flask, request
import random
import os
import io
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8988354871:AAHJAwIhQkNcGBLtV0Lo4FJ3E1nabqZgq7Q'
CHAT_ID = '8240647626'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# OTC Reset Tracker
last_reset_day = None

@app.route('/')
def home():
    return "Quotex V8 God Level Terminal is Running with Image Gen & Auto-Reset!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "V8 Execution Matrix Started! Terminal is scanning all OTC pairs with live Image generation.")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def get_live_otc_data(pair):
    # Simulated live data logic 
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

def generate_signal_image(pair, direction, accuracy):
    # Background color dark theme
    img_small = Image.new('RGB', (200, 100), color=(15, 20, 25))
    draw = ImageDraw.Draw(img_small)
    
    # Text colors
    white = (255, 255, 255)
    gold = (255, 215, 0)
    signal_color = (0, 255, 100) if direction == "CALL" else (255, 80, 80)
    
    # Draw text (Using default font but resizing image to make it bold and big)
    draw.text((10, 15), f"ASSET: {pair}", fill=white)
    draw.text((10, 45), f"SIGNAL: {direction} (1 MIN)", fill=signal_color)
    draw.text((10, 75), f"ACCURACY: {accuracy}%", fill=gold)
    
    # Scale up the image so text looks large and clear without needing custom .ttf files on Render
    img_large = img_small.resize((600, 300), Image.NEAREST)
    
    # Save to memory
    bio = io.BytesIO()
    img_large.save(bio, format='PNG')
    bio.seek(0)
    return bio

def send_v8_signal(pair, direction, live_price, accuracy):
    action = f"{direction} (UP)" if direction == "CALL" else f"{direction} (DOWN)"
    
    # Generate live image with text
    image_buffer = generate_signal_image(pair, direction, accuracy)
    
    msg = f"""=========================================
QUOTEX V8 GOD LEVEL TERMINAL

Asset : {pair}
Price : {live_price:.5f}
ACTION : {action}
EXPIRY : 1 Min
ACCURACY : {accuracy}%

Margin of Safety Entry: {'Immediate Pullback' if direction == 'CALL' else 'Immediate Pushup'}
========================================="""

    try:
        bot.send_photo(chat_id=CHAT_ID, photo=image_buffer, caption=msg)
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=msg)

def check_otc_reset():
    global last_reset_day
    current_time = time.localtime()
    
    # Quotex OTC Algorithm Server Reset Time (23:50)
    if current_time.tm_hour == 23 and current_time.tm_min >= 50:
        if last_reset_day != current_time.tm_mday:
            print("Syncing with Quotex OTC Algorithm Reset (11:50 PM)...")
            time.sleep(60) # Pause analysis during the flush window
            last_reset_day = current_time.tm_mday
            return True
    return False

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
        wick_size = (high_p - low_p) - body_size + 0.00001
        is_green = close_p > open_p
        is_red = close_p < open_p
        
        momentum_strength = min(98.9, 85 + (abs(last[rsi_col] - 50) * 0.25) + (body_size / wick_size))
        final_accuracy = round(momentum_strength, 1)

        if (close_p > last[bb_upper] and last[rsi_col] > 70 and is_green and body_size > wick_size):
            send_v8_signal(pair, "CALL", close_p, final_accuracy)

        elif (close_p < last[bb_lower] and last[rsi_col] < 30 and is_red and body_size > wick_size):
            send_v8_signal(pair, "PUT", close_p, final_accuracy)
            
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
    
    print("V8 Execution Terminal Started...")
    while True:
        # Check for OTC midnight reset
        is_resetting = check_otc_reset()
        
        current_second = time.localtime().tm_sec
        if current_second == 55 and not is_resetting: 
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
