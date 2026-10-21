import os
import time
import threading
import requests
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from flask import Flask
from quotexpy import Quotex  # Unofficial Quotex API

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8754386975:AAGpsRdk84bP7dFQTiEPF2JmkjQHNhPVPPU")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5016643207")
QUOTEX_EMAIL = os.environ.get("QUOTEX_EMAIL", "nanikeho@gmail.com")
QUOTEX_PASS = os.environ.get("QUOTEX_PASS", "78907890@Ho")

# Multiple OTC Pairs to scan
OTC_PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", 
    "AUDUSD_otc", "USDCAD_otc", "NZDUSD_otc",
    "EURJPY_otc", "GBPJPY_otc"
]

class MultiPairChartBot:
    def __init__(self):
        self.client = Quotex(email=QUOTEX_EMAIL, password=QUOTEX_PASS)
        self.connect_to_quotex()

    def connect_to_quotex(self):
        print("Connecting to Quotex API...")
        check, reason = self.client.connect()
        if check:
            print("Successfully connected to Quotex!")
        else:
            print(f"Connection failed: {reason}")

    def generate_and_save_chart(self, df, pair, direction):
        """Matplotlib ka use karke dark theme real-time chart draw karna"""
        plt.figure(figsize=(10, 5))
        plt.style.use('dark_background')
        
        # Plot price line and indicators
        plt.plot(df.index, df['close'], label='Price', color='#ffffff', linewidth=2)
        plt.plot(df.index, df['ema_9'], label='9 EMA', color='#00ffff', linestyle='--')
        plt.plot(df.index, df['ema_21'], label='21 EMA', color='#ff00ff', linestyle='--')
        plt.plot(df.index, df['bb_upper'], label='BB Upper', color='#ff3333', alpha=0.7)
        plt.plot(df.index, df['bb_lower'], label='BB Lower', color='#33ff33', alpha=0.7)
        
        # Fill Bollinger Bands area
        plt.fill_between(df.index, df['bb_upper'], df['bb_lower'], color='grey', alpha=0.1)
        
        # Chart formatting
        title_color = '#00ff00' if direction == 'CALL' else '#ff0000'
        plt.title(f"{pair.replace('_', '/')} - {direction} SIGNAL", color=title_color, fontsize=14, fontweight='bold')
        plt.legend(loc="upper left")
        plt.grid(color='gray', linestyle=':', alpha=0.3)
        plt.xticks([])  # Hide x-axis time labels for cleaner look
        
        # Save image
        image_path = f"{pair}_signal.png"
        plt.savefig(image_path, bbox_inches='tight', dpi=100)
        plt.close()
        return image_path

    def send_telegram_alert(self, pair, direction, price, rsi, image_path):
        """Telegram par photo aur mathematical stats bhejna"""
        emoji = "🟢 CALL (UP)" if direction == "CALL" else "🔴 PUT (DOWN)"
        caption = (
            f"⚡ <b>QUOTEX MULTI-PAIR SIGNAL</b> ⚡\n\n"
            f"📊 <b>Asset:</b> {pair.replace('_', ' ').upper()}\n"
            f"🎯 <b>Direction:</b> {emoji}\n"
            f"💲 <b>Entry Price:</b> {price}\n"
            f"⏳ <b>Timeframe:</b> 1 Minute\n\n"
            f"📈 <b>RSI Level:</b> {round(rsi, 2)}\n"
            f"🛡️ <b>Setup:</b> EMA Cross + BB + RSI Confluence\n\n"
            f"<i>Note: Trade instantly on the next candle open. Use 1-step MTG if needed.</i>"
        )
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        try:
            with open(image_path, 'rb') as photo:
                payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "HTML"}
                response = requests.post(url, data=payload, files={"photo": photo})
                if response.status_code == 200:
                    print(f"[{time.strftime('%H:%M:%S')}] Chart Signal Sent for {pair}")
        except Exception as e:
            print(f"Telegram Image Error: {e}")
        finally:
            # File send hone ke baad server se delete kar dein taaki memory full na ho
            if os.path.exists(image_path):
                os.remove(image_path)

    def fetch_and_analyze(self, pair):
        """API se real-time 1-min candles nikal kar math calculations karna"""
        # Get last 50 candles of 1-minute (60 seconds) timeframe
        candles = self.client.get_candles(pair, 60, 50, time.time())
        
        if not candles:
            return
            
        df = pd.DataFrame(candles)
        df = df.rename(columns={'time': 'datetime'})
        df['close'] = df['close'].astype(float)
        
        # Mathematical Indicators
        df['ema_9'] = ta.ema(df['close'], length=9)
        df['ema_21'] = ta.ema(df['close'], length=21)
        df['rsi'] = ta.rsi(df['close'], length=14)
        
        bbands = ta.bbands(df['close'], length=20, std=2)
        df['bb_upper'] = bbands['BBL_20_2.0']
        df['bb_lower'] = bbands['BBL_20_2.0']

        # Last closed candle data
        current = df.iloc[-1]
        
        # High Accuracy CALL Setup
        if (current['ema_9'] > current['ema_21']) and (current['close'] > current['bb_upper']) and (50 < current['rsi'] < 70):
            # Pass last 30 candles to chart for better zoom
            img_path = self.generate_and_save_chart(df.tail(30), pair, "CALL")
            self.send_telegram_alert(pair, "CALL", current['close'], current['rsi'], img_path)
            time.sleep(60) # Usi pair par turant repeat signal rokne ke liye cooldown
            
        # High Accuracy PUT Setup
        elif (current['ema_9'] < current['ema_21']) and (current['close'] < current['bb_lower']) and (30 < current['rsi'] < 50):
            img_path = self.generate_and_save_chart(df.tail(30), pair, "PUT")
            self.send_telegram_alert(pair, "PUT", current['close'], current['rsi'], img_path)
            time.sleep(60) # Cooldown

    def run(self):
        print("Multi-Pair Scanner & Charting Engine Started!")
        
        # Startup notification
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
            data={"chat_id": TELEGRAM_CHAT_ID, "text": "🟢 <b>Quotex AI Engine Online</b>\nScanning 8+ OTC pairs for mathematical setups with real-time charts.", "parse_mode": "HTML"}
        )

        while True:
            for pair in OTC_PAIRS:
                try:
                    self.fetch_and_analyze(pair)
                except Exception as e:
                    print(f"Error on {pair}: {e}")
                
                # Quotex API par load kam rakhne ke liye har pair ke beech 2 second ka gap
                time.sleep(2)
            
            # Sabhi pairs scan hone ke baad 10 second ruk kar naya round shuru karna
            time.sleep(10)

# --- FLASK SERVER FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Quotex Multi-Pair Charting Bot is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Render port timeout bypass
    server_thread = threading.Thread(target=run_flask)
    server_thread.start()
    
    # Start the trading engine
    bot = MultiPairChartBot()
    bot.run()
