import telebot
import pandas as pd
import pandas_ta as ta
import time
import threading
from flask import Flask
from datetime import datetime
import random # Placeholder for real API data

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
    (Yahan apne Quotex WebSocket wrapper ka code add karein)
    Dummy OHLC generator for testing logic:
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
    """
    Advanced Mathematical Logic for High Accuracy:
    1. BB (14, 2) - Mean Reversion breakout.
    2. RSI (7) - Momentum Exhaustion.
    3. EMA (50) - Trend filter.
    4. Body Volume - Minimum candle body size required (avoids Doji traps).
    """
    try:
        # Technical Indicators calculation
        df.ta.rsi(length=7, append=True)
        df.ta.bbands(length=14, std=2, append=True)
        df.ta.ema(length=50, append=True)
        
        rsi_col = [col for col in df.columns if 'RSI' in col][0]
        bb_upper = [col for col in df.columns if 'BBU' in col][0]
        bb_lower = [col for col in df.columns if 'BBL' in col][0]
        ema_col = [col for col in df.columns if 'EMA' in col][0]
        
        last_candle = df.iloc[-1]
        
        # Core Variables
        close_price = last_candle['Close']
        open_price = last_candle['Open']
        body_size = abs(close_price - open_price)
        min_body_size = 0.0001 # Filter for flat markets/dojis
        
        is_green = close_price > open_price
        is_red = close_price < open_price
        
        # 📉 HIGH ACCURACY PUT (DOWN) SIGNAL
        # Condition: Price BB ke upar ho, RSI > 78 (Extreme), Candle Green ho aur decent size ki ho.
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

        # 📈 HIGH ACCURACY CALL (UP) SIGNAL
        # Condition: Price BB ke niche ho, RSI < 22 (Extreme), Candle Red ho aur decent size ki ho.
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
        pass # Ignore errors to keep loop running

def signal_scanner():
    # 12 Most traded Quotex OTC pairs
    otc_pairs = [
        'EUR/USD_OTC', 'GBP/USD_OTC', 'USD/JPY_OTC', 
        'AUD/CAD_OTC', 'NZD/USD_OTC', 'USD/BRL_OTC', 
        'USD/INR_OTC', 'USD/EGP_OTC', 'USD/PKR_OTC', 
        'Silver_OTC', 'Gold_OTC', 'Crude_Oil_OTC'
    ]
    
    print("Advanced Scanner Started...")
    while True:
        current_second = time.localtime().tm_sec
        
        # Exactly 5 seconds before candle closes (55th second)
        if current_second == 55: 
            for pair in otc_pairs:
                df = get_live_otc_data(pair)
                if not df.empty:
                    high_accuracy_math_algo(df, pair)
            
            # 2 second sleep taaki same second mein do baar loop na chale
            time.sleep(2) 
        
        time.sleep(0.5) # Fast checking loop

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_flask)
    server_thread.start()
    
    scanner_thread = threading.Thread(target=signal_scanner)
    scanner_thread.start()
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Telegram Bot Error: {e}")
        
