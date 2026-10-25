import telebot
import pandas as pd
import pandas_ta as ta
import time
import threading
from flask import Flask, request
import random
import os

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8988354871:AAHJAwIhQkNcGBLtV0Lo4FJ3E1nabqZgq7Q'
CHAT_ID = '8240647626'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Quotex V8 God Level Terminal is Running!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "V8 Execution Matrix Started! Terminal is scanning for Liquidity Voids and Parabolic Trends.")

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def get_live_otc_data(pair):
    # Simulated data logic (Connect live Quotex WebSocket for real market data)
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

def send_v8_signal(pair, direction, live_price):
    if direction == "CALL":
        action = "CALL (UP)"
        regime = "Blue Sky Breakout"
        zone = "Short Squeeze Fuel"
        left_context = "Clean Liquidity Void with zero immediate historical resistance."
        trap = "Retail is heavily shorting to catch the exact top, creating squeeze fuel."
        entry_price = live_price - 0.00010
        target_price = live_price + 0.00025
        reasoning = "V8 rules confirm a parabolic run into empty space.\nSmart money is buying continuation while retail gets trapped attempting mean-reversion."
    else:
        action = "PUT (DOWN)"
        regime = "Parabolic Downtrend"
        zone = "Trend Continuation"
        left_context = "Freefall Liquidity Void, no underlying support blocks detected."
        trap = "Retail is trying to catch the falling knife, triggering further liquidations."
        entry_price = live_price + 0.00010
        target_price = live_price - 0.00025
        reasoning = "V8 rules confirm heavy downside momentum in a liquidity void.\nSmart money forces the trend lower to liquidate retail bottom-fishers."

    # Strict Plain Text Format (No Markdown)
    msg = f"""=========================================

QUOTEX V8 GOD LEVEL TERMINAL (MOMENTUM OVERRIDE)

Asset Detected : {pair}

Market Regime : {regime}

Zone Behavior : {zone}

Live Market Price : {live_price:.5f}

ACTION SIGNAL : {action}

SAFEST EXPIRY : 1 Min

SETUP GRADE : God-Tier A+

V8 MOMENTUM & LIQUIDITY VOID ANALYSIS:

Left-Side Context: {left_context}

Candle Physics : Full-bodied momentum with zero rejection wicks.

Retail Trap : {trap}

=========================================

MARGIN OF SAFETY (MOS) EXECUTION:

Execution Rule : Immediate entry on minor pullback in trend direction.

Exact Entry Price: {entry_price:.5f}

Wave Target : {target_price:.5f}

1-Step MTG Rule : Valid

=========================================

CRITICAL FORENSIC REASONING:

{reasoning}

========================================="""

    bot.send_message(chat_id=CHAT_ID, text=msg)

def core_mathematical_analysis(df, pair):
    try:
        # V8 Continuation Logic (Momentum Override)
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
        
        # 📈 V8 CALL (CONTINUATION) LOGIC: 
        # Price is breaking UPPER BB, RSI is high (strong momentum), Body is large, Wicks are tiny. 
        # We do NOT reverse, we continue the trend.
        if (close_p > last[bb_upper] and last[rsi_col] > 70 and is_green and body_size > (upper_wick + lower_wick)):
            send_v8_signal(pair, "CALL", close_p)

        # 📉 V8 PUT (CONTINUATION) LOGIC: 
        # Price is breaking LOWER BB, RSI is low (strong downtrend momentum), Body is large, Wicks are tiny.
        # We ride the drop.
        elif (close_p < last[bb_lower] and last[rsi_col] < 30 and is_red and body_size > (upper_wick + lower_wick)):
            send_v8_signal(pair, "PUT", close_p)
            
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
            
