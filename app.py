import os
import time
import threading
import asyncio
import requests
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from flask import Flask
from quotexpy import Quotex
import undetected_chromedriver as uc

# --- FIX FOR QUOTEXPY CHROME CRASH ON RENDER ---
os.environ["PATH"] += os.pathsep + "/opt/render/project/free/chrome/opt/google/chrome"
os.environ["CHROME_EXECUTABLE_PATH"] = "/opt/render/project/free/chrome/opt/google/chrome/google-chrome"
os.environ["CHROME_BINARY_LOCATION"] = "/opt/render/project/free/chrome/opt/google/chrome/google-chrome"

original_init = uc.Chrome.__init__
def patched_init(self, *args, **kwargs):
    options = kwargs.get('options')
    if not options:
        options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless=new')
    kwargs['options'] = options
    original_init(self, *args, **kwargs)

uc.Chrome.__init__ = patched_init

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8754386975:AAGpsRdk84bP7dFQTiEPF2JmkjQHNhPVPPU")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5016643207")
QUOTEX_EMAIL = os.environ.get("QUOTEX_EMAIL", "nanikeho@gmail.com")
QUOTEX_PASS = os.environ.get("QUOTEX_PASS", "78907890@Ho")

OTC_PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", 
    "AUDUSD_otc", "USDCAD_otc", "NZDUSD_otc",
    "EURJPY_otc", "GBPJPY_otc"
]

class MultiPairChartBot:
    def __init__(self):
        self.client = Quotex(email=QUOTEX_EMAIL, password=QUOTEX_PASS)

    async def connect_to_quotex(self):
        print("Connecting to Quotex API (Max wait 60 seconds)...")
        try:
            # 60 second ka timeout lagaya hai taaki bot hamesha ke liye hang na ho
            check, reason = await asyncio.wait_for(self.client.connect(), timeout=60.0)
            if check:
                print("✅ Successfully connected to Quotex!")
                return True
            else:
                print(f"❌ Connection failed: {reason}")
                return False
        except asyncio.TimeoutError:
            print("❌ API Connection Timeout: Chrome background mein hang ho gaya hai (Render memory issue ho sakta hai).")
            return False
        except Exception as e:
            print(f"❌ API Connection Error: {e}")
            return False
            
    def generate_and_save_chart(self, df, pair, direction):
        plt.figure(figsize=(10, 5))
        plt.style.use('dark_background')
        
        plt.plot(df.index, df['close'], label='Price', color='#ffffff', linewidth=2)
        plt.plot(df.index, df['ema_9'], label='9 EMA', color='#00ffff', linestyle='--')
        plt.plot(df.index, df['ema_21'], label='21 EMA', color='#ff00ff', linestyle='--')
        plt.plot(df.index, df['bb_upper'], label='BB Upper', color='#ff3333', alpha=0.7)
        plt.plot(df.index, df['bb_lower'], label='BB Lower', color='#33ff33', alpha=0.7)
        
        plt.fill_between(df.index, df['bb_upper'], df['bb_lower'], color='grey', alpha=0.1)
        
        title_color = '#00ff00' if direction == 'CALL' else '#ff0000'
        plt.title(f"{pair.replace('_', '/')} - {direction} SIGNAL", color=title_color, fontsize=14, fontweight='bold')
        plt.legend(loc="upper left")
        plt.grid(color='gray', linestyle=':', alpha=0.3)
        plt.xticks([])  
        
        image_path = f"{pair}_signal.png"
        plt.savefig(image_path, bbox_inches='tight', dpi=100)
        plt.close()
        return image_path

    def send_telegram_alert(self, pair, direction, price, rsi, image_path):
        emoji = "🟢 CALL (UP)" if direction == "CALL" else "🔴 PUT (DOWN)"
        caption = (
            f"⚡ <b>QUOTEX MULTI-PAIR SIGNAL</b> ⚡\n\n"
            f"📊 <b>Asset:</b> {pair.replace('_', ' ').upper()}\n"
            f"🎯 <b>Direction:</b> {emoji}\n"
            f"💲 <b>Entry Price:</b> {price}\n"
            f"⏳ <b>Timeframe:</b> 1 Minute\n\n"
            f"📈 <b>RSI Level:</b> {round(rsi, 2)}\n"
            f"🛡️ <b>Setup:</b> EMA Cross + BB + RSI Confluence\n\n"
            f"<i>Note: Trade instantly on the next candle open.</i>"
        )
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        try:
            with open(image_path, 'rb') as photo:
                payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "HTML"}
                requests.post(url, data=payload, files={"photo": photo})
                print(f"[{time.strftime('%H:%M:%S')}] 🚀 Chart Signal Sent for {pair}")
        except Exception as e:
            print(f"Telegram Image Error: {e}")
        finally:
            if os.path.exists(image_path):
                os.remove(image_path)

    async def fetch_and_analyze(self, pair):
        try:
            # Print statement add kiya hai taaki logs mein progress dikhe
            print(f"🔍 Scanning real-time data for {pair}...")
            
            candles = await self.client.get_candles(pair, 60, 50, time.time())
            if not candles:
                print(f"⚠️ No data received for {pair}")
                return
                
            df = pd.DataFrame(candles)
            if 'time' in df.columns:
                df = df.rename(columns={'time': 'datetime'})
            df['close'] = df['close'].astype(float)
            
            df['ema_9'] = ta.ema(df['close'], length=9)
            df['ema_21'] = ta.ema(df['close'], length=21)
            df['rsi'] = ta.rsi(df['close'], length=14)
            
            bbands = ta.bbands(df['close'], length=20, std=2)
            df['bb_upper'] = bbands['BBL_20_2.0']
            df['bb_lower'] = bbands['BBL_20_2.0']

            current = df.iloc[-1]
            
            if (current['ema_9'] > current['ema_21']) and (current['close'] > current['bb_upper']) and (50 < current['rsi'] < 70):
                print(f"🟢 CALL Setup found for {pair}. Generating chart...")
                img_path = self.generate_and_save_chart(df.tail(30), pair, "CALL")
                self.send_telegram_alert(pair, "CALL", current['close'], current['rsi'], img_path)
                await asyncio.sleep(60) 
                
            elif (current['ema_9'] < current['ema_21']) and (current['close'] < current['bb_lower']) and (30 < current['rsi'] < 50):
                print(f"🔴 PUT Setup found for {pair}. Generating chart...")
                img_path = self.generate_and_save_chart(df.tail(30), pair, "PUT")
                self.send_telegram_alert(pair, "PUT", current['close'], current['rsi'], img_path)
                await asyncio.sleep(60)
        except Exception as e:
            print(f"Error analyzing {pair}: {e}")

    async def run(self):
        connected = await self.connect_to_quotex()
        
        # Agar connect nahi hua toh bot aage nahi badhega
        if not connected:
            print("Bot stopped due to connection failure. Please check logs.")
            return

        print("Multi-Pair Scanner & Charting Engine Started Successfully!")
        
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                data={"chat_id": TELEGRAM_CHAT_ID, "text": "🟢 <b>Quotex AI Engine Online</b>\nScanning pairs successfully connected.", "parse_mode": "HTML"}
            )
        except Exception:
            pass

        while True:
            for pair in OTC_PAIRS:
                await self.fetch_and_analyze(pair)
                await asyncio.sleep(2)
            print("--- Completed one full cycle. Waiting 10 seconds before next scan ---")
            await asyncio.sleep(10)

# --- FLASK SERVER FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Quotex Bot is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    
    bot = MultiPairChartBot()
    asyncio.run(bot.run())
    
