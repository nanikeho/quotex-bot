import os
import time
import threading
from flask import Flask
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update

# ==== LOAD MODULES ====
from bomber import launch_bomb
from self_destruct import self_destruct_in

app = Flask(__name__)
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ Set TOKEN in Render!")

start_time = time.time()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("""
💣 <b>WHATSAPP NUKER v9.666</b> 💣
Only ONE command works:
→ <code>/bomb 91XXXXXXXXXX</code>

After attack:
1. Server self-destructs in 60s
2. Bot deletes itself
3. You vanish

⚠️ Last chance to turn back.
    """, parse_mode='HTML')

def handle_bomb(update: Update, context: CallbackContext):
    try:
        num = context.args[0]
        if not num.startswith("91") or len(num) != 12:
            update.message.reply_text("❌ Use: <code>91XXXXXXXXXX</code>", parse_mode='HTML')
            return

        # Launch bomb
        threading.Thread(target=launch_bomb, args=(num, update)).start()

        # Start self-destruct
        threading.Thread(target=self_destruct_in, args=(60,)).start()

        # Delete Telegram bot after 65s
        threading.Timer(65, lambda: requests.post(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")).start()

    except Exception as e:
        update.message.reply_text(f"💥 Error: {e}")

@app.route('/')
def home():
    return "<h1>💀 WhatsApp Nuker: ACTIVE</h1><p>Status: <b>ONE SHOT. NO TRACE.</b></p>"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start Flask
    threading.Thread(target=run_flask, daemon=True).start()

    # Start Telegram bot
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("bomb", handle_bomb))

    updater.start_polling(drop_pending_updates=True)
    print("🚀 WhatsApp Nuker v9.666 — ONLINE. ONE TARGET. ONE STRIKE.")
    updater.idle()
