import telebot
import time
import threading
from flask import Flask, request
from datetime import datetime
import random
import os

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8988354871:AAHJAwIhQkNcGBLtV0Lo4FJ3E1nabqZgq7Q'
CHAT_ID = '8240647626'

IMAGE_URL_CALL = "https://i.imgur.com/dummy_call_image.png" 
IMAGE_URL_PUT = "https://i.imgur.com/dummy_put_image.png"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Quotex Fast Testing Bot is Running!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "✅ Fast Testing Bot Started! Ab aapko har 1 minute mein test signals milenge.")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

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
        print("Image failed, text sent.")

def test_fast_logic(pair):
    # FAST TEST: Har baar random CALL ya PUT generate karega
    direction = random.choice(["CALL", "PUT"])
    send_vip_signal(pair, direction)

def signal_scanner():
    # Testing ke liye sirf 3 pairs rakhe hain taaki Telegram spam block na kare
    test_pairs = ['EUR/USD_OTC', 'GBP/USD_OTC', 'USD/INR_OTC']
    
    print("Fast Test Scanner Started...")
    while True:
        current_second = time.localtime().tm_sec
        # Har minute ke 55th second par yeh turant signal bhej dega
        if current_second == 55: 
            # 3 mein se koi 1 random pair pick karega test signal ke liye
            pair = random.choice(test_pairs)
            test_fast_logic(pair)
            time.sleep(2) # Double trigger rokne ke liye
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
            print("Webhook Set Successfully!")
        except Exception as e:
            print(f"Webhook error: {e}")
            
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)
